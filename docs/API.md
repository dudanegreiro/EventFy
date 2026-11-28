# API REST — EventFy

A API do fluxo principal usa FastAPI, Psycopg 3 e PostgreSQL 17. O contrato OpenAPI e a interface Swagger ficam em `/openapi.json` e `/docs` quando o servidor esta em execucao.

O prazo de expiração por etapa é configurado por `PRAZO_EXPIRACAO_RESERVA_HORAS` (padrão de compatibilidade: 48 horas). A regra fica isolada no backend e não depende das telas.

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

Para desenvolvimento local, a API aceita chamadas do frontend servido em `localhost` ou `127.0.0.1`, nas portas `5500` (servidor estatico) e `5173` (Vite). Se o frontend usar outra origem, ajuste a lista `allow_origins` do `CORSMiddleware` em `api/eventfy_api/main.py` antes de iniciar a API.

## Autenticacao e erros

`POST /api/auth/register` recebe `nome`, `email`, `senha` (12 a 72 bytes em UTF-8) e `tipo_usuario` (`ORGANIZADOR` ou `PRESTADOR`). O papel `ADMINISTRADOR` nao pode ser escolhido no cadastro publico. Senhas sao armazenadas como hashes bcrypt com fator 12 usando `pgcrypto`.

`POST /api/auth/login` recebe `email` e `senha` em JSON. A resposta contem um token Bearer JWT com validade de 30 minutos. Cada requisicao protegida deve enviar `Authorization: Bearer <token>`. O usuario e o papel sao consultados novamente no banco; contas inativas nao autenticam. Cada token esta associado a uma sessao persistida, permitindo invalidacao imediata.

`POST /api/auth/logout` revoga a sessao do token autenticado. O token deixa de ser aceito e as demais sessoes do usuario permanecem ativas. O logout requer um token valido.

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
| `413` | Arquivo acima de 10.000.000 bytes |
| `415` | Conteudo ou MIME de anexo nao permitido |
| `422` | Corpo invalido ou regra de periodo/justificativa nao atendida |

## Operacoes implementadas

| Metodo | Rota | Papel | Descricao |
|---|---|---|---|
| `GET` | `/api/health` | Publico | Verifica disponibilidade do processo da API |
| `POST` | `/api/auth/register` | Publico | Cria conta de organizador ou prestador |
| `POST` | `/api/auth/login` | Publico | Emite token Bearer |
| `POST` | `/api/auth/logout` | Autenticado | Revoga a sessao do token enviado |
| `GET` | `/api/servicos` | Publico | Busca servicos ativos por `termo`, `categoria`, `preco_minimo`, `preco_maximo`, `localizacao` e periodo (`data_inicio` + `data_fim`); suporta paginacao `limit`/`offset` |
| `GET` | `/api/servicos/{id}` | Publico | Consulta um servico ativo |
| `POST` | `/api/servicos` | Prestador | Cadastra servico proprio com preco e localizacao |
| `GET` | `/api/prestador/servicos` | Prestador | Lista servicos proprios ativos e inativos |
| `PATCH` | `/api/servicos/{id}` | Prestador titular | Atualiza dados descritivos; preco/localizacao ficam protegidos por reserva ativa |
| `DELETE` | `/api/servicos/{id}` | Prestador titular | Desativa logicamente o servico se nao houver reserva ativa |
| `POST` | `/api/servicos/{id}/disponibilidades` | Prestador titular | Adiciona periodo disponivel ou bloqueio manual |
| `GET` | `/api/servicos/{id}/disponibilidades` | Prestador titular | Lista periodos de disponibilidade e bloqueios proprios |
| `DELETE` | `/api/servicos/{id}/disponibilidades/{availability_id}` | Prestador titular | Desativa periodo de disponibilidade |
| `POST` | `/api/servicos/{id}/arquivos` | Prestador titular | Armazena JPEG/PNG/WebP/PDF/DOCX de ate 10.000.000 bytes |
| `GET` | `/api/arquivos/{uuid}` | Publico | Baixa anexo ativo de servico ativo |
| `DELETE` | `/api/servicos/{id}/arquivos/{file_id}` | Prestador titular | Desativa logicamente anexo proprio |
| `POST` | `/api/eventos` | Organizador | Cria evento proprio |
| `GET` | `/api/eventos` | Organizador | Lista eventos proprios |
| `POST` | `/api/reservas` | Organizador | Solicita reserva em periodo disponivel e registra auditoria |
| `GET` | `/api/reservas` | Organizador ou prestador | Lista as reservas do ator autenticado |
| `GET` | `/api/reservas/{id}` | Participante | Consulta reserva propria |
| `POST` | `/api/reservas/{id}/analise` | Prestador titular | Transita de `SOLICITADA` para `EM_ANALISE` |
| `POST` | `/api/reservas/{id}/decisao` | Prestador titular | Aprova ou recusa; recusa exige justificativa com 10 caracteres ou mais |
| `POST` | `/api/reservas/{id}/confirmacao` | Organizador titular | Confirma aprovacao em ate 48 horas, sob bloqueio transacional da reserva |
| `POST` | `/api/reservas/{id}/cancelamento` | Organizador titular ou prestador titular | Cancela com justificativa de pelo menos 10 caracteres antes do inicio do evento; prestador somente cancela reservas confirmadas |
| `POST` | `/api/jobs/reservas/expiracoes` | Administrador | Expira reservas sem resposta ha 48 horas; destinado a uma rotina agendada |
| `GET` | `/api/reservas/{id}/historico` | Participante | Consulta transicoes em ordem cronologica |

O servidor valida papel, titularidade, periodo do evento, disponibilidade, estado atual, justificativa, prazo e conflitos. A expiracao tambem e verificada ao consultar ou tentar alterar uma reserva. As mutacoes e os respectivos registros de historico usam a mesma transacao PostgreSQL; o pre-bloqueio de agenda referencia diretamente a reserva e e liberado ao cancelar ou expirar. A restricao de exclusao de `reserva` e os bloqueios de linha protegem contra conflitos e requisicoes concorrentes.

Filtros de data devem ser enviados juntos e incluir fuso horario. Quando usados, o servico precisa ter um intervalo `DISPONIVEL` que cubra todo o periodo, sem bloqueio manual ou reserva ativa conflitante. A ordenacao por identificador e a paginacao limitada a 100 resultados permitem percorrer catalogos maiores.

Uploads verificam limite de bytes, extensao, assinatura do conteudo e MIME declarado. Em desenvolvimento, os binarios ficam em `LOCAL_DOS_ARQUIVOS` (padrao `./uploads`) e o banco armazena somente os metadados e URL. A rota de download consulta novamente o estado logico do anexo e do servico antes de entregar o arquivo.

## Testes

Prepare um banco isolado com as migracoes aplicadas e aponte `TEST_DATABASE_URL` para ele; nao use uma base com dados importantes. Execute:

```powershell
$env:TEST_DATABASE_URL = 'postgresql://postgres:SENHA_LOCAL@localhost:5432/eventfy_test'
pytest
```

Os testes de integracao cobrem cadastro e hash de senha, login/logout e revogacao de token, usuarios inativos, matriz de papeis e titularidade, filtros de catalogo, 200 servicos dentro do limite de 3 segundos, protecao de servico com reserva ativa, disponibilidade, validacao e ciclo de vida de anexos, fluxo de solicitacao ate confirmacao, cancelamento e liberacao de agenda, expiracao em cada etapa, historico, recusa sem motivo suficiente, controle de acesso, conflito de agenda e confirmacoes concorrentes.

Ao iniciar e ao terminar uma execucao, a fixture de testes recria completamente o schema do banco apontado por `TEST_DATABASE_URL` a partir das migracoes. Use exclusivamente um banco descartavel de testes: executar `pytest` duas vezes seguidas deve produzir o mesmo conjunto de dados sem conflitos residuais.
