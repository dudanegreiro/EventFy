<div align="center">

# 🎪 EventFy

**Plataforma web para centralização de serviços e estruturas para gestão de eventos**

[![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)](#)
[![Licença](https://img.shields.io/badge/licença-pendente-lightgrey)](#-licença)
[![UFT](https://img.shields.io/badge/UFT-Câmpus%20Palmas-blue)](#)
[![Disciplina](https://img.shields.io/badge/disciplina-Engenharia%20de%20Software-green)](#)

</div>

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
| 🛡️ **Administrador** | O requisito RF20 especifica gerenciamento de contas e moderação de publicações. A inclusão dessa funcionalidade no MVP depende da decisão registrada em “Decisões que dependem da equipe”. |

As permissões dos papéis estão especificadas em [`docs/REQUISITOS.md`](./docs/REQUISITOS.md). A decisão pendente refere-se à inclusão da administração e moderação no escopo do MVP, não à existência do papel nos requisitos.

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
| Requisitos | [`docs/REQUISITOS.md`](./docs/REQUISITOS.md) | Requisitos funcionais, não funcionais e regras de negócio |
| Projeto | [`docs/PROJETO.md`](./docs/PROJETO.md) | Informações do projeto, decisões, fichas CRC e critérios de Parnas |
| Tema | [`docs/TEMA.md`](./docs/TEMA.md) | Contextualização do tema, problemas, usuários e alinhamento com a disciplina |
| Descoberta | [`DESCOBERTA.md`](./DESCOBERTA.md) | Problema, partes interessadas, personas, necessidades N1..N5 e riscos |
| Processo de Desenvolvimento | [`PROCESSO.md`](./PROCESSO.md) | Fatores de Boehm & Turner, iterações de 2 semanas, papéis e Definição de Pronto |
| Processos de Negócio | [`docs/PROCESSOS-NEGOCIO.md`](./docs/PROCESSOS-NEGOCIO.md) | Especificação detalhada dos processos de negócio e máquina de estados |
| Modelagem | [`docs/diagrams/`](./docs/diagrams) | Domínio, dados, estados da reserva e sequência UML |
| Protótipo | [`prototipo/`](./prototipo) | Protótipo navegável da aplicação |
| Conferência cruzada | [`docs/CONFERENCIA_CRUZADA.md`](./docs/CONFERENCIA_CRUZADA.md) | Registro da conferência entre os diferentes artefatos do projeto |
| Contribuição | [`CONTRIBUTING.md`](./CONTRIBUTING.md) | Orientações de contribuição, revisão e critérios de qualidade |
| Registro de Mudanças | [`CHANGELOG.md`](./CHANGELOG.md) | Histórico de versões e notas de lançamento (SemVer) |

---

## 🧩 Arquitetura e Modelagem

A arquitetura do EventFy deve seguir os requisitos e modelos estabelecidos para o sistema. A especificação determina frontend desacoplado consumindo backend por API REST/JSON e persistência relacional (RE-01 e RE-02).

O documento arquitetural deve especificar:

- Componentes da aplicação
- Responsabilidades de cada componente
- Comunicação entre os componentes
- Persistência dos dados
- Contrato da API entre frontend e backend
- Tecnologias utilizadas
- Decisões arquiteturais e suas justificativas

Essa especificação é responsabilidade da Pessoa 5, com decisão de stack pendente de validação pela equipe.

---

## 🛠️ Tecnologias

**Decisão pendente:** a Pessoa 5 deve propor frontend, backend, banco de dados e versões em `ARQUITETURA.md`; a equipe precisa aprovar a escolha antes de esta seção registrar uma stack.

---

## 🚀 Execução

O repositório contém especificação, modelos e um protótipo estático; ainda não contém uma aplicação executável com backend e banco de dados. Para percorrer o protótipo, siga as instruções em [`prototipo/README.md`](./prototipo/README.md) e abra `prototipo/index.html` em um navegador.

---

## 📚 Documentação

| Documento | Descrição |
|---|---|
| [`docs/PROJETO.md`](./docs/PROJETO.md) | Organização, decisões, fichas CRC e critérios de isolamento |
| [`docs/REQUISITOS.md`](./docs/REQUISITOS.md) | Especificação dos requisitos, backlog ordenado e critérios |
| [`docs/TEMA.md`](./docs/TEMA.md) | Contextualização do tema, problemas, usuários e verificação |
| [`DESCOBERTA.md`](./DESCOBERTA.md) | Descoberta do problema, stakeholders, personas e riscos |
| [`PROCESSO.md`](./PROCESSO.md) | Processo de desenvolvimento, fatores de Boehm & Turner e DoD |
| [`docs/PROCESSOS-NEGOCIO.md`](./docs/PROCESSOS-NEGOCIO.md) | Processos de negócio e máquina de estados |
| [`docs/diagrams/`](./docs/diagrams) | Diagramas conceituais, relacionais e comportamentais (.mmd) |
| [`docs/CONFERENCIA_CRUZADA.md`](./docs/CONFERENCIA_CRUZADA.md) | Conferência cruzada formal entre artefatos |
| [`CONTRIBUTING.md`](./CONTRIBUTING.md) | Processo de contribuição e diretrizes de revisão |
| [`CHANGELOG.md`](./CHANGELOG.md) | Registro de mudanças e versionamento semântico |
| [`prototipo/`](./prototipo) | Protótipo navegável da aplicação |

---

## 👥 Equipe

Projeto desenvolvido para a disciplina de **Engenharia de Software** da Universidade Federal do Tocantins — Câmpus Palmas.

| Integrante | Papel | GitHub |
|---|---|---|
| Eduarda Negreiro | Levantamento, revisão e rastreabilidade de requisitos ([PROJETO.md](./docs/PROJETO.md)). A função de PO está atribuída a “Duda Negreiro” em [PROCESSO.md](./PROCESSO.md); confirmar se o nome corresponde. | [@dudanegreiro](https://github.com/dudanegreiro) |
| Gustavo Leite Bringel | Atribuição individual não registrada nos artefatos consultados; confirmar com a equipe. | [@GustavoBringel](https://github.com/GustavoBringel) |
| Igor Anicezio Oliveira | Arquitetura, modelagem e integridade técnica ([PROCESSO.md](./PROCESSO.md) e [PROJETO.md](./docs/PROJETO.md)). | [@IgorAnicezioOliveira](https://github.com/IgorAnicezioOliveira) |
| Thalita Teixeira Menezes | Processos de negócio e reconciliação ([PROJETO.md](./docs/PROJETO.md)). | [@thalist](https://github.com/thalist) |
| José Guilherme Costa Oliveira | Atribuição individual não registrada nos artefatos consultados; confirmar com a equipe. | [@ZezinG14](https://github.com/ZezinG14) |

**Docente responsável:** Prof. Jackson Gomes de Souza

### Decisões que dependem da equipe

- Confirmar a correspondência entre “Duda Negreiro” e “Eduarda Negreiro”, a atribuição de Product Owner e o mapeamento dos papéis Pessoa 1–5 para os integrantes. O plano de divisão de tarefas disponível não identifica os nomes por pessoa.
- Decidir se administração e moderação (RF20) integram o MVP. O requisito está especificado, mas não consta no escopo ativo de [`DESCOBERTA.md`](./DESCOBERTA.md).
- Aprovar a licença de distribuição antes de criar um arquivo `LICENSE`.
- Aprovar a stack proposta pela Pessoa 5 antes de registrá-la como tecnologia adotada.
- Realizar e registrar a validação de usabilidade do protótipo e a linha de base quantitativa descrita em [`docs/TEMA.md`](./docs/TEMA.md).

---

## 📜 Licença

Este projeto foi desenvolvido para fins acadêmicos no contexto da disciplina de Engenharia de Software da Universidade Federal do Tocantins.

**Status:** licença ainda não aprovada. A equipe deve decidir os termos de distribuição antes de adicionar um arquivo `LICENSE` ou divulgar uma licença como adotada.

---

<div align="center">

Feito com 💙 por alunos da **UFT — Câmpus Palmas**

</div>
