"""Ponto de entrada local da EVT-01 para conferir interface, API e banco."""

import os
from pathlib import Path

import psycopg
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="EventFy · Ambiente local")


@app.get("/api/ambiente")
def verificar_ambiente() -> dict[str, str]:
    url = os.getenv("URL_DO_BANCO")
    if not url:
        raise HTTPException(503, "Configure URL_DO_BANCO no arquivo .env.")

    try:
        with psycopg.connect(url, connect_timeout=3) as banco:
            versao = banco.execute("SHOW server_version").fetchone()[0]
    except psycopg.Error:
        raise HTTPException(503, "Verifique o serviço PostgreSQL e a URL_DO_BANCO.") from None

    return {"aplicacao": "EventFy", "postgresql": versao}


# As rotas de API têm precedência sobre a montagem da interface em /.
prototipo = Path(__file__).resolve().parents[1] / "prototipo"
app.mount("/", StaticFiles(directory=prototipo, html=True), name="prototipo")
