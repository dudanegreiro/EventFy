from collections.abc import Generator

import psycopg
from fastapi import Depends
from psycopg.rows import dict_row

from eventfy_api.config import Settings, get_settings


def get_connection(
    settings: Settings = Depends(get_settings),
) -> Generator[psycopg.Connection, None, None]:
    with psycopg.connect(settings.url_do_banco, row_factory=dict_row) as connection:
        yield connection
