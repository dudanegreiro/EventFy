# PROJETO — EventFy

## 📑 Sumário

- [1. Identificação](#1-identificação)
- [2. Problema](#2-problema)
- [3. Objetivo](#3-objetivo)
- [4. Stakeholders e Usuários](#4-stakeholders-e-usuários)
- [5. Escopo](#5-escopo)
- [6. Modelo de Domínio](#6-modelo-de-domínio)
- [7. Rastreabilidade](#7-rastreabilidade)
- [8. Modelo de Dados](#8-modelo-de-dados)
- [9. Decisões de Identidade](#9-decisões-de-identidade)
- [10. Decisões de Apagamento](#10-decisões-de-apagamento)
- [11. Representação de Tempo](#11-representação-de-tempo)
- [12. Armazenamento de Arquivos](#12-armazenamento-de-arquivos)
- [13. Ciclo de Vida da Reserva](#13-ciclo-de-vida-da-reserva)
- [14. Lacunas Identificadas pela Modelagem](#14-lacunas-identificadas-pela-modelagem)
- [15. Distribuição de Responsabilidades](#15-distribuição-de-responsabilidades)
- [16. Decisões do Projeto](#16-decisões-do-projeto)
- [17. Conferência Cruzada](#17-conferência-cruzada)
- [18. Protótipo](#18-protótipo)
- [19. Relação entre os Artefatos](#19-relação-entre-os-artefatos)
- [20. Estrutura da Entrega](#20-estrutura-da-entrega)

---

## 1. Identificação

| Campo | Descrição |
|---|---|
| **Projeto** | EventFy |
| **Disciplina** | Engenharia de Software |
| **Instituição** | Universidade Federal do Tocantins (UFT) — Câmpus Palmas |

O **EventFy** é uma proposta de plataforma web destinada a conectar organizadores de eventos a prestadores de serviços e fornecedores de infraestrutura, centralizando a consulta de serviços, a solicitação de reservas e o acompanhamento das contratações.

O projeto é desenvolvido utilizando práticas de Engenharia de Software, contemplando levantamento e especificação de requisitos, modelagem do domínio, modelagem de dados, prototipação e definição arquitetural.

---

## 2. Problema

A organização de eventos pode exigir que o responsável procure diferentes prestadores e fornecedores por meio de canais distintos.

Essa dispersão dificulta:

- A localização de serviços adequados
- A consulta das informações dos serviços
- A comparação entre opções disponíveis
- O acompanhamento das solicitações
- O controle das reservas relacionadas a um evento

O EventFy busca centralizar essas atividades em uma única plataforma, permitindo que organizadores encontrem serviços e que prestadores gerenciem as solicitações relacionadas aos serviços disponibilizados.

---

## 3. Objetivo

### 3.1 Objetivo geral

Desenvolver uma plataforma web que centralize a consulta, solicitação e acompanhamento de serviços destinados à organização de eventos.

### 3.2 Objetivos específicos

- Permitir o cadastro e a autenticação dos usuários
- Permitir o cadastro e o gerenciamento de eventos
- Disponibilizar um catálogo de serviços e estruturas
- Permitir a consulta e a busca de serviços
- Permitir que organizadores solicitem serviços para seus eventos
- Permitir que prestadores analisem solicitações de reserva
- Controlar o ciclo de vida das reservas
- Registrar informações necessárias para manter o histórico das reservas
- Permitir a avaliação de serviços quando essa funcionalidade estiver habilitada no escopo da versão

---

## 4. Stakeholders e Usuários

### 4.1 Organizador

É o usuário responsável pela organização de um evento.

Suas principais necessidades são:

- Cadastrar e gerenciar eventos
- Consultar serviços
- Encontrar serviços adequados ao evento
- Solicitar reservas
- Acompanhar o estado das solicitações
- Cancelar reservas de acordo com as regras estabelecidas
- Avaliar serviços quando a funcionalidade estiver disponível

### 4.2 Prestador ou fornecedor

É o usuário responsável por disponibilizar serviços ou estruturas na plataforma.

Suas principais necessidades são:

- Cadastrar serviços
- Manter as informações dos serviços
- Disponibilizar informações sobre preço e disponibilidade
- Receber solicitações
- Analisar solicitações de reserva
- Aprovar ou recusar solicitações
- Acompanhar as reservas relacionadas aos seus serviços

### 4.3 Administrador

A necessidade de um perfil administrativo deverá ser confirmada durante a especificação dos requisitos.

> Caso esse perfil permaneça no escopo do sistema, suas responsabilidades e permissões deverão ser definidas explicitamente em [`REQUISITOS.md`](./REQUISITOS.md).

---

## 5. Escopo

### 5.1 Funcionalidades previstas

O escopo atual contempla:

- Cadastro de usuários
- Autenticação
- Gerenciamento de eventos
- Cadastro e gerenciamento de serviços
- Consulta de serviços
- Busca e filtragem de serviços
- Solicitação de reservas
- Análise de solicitações
- Aprovação de reservas
- Recusa de reservas
- Cancelamento de reservas
- Acompanhamento do estado das reservas
- Preservação do histórico das reservas
- Avaliação após contratação, caso mantida no escopo final

### 5.2 Fora do escopo definido

> Funcionalidades que não estejam especificadas em [`REQUISITOS.md`](./REQUISITOS.md) não devem ser consideradas parte do escopo da versão atual.

Novas funcionalidades deverão ser analisadas e registradas por meio do processo de alteração de requisitos adotado pela equipe.

---

## 6. Modelo de Domínio

As principais entidades identificadas são:

| Entidade | Descrição |
|---|---|
| **Usuario** | Representa os usuários da plataforma e seus respectivos papéis |
| **Evento** | Representa o evento organizado pelo usuário |
| **Servico** | Representa um serviço ou estrutura disponibilizado por um prestador |
| **Reserva** | Representa a solicitação e o acompanhamento da contratação de um serviço para um evento |
| **Avaliacao** | Representa uma avaliação associada a uma contratação, quando habilitada |
| **Arquivo** | Representa arquivos associados aos serviços |

> O modelo de domínio completo está documentado em [`diagrams/modelo-dominio.md`](./diagrams/modelo-dominio.md).

---

## 7. Rastreabilidade

A modelagem deve possuir rastreabilidade com os requisitos que justificam cada elemento do domínio.

| Classe | Requisitos relacionados |
|---|---|
| Usuario | RF01, RF02, RF03, RN01 |
| Evento | RF09, RF15, RN01 |
| Servico | RF04, RF05, RF06, RF07, RF08, RN06 |
| Reserva | RF09, RF10, RF11, RF12, RF13, RF14, RF15, RF16, RN02–RN07 |
| Avaliacao | RF17 |
| Arquivo | RF04, RF08, RN06 |

> A rastreabilidade deverá ser ampliada à medida que os critérios de aceitação e os demais artefatos forem especificados.

A relação esperada entre os artefatos é:

```
Requisito → Regra de negócio → Modelo de domínio → Modelo de dados → Protótipo → Critério de aceitação
```

---

## 8. Modelo de Dados

O modelo de dados é derivado do modelo de domínio e dos requisitos especificados.

As entidades atualmente previstas são:

- `USUARIO`
- `EVENTO`
- `SERVICO`
- `ARQUIVO`
- `RESERVA`
- `AVALIACAO`

> O modelo relacional completo está documentado em [`diagrams/modelo-dados.md`](./diagrams/modelo-dados.md).

A estrutura definitiva das entidades deverá permanecer consistente com os requisitos e com o modelo de domínio.

---

## 9. Decisões de Identidade

| Entidade | Identificador | Decisão |
|---|---|---|
| Usuario | `id_usuario` | Chave primária única |
| Evento | `id_evento` | Chave primária única |
| Servico | `id_servico` | Chave primária única |
| Arquivo | `id_arquivo` | Chave primária única |
| Reserva | `id_reserva` | Chave primária única |
| Avaliacao | `id_avaliacao` | Chave primária única |

> Além da chave técnica, o `Usuario.email` deverá ser único. Essas decisões deverão ser refletidas no modelo de dados.

---

## 10. Decisões de Apagamento

### 10.1 Usuários

Usuários que possuam histórico relevante não deverão ser removidos fisicamente. A alternativa adotada é a **desativação lógica** por meio do atributo `ativo`.

### 10.2 Serviços

Serviços que já tenham participado de reservas não deverão ter seu histórico destruído. Quando necessário, deverão ser desativados.

### 10.3 Reservas

Reservas que possuam histórico não deverão ser removidas fisicamente. A preservação dessas informações é necessária para manter a rastreabilidade das contratações.

### 10.4 Arquivos

Arquivos sem referência poderão ser removidos de acordo com a política de manutenção definida para o sistema. Arquivos necessários para preservar informações relevantes do histórico deverão permanecer disponíveis.

---

## 11. Representação de Tempo

Os atributos temporais deverão utilizar tipos apropriados ao seu significado e não deverão ser armazenados como texto livre.

A representação deverá considerar:

- `DATE` para datas sem horário
- `TIME` para horários isolados, quando necessário
- `DATETIME` ou equivalente para registros que exijam data e hora
- Início e fim para períodos de reserva

> As regras de validação dos períodos deverão ser especificadas em [`REQUISITOS.md`](./REQUISITOS.md).

---

## 12. Armazenamento de Arquivos

Os arquivos associados aos serviços deverão ser armazenados em um mecanismo de armazenamento apropriado.

O banco de dados deverá manter os metadados e a referência do arquivo, incluindo:

- `url`
- `nome_original`
- `tipo_mime`
- `tamanho`

A decisão evita armazenar diretamente o conteúdo binário dos arquivos no banco de dados e mantém a persistência dos metadados associada ao serviço.

---

## 13. Ciclo de Vida da Reserva

A **Reserva** é o objeto central do fluxo de contratação.

**Fluxo principal:**

```
SOLICITADA → EM ANÁLISE → APROVADA → CONFIRMADA → FINALIZADA
```

**Fluxo de recusa:**

```
EM ANÁLISE → RECUSADA
```

**Fluxo de cancelamento:**

```
CONFIRMADA → CANCELADA
```

> Uma recusa deverá possuir um motivo registrado.

As condições para cada transição e os usuários autorizados a executá-las deverão ser especificados em [`REQUISITOS.md`](./REQUISITOS.md) e representados em [`diagrams/estados-reserva.md`](./diagrams/estados-reserva.md).

---

## 14. Lacunas Identificadas pela Modelagem

A modelagem atual revelou pontos que precisam ser especificados antes da implementação.

### 14.1 Papéis dos usuários

É necessário definir explicitamente os tipos de usuário e as permissões associadas a cada tipo.

### 14.2 Disponibilidade dos serviços

O sistema precisa definir como a disponibilidade de um serviço será representada e como serão identificados conflitos entre períodos de disponibilidade e reservas.

> A representação atual de disponibilidade deverá ser revisada durante a atualização do modelo de domínio e do modelo de dados.

### 14.3 Histórico de estados da reserva

O atributo `status` representa o estado atual da reserva, mas não é suficiente, isoladamente, para representar seu histórico. Deverá ser definida uma forma de registrar as alterações de estado caso o requisito de histórico seja mantido.

### 14.4 Transições da reserva

Cada transição deverá possuir:

- Estado inicial
- Estado final
- Usuário autorizado
- Condições necessárias
- Dados obrigatórios
- Comportamento em caso de erro

### 14.5 Cancelamento

As condições para cancelamento por organizador e prestador/fornecedor deverão ser explicitadas nas regras de negócio.

### 14.6 Avaliação

Deverão ser definidas as condições que permitem avaliar uma contratação, quem pode realizar a avaliação e quais informações podem ser registradas.

---

## 15. Distribuição de Responsabilidades

| Responsabilidade | Papel principal | Apoio |
|---|---|---|
| Levantamento e revisão de requisitos | Equipe | Todos |
| Modelo de domínio | Equipe de modelagem | Todos |
| Modelo de dados | Responsável por dados | Equipe |
| Diagrama de estados | Responsável por modelagem | Equipe |
| Protótipo navegável | Responsável por interface | Equipe |
| Conferência cruzada | Revisor diferente do autor | Equipe |
| Integração por PR | Autor da alteração | Revisor |

> A definição dos responsáveis deve ser mantida atualizada conforme as atividades do projeto forem realizadas.

---

## 16. Decisões do Projeto

| ID | Decisão | Motivo | Consequência |
|---|---|---|---|
| D01 | Utilizar identificadores próprios para as entidades | Evitar ambiguidade entre registros | Cada entidade possui uma chave primária |
| D02 | Utilizar e-mail único para usuários | Evitar duplicidade de contas | Restrição de unicidade em `Usuario.email` |
| D03 | Utilizar exclusão lógica para registros com histórico | Preservar informações relevantes | Registros permanecem armazenados |
| D04 | Representar o ciclo da reserva por estados | Representar o processo de contratação | O estado da reserva deve obedecer às transições definidas |
| D05 | Exigir motivo para uma recusa | Registrar a justificativa da decisão | A reserva deve armazenar o motivo da recusa |
| D06 | Utilizar tipos temporais apropriados | Evitar inconsistências na representação de datas e horários | Períodos são armazenados de forma estruturada |
| D07 | Armazenar arquivos externamente e metadados no banco | Separar armazenamento binário da persistência dos dados | O banco mantém referências e metadados |
| D08 | Preservar o histórico das reservas | Manter rastreabilidade | Reservas com histórico não são removidas fisicamente |

---

## 17. Conferência Cruzada

A conferência cruzada deverá ser realizada por um integrante diferente do autor do artefato.

| Artefato | Autor | Revisor | Verificações | Resultado |
|---|---|---|---|---|
| `REQUISITOS.md` | Equipe | Integrante diferente do autor | IDs, requisitos, regras e critérios de aceitação | 🔲 A realizar |
| Modelo de domínio | Equipe de modelagem | Integrante diferente do autor | Classes, relações e rastreabilidade | 🔲 A realizar |
| Modelo de dados | Responsável por dados | Integrante diferente do autor | PK, FK, relacionamentos e restrições | 🔲 A realizar |
| Estados da reserva | Responsável por modelagem | Integrante diferente do autor | Estados, transições e condições | 🔲 A realizar |
| Protótipo | Responsável por interface | Integrante diferente do autor | Fluxos, telas e correspondência com requisitos | 🔲 A realizar |

> O resultado deverá ser atualizado após a realização das revisões.

---

## 18. Protótipo

O protótipo atual representa o fluxo principal de solicitação e gerenciamento de uma reserva.

**Fluxo principal:**

```
Início → Catálogo → Detalhes do serviço → Solicitação → Em análise → Aceitar ou Recusar
```

**Fluxo de recusa:**

```
Recusar → Motivo da recusa → Solicitação recusada → Voltar ao catálogo
```

**Fluxo de aprovação:**

```
Aceitar → Reserva aprovada → Confirmar → Reserva confirmada
```

O protótipo está disponível em [`prototipo/`](./prototipo).

> A cobertura do protótipo deverá ser ampliada conforme os requisitos forem revisados e novos critérios de aceitação forem definidos.

---

## 19. Relação entre os Artefatos

A relação entre os artefatos do projeto é:

```
REQUISITOS.md
      │
      ├──────────────► Modelo de domínio
      │                      │
      │                      ▼
      │               Modelo de dados
      │
      ├──────────────► Diagrama de estados
      │                      │
      │                      ▼
      └──────────────► Protótipo navegável
```

Os artefatos devem permanecer consistentes entre si.

> Quando a modelagem revelar uma regra ou informação necessária que não esteja documentada nos requisitos, `REQUISITOS.md` deverá ser atualizado antes que a alteração seja consolidada nos demais artefatos.

---

## 20. Estrutura da Entrega

```
/
├── README.md
├── CONTRIBUTING.md
├── PROJETO.md
├── REQUISITOS.md
├── CONFERENCIA_CRUZADA.md
├── diagrams/
│   ├── modelo-dominio.md
│   ├── modelo-dados.md
│   └── estados-reserva.md
└── prototipo/
    ├── index.html
    ├── catalogo.html
    ├── servico.html
    ├── reserva.html
    ├── recusada.html
    ├── aprovada.html
    ├── confirmada.html
    ├── css/
    │   └── style.css
    └── js/
        └── script.js
```
