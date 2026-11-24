# API REST — EventFy

A API do fluxo principal usa FastAPI, Psycopg 3 e PostgreSQL 17. O contrato OpenAPI e a interface Swagger ficam em `/openapi.json` e `/docs` quando o servidor esta em execucao.

## Executar localmente

1. Prepare o PostgreSQL e aplique as migracoes conforme [`DATABASE.md`](./DATABASE.md).
2. Crie `.env` a partir de `.env.example`, ajuste `URL_DO_BANCO` e gere `CHAVE_SECRETA_JWT` com pelo menos 32 caracteres aleatorios.
3. Na raiz do repositorio:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
uvicorn eventfy_api.main:app --app-dir api --reload
```

O health check fica em `http://127.0.0.1:8000/api/health`. As contas ficticias e suas credenciais locais estao descritas em [`DATABASE.md`](./DATABASE.md).

## Autenticacao e erros

`POST /api/auth/login` recebe `email` e `senha` em JSON. A resposta contem um token Bearer JWT com validade de 30 minutos. Cada requisicao protegida deve enviar `Authorization: Bearer <token>`. O usuario e o papel sao consultados novamente no banco; contas inativas nao autenticam.

Erros usam um envelope uniforme:

```json
{
  "error": {
    "code": "SCHEDULE_CONFLICT",
    "message": "Ja existe uma reserva ativa para este servico e periodo."
  }
}
```

Respostas principais:

| HTTP | Uso |
|---|---|
| `201` | Recurso criado |
| `200` | Consulta ou transicao concluida |
| `401` | Credenciais ou token ausentes/invalidos |
| `403` | Papel ou propriedade nao autorizados |
| `404` | Recurso inexistente ou nao visivel |
| `409` | Estado invalido, reserva expirada ou conflito de agenda |
| `422` | Corpo invalido ou regra de periodo/justificativa nao atendida |

## Operacoes implementadas

| Metodo | Rota | Papel | Descricao |
|---|---|---|---|
| `GET` | `/api/health` | Publico | Verifica disponibilidade do processo da API |
| `POST` | `/api/auth/login` | Publico | Emite token Bearer |
| `GET` | `/api/servicos` | Publico | Lista servicos ativos; suporta `categoria`, `preco_minimo`, `preco_maximo`, `limit` e `offset` |
| `GET` | `/api/servicos/{id}` | Publico | Consulta um servico ativo |
| `POST` | `/api/eventos` | Organizador | Cria evento proprio |
| `GET` | `/api/eventos` | Organizador | Lista eventos proprios |
| `POST` | `/api/reservas` | Organizador | Solicita reserva em periodo disponivel e registra auditoria |
| `GET` | `/api/reservas` | Organizador ou prestador | Lista as reservas do ator autenticado |
| `GET` | `/api/reservas/{id}` | Participante | Consulta reserva propria |
| `POST` | `/api/reservas/{id}/analise` | Prestador titular | Transita de `SOLICITADA` para `EM_ANALISE` |
| `POST` | `/api/reservas/{id}/decisao` | Prestador titular | Aprova ou recusa; recusa exige justificativa com 10 caracteres ou mais |
| `POST` | `/api/reservas/{id}/confirmacao` | Organizador titular | Confirma aprovacao em ate 48 horas |
| `GET` | `/api/reservas/{id}/historico` | Participante | Consulta transicoes em ordem cronologica |

O servidor valida papel, titularidade, periodo do evento, disponibilidade, estado atual, justificativa, prazo e conflitos. As mutacoes e os respectivos registros de historico usam a mesma transacao PostgreSQL. A restricao de exclusao de `reserva` protege tambem contra requisicoes concorrentes.

## Testes

Prepare um banco isolado com as migracoes aplicadas e aponte `TEST_DATABASE_URL` para ele; nao use uma base com dados importantes. Execute:

```powershell
$env:TEST_DATABASE_URL = 'postgresql://postgres:SENHA_LOCAL@localhost:5432/eventfy_test'
pytest
```

Os testes de integracao cobrem login, cadastro e hash de senha, logout e revogacao de token, usuarios inativos, catalogo, matriz de papeis e titularidade, filtros e protecao de servicos, fluxo de solicitacao ate confirmacao, cancelamento e liberacao de agenda, expiracao em cada etapa, historico, recusa sem motivo suficiente, controle de acesso, conflito de agenda e confirmacoes concorrentes.

Ao iniciar e ao terminar uma execucao, a fixture de testes recria completamente o schema do banco apontado por `TEST_DATABASE_URL` a partir das migracoes. Use exclusivamente um banco descartavel de testes: executar `pytest` duas vezes seguidas deve produzir o mesmo conjunto de dados sem conflitos residuais.
