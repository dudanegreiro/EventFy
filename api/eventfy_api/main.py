import io
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4
import zipfile

import psycopg
from fastapi import Depends, FastAPI, File, Query, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from psycopg.errors import ExclusionViolation, ForeignKeyViolation, UniqueViolation

from eventfy_api.config import Settings, get_settings
from eventfy_api.database import get_connection
from eventfy_api.errors import ApiError, error_response
from eventfy_api.schemas import (
    AvailabilityCreate,
    CancellationResponse,
    DecisionResponse,
    EventCreate,
    EventResponse,
    ExpirationResponse,
    LoginRequest,
    PublicService,
    ReservationCreate,
    ReservationCancellation,
    ReservationDecision,
    ReservationHistoryEntry,
    ReservationResponse,
    ServiceCreate,
    ServiceUpdate,
    TransitionResponse,
    TokenResponse,
    UserRegistrationRequest,
    UserResponse,
    require_timezone,
)
from eventfy_api.security import create_access_token, get_current_user, require_role

app = FastAPI(
    title="EventFy API",
    version="0.1.0",
    description="API REST para catalogo, eventos e fluxo principal de reservas.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_ATTACHMENT_BYTES = 10_000_000
ATTACHMENT_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".pdf": "application/pdf",
    ".docx": (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ),
}


@app.exception_handler(ApiError)
async def handle_api_error(_: Request, exception: ApiError) -> JSONResponse:
    return JSONResponse(
        status_code=exception.status_code,
        content=error_response(exception.code, exception.message),
        headers=exception.headers,
    )


@app.exception_handler(RequestValidationError)
async def handle_validation_error(
    _: Request,
    exception: RequestValidationError,
) -> JSONResponse:
    details = [
        {
            "field": ".".join(str(part) for part in error["loc"]),
            "message": error["msg"],
            "code": error["type"],
        }
        for error in exception.errors()
    ]
    return JSONResponse(
        status_code=422,
        content=error_response(
            "VALIDATION_ERROR",
            "A requisicao contem dados invalidos.",
            details,
        ),
    )


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/auth/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    settings: Settings = Depends(get_settings),
    connection: psycopg.Connection = Depends(get_connection),
) -> TokenResponse:
    user = connection.execute(
        """
        SELECT id_usuario, tipo_usuario
        FROM public.usuario
        WHERE lower(email) = lower(%s)
          AND ativo
          AND senha_hash = crypt(%s, senha_hash)
        """,
        (request.email, request.senha),
    ).fetchone()
    if user is None:
        raise ApiError(
            401,
            "INVALID_CREDENTIALS",
            "E-mail ou senha invalidos.",
            {"WWW-Authenticate": "Bearer"},
        )
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=settings.duracao_token_minutos)
    token_id = uuid4()
    connection.execute(
        "DELETE FROM public.sessao_autenticacao WHERE expira_em <= %s",
        (now,),
    )
    connection.execute(
        """
        INSERT INTO public.sessao_autenticacao (token_id, id_usuario, expira_em)
        VALUES (%s, %s, %s)
        """,
        (token_id, user["id_usuario"], expires_at),
    )
    return TokenResponse(
        access_token=create_access_token(
            user["id_usuario"],
            user["tipo_usuario"],
            token_id,
            settings,
        )
    )


@app.post("/api/auth/register", status_code=201, response_model=UserResponse)
def register(
    request: UserRegistrationRequest,
    connection: psycopg.Connection = Depends(get_connection),
) -> dict[str, Any]:
    user = connection.execute(
        """
        INSERT INTO public.usuario (nome, email, senha_hash, tipo_usuario)
        VALUES (%s, %s, crypt(%s, gen_salt('bf', 12)), %s)
        RETURNING id_usuario, nome, email, tipo_usuario
        """,
        (
            request.nome,
            request.email,
            request.senha,
            request.tipo_usuario,
        ),
    ).fetchone()
    return user


@app.post("/api/auth/logout", status_code=204)
def logout(
    user: dict[str, Any] = Depends(get_current_user),
    connection: psycopg.Connection = Depends(get_connection),
) -> None:
    connection.execute(
        """
        UPDATE public.sessao_autenticacao
        SET revogada_em = now()
        WHERE token_id = %s AND revogada_em IS NULL
        """,
        (user["_token_id"],),
    )


def _validate_catalog_period(
    data_inicio: datetime | None,
    data_fim: datetime | None,
) -> bool:
    if (data_inicio is None) != (data_fim is None):
        raise ApiError(
            422,
            "INVALID_AVAILABILITY_FILTER",
            "Informe data_inicio e data_fim juntos para filtrar disponibilidade.",
        )
    if data_inicio is None or data_fim is None:
        return False
    try:
        require_timezone(data_inicio)
        require_timezone(data_fim)
    except ValueError as exception:
        raise ApiError(
            422,
            "INVALID_AVAILABILITY_FILTER",
            str(exception),
        ) from exception
    if data_fim <= data_inicio:
        raise ApiError(
            422,
            "INVALID_AVAILABILITY_FILTER",
            "data_fim deve ser posterior a data_inicio.",
        )
    return True


def _service_has_active_reservations(
    connection: psycopg.Connection,
    service_id: int,
) -> bool:
    return connection.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM public.reserva
            WHERE id_servico = %s
              AND ativo
              AND status IN ('SOLICITADA', 'EM_ANALISE', 'APROVADA', 'CONFIRMADA')
        ) AS possui_reservas_ativas
        """,
        (service_id,),
    ).fetchone()["possui_reservas_ativas"]


def _owned_service(
    connection: psycopg.Connection,
    service_id: int,
    user: dict[str, Any],
) -> dict[str, Any]:
    service = connection.execute(
        """
        SELECT id_servico, id_prestador, nome, categoria, descricao,
               preco, localizacao, ativo
        FROM public.servico
        WHERE id_servico = %s
        FOR UPDATE
        """,
        (service_id,),
    ).fetchone()
    if service is None:
        raise ApiError(404, "SERVICE_NOT_FOUND", "Servico nao encontrado.")
    if service["id_prestador"] != user["id_usuario"]:
        raise ApiError(403, "FORBIDDEN", "Voce nao e titular deste servico.")
    return service


def _detect_attachment_type(filename: str, content: bytes) -> str | None:
    if filename.rsplit(".", 1)[-1].lower() not in {
        extension.removeprefix(".") for extension in ATTACHMENT_TYPES
    }:
        return None

    extension = Path(filename).suffix.lower()
    if content.startswith(b"\xff\xd8\xff"):
        detected = "image/jpeg"
    elif content.startswith(b"\x89PNG\r\n\x1a\n"):
        detected = "image/png"
    elif (
        len(content) >= 12 and content.startswith(b"RIFF") and content[8:12] == b"WEBP"
    ):
        detected = "image/webp"
    elif content.startswith(b"%PDF-"):
        detected = "application/pdf"
    elif zipfile.is_zipfile(io.BytesIO(content)):
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as archive:
                names = set(archive.namelist())
        except zipfile.BadZipFile:
            return None
        if {"[Content_Types].xml", "word/document.xml"}.issubset(names):
            detected = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        else:
            return None
    else:
        return None
    if ATTACHMENT_TYPES.get(extension) != detected:
        return None
    return detected


@app.get("/api/servicos", response_model=list[PublicService])
def list_services(
    categoria: str | None = None,
    termo: str | None = Query(default=None, max_length=160),
    preco_minimo: Decimal | None = Query(default=None, ge=0),
    preco_maximo: Decimal | None = Query(default=None, ge=0),
    localizacao: str | None = Query(default=None, max_length=200),
    data_inicio: datetime | None = None,
    data_fim: datetime | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    connection: psycopg.Connection = Depends(get_connection),
) -> list[dict[str, Any]]:
    has_availability_filter = _validate_catalog_period(data_inicio, data_fim)
    if (
        preco_minimo is not None
        and preco_maximo is not None
        and preco_maximo < preco_minimo
    ):
        raise ApiError(
            422,
            "INVALID_PRICE_RANGE",
            "preco_maximo deve ser maior ou igual a preco_minimo.",
        )

    normalized_term = termo.strip() if termo and termo.strip() else None
    normalized_location = (
        localizacao.strip() if localizacao and localizacao.strip() else None
    )
    search_pattern = f"%{normalized_term}%" if normalized_term else None
    location_pattern = f"%{normalized_location}%" if normalized_location else None
    rows = connection.execute(
        """
        SELECT s.id_servico, s.nome, s.categoria, s.descricao,
               s.preco, s.id_prestador, s.localizacao, s.ativo
        FROM public.servico AS s
        WHERE s.ativo
          AND (%s::text IS NULL OR lower(s.categoria) = lower(%s))
          AND (
              %s::text IS NULL
              OR s.nome ILIKE %s
              OR coalesce(s.descricao, '') ILIKE %s
          )
          AND (%s::numeric IS NULL OR s.preco >= %s)
          AND (%s::numeric IS NULL OR s.preco <= %s)
          AND (
              %s::text IS NULL
              OR coalesce(s.localizacao, '') ILIKE %s
          )
          AND (
              NOT %s
              OR (
                  EXISTS (
                      SELECT 1
                      FROM public.disponibilidade_servico AS d
                      WHERE d.id_servico = s.id_servico
                        AND d.ativo
                        AND d.tipo = 'DISPONIVEL'
                        AND d.data_inicio <= %s
                        AND d.data_fim >= %s
                  )
                  AND NOT EXISTS (
                      SELECT 1
                      FROM public.disponibilidade_servico AS d
                      WHERE d.id_servico = s.id_servico
                        AND d.ativo
                        AND d.tipo = 'BLOQUEIO_MANUAL'
                        AND tstzrange(d.data_inicio, d.data_fim, '[)')
                            && tstzrange(%s, %s, '[)')
                  )
                  AND NOT EXISTS (
                      SELECT 1
                      FROM public.reserva AS r
                      WHERE r.id_servico = s.id_servico
                        AND r.ativo
                        AND r.status IN (
                            'SOLICITADA', 'EM_ANALISE', 'APROVADA', 'CONFIRMADA'
                        )
                        AND tstzrange(r.data_inicio, r.data_fim, '[)')
                            && tstzrange(%s, %s, '[)')
                  )
              )
          )
        ORDER BY s.id_servico
        LIMIT %s OFFSET %s
        """,
        (
            categoria,
            categoria,
            normalized_term,
            search_pattern,
            search_pattern,
            preco_minimo,
            preco_minimo,
            preco_maximo,
            preco_maximo,
            normalized_location,
            location_pattern,
            has_availability_filter,
            data_inicio,
            data_fim,
            data_inicio,
            data_fim,
            data_inicio,
            data_fim,
            limit,
            offset,
        ),
    ).fetchall()
    return rows


@app.get("/api/servicos/{service_id}", response_model=PublicService)
def get_service(
    service_id: int,
    connection: psycopg.Connection = Depends(get_connection),
) -> dict[str, Any]:
    service = connection.execute(
        """
        SELECT id_servico, nome, categoria, descricao, preco, id_prestador,
               localizacao, ativo
        FROM public.servico
        WHERE id_servico = %s AND ativo
        """,
        (service_id,),
    ).fetchone()
    if service is None:
        raise ApiError(404, "SERVICE_NOT_FOUND", "Servico nao encontrado.")
    files = connection.execute(
        """
        SELECT id_arquivo, nome_original, url, tipo_mime, tamanho
        FROM public.arquivo
        WHERE id_servico = %s AND ativo
        ORDER BY id_arquivo
        """,
        (service_id,),
    ).fetchall()
    availability = connection.execute(
        """
        SELECT data_inicio, data_fim
        FROM public.disponibilidade_servico
        WHERE id_servico = %s AND ativo AND tipo = 'DISPONIVEL'
        ORDER BY data_inicio
        """,
        (service_id,),
    ).fetchall()
    return {
        **service,
        "arquivos": files,
        "disponibilidades": availability,
    }


@app.post("/api/servicos", status_code=201, response_model=PublicService)
def create_service(
    request: ServiceCreate,
    user: dict[str, Any] = Depends(require_role("PRESTADOR")),
    connection: psycopg.Connection = Depends(get_connection),
) -> dict[str, Any]:
    return connection.execute(
        """
        INSERT INTO public.servico (
            id_prestador, nome, categoria, descricao, preco, localizacao
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id_servico, id_prestador, nome, categoria, descricao,
                  preco, localizacao, ativo
        """,
        (
            user["id_usuario"],
            request.nome,
            request.categoria,
            request.descricao,
            request.preco,
            request.localizacao,
        ),
    ).fetchone()


@app.get("/api/prestador/servicos", response_model=list[PublicService])
def list_provider_services(
    user: dict[str, Any] = Depends(require_role("PRESTADOR")),
    connection: psycopg.Connection = Depends(get_connection),
) -> list[dict[str, Any]]:
    return connection.execute(
        """
        SELECT id_servico, id_prestador, nome, categoria, descricao,
               preco, localizacao, ativo
        FROM public.servico
        WHERE id_prestador = %s
        ORDER BY id_servico
        """,
        (user["id_usuario"],),
    ).fetchall()


@app.patch("/api/servicos/{service_id}", response_model=PublicService)
def update_service(
    service_id: int,
    request: ServiceUpdate,
    user: dict[str, Any] = Depends(require_role("PRESTADOR")),
    connection: psycopg.Connection = Depends(get_connection),
) -> dict[str, Any]:
    _owned_service(connection, service_id, user)
    changes = request.model_dump(exclude_unset=True)
    if {"preco", "localizacao"}.intersection(
        changes
    ) and _service_has_active_reservations(connection, service_id):
        raise ApiError(
            409,
            "SERVICE_HAS_ACTIVE_RESERVATIONS",
            "Preco e localizacao nao podem ser alterados enquanto houver reservas ativas.",
        )
    assignments = ", ".join(f"{field} = %s" for field in changes)
    values = list(changes.values()) + [service_id]
    updated = connection.execute(
        f"""
        UPDATE public.servico
        SET {assignments}, atualizado_em = now()
        WHERE id_servico = %s
        RETURNING id_servico, id_prestador, nome, categoria, descricao,
                  preco, localizacao, ativo
        """,
        values,
    ).fetchone()
    return updated


@app.delete("/api/servicos/{service_id}", status_code=204)
def deactivate_service(
    service_id: int,
    user: dict[str, Any] = Depends(require_role("PRESTADOR")),
    connection: psycopg.Connection = Depends(get_connection),
) -> None:
    service = _owned_service(connection, service_id, user)
    if not service["ativo"]:
        raise ApiError(409, "SERVICE_ALREADY_INACTIVE", "O servico ja esta desativado.")
    if _service_has_active_reservations(connection, service_id):
        raise ApiError(
            409,
            "SERVICE_HAS_ACTIVE_RESERVATIONS",
            "O servico nao pode ser desativado enquanto houver reservas ativas.",
        )
    connection.execute(
        """
        UPDATE public.servico
        SET ativo = false, atualizado_em = now()
        WHERE id_servico = %s
        """,
        (service_id,),
    )


@app.post(
    "/api/servicos/{service_id}/disponibilidades",
    status_code=201,
)
def add_service_availability(
    service_id: int,
    request: AvailabilityCreate,
    user: dict[str, Any] = Depends(require_role("PRESTADOR")),
    connection: psycopg.Connection = Depends(get_connection),
) -> dict[str, Any]:
    service = _owned_service(connection, service_id, user)
    if not service["ativo"]:
        raise ApiError(
            409, "SERVICE_INACTIVE", "Nao e possivel editar servico inativo."
        )
    if _service_has_active_reservations(connection, service_id):
        raise ApiError(
            409,
            "SERVICE_HAS_ACTIVE_RESERVATIONS",
            "A disponibilidade nao pode ser alterada enquanto houver reservas ativas.",
        )
    availability = connection.execute(
        """
        INSERT INTO public.disponibilidade_servico (
            id_servico, data_inicio, data_fim, tipo, motivo
        )
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id_disponibilidade, id_servico, data_inicio, data_fim,
                  tipo, motivo, ativo
        """,
        (
            service_id,
            request.data_inicio,
            request.data_fim,
            request.tipo,
            request.motivo,
        ),
    ).fetchone()
    return availability


@app.get("/api/servicos/{service_id}/disponibilidades")
def list_service_availability(
    service_id: int,
    user: dict[str, Any] = Depends(require_role("PRESTADOR")),
    connection: psycopg.Connection = Depends(get_connection),
) -> list[dict[str, Any]]:
    _owned_service(connection, service_id, user)
    return connection.execute(
        """
        SELECT id_disponibilidade, id_servico, data_inicio, data_fim,
               tipo, motivo, ativo
        FROM public.disponibilidade_servico
        WHERE id_servico = %s
        ORDER BY data_inicio, id_disponibilidade
        """,
        (service_id,),
    ).fetchall()


@app.delete(
    "/api/servicos/{service_id}/disponibilidades/{availability_id}",
    status_code=204,
)
def deactivate_service_availability(
    service_id: int,
    availability_id: int,
    user: dict[str, Any] = Depends(require_role("PRESTADOR")),
    connection: psycopg.Connection = Depends(get_connection),
) -> None:
    _owned_service(connection, service_id, user)
    if _service_has_active_reservations(connection, service_id):
        raise ApiError(
            409,
            "SERVICE_HAS_ACTIVE_RESERVATIONS",
            "A disponibilidade nao pode ser alterada enquanto houver reservas ativas.",
        )
    result = connection.execute(
        """
        UPDATE public.disponibilidade_servico
        SET ativo = false
        WHERE id_disponibilidade = %s
          AND id_servico = %s
          AND ativo
        """,
        (availability_id, service_id),
    )
    if result.rowcount == 0:
        raise ApiError(
            404,
            "AVAILABILITY_NOT_FOUND",
            "Periodo de disponibilidade nao encontrado.",
        )


@app.post(
    "/api/servicos/{service_id}/arquivos",
    status_code=201,
)
def upload_service_file(
    service_id: int,
    file: UploadFile = File(...),
    user: dict[str, Any] = Depends(require_role("PRESTADOR")),
    connection: psycopg.Connection = Depends(get_connection),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    service = _owned_service(connection, service_id, user)
    if not service["ativo"]:
        raise ApiError(
            409, "SERVICE_INACTIVE", "Nao e possivel editar servico inativo."
        )
    if _service_has_active_reservations(connection, service_id):
        raise ApiError(
            409,
            "SERVICE_HAS_ACTIVE_RESERVATIONS",
            "Anexos nao podem ser alterados enquanto houver reservas ativas.",
        )

    filename = Path(file.filename or "").name
    if not filename or len(filename) > 255:
        raise ApiError(422, "INVALID_FILE_NAME", "Nome do arquivo invalido.")
    content = file.file.read(MAX_ATTACHMENT_BYTES + 1)
    if not content:
        raise ApiError(422, "EMPTY_FILE", "O arquivo enviado esta vazio.")
    if len(content) > MAX_ATTACHMENT_BYTES:
        raise ApiError(
            413,
            "FILE_TOO_LARGE",
            "O tamanho maximo permitido por arquivo e 10.000.000 bytes.",
        )

    detected_type = _detect_attachment_type(filename, content)
    if detected_type is None or file.content_type != detected_type:
        raise ApiError(
            415,
            "UNSUPPORTED_FILE_TYPE",
            "Envie JPEG, PNG, WebP, PDF ou DOCX com tipo MIME correspondente ao conteudo.",
        )

    file_key = uuid4()
    file_path = settings.local_dos_arquivos / str(file_key)
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("xb") as stored_file:
            stored_file.write(content)
    except OSError as exception:
        raise ApiError(
            500,
            "FILE_STORAGE_ERROR",
            "Nao foi possivel armazenar o arquivo.",
        ) from exception

    file_url = f"/api/arquivos/{file_key}"
    try:
        metadata = connection.execute(
            """
            INSERT INTO public.arquivo (
                id_servico, nome_original, url, tipo_mime, tamanho
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id_arquivo, id_servico, nome_original, url,
                      tipo_mime, tamanho, ativo, criado_em
            """,
            (
                service_id,
                filename,
                file_url,
                detected_type,
                len(content),
            ),
        ).fetchone()
        connection.commit()
    except psycopg.Error:
        file_path.unlink(missing_ok=True)
        raise
    return metadata


@app.get("/api/arquivos/{file_key}")
def download_service_file(
    file_key: UUID,
    connection: psycopg.Connection = Depends(get_connection),
    settings: Settings = Depends(get_settings),
) -> FileResponse:
    file_record = connection.execute(
        """
        SELECT f.nome_original, f.tipo_mime, f.url
        FROM public.arquivo AS f
        JOIN public.servico AS s ON s.id_servico = f.id_servico
        WHERE f.url = %s AND f.ativo AND s.ativo
        """,
        (f"/api/arquivos/{file_key}",),
    ).fetchone()
    if file_record is None:
        raise ApiError(404, "FILE_NOT_FOUND", "Arquivo nao encontrado.")
    file_path = settings.local_dos_arquivos / str(file_key)
    if not file_path.is_file():
        raise ApiError(404, "FILE_NOT_FOUND", "Arquivo nao encontrado.")
    return FileResponse(
        file_path,
        media_type=file_record["tipo_mime"],
        filename=file_record["nome_original"],
    )


@app.delete(
    "/api/servicos/{service_id}/arquivos/{file_id}",
    status_code=204,
)
def deactivate_service_file(
    service_id: int,
    file_id: int,
    user: dict[str, Any] = Depends(require_role("PRESTADOR")),
    connection: psycopg.Connection = Depends(get_connection),
) -> None:
    _owned_service(connection, service_id, user)
    if _service_has_active_reservations(connection, service_id):
        raise ApiError(
            409,
            "SERVICE_HAS_ACTIVE_RESERVATIONS",
            "Anexos nao podem ser alterados enquanto houver reservas ativas.",
        )
    result = connection.execute(
        """
        UPDATE public.arquivo
        SET ativo = false
        WHERE id_arquivo = %s AND id_servico = %s AND ativo
        """,
        (file_id, service_id),
    )
    if result.rowcount == 0:
        raise ApiError(404, "FILE_NOT_FOUND", "Arquivo nao encontrado.")


@app.post("/api/eventos", status_code=201, response_model=EventResponse)
def create_event(
    request: EventCreate,
    user: dict[str, Any] = Depends(require_role("ORGANIZADOR")),
    connection: psycopg.Connection = Depends(get_connection),
) -> dict[str, Any]:
    event = connection.execute(
        """
        INSERT INTO public.evento (
            id_organizador, nome, descricao, data_inicio, data_fim, local
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id_evento, id_organizador, nome, descricao,
                  data_inicio, data_fim, local, criado_em
        """,
        (
            user["id_usuario"],
            request.nome,
            request.descricao,
            request.data_inicio,
            request.data_fim,
            request.local,
        ),
    ).fetchone()
    return event


@app.get("/api/eventos", response_model=list[EventResponse])
def list_events(
    user: dict[str, Any] = Depends(require_role("ORGANIZADOR")),
    connection: psycopg.Connection = Depends(get_connection),
) -> list[dict[str, Any]]:
    return connection.execute(
        """
        SELECT id_evento, nome, descricao, data_inicio, data_fim, local
        FROM public.evento
        WHERE id_organizador = %s AND ativo
        ORDER BY data_inicio, id_evento
        """,
        (user["id_usuario"],),
    ).fetchall()


def _reservation_for_user(
    connection: psycopg.Connection,
    reservation_id: int,
    user: dict[str, Any],
) -> dict[str, Any]:
    reservation = connection.execute(
        """
        SELECT r.id_reserva, r.id_evento, r.id_servico, r.id_solicitante,
               r.status, r.data_inicio, r.data_fim, r.observacao,
               r.motivo_recusa, r.criado_em, e.id_organizador,
               e.data_inicio AS evento_data_inicio, s.id_prestador
        FROM public.reserva AS r
        JOIN public.evento AS e ON e.id_evento = r.id_evento
        JOIN public.servico AS s ON s.id_servico = r.id_servico
        WHERE r.id_reserva = %s AND r.ativo
        FOR UPDATE OF r
        """,
        (reservation_id,),
    ).fetchone()
    if reservation is None:
        raise ApiError(404, "RESERVATION_NOT_FOUND", "Reserva nao encontrada.")

    is_organizer = (
        user["tipo_usuario"] == "ORGANIZADOR"
        and user["id_usuario"] == reservation["id_solicitante"]
        and user["id_usuario"] == reservation["id_organizador"]
    )
    is_provider = (
        user["tipo_usuario"] == "PRESTADOR"
        and user["id_usuario"] == reservation["id_prestador"]
    )
    if not (is_organizer or is_provider):
        raise ApiError(
            403,
            "FORBIDDEN",
            "Voce nao participa desta reserva.",
        )
    if _expire_if_overdue(connection, reservation):
        connection.commit()
    return reservation


def _record_transition(
    connection: psycopg.Connection,
    reservation_id: int,
    actor_id: int | None,
    previous_status: str | None,
    new_status: str,
    note: str | None = None,
    reason: str | None = None,
) -> None:
    connection.execute(
        """
        INSERT INTO public.historico_reserva (
            id_reserva, id_usuario, status_anterior, status_novo,
            observacao, motivo
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            reservation_id,
            actor_id,
            previous_status,
            new_status,
            note,
            reason,
        ),
    )


def _expiration_started_at(
    connection: psycopg.Connection,
    reservation: dict[str, Any],
) -> datetime:
    if reservation["status"] == "SOLICITADA":
        return reservation["criado_em"]
    status = reservation["status"]
    entered_at = connection.execute(
        """
        SELECT max(data_hora) AS entrou_em
        FROM public.historico_reserva
        WHERE id_reserva = %s AND status_novo = %s
        """,
        (reservation["id_reserva"], status),
    ).fetchone()["entrou_em"]
    return entered_at or reservation["criado_em"]


def _transition_to_expired(
    connection: psycopg.Connection,
    reservation: dict[str, Any],
) -> None:
    previous_status = reservation["status"]
    connection.execute(
        """
        UPDATE public.reserva
        SET status = 'EXPIRADA', atualizado_em = now()
        WHERE id_reserva = %s
        """,
        (reservation["id_reserva"],),
    )
    connection.execute(
        """
        UPDATE public.disponibilidade_servico
        SET ativo = false
        WHERE id_reserva = %s AND ativo
        """,
        (reservation["id_reserva"],),
    )
    _record_transition(
        connection,
        reservation["id_reserva"],
        None,
        previous_status,
        "EXPIRADA",
        "Prazo de 48 horas sem resposta expirado.",
    )
    reservation["status"] = "EXPIRADA"


def _expire_if_overdue(
    connection: psycopg.Connection,
    reservation: dict[str, Any],
) -> bool:
    if reservation["status"] not in {"SOLICITADA", "EM_ANALISE", "APROVADA"}:
        return False
    deadline = _expiration_started_at(connection, reservation) + timedelta(hours=48)
    if datetime.now(timezone.utc) < deadline:
        return False
    _transition_to_expired(connection, reservation)
    return True


def _expire_overdue_reservations(
    connection: psycopg.Connection,
    scope_predicate: str | None = None,
    scope_params: tuple[Any, ...] = (),
    *,
    skip_locked: bool = True,
) -> list[int]:
    now = datetime.now(timezone.utc)
    extra_filter = f"AND {scope_predicate}" if scope_predicate else ""
    lock_clause = "FOR UPDATE OF r SKIP LOCKED" if skip_locked else "FOR UPDATE OF r"
    expired = connection.execute(
        f"""
        SELECT r.id_reserva, r.status, r.criado_em, sla.estado_desde
        FROM public.reserva AS r
        JOIN public.servico AS s ON s.id_servico = r.id_servico
        CROSS JOIN LATERAL (
            SELECT CASE r.status
                       WHEN 'SOLICITADA' THEN r.criado_em
                       WHEN 'EM_ANALISE' THEN COALESCE(
                           (
                               SELECT max(h.data_hora)
                               FROM public.historico_reserva AS h
                               WHERE h.id_reserva = r.id_reserva
                                 AND h.status_novo = 'EM_ANALISE'
                           ),
                           r.criado_em
                       )
                       WHEN 'APROVADA' THEN COALESCE(
                           (
                               SELECT max(h.data_hora)
                               FROM public.historico_reserva AS h
                               WHERE h.id_reserva = r.id_reserva
                                 AND h.status_novo = 'APROVADA'
                           ),
                           r.criado_em
                       )
                   END AS estado_desde
        ) AS sla
        WHERE r.ativo
          AND r.status IN ('SOLICITADA', 'EM_ANALISE', 'APROVADA')
          AND sla.estado_desde <= %s - interval '48 hours'
          {extra_filter}
        ORDER BY sla.estado_desde, r.id_reserva
        {lock_clause}
        """,
        (now, *scope_params),
    ).fetchall()
    for reservation in expired:
        _transition_to_expired(connection, reservation)
    return [reservation["id_reserva"] for reservation in expired]


def _raise_if_expired(reservation: dict[str, Any]) -> None:
    if reservation["status"] == "EXPIRADA":
        raise ApiError(
            409,
            "RESERVATION_EXPIRED",
            "O prazo de 48 horas para responder a reserva expirou.",
        )


@app.post("/api/reservas", status_code=201, response_model=ReservationResponse)
def create_reservation(
    request: ReservationCreate,
    user: dict[str, Any] = Depends(require_role("ORGANIZADOR")),
    connection: psycopg.Connection = Depends(get_connection),
) -> dict[str, Any]:
    event = connection.execute(
        """
        SELECT id_evento, data_inicio, data_fim
        FROM public.evento
        WHERE id_evento = %s AND id_organizador = %s AND ativo
        """,
        (request.id_evento, user["id_usuario"]),
    ).fetchone()
    if event is None:
        raise ApiError(404, "EVENT_NOT_FOUND", "Evento nao encontrado.")
    if (
        request.data_inicio < event["data_inicio"]
        or request.data_fim > event["data_fim"]
    ):
        raise ApiError(
            422,
            "RESERVATION_OUTSIDE_EVENT",
            "O periodo solicitado deve estar dentro do periodo do evento.",
        )

    service = connection.execute(
        """
        SELECT id_servico
        FROM public.servico
        WHERE id_servico = %s AND ativo
        FOR UPDATE
        """,
        (request.id_servico,),
    ).fetchone()
    if service is None:
        raise ApiError(404, "SERVICE_NOT_FOUND", "Servico nao encontrado.")

    availability = connection.execute(
        """
        SELECT
            EXISTS (
                SELECT 1
                FROM public.disponibilidade_servico AS d
                WHERE d.id_servico = %s
                  AND d.ativo
                  AND d.tipo = 'DISPONIVEL'
                  AND tstzrange(d.data_inicio, d.data_fim, '[)')
                      @> tstzrange(%s, %s, '[)')
            )
            AND NOT EXISTS (
                SELECT 1
                FROM public.disponibilidade_servico AS d
                WHERE d.id_servico = %s
                  AND d.ativo
                  AND d.tipo = 'BLOQUEIO_MANUAL'
                  AND tstzrange(d.data_inicio, d.data_fim, '[)')
                      && tstzrange(%s, %s, '[)')
            ) AS disponivel
        """,
        (
            request.id_servico,
            request.data_inicio,
            request.data_fim,
            request.id_servico,
            request.data_inicio,
            request.data_fim,
        ),
    ).fetchone()["disponivel"]
    if not availability:
        raise ApiError(
            409,
            "SERVICE_UNAVAILABLE",
            "O servico nao esta disponivel no periodo solicitado.",
        )

    try:
        reservation = connection.execute(
            """
            INSERT INTO public.reserva (
                id_evento, id_servico, id_solicitante, status,
                data_inicio, data_fim, observacao
            )
            VALUES (%s, %s, %s, 'SOLICITADA', %s, %s, %s)
            RETURNING id_reserva, id_evento, id_servico, id_solicitante,
                      status, data_inicio, data_fim, observacao, criado_em
            """,
            (
                request.id_evento,
                request.id_servico,
                user["id_usuario"],
                request.data_inicio,
                request.data_fim,
                request.observacao,
            ),
        ).fetchone()
    except ExclusionViolation:
        raise ApiError(
            409,
            "SCHEDULE_CONFLICT",
            "Ja existe uma reserva ativa para este servico e periodo.",
        ) from None

    _record_transition(
        connection,
        reservation["id_reserva"],
        user["id_usuario"],
        None,
        "SOLICITADA",
        "Solicitacao criada.",
    )
    return reservation


@app.get("/api/reservas", response_model=list[ReservationResponse])
def list_reservations(
    user: dict[str, Any] = Depends(get_current_user),
    connection: psycopg.Connection = Depends(get_connection),
) -> list[dict[str, Any]]:
    if user["tipo_usuario"] == "ORGANIZADOR":
        predicate = "r.id_solicitante = %s"
    elif user["tipo_usuario"] == "PRESTADOR":
        predicate = "s.id_prestador = %s"
    else:
        raise ApiError(403, "FORBIDDEN", "Seu perfil nao pode consultar reservas.")

    if _expire_overdue_reservations(
        connection,
        predicate,
        (user["id_usuario"],),
        skip_locked=False,
    ):
        connection.commit()

    return connection.execute(
        f"""
        SELECT r.id_reserva, r.id_evento, r.id_servico, r.id_solicitante,
               r.status, r.data_inicio, r.data_fim, r.observacao,
               r.motivo_recusa, r.criado_em
        FROM public.reserva AS r
        JOIN public.servico AS s ON s.id_servico = r.id_servico
        WHERE r.ativo AND {predicate}
        ORDER BY r.criado_em DESC, r.id_reserva DESC
        """,
        (user["id_usuario"],),
    ).fetchall()


@app.get("/api/reservas/{reservation_id}", response_model=ReservationResponse)
def get_reservation(
    reservation_id: int,
    user: dict[str, Any] = Depends(get_current_user),
    connection: psycopg.Connection = Depends(get_connection),
) -> dict[str, Any]:
    return _reservation_for_user(connection, reservation_id, user)


@app.post(
    "/api/reservas/{reservation_id}/analise",
    response_model=TransitionResponse,
)
def begin_analysis(
    reservation_id: int,
    user: dict[str, Any] = Depends(require_role("PRESTADOR")),
    connection: psycopg.Connection = Depends(get_connection),
) -> dict[str, Any]:
    reservation = _reservation_for_user(connection, reservation_id, user)
    _raise_if_expired(reservation)
    if reservation["status"] != "SOLICITADA":
        raise ApiError(
            409,
            "INVALID_RESERVATION_STATE",
            "Somente reservas solicitadas podem iniciar analise.",
        )

    connection.execute(
        """
        UPDATE public.reserva
        SET status = 'EM_ANALISE', atualizado_em = now()
        WHERE id_reserva = %s
        """,
        (reservation_id,),
    )
    _record_transition(
        connection,
        reservation_id,
        user["id_usuario"],
        "SOLICITADA",
        "EM_ANALISE",
        "Prestador iniciou a analise.",
    )
    return {"id_reserva": reservation_id, "status": "EM_ANALISE"}


@app.post(
    "/api/reservas/{reservation_id}/decisao",
    response_model=DecisionResponse,
)
def decide_reservation(
    reservation_id: int,
    request: ReservationDecision,
    user: dict[str, Any] = Depends(require_role("PRESTADOR")),
    connection: psycopg.Connection = Depends(get_connection),
) -> dict[str, Any]:
    reservation = _reservation_for_user(connection, reservation_id, user)
    _raise_if_expired(reservation)
    if reservation["status"] != "EM_ANALISE":
        raise ApiError(
            409,
            "INVALID_RESERVATION_STATE",
            "Somente reservas em analise podem receber uma decisao.",
        )

    reason = request.motivo.strip() if request.motivo else None
    if request.decisao == "APROVADA":
        connection.execute(
            """
            UPDATE public.reserva
            SET status = 'APROVADA', atualizado_em = now()
            WHERE id_reserva = %s
            """,
            (reservation_id,),
        )
        connection.execute(
            """
            INSERT INTO public.disponibilidade_servico (
                id_servico, id_reserva, data_inicio, data_fim, tipo, motivo
            )
            VALUES (%s, %s, %s, %s, 'RESERVA', %s)
            """,
            (
                reservation["id_servico"],
                reservation_id,
                reservation["data_inicio"],
                reservation["data_fim"],
                f"Pre-bloqueio da reserva {reservation_id}",
            ),
        )
        note = "Solicitacao aprovada."
    else:
        connection.execute(
            """
            UPDATE public.reserva
            SET status = 'RECUSADA', motivo_recusa = %s, atualizado_em = now()
            WHERE id_reserva = %s
            """,
            (reason, reservation_id),
        )
        note = "Solicitacao recusada."

    _record_transition(
        connection,
        reservation_id,
        user["id_usuario"],
        "EM_ANALISE",
        request.decisao,
        note,
        reason,
    )
    return {
        "id_reserva": reservation_id,
        "status": request.decisao,
        "motivo": reason,
    }


@app.post(
    "/api/reservas/{reservation_id}/cancelamento",
    response_model=CancellationResponse,
)
def cancel_reservation(
    reservation_id: int,
    request: ReservationCancellation,
    user: dict[str, Any] = Depends(require_role("ORGANIZADOR", "PRESTADOR")),
    connection: psycopg.Connection = Depends(get_connection),
) -> dict[str, Any]:
    reservation = _reservation_for_user(connection, reservation_id, user)
    _raise_if_expired(reservation)
    status = reservation["status"]
    organizer_can_cancel = user["tipo_usuario"] == "ORGANIZADOR" and status in {
        "SOLICITADA",
        "EM_ANALISE",
        "APROVADA",
        "CONFIRMADA",
    }
    provider_can_cancel = user["tipo_usuario"] == "PRESTADOR" and status == "CONFIRMADA"
    if not (organizer_can_cancel or provider_can_cancel):
        raise ApiError(
            409,
            "INVALID_RESERVATION_STATE",
            "Seu papel nao pode cancelar a reserva neste estado.",
        )
    if datetime.now(timezone.utc) >= reservation["evento_data_inicio"]:
        raise ApiError(
            409,
            "CANCELLATION_WINDOW_CLOSED",
            "A reserva so pode ser cancelada antes do inicio do evento.",
        )

    connection.execute(
        """
        UPDATE public.reserva
        SET status = 'CANCELADA', atualizado_em = now()
        WHERE id_reserva = %s
        """,
        (reservation_id,),
    )
    connection.execute(
        """
        UPDATE public.disponibilidade_servico
        SET ativo = false
        WHERE id_reserva = %s AND ativo
        """,
        (reservation_id,),
    )
    _record_transition(
        connection,
        reservation_id,
        user["id_usuario"],
        status,
        "CANCELADA",
        "Reserva cancelada.",
        request.motivo,
    )
    return {
        "id_reserva": reservation_id,
        "status": "CANCELADA",
        "motivo": request.motivo,
    }


@app.post(
    "/api/reservas/{reservation_id}/confirmacao",
    response_model=TransitionResponse,
)
def confirm_reservation(
    reservation_id: int,
    user: dict[str, Any] = Depends(require_role("ORGANIZADOR")),
    connection: psycopg.Connection = Depends(get_connection),
) -> dict[str, Any]:
    reservation = _reservation_for_user(connection, reservation_id, user)
    _raise_if_expired(reservation)
    if reservation["status"] != "APROVADA":
        raise ApiError(
            409,
            "INVALID_RESERVATION_STATE",
            "Somente reservas aprovadas podem ser confirmadas.",
        )

    approved_at = connection.execute(
        """
        SELECT max(data_hora) AS aprovada_em
        FROM public.historico_reserva
        WHERE id_reserva = %s AND status_novo = 'APROVADA'
        """,
        (reservation_id,),
    ).fetchone()["aprovada_em"]
    if approved_at is None:
        raise ApiError(
            409,
            "MISSING_APPROVAL_HISTORY",
            "A reserva nao possui registro da aprovacao.",
        )

    block = connection.execute(
        """
        UPDATE public.disponibilidade_servico
        SET motivo = %s
        WHERE id_reserva = %s AND tipo = 'RESERVA' AND ativo
        RETURNING id_disponibilidade
        """,
        (
            f"Bloqueio definitivo da reserva {reservation_id}",
            reservation_id,
        ),
    ).fetchone()
    if block is None:
        raise ApiError(
            409,
            "MISSING_SCHEDULE_BLOCK",
            "A reserva aprovada nao possui pre-bloqueio ativo na agenda.",
        )
    connection.execute(
        """
        UPDATE public.reserva
        SET status = 'CONFIRMADA', atualizado_em = now()
        WHERE id_reserva = %s
        """,
        (reservation_id,),
    )
    _record_transition(
        connection,
        reservation_id,
        user["id_usuario"],
        "APROVADA",
        "CONFIRMADA",
        "Contratacao confirmada.",
    )
    return {"id_reserva": reservation_id, "status": "CONFIRMADA"}


@app.post(
    "/api/jobs/reservas/expiracoes",
    response_model=ExpirationResponse,
)
def expire_overdue_reservations(
    _: dict[str, Any] = Depends(require_role("ADMINISTRADOR")),
    connection: psycopg.Connection = Depends(get_connection),
) -> dict[str, Any]:
    reservation_ids = _expire_overdue_reservations(connection)
    return {
        "quantidade": len(reservation_ids),
        "reservas_expiradas": reservation_ids,
    }


@app.get(
    "/api/reservas/{reservation_id}/historico",
    response_model=list[ReservationHistoryEntry],
)
def reservation_history(
    reservation_id: int,
    user: dict[str, Any] = Depends(get_current_user),
    connection: psycopg.Connection = Depends(get_connection),
) -> list[dict[str, Any]]:
    _reservation_for_user(connection, reservation_id, user)
    return connection.execute(
        """
        SELECT h.id_historico, h.id_reserva, h.id_usuario,
               h.status_anterior, h.status_novo, h.data_hora,
               h.observacao, h.motivo,
               COALESCE(u.nome, 'Sistema') AS autor_nome,
               u.tipo_usuario AS autor_perfil
        FROM public.historico_reserva AS h
        LEFT JOIN public.usuario AS u ON u.id_usuario = h.id_usuario
        WHERE h.id_reserva = %s
        ORDER BY h.data_hora, h.id_historico
        """,
        (reservation_id,),
    ).fetchall()


@app.exception_handler(UniqueViolation)
async def handle_unique_violation(_: Request, __: UniqueViolation) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content=error_response(
            "DUPLICATE_RESOURCE",
            "A operacao viola uma restricao de unicidade.",
        ),
    )


@app.exception_handler(ForeignKeyViolation)
async def handle_foreign_key_violation(
    _: Request,
    __: ForeignKeyViolation,
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=error_response(
            "INVALID_REFERENCE",
            "Um dos recursos informados nao existe ou nao esta disponivel.",
        ),
    )
