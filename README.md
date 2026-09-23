<div align="center">

# 🎪 EventFy

**Plataforma web para centralização de serviços e estruturas para gestão de eventos**

[![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)](#)
[![Licença](https://img.shields.io/badge/licença-a%20definir-lightgrey)](#-licença)
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

> O funcionamento detalhado dessas funcionalidades está especificado no documento de requisitos do projeto: [`REQUISITOS.md`](./REQUISITOS.md).

---

## 👥 Principais Usuários

O sistema considera diferentes papéis envolvidos no processo de organização de eventos.

| Papel | Descrição |
|---|---|
| 🧑‍💼 **Organizador** | Usuário responsável por criar e gerenciar eventos e solicitar serviços para esses eventos. |
| 🏢 **Prestador ou fornecedor** | Usuário responsável por disponibilizar serviços ou estruturas e analisar solicitações de reserva. |
| 🛡️ **Administrador** | Caso seja adotado no escopo final do sistema, será responsável por atividades administrativas necessárias ao gerenciamento da plataforma. |

> As permissões e responsabilidades de cada perfil devem ser definidas na especificação de requisitos.

---

## ⚙️ Funcionalidades

As principais funcionalidades previstas para o EventFy incluem:

- [ ] **Cadastro de usuários** — criação de contas com informações necessárias para utilização da plataforma
- [ ] **Autenticação** — acesso à plataforma por meio das credenciais cadastradas
- [ ] **Catálogo de serviços** — consulta aos serviços e estruturas disponibilizados pelos prestadores
- [ ] **Busca e filtragem** — localização de serviços de acordo com critérios definidos pelo sistema
- [ ] **Gerenciamento de eventos** — criação e gerenciamento dos eventos do organizador
- [ ] **Solicitação de reserva** — solicitação de um serviço para determinado evento e período
- [ ] **Gerenciamento de reservas** — acompanhamento do ciclo de vida das solicitações
- [ ] **Análise de solicitações** — possibilidade de o prestador analisar uma solicitação e aprová-la ou recusá-la
- [ ] **Cancelamento** — cancelamento de reservas de acordo com as regras de negócio definidas
- [ ] **Avaliação** — avaliação de serviços após a conclusão de uma contratação *(caso permaneça no escopo da versão atual)*

> Os detalhes e critérios de cada funcionalidade estão documentados em [`REQUISITOS.md`](./REQUISITOS.md).

---

## 🏗️ Artefatos de Engenharia de Software

Os principais artefatos produzidos durante o desenvolvimento do projeto estão organizados no próprio repositório.

| Artefato | Local | Descrição |
|---|---|---|
| Requisitos | [`REQUISITOS.md`](./REQUISITOS.md) | Requisitos funcionais, requisitos não funcionais e regras de negócio |
| Projeto | [`PROJETO.md`](./PROJETO.md) | Informações sobre o projeto, decisões e organização dos artefatos |
| Modelagem | [`diagrams/`](./diagrams) | Modelo de domínio, modelo de dados, modelo de estados e demais diagramas |
| Protótipo | [`prototipo/`](./prototipo) | Protótipo navegável da aplicação |
| Conferência cruzada | [`CONFERENCIA_CRUZADA.md`](./CONFERENCIA_CRUZADA.md) | Registro da conferência entre os diferentes artefatos do projeto |
| Contribuição | [`CONTRIBUTING.md`](./CONTRIBUTING.md) | Orientações relacionadas ao processo de contribuição e organização do projeto |

---

## 🧩 Arquitetura e Modelagem

A arquitetura do EventFy será definida a partir dos requisitos e modelos estabelecidos para o sistema.

A documentação arquitetural deverá especificar:

- Componentes da aplicação
- Responsabilidades de cada componente
- Comunicação entre os componentes
- Persistência dos dados
- Interfaces entre frontend e backend, caso sejam adotados
- Tecnologias utilizadas
- Decisões arquiteturais e suas justificativas

> Os diagramas e decisões arquiteturais devem permanecer consistentes com os requisitos e com o modelo de domínio.

---

## 🛠️ Tecnologias

> ⚠️ As tecnologias de implementação **ainda não estão definidas/documentadas** neste repositório.

Quando a implementação for iniciada, esta seção deverá informar, no mínimo:

| Camada | Informação a preencher |
|---|---|
| **Frontend** | Tecnologia e versão |
| **Backend** | Tecnologia e versão |
| **Banco de dados** | SGBD e versão |
| **Outras tecnologias** | Bibliotecas, frameworks e ferramentas relevantes |

Não são informadas tecnologias nesta versão do README sem que elas estejam efetivamente definidas no projeto.

---

## 🚀 Execução

No estado atual do repositório, os artefatos disponíveis são predominantemente de **especificação, modelagem e prototipação**. Por isso, não é apresentado um comando de execução de uma aplicação que ainda não esteja disponível no repositório.

Quando a implementação estiver disponível, esta seção deverá conter:

- [ ] Pré-requisitos
- [ ] Versão das ferramentas necessárias
- [ ] Procedimento para instalação
- [ ] Configuração das variáveis de ambiente
- [ ] Configuração do banco de dados
- [ ] Comando para iniciar o backend
- [ ] Comando para iniciar o frontend
- [ ] Endereço para acesso à aplicação
- [ ] Informações necessárias para executar o sistema localmente

---

## 📚 Documentação

| Documento | Descrição |
|---|---|
| [`PROJETO.md`](./PROJETO.md) | Organização e informações gerais do projeto |
| [`REQUISITOS.md`](./REQUISITOS.md) | Especificação dos requisitos e regras de negócio |
| [`CONFERENCIA_CRUZADA.md`](./CONFERENCIA_CRUZADA.md) | Conferência entre os artefatos |
| [`CONTRIBUTING.md`](./CONTRIBUTING.md) | Processo de contribuição |
| [`diagrams/`](./diagrams) | Diagramas e modelos do sistema |
| [`prototipo/`](./prototipo) | Protótipo da aplicação |

---

## 👥 Equipe

Projeto desenvolvido para a disciplina de **Engenharia de Software** da Universidade Federal do Tocantins — Câmpus Palmas.

| Integrante | Papel | GitHub |
|---|---|---|
| Eduarda Negreiro | A definir | [@dudanegreiro](https://github.com/dudanegreiro) |
| Gustavo Leite Bringel | A definir | [@GustavoBringel](https://github.com/GustavoBringel) |
| Igor Anicezio Oliveira | A definir | [@IgorAnicezioOliveira](https://github.com/IgorAnicezioOliveira) |
| Thalita Teixeira Menezes | A definir | [@thalist](https://github.com/thalist) |
| José Guilherme Costa Oliveira | A definir | [@ZezinG14](https://github.com/ZezinG14) |

**Docente responsável:** Prof. Jackson Gomes de Souza

---

## 📜 Licença

Este projeto foi desenvolvido para fins acadêmicos no contexto da disciplina de Engenharia de Software da Universidade Federal do Tocantins.

A licença de distribuição do projeto deverá ser definida pela equipe caso o repositório seja disponibilizado como software de código aberto.

---

<div align="center">

Feito com 💙 por alunos da **UFT — Câmpus Palmas**

</div>
