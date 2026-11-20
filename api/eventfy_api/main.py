from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

import psycopg
from fastapi import Depends, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from psycopg.errors import ExclusionViolation, ForeignKeyViolation, UniqueViolation

from eventfy_api.config import Settings, get_settings
from eventfy_api.database import get_connection
from eventfy_api.errors import ApiError, error_response
from eventfy_api.schemas import (
    DecisionResponse,
    EventCreate,
    EventResponse,
    LoginRequest,
    PublicService,
    ReservationCreate,
    ReservationDecision,
    ReservationHistoryEntry,
    ReservationResponse,
    TransitionResponse,
    TokenResponse,
)
from eventfy_api.security import create_access_token, get_current_user, require_role

app = FastAPI(
    title="EventFy API",
    version="0.1.0",
    description="API REST para catalogo, eventos e fluxo principal de reservas.",
)


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
    return TokenResponse(
        access_token=create_access_token(
            user["id_usuario"],
            user["tipo_usuario"],
            settings,
        )
    )


@app.get("/api/servicos", response_model=list[PublicService])
def list_services(
    categoria: str | None = None,
    preco_minimo: Decimal | None = Query(default=None, ge=0),
    preco_maximo: Decimal | None = Query(default=None, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    connection: psycopg.Connection = Depends(get_connection),
) -> list[dict[str, Any]]:
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

    rows = connection.execute(
        """
        SELECT s.id_servico, s.nome, s.categoria, s.descricao,
               s.preco, s.id_prestador
        FROM public.servico AS s
        WHERE s.ativo
          AND (%s::text IS NULL OR lower(s.categoria) = lower(%s))
          AND (%s::numeric IS NULL OR s.preco >= %s)
          AND (%s::numeric IS NULL OR s.preco <= %s)
        ORDER BY s.id_servico
        LIMIT %s OFFSET %s
        """,
        (
            categoria,
            categoria,
            preco_minimo,
            preco_minimo,
            preco_maximo,
            preco_maximo,
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
        SELECT id_servico, nome, categoria, descricao, preco, id_prestador
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
    return {**service, "arquivos": files}


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
               s.id_prestador
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
                id_servico, data_inicio, data_fim, tipo, motivo
            )
            VALUES (%s, %s, %s, 'RESERVA', %s)
            """,
            (
                reservation["id_servico"],
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
    "/api/reservas/{reservation_id}/confirmacao",
    response_model=TransitionResponse,
)
def confirm_reservation(
    reservation_id: int,
    user: dict[str, Any] = Depends(require_role("ORGANIZADOR")),
    connection: psycopg.Connection = Depends(get_connection),
) -> dict[str, Any]:
    reservation = _reservation_for_user(connection, reservation_id, user)
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

    if datetime.now(timezone.utc) - approved_at > timedelta(hours=48):
        connection.execute(
            """
            UPDATE public.reserva
            SET status = 'EXPIRADA', atualizado_em = now()
            WHERE id_reserva = %s
            """,
            (reservation_id,),
        )
        connection.execute(
            """
            UPDATE public.disponibilidade_servico
            SET ativo = false
            WHERE id_servico = %s
              AND tipo = 'RESERVA'
              AND data_inicio = %s
              AND data_fim = %s
              AND ativo
            """,
            (
                reservation["id_servico"],
                reservation["data_inicio"],
                reservation["data_fim"],
            ),
        )
        _record_transition(
            connection,
            reservation_id,
            None,
            "APROVADA",
            "EXPIRADA",
            "Prazo de confirmacao de 48 horas expirado.",
        )
        connection.commit()
        raise ApiError(
            409,
            "RESERVATION_EXPIRED",
            "O prazo de 48 horas para confirmar a reserva expirou.",
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
