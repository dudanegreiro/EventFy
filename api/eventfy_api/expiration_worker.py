"""Background worker for the reservation expiration SLA."""

import argparse
import logging
import time
from collections.abc import Sequence

from psycopg.rows import dict_row

from eventfy_api.config import get_settings
from eventfy_api.main import _expire_overdue_reservations

LOGGER = logging.getLogger("eventfy.expiration")


def run_expiration_sweep() -> int:
    settings = get_settings()
    with psycopg.connect(settings.url_do_banco, row_factory=dict_row) as connection:
        expired_reservations = _expire_overdue_reservations(connection)
    expired_count = len(expired_reservations)
    LOGGER.info("Varredura concluida; reservas expiradas=%d", expired_count)
    return expired_count


def _positive_integer(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exception:
        raise argparse.ArgumentTypeError("must be an integer") from exception
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def _parse_arguments(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Expire reservations that exceeded their response SLA."
    )
    execution = parser.add_mutually_exclusive_group()
    execution.add_argument(
        "--once",
        action="store_true",
        help="run one sweep and exit (for a system scheduler)",
    )
    execution.add_argument(
        "--interval-seconds",
        type=_positive_integer,
        default=60,
        metavar="SECONDS",
        help="repeat the sweep at this interval (default: 60)",
    )
    return parser.parse_args(arguments)


def main(arguments: Sequence[str] | None = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    options = _parse_arguments(arguments)
    if options.once:
        try:
            run_expiration_sweep()
        except Exception:
            LOGGER.exception("Falha na varredura do SLA")
            return 1
        return 0

    LOGGER.info(
        "Iniciando worker de expiracao de reservas; intervalo-segundos=%d",
        options.interval_seconds,
    )
    while True:
        try:
            run_expiration_sweep()
        except Exception:
            LOGGER.exception(
                "Falha na varredura do SLA; nova tentativa apos o intervalo configurado"
            )
        time.sleep(options.interval_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
