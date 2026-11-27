# Entrega Incremental 6.14 - EventFy

## Baseline operacional

Esta entrega usa como baseline o commit `5e15fa1`, merge da PR #94. A baseline executavel inclui a API FastAPI/Uvicorn, autenticacao Bearer, catalogo, eventos, reservas, historico, migracoes V1 a V5, PostgreSQL 17 e prototipo estatico. O contrato das rotas esta em [`API.md`](./API.md).

A evolucao EVT-20 adiciona a migracao V6 para moderacao administrativa, as rotas protegidas de gerenciamento de contas e publicacoes e o historico imutavel de moderacao. A visibilidade de uma publicacao e independente do estado ativo do servico e nao modifica reservas existentes.

## Pre-requisitos e instalacao

Instale Git 2.x, Python 3.14, PostgreSQL 17.x e coloque `psql` e `createdb` no `PATH`. Na raiz do repositorio:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

O arquivo `.env.example` possui apenas placeholders. Configure localmente `URL_DO_BANCO`, `CHAVE_SECRETA_JWT` e, se necessario, `LOCAL_DOS_ARQUIVOS`. Nunca versiona senhas, tokens, chaves ou dados pessoais reais.

## Migracao e dados

Com o PostgreSQL em execucao, aplique as migracoes em ordem:

```powershell
.\scripts\db-setup.ps1 -Username eventfy_dev
```

O script registra checksums em `schema_migrations`. Nao edite uma migracao ja aplicada; crie uma nova `V<numero>__<descricao>.sql`. A restauracao da demonstracao deve usar o roteiro do EVT-08, que e alinhado com V1 a V5 e recompõe o vinculo de agenda da V5.

## Testes

Com um banco de testes PostgreSQL configurado, execute duas vezes:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest -q
```

Os testes recriam o schema e reaplicam V1 a V5. O resultado esperado nesta baseline e `18 passed` em cada execucao.

## Execucao e operacao

```powershell
.\.venv\Scripts\python.exe -m uvicorn eventfy_api.main:app --app-dir api --env-file .env --reload
```

Verifique `http://127.0.0.1:8000/api/health` e `http://127.0.0.1:8000/docs`. Para encerrar, use `Ctrl+C`. As rotas, papeis, credenciais ficticias e codigos de erro estao em [`API.md`](./API.md). O prototipo estatico e aberto conforme [`prototipo/README.md`](../prototipo/README.md).

## Conferencia cruzada

README, API, banco, requisitos, arquitetura e CHANGELOG devem apontar para a mesma baseline `5e15fa1`, para V1 a V5 e para `requirements-dev.txt`. A conferencia formal esta em [`CONFERENCIA_CRUZADA.md`](./CONFERENCIA_CRUZADA.md).
