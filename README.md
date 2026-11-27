<div align="center">

# 🎪 EventFy

**Plataforma web para centralização de serviços e estruturas para gestão de eventos**

[![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)](#)
[![Licença](https://img.shields.io/badge/licença-pendente-lightgrey)](#-licença)
[![UFT](https://img.shields.io/badge/UFT-Câmpus%20Palmas-blue)](#)
[![Disciplina](https://img.shields.io/badge/disciplina-Engenharia%20de%20Software-green)](#)

</div>

## Baseline e operacao pos-PR94

A baseline de partida desta entrega e o commit `5e15fa1`, merge da PR #94. Ela inclui a API FastAPI, autenticacao, migracoes V1 a V5, contrato em [`docs/API.md`](./docs/API.md), testes PostgreSQL e o prototipo estatico. A EVT-20 acrescenta a migracao V6 e as rotas administrativas descritas no contrato.

Pre-requisitos: Git 2.x, Python 3.14, PostgreSQL 17.x, `psql` e `createdb` no `PATH`. Instale as dependencias com `python -m pip install -r requirements-dev.txt`, copie `.env.example` para `.env` e configure somente valores locais para `URL_DO_BANCO`, `CHAVE_SECRETA_JWT` e `LOCAL_DOS_ARQUIVOS`. O repositorio nao deve conter segredos ou dados pessoais reais.

Aplique as migracoes com `scripts/db-setup.ps1 -Username eventfy_dev`; o script registra checksums e aplica V1 a V6 em ordem. Execute `pytest -q` duas vezes contra o banco de testes; a baseline original espera `18 passed` em cada rodada. Inicie a API com `uvicorn eventfy_api.main:app --app-dir api --env-file .env --reload` e confira `/api/health` e `/docs`.

A operacao, os limites e a conferencia cruzada estao em [`docs/README_ENTREGA.md`](./docs/README_ENTREGA.md) e [`docs/CONFERENCIA_CRUZADA.md`](./docs/CONFERENCIA_CRUZADA.md).

---

## 📑 Sumário

- [📌 Sobre o Projeto](#-sobre-o-projeto)
- [🛑 Problema](#-problema)
- [💡 Solução Proposta](#-solução-proposta)
- [👥 Principais Usuários](#-principais-usuários)
- [⚙️ Funcionalidades](#️-funcionalidades)
- [🏗️ Artefatos de Engenharia de Software](#️-artefatos-de-engenharia-de-software)
- [🧩 Arquitetura e Modelagem](#-arquitetura-e-modelagem)
- [🛠️ Tecnologias](#️-tecnologias)
- [🚀 Execução](#-execução)
- [📚 Documentação](#-documentação)
- [👥 Equipe](#-equipe)
- [📜 Licença](#-licença)

---

## 📌 Sobre o Projeto

O **EventFy** é uma proposta de plataforma web destinada a conectar **organizadores de eventos** a **prestadores de serviços e fornecedores de infraestrutura**.

A plataforma busca centralizar a descoberta de serviços, o gerenciamento de eventos e o processo de solicitação e acompanhamento de reservas, reduzindo a necessidade de utilizar diferentes canais para organizar os serviços necessários para um evento.

> Projeto acadêmico desenvolvido para a disciplina de **Engenharia de Software** do curso de **Ciência da Computação** da **Universidade Federal do Tocantins (UFT)** — Câmpus Palmas.

O projeto está sendo desenvolvido seguindo práticas de Engenharia de Software, com foco em:

- Definição e validação de requisitos
- Modelagem do domínio
- Modelagem de dados
- Prototipação
- Definição da arquitetura do sistema

---

## 🛑 Problema

A organização de eventos pode exigir que o responsável procure diferentes prestadores e fornecedores utilizando canais distintos, como redes sociais, aplicativos de mensagens e outros meios de comunicação.

Essa dispersão pode dificultar:

- 🔍 A localização de serviços adequados
- ⚖️ A comparação entre diferentes opções
- 📋 O acompanhamento das solicitações
- 📅 O controle das datas e reservas
- 🗂️ A organização dos serviços contratados para cada evento

O EventFy busca centralizar essas atividades em uma única plataforma.

---

## 💡 Solução Proposta

O EventFy disponibiliza um **catálogo de serviços e estruturas** que permite ao organizador consultar opções disponíveis e solicitar reservas de acordo com as necessidades de seu evento.

A proposta contempla, entre outras atividades:

- Cadastro e autenticação de usuários
- Gerenciamento de eventos
- Cadastro e consulta de serviços
- Busca e filtragem de serviços
- Solicitação de reservas
- Análise de solicitações pelos prestadores
- Aprovação ou recusa de reservas
- Acompanhamento do estado das reservas
- Gerenciamento dos serviços associados a um evento

> O funcionamento detalhado dessas funcionalidades está especificado no documento de requisitos do projeto: [`REQUISITOS.md`](./docs/REQUISITOS.md).

---

## 👥 Principais Usuários

O sistema considera diferentes papéis envolvidos no processo de organização de eventos.

| Papel | Descrição |
|---|---|
| 🧑‍💼 **Organizador** | Usuário responsável por criar e gerenciar eventos e solicitar serviços para esses eventos. |
| 🏢 **Prestador ou fornecedor** | Usuário responsável por disponibilizar serviços ou estruturas e analisar solicitações de reserva. |
| 🛡️ **Administrador** | Gerencia contas e modera publicações conforme RF20; as rotas implementadas estão em [`docs/API.md`](./docs/API.md). |

As permissões dos papéis estão especificadas em [`docs/REQUISITOS.md`](./docs/REQUISITOS.md). A administração e moderação estão implementadas no backend conforme a EVT-20.

---

## ⚙️ Funcionalidades

O escopo funcional especificado para o EventFy inclui:

- Cadastro, autenticação e gerenciamento de perfil de usuários.
- Cadastro e manutenção de serviços e eventos.
- Catálogo, busca, filtros e consulta de detalhes dos serviços.
- Disponibilidade e solicitação de reserva vinculada a evento e período.
- Análise pelo prestador, aprovação ou recusa com motivo obrigatório e confirmação pelo organizador.
- Acompanhamento e histórico das transições da reserva.
- Cancelamento justificado conforme as regras de negócio.
- Avaliação do serviço pelo organizador após a finalização.
- Anexos de serviços e gerenciamento de contas/moderação, conforme RF19 e RF20.

Esta lista descreve funcionalidades especificadas, não afirma que a aplicação já esteja implementada. A situação de implementação é descrita em “Execução”.

> Os detalhes e critérios de cada funcionalidade estão documentados em [`REQUISITOS.md`](./docs/REQUISITOS.md).

---

## 🏗️ Artefatos de Engenharia de Software

Os principais artefatos produzidos durante o desenvolvimento do projeto estão organizados no próprio repositório.

| Artefato | Local | Descrição |
|---|---|---|
| Backlog de execução | [`docs/BACKLOG.md`](./docs/BACKLOG.md) | Lacunas, responsáveis, dependências e issues prontas para o GitHub |
| Validação com usuário externo | [`docs/VALIDACAO-USUARIO-EVT-24.md`](./docs/VALIDACAO-USUARIO-EVT-24.md) | Roteiro, registro de observações, rastreabilidade e retorno ao backlog |
| Review parcial executável | [`docs/REVIEW-PARCIAL-EVT-08.md`](./docs/REVIEW-PARCIAL-EVT-08.md) | Baseline, roteiro por tela e critério, limitações e plano de falha |
| Banco de dados local | [`docs/DATABASE.md`](./docs/DATABASE.md) | PostgreSQL, migrações versionadas e dados fictícios de demonstração |
| API REST | [`docs/API.md`](./docs/API.md) | Execução local, autenticação e contrato dos endpoints |
| Requisitos | [`docs/REQUISITOS.md`](./docs/REQUISITOS.md) | Requisitos funcionais, não funcionais e regras de negócio |
| Projeto | [`docs/PROJETO.md`](./docs/PROJETO.md) | Informações do projeto, decisões, fichas CRC e critérios de Parnas |
| Tema | [`docs/TEMA.md`](./docs/TEMA.md) | Contextualização do tema, problemas, usuários e alinhamento com a disciplina |
| Descoberta | [`DESCOBERTA.md`](./DESCOBERTA.md) | Problema, partes interessadas, personas, necessidades N1..N5 e riscos |
| Processo de Desenvolvimento | [`PROCESSO.md`](./PROCESSO.md) | Fatores de Boehm & Turner, iterações de 2 semanas, papéis e Definição de Pronto |
| Processos de Negócio | [`docs/PROCESSOS-NEGOCIO.md`](./docs/PROCESSOS-NEGOCIO.md) | Especificação detalhada dos processos de negócio e máquina de estados |
| Modelagem | [`docs/diagrams/`](./docs/diagrams) | Domínio, dados, estados da reserva e sequência UML |
| Protótipo | [`prototipo/`](./prototipo) | Protótipo navegável da aplicação |
| Conferência cruzada | [`docs/CONFERENCIA_CRUZADA.md`](./docs/CONFERENCIA_CRUZADA.md) | Registro da conferência entre os diferentes artefatos do projeto |
| Entrega e operação | [`docs/README_ENTREGA.md`](./docs/README_ENTREGA.md) | Baseline, reprodução local, operação e limites conhecidos |
| Inspeção formal de requisitos | [`INSPECOES.md`](./INSPECOES.md) | Papéis, achados classificados, retrabalho, recheck e rastreabilidade da EVT-22 |
| Contribuição | [`CONTRIBUTING.md`](./CONTRIBUTING.md) | Orientações de contribuição, revisão e critérios de qualidade |
| Registro de Mudanças | [`CHANGELOG.md`](./CHANGELOG.md) | Histórico de versões e notas de lançamento (SemVer) |

---

## 🧩 Arquitetura e Modelagem

O frontend usa uma API REST/JSON. O backend segue um monólito modular para que reserva, bloqueio de agenda e histórico possam ser gravados na mesma transação. As quatro vistas e as decisões sobre banco, anexos e autenticação estão em [ARQUITETURA.md](./ARQUITETURA.md).

---

## 🛠️ Tecnologias

O ambiente local usa HTML, CSS e JavaScript nativos, Python 3.14, FastAPI, Uvicorn, Psycopg 3 e PostgreSQL 17. As versões das dependências do ambiente estão em [requirements-dev.txt](./requirements-dev.txt). As escolhas para autenticação e testes constam na [arquitetura](./ARQUITETURA.md).

---

## 🚀 Execução

Instale Git, Python **3.14** e PostgreSQL **17** com as ferramentas de linha de comando. Inicie o serviço PostgreSQL. Na primeira execução, clone o projeto e crie um usuário e um banco locais. Os comandos abaixo presumem que o administrador local se chama `postgres`. O primeiro comando do PostgreSQL solicita que você escolha a senha de `eventfy_dev`.

```sh
git clone https://github.com/dudanegreiro/EventFy.git
cd EventFy
createuser -h 127.0.0.1 -U postgres --pwprompt eventfy_dev
createdb -h 127.0.0.1 -U postgres --owner=eventfy_dev eventfy
```

No Windows, você também pode preparar o esquema e os dados de demonstração com o script de migrações, usando o usuário criado acima:

```powershell
.\scripts\db-setup.ps1 -Username eventfy_dev
```

Para restaurar os dados isolados da review parcial, execute `.\scripts\restore-demo-data.ps1 -Confirm`. O roteiro e o plano de falha estão em [`docs/REVIEW-PARCIAL-EVT-08.md`](./docs/REVIEW-PARCIAL-EVT-08.md).

Consulte [Banco de dados local](./docs/DATABASE.md) para os pré-requisitos e detalhes do script.

Na raiz do projeto, prepare o ambiente conforme seu sistema.

**Windows (PowerShell)**

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

**Linux ou macOS**

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
cp .env.example .env
```

Em `.env`, substitua `SUBSTITUA_LOCALMENTE` pela senha de `eventfy_dev` em `URL_DO_BANCO`, gere um segredo aleatório com pelo menos 32 caracteres para `CHAVE_SECRETA_JWT` e configure `LOCAL_DOS_ARQUIVOS` se necessário. Codifique caracteres reservados da senha na URL (por exemplo, `@` vira `%40`). Guarde o arquivo apenas na sua máquina.

| Sistema | Comando para iniciar na raiz do projeto |
|---|---|
| Windows | `.\.venv\Scripts\python.exe -m uvicorn eventfy_api.main:app --app-dir api --env-file .env --reload` |
| Linux ou macOS | `.venv/bin/python -m uvicorn eventfy_api.main:app --app-dir api --env-file .env --reload` |

O health check da API fica em `http://127.0.0.1:8000/api/health`; a documentação interativa fica em `http://127.0.0.1:8000/docs`. Para percorrer o protótipo estático, siga [`prototipo/README.md`](./prototipo/README.md) e abra `prototipo/index.html` em um navegador.

Use `Ctrl+C` para encerrar o servidor. Nas próximas execuções, basta iniciar o PostgreSQL e repetir o comando do Uvicorn. O esquema, as migrações e as contas fictícias estão descritos em [Banco de dados local](./docs/DATABASE.md); as rotas e credenciais de demonstração estão em [API REST](./docs/API.md).

---

## 📚 Documentação

| Documento | Descrição |
|---|---|
| [`docs/VALIDACAO-USUARIO-EVT-24.md`](./docs/VALIDACAO-USUARIO-EVT-24.md) | Roteiro e relatório de validação do fluxo principal com usuário externo |
| [`docs/REVIEW-PARCIAL-EVT-08.md`](./docs/REVIEW-PARCIAL-EVT-08.md) | Baseline e roteiro da demonstração parcial com plano de falha |
| [`docs/DATABASE.md`](./docs/DATABASE.md) | Configuração do PostgreSQL, migrações e dados de demonstração |
| [`docs/API.md`](./docs/API.md) | Execução local, autenticação e contrato da API REST |
| [`docs/PROJETO.md`](./docs/PROJETO.md) | Organização, decisões, fichas CRC e critérios de isolamento |
| [`docs/REQUISITOS.md`](./docs/REQUISITOS.md) | Especificação dos requisitos, backlog ordenado e critérios |
| [`docs/TEMA.md`](./docs/TEMA.md) | Contextualização do tema, problemas, usuários e verificação |
| [`DESCOBERTA.md`](./DESCOBERTA.md) | Descoberta do problema, stakeholders, personas e riscos |
| [`PROCESSO.md`](./PROCESSO.md) | Processo de desenvolvimento, fatores de Boehm & Turner e DoD |
| [`docs/PROCESSOS-NEGOCIO.md`](./docs/PROCESSOS-NEGOCIO.md) | Processos de negócio e máquina de estados |
| [`docs/diagrams/`](./docs/diagrams) | Diagramas conceituais, relacionais e comportamentais (.mmd) |
| [`docs/CONFERENCIA_CRUZADA.md`](./docs/CONFERENCIA_CRUZADA.md) | Conferência cruzada formal entre artefatos |
| [`docs/README_ENTREGA.md`](./docs/README_ENTREGA.md) | Baseline operacional, reprodução local e limites da entrega |
| [`INSPECOES.md`](./INSPECOES.md) | Inspeção formal de requisitos da EVT-22 |
| [`CONTRIBUTING.md`](./CONTRIBUTING.md) | Processo de contribuição e diretrizes de revisão |
| [`CHANGELOG.md`](./CHANGELOG.md) | Registro de mudanças e versionamento semântico |
| [`prototipo/`](./prototipo) | Protótipo navegável da aplicação |

---

## 👥 Equipe

Projeto desenvolvido para a disciplina de **Engenharia de Software** da Universidade Federal do Tocantins — Câmpus Palmas.

| Integrante | Papel | GitHub |
|---|---|---|
| Eduarda Negreiro | Produto e requisitos | [@dudanegreiro](https://github.com/dudanegreiro) |
| Gustavo Leite Bringel | Dados e backend | [@GustavoBringel](https://github.com/GustavoBringel) |
| Igor Anicezio Oliveira | Arquitetura e integração | [@IgorAnicezioOliveira](https://github.com/IgorAnicezioOliveira) |
| Thalita Teixeira Menezes | Processos e qualidade | [@thalist](https://github.com/thalist) |
| José Guilherme Costa Oliveira | Interface e experiência | [@ZezinG14](https://github.com/ZezinG14) |

**Docente responsável:** Prof. Jackson Gomes de Souza

### Decisões que dependem da equipe

- Confirmar a correspondência entre “Duda Negreiro” e “Eduarda Negreiro”, a atribuição de Product Owner e o mapeamento dos papéis Pessoa 1–5 para os integrantes. O plano de divisão de tarefas disponível não identifica os nomes por pessoa.
- Aprovar a licença de distribuição antes de criar um arquivo `LICENSE`.
- Revisar as decisões da [EVT-01](./ARQUITETURA.md) no pull request da entrega.
- Realizar e registrar a validação de usabilidade do protótipo e a linha de base quantitativa descrita em [`docs/TEMA.md`](./docs/TEMA.md).

---

## 📜 Licença

Este projeto foi desenvolvido para fins acadêmicos no contexto da disciplina de Engenharia de Software da Universidade Federal do Tocantins.

**Status:** licença ainda não aprovada. A equipe deve decidir os termos de distribuição antes de adicionar um arquivo `LICENSE` ou divulgar uma licença como adotada.

---

<div align="center">

Feito com 💙 por alunos da **UFT — Câmpus Palmas**

</div>
