"""Aplica migracoes SQL versionadas no PostgreSQL com verificacao SHA-256.

Alternativa multiplataforma ao scripts/db-setup.ps1 para uso local e em CI
(Linux, macOS e Windows), preservando exatamente a tabela public.schema_migrations
e a validacao de checksum adotadas pelo projeto.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
from pathlib import Path

import psycopg

MIGRATION_PATTERN = re.compile(r"^V(?P<version>[0-9]+)__(?P<desc>[A-Za-z0-9_-]+)\.sql$")


def discover_migrations(directory: Path) -> list[tuple[int, Path]]:
    """Lista migracoes V<n>__<descricao>.sql ordenadas numericamente."""
    if not directory.is_dir():
        raise FileNotFoundError(f"Diretorio de migracoes nao encontrado: {directory}")

    migrations: list[tuple[int, Path]] = []
    seen_versions: set[int] = set()
    for path in sorted(directory.glob("V*__*.sql")):
        if not path.is_file():
            continue
        match = MIGRATION_PATTERN.match(path.name)
        if not match:
            raise ValueError(
                f"Nome de migracao invalido: {path.name}. "
                "Use V<numero>__<descricao>.sql."
            )
        version = int(match.group("version"))
        if version in seen_versions:
            raise ValueError(f"Ha versoes de migracao duplicadas: V{version}.")
        seen_versions.add(version)
        migrations.append((version, path))

    if not migrations:
        raise RuntimeError(f"Nenhuma migracao encontrada em {directory}.")

    migrations.sort(key=lambda item: item[0])
    return migrations


def apply_migrations(database_url: str, migrations_dir: Path) -> list[int]:
    """Aplica migracoes pendentes em transacoes individuais com checksum SHA-256."""
    migrations = discover_migrations(migrations_dir)
    applied_now: list[int] = []

    with psycopg.connect(database_url) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS public.schema_migrations (
                version integer PRIMARY KEY,
                checksum char(64) NOT NULL,
                applied_at timestamptz NOT NULL DEFAULT now()
            );
            """
        )
        connection.commit()

        rows = connection.execute(
            "SELECT version, checksum FROM public.schema_migrations ORDER BY version;"
        ).fetchall()
        applied = {int(row[0]): str(row[1]).strip().lower() for row in rows}

        for version, file_path in migrations:
            raw_bytes = file_path.read_bytes()
            checksum = hashlib.sha256(raw_bytes).hexdigest().lower()

            if version in applied:
                if applied[version] != checksum:
                    raise RuntimeError(
                        f"A migracao {file_path.name} foi alterada depois de aplicada. "
                        "Crie uma nova migracao."
                    )
                print(f"Migracao V{version} ja aplicada.")
                continue

            sql = raw_bytes.decode("utf-8")
            with connection.transaction():
                connection.execute(sql)
                connection.execute(
                    """
                    INSERT INTO public.schema_migrations (version, checksum)
                    VALUES (%s, %s);
                    """,
                    (version, checksum),
                )
            applied_now.append(version)
            print(f"Migracao V{version} aplicada: {file_path.name}")

    return applied_now


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Aplica migracoes versionadas do EventFy no PostgreSQL."
    )
    parser.add_argument(
        "--database-url",
        default=os.getenv("URL_DO_BANCO") or os.getenv("TEST_DATABASE_URL"),
        help="URL de conexao PostgreSQL (padrao: URL_DO_BANCO ou TEST_DATABASE_URL).",
    )
    parser.add_argument(
        "--migrations-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "db" / "migrations",
        help="Diretorio contendo arquivos V<n>__<descricao>.sql.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if not args.database_url:
        print(
            "Erro: informe --database-url ou defina URL_DO_BANCO/TEST_DATABASE_URL.",
            file=sys.stderr,
        )
        return 1

    apply_migrations(args.database_url, args.migrations_dir)
    print("Banco pronto.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
