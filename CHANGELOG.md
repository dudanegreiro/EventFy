# 📝 Registro de Mudanças (Changelog) — EventFy

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

---

## [Unreleased]

> Rascunho de release; nenhuma tag é criada por esta alteração.

### Adicionado
- EVT-23 (#43) — `TESTES.md` com a estratégia de testes em quatro níveis, 31 casos nas seis áreas críticas (agenda, autenticação, autorização, estados, anexos e auditoria), omissões deliberadas e dúvidas em aberto.
- EVT-24 (#44) — Roteiro de validação externa com tarefas neutras, registro de observações, rastreabilidade, retorno ao backlog e testes automatizados da estrutura documental.
- EVT-01 (#21) — Quatro vistas arquiteturais, decisões de banco, anexos e autenticação e ambiente local com verificação da conexão ao PostgreSQL.
- Esquema PostgreSQL 17, migrações versionadas, dados fictícios e script PowerShell para preparar o banco local.
- Documentação de configuração e acesso ao banco pelo pgAdmin em `docs/DATABASE.md`.
- Governança do processo, rastreabilidade de Issues/PRs e orientações de configuração do repositório entregues pela Pessoa 1.
- Fluxo navegável do protótipo para solicitação, análise, aprovação, recusa, confirmação, histórico e cancelamento justificado.
- `ITERACOES.md` com o replanejamento até 03/12, o plano da Iteração 2 e a retrospectiva da Iteração 1, com a fonte de cada dado (EVT-11, #31, parcial).

### Review parcial e operação da baseline
- `review-parcial-evt08` permanece identificada como a baseline anterior à PR [#94](https://github.com/dudanegreiro/EventFy/pull/94), baseada em `dev/ambiente.py`, no protótipo e nas migrações V1/V2.
- A baseline pós-PR #94 deverá ser identificada por uma nova tag, como `review-parcial-evt08-v2`, somente depois do merge e da demonstração do commit correspondente.
- Após a integração das migrações V3–V5, a restauração de dados demo deverá usar `scripts/restore-demo-data.ps1`, incluindo `public.sessao_autenticacao` no conjunto de tabelas dependentes e recompondo o vínculo `id_reserva` exigido pela V5. A execução isolada da V2 não é um procedimento válido para essa baseline.

### Alterado
- README e documentação do projeto para registrar a escolha do PostgreSQL no escopo da issue #22.
- README e changelog alinhados às duas baselines da review parcial e ao procedimento de restauração compatível com a pilha de migrações V1–V5 da PR #94.
- Documentação institucional, tema e papéis da equipe; arquivos de ambiente e instruções de Git.
- Guia de navegação do protótipo e documentação das limitações da demonstração estática.

### Preparação da versão
- A próxima versão e a tag pós-PR #94 devem ser confirmadas pela equipe antes da publicação. A seção permanece `Unreleased` até essa decisão.

---

## [0.2.0] - 2026-10-21

### Adicionado
- Especificação formal da arquitetura e decisões de isolamento por critérios de David Parnas em `PROJETO.md`.
- Consolidação dos 8 estados do ciclo de vida da reserva (`SOLICITADA`, `EM_ANALISE`, `APROVADA`, `CONFIRMADA`, `RECUSADA`, `CANCELADA`, `EXPIRADA`, `FINALIZADA`).
- Diagrama de sequência UML para o fluxo principal de reserva e recusa justificada.
- Protótipo navegável em HTML/CSS/JS cobrindo fluxo de solicitação, aprovação e tela de recusa com motivo obrigatório.
- Documentação do tema do projeto em `docs/TEMA.md`.

### Alterado
- Reconciliação dos requisitos em `REQUISITOS.md` com os novos diagramas e regras de negócio RN01 a RN07.
- Reestruturação de `PROCESSOS-NEGOCIO.md` com mapeamento detalhado dos fluxos P01 a P10.

---

## [0.1.0] - 2026-09-03

### Adicionado
- Estrutura inicial do repositório configurada.
- Documento `README.md` com apresentação da proposta do EventFy, atores e escopo inicial.
- Guia de contribuição `CONTRIBUTING.md` com convenções de ramos, commits e pull requests.
- Especificação inicial de requisitos e regras de negócio.
- Modelagem conceitual preliminar de domínio e dados.
