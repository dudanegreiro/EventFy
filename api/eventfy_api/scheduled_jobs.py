"""Idempotent reservation maintenance job for a platform scheduler or service."""

import argparse
import logging
import time

import psycopg
from psycopg.rows import dict_row

from eventfy_api.config import get_settings

logger = logging.getLogger("eventfy.jobs")
JOB_LOCK_ID = 714_020_038


def run_once() -> dict[str, list[int]]:
    settings = get_settings()
    with psycopg.connect(settings.url_do_banco, row_factory=dict_row) as connection:
        with connection.transaction():
            locked = connection.execute(
                "SELECT pg_try_advisory_xact_lock(%s) AS acquired", (JOB_LOCK_ID,)
            ).fetchone()["acquired"]
            if not locked:
                logger.info("Job ignorado: outra instância mantém o lock.")
                return {"reservas_expiradas": [], "reservas_finalizadas": []}

            from eventfy_api.main import _expire_overdue_reservations

            expired = _expire_overdue_reservations(connection, skip_locked=True)
            completed = connection.execute(
                """
                SELECT r.id_reserva
                FROM public.reserva AS r
                WHERE r.ativo AND r.status = 'CONFIRMADA'
                  AND r.data_fim <= now()
                ORDER BY r.data_fim, r.id_reserva
                FOR UPDATE SKIP LOCKED
                """
            ).fetchall()
            completed_ids = [row["id_reserva"] for row in completed]
            if completed_ids:
                connection.execute(
                    """
                    UPDATE public.reserva
                    SET status = 'FINALIZADA', atualizado_em = now()
                    WHERE id_reserva = ANY(%s) AND status = 'CONFIRMADA'
                    """,
                    (completed_ids,),
                )
                connection.execute(
                    """
                    INSERT INTO public.historico_reserva (
                        id_reserva, id_usuario, status_anterior, status_novo,
                        observacao
                    )
                    SELECT id_reserva, NULL, 'CONFIRMADA', 'FINALIZADA',
                           'Finalizada automaticamente pelo job agendado.'
                    FROM unnest(%s::integer[]) AS ids(id_reserva)
                    """,
                    (completed_ids,),
                )
                connection.execute(
                    """
                    UPDATE public.disponibilidade_servico
                    SET ativo = false
                    WHERE id_reserva = ANY(%s) AND ativo
                    """,
                    (completed_ids,),
                )

    result = {
        "reservas_expiradas": expired,
        "reservas_finalizadas": completed_ids,
    }
    logger.info("Job concluído: %s", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--once", action="store_true", help="Executa uma única varredura")
    parser.add_argument("--interval-seconds", type=int, default=60)
    args = parser.parse_args()
    if args.interval_seconds < 1:
        parser.error("--interval-seconds deve ser positivo")

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    while True:
        try:
            run_once()
        except Exception:
            logger.exception("Falha no job de manutenção de reservas.")
            if args.once:
                raise
        if args.once:
            return
        time.sleep(args.interval_seconds)


if __name__ == "__main__":
    main()
