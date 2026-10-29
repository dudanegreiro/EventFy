# 📋 REQUISITOS — EventFy

> Documento de especificação de requisitos, glossário do domínio, backlog priorizado, histórias de usuário, casos de uso, requisitos não funcionais mensuráveis e rastreabilidade do sistema **EventFy**, consolidado para o **Marco 1** da disciplina de Engenharia de Software.

---

## 📑 Sumário

- [1. Glossário do Domínio](#1-glossário-do-domínio)
- [2. Backlog Ordenado do Projeto](#2-backlog-ordenado-do-projeto)
- [3. Histórias de Usuário e Critérios da Fatia Vertical (MVP)](#3-histórias-de-usuário-e-critérios-da-fatia-vertical-mvp)
- [4. Caso de Uso Estruturado (UC-01)](#4-caso-de-uso-estruturado-uc-01)
- [5. Requisitos Funcionais Gerais](#5-requisitos-funcionais-gerais)
- [6. Requisitos Não Funcionais Verificáveis (ISO/IEC 25010)](#6-requisitos-não-funcionais-verificáveis-isoiec-25010)
- [7. Regras de Negócio e Restrições](#7-regras-de-negócio-e-restrições)
- [8. Decisões de Escopo (DP01–DP08)](#8-decisões-de-escopo-dp01dp08)
- [9. Matriz de Rastreabilidade Unificada](#9-matriz-de-rastreabilidade-unificada)
- [10. Validações Realizadas](#10-validações-realizadas)
- [11. Lista de Verificação da Revisão (Checklist de Fagan)](#11-lista-de-verificação-da-revisão-checklist-de-fagan)
- [12. Histórico de Revisão e Linha de Base do Marco 1](#12-histórico-de-revisão-e-linha-de-base-do-marco-1)

---

## 1. Glossário do Domínio

A tabela abaixo unifica o vocabulário utilizado em todos os artefatos do projeto, eliminando ambiguidades conceituais conforme a Seção 5.4 do livro didático.

| Termo | Definição no Domínio | Fonte |
|---|---|:---:|
| **Organizador** | Usuário cadastrado que planeja e realiza eventos, buscando e contratando serviços de fornecedores. | `E1, D1` |
| **Prestador / Fornecedor** | Usuário cadastrado que disponibiliza serviços, estruturas ou equipamentos para eventos e gerencia sua agenda. | `E2, D1` |
| **Evento** | Ocasião planejada pelo organizador com nome, local e período (`dataInicio` e `dataFim`) determinado. | `D1, E1` |
| **Serviço** | Atividade ou infraestrutura ofertada por um prestador (ex.: sonorização, espaço, buffet) com valor e categoria. | `D1, E2` |
| **Disponibilidade** | Estrutura de intervalos temporais e bloqueios de agenda de um serviço, definindo quando ele pode ser reservado. | `D1, E2` |
| **Reserva ativa** | Reserva nos estados `SOLICITADA`, `EM_ANALISE`, `APROVADA` ou `CONFIRMADA`; estados terminais não são ativos. | `DP07, DP08` |
| **Arquivo de Serviço** | Imagem ou documento vinculado a um serviço; o conteúdo fica em storage externo e seus metadados, em `ARQUIVO`. | `D07, D1` |
| **Reserva** | Solicitação e contratação formal de um serviço para determinado evento e período, regida por máquina de estados. | `D1, E1` |
| **Administrador** | Papel responsável por gerenciar contas e moderar serviços e conteúdos publicados na plataforma. | `D1, DP04` |
| **Motivo de Recusa** | Justificativa textual obrigatória registrada pelo prestador ao declinar uma solicitação de reserva. | `E1, RN04` |
| **Histórico da Reserva** | Trilha de auditoria imutável que registra cada mudança de estado da reserva com data, hora e responsável. | `RN07, RNF05` |
| **SLA / Expiração** | Transição automática para `EXPIRADA` se não houver ação por 48 horas após a entrada em `SOLICITADA`, `EM_ANALISE` ou `APROVADA`. | `DESCOBERTA.md`, `DP03` |

---

## 2. Backlog Ordenado do Projeto

O backlog está priorizado segundo a combinação dos métodos **MoSCoW**, **Risco Técnico** e **Dependência** (Seção 5.9 do livro).

Os itens classificados como **Obrigatório** somam **21 pontos** de um total de **46 pontos estimados** (**45,7% do esforço**), respeitando o limite máximo de 60% recomendado pelo DSDM / Agile Business Consortium (2026) e preservando margem contra imprevistos.

| Ordem | Item | Descrição Resumida | Origem | MoSCoW | Risco Técnico | Depende de | Estimativa (Pontos) |
|:---:|---|---|:---:|:---:|:---:|:---:|:---:|
| **1** | **HU-01** | Solicitação de reserva pelo organizador com verificação de agenda | N2, RF10 | **Obrigatório** | Alto *(concorrência de datas)* | — | 5 |
| **2** | **HU-02** | Análise pelo prestador com aprovação ou recusa justificada | N3, RF11, RF12 | **Obrigatório** | Médio *(motivo obrigatório)* | HU-01 | 3 |
| **3** | **HU-03** | Confirmação da contratação e bloqueio definitivo da agenda | N4, RF13, RN06 | **Obrigatório** | Alto *(transação atômica)* | HU-02 | 5 |
| **4** | **HU-04** | Acompanhamento do estado e histórico imutável da reserva | N5, RF16, RF18 | **Obrigatório** | Baixo *(auditoria)* | HU-01 | 3 |
| **5** | **HU-05** | Catálogo com busca e filtragem por categoria e data | N1, RF05, RF06 | **Obrigatório** | Baixo *(consultas)* | — | 5 |
| **6** | **HU-06** | Cadastro e gerenciamento de serviços pelo prestador | RF04, RF08 | **Importante** | Baixo | — | 5 |
| **7** | **HU-07** | Gerenciamento e cadastro de eventos do organizador | RF09, RF15 | **Importante** | Baixo | — | 3 |
| **8** | **HU-08** | Cancelamento justificado de reservas pelo organizador/prestador | RF14, RN05 | **Importante** | Médio *(política de prazos)* | HU-03 | 3 |
| **9** | **HU-09** | Expiração automática de solicitações por estouro de SLA (48h) | E1, E2, DP03 | **Importante** | Médio *(rotina agendada)* | HU-01 | 3 |
| **10** | **HU-10** | Avaliação do serviço após finalização da reserva | RF17, RN05 | **Desejável** | Baixo | HU-03 | 3 |
| **11** | **HU-11** | Pagamento online e split financeiro na plataforma | N6 | **Fora de escopo** | Alto *(dependência terceira)* | — | — |
| **12** | **HU-12** | Anexos de imagem e documentos nos serviços | N1, RF19 | **Importante** | Médio *(validação e storage externo)* | HU-06 | 3 |
| **13** | **HU-13** | Gerenciamento de contas e moderação pelo administrador | D1, RF20 | **Importante** | Médio *(autorização por papel)* | — | 3 |
| **14** | **HU-14** | Sugestão de nova data após recusa | E2 | **Fora de escopo** | Médio | HU-02 | — |

---

## 3. Histórias de Usuário e Critérios da Fatia Vertical (MVP)

As histórias a seguir compõem o fluxo prioritário do sistema (arquitetura executável), escritas no formato **INVEST** com critérios no padrão **Dado-Quando-Então** cobrindo caminho principal, recusas/limites e efeito persistente.

### HU-01 — Solicitação de Reserva de Serviço
> **Como** organizador de eventos,  
> **quero** solicitar a reserva de um serviço informando o evento e o período desejado,  
> **para** reservar a data com o fornecedor sem risco de agendamentos duplicados.  
> `[Origem: N2, confirmada em E1 e O1]`

- **CA-01.1 (Caminho principal — Solicitação aceita):**  
  **Dado** que o organizador está autenticado, possui um evento ativo e o serviço está livre no período,  
  **Quando** ele submete a solicitação de reserva,  
  **Então** o sistema cria a reserva no estado `SOLICITADA`, grava o registro inicial em `HISTORICO_RESERVA` e notifica o prestador.
- **CA-01.2 (Recusa e limite — Conflito de agenda):**  
  **Dado** que o serviço já possui reserva confirmada ou bloqueio no mesmo intervalo de datas/horários,  
  **Quando** o organizador tenta solicitar a reserva,  
  **Então** o sistema recusa a criação, informa que o serviço está indisponível para o período e não grava registro de reserva.
- **CA-01.3 (Recusa e limite — Período fora dos limites do evento):**  
  **Dado** que o horário da reserva solicitado extrapola o intervalo de `dataInicio` e `dataFim` do evento,  
  **Quando** o organizador tenta confirmar a solicitação,  
  **Então** o sistema recusa a submissão e exige ajuste dos horários.
- **CA-01.4 (Efeito persistente — Auditoria e persistência):**  
  **Dado** que uma solicitação foi criada com sucesso,  
  **Quando** o organizador consulta a lista de suas reservas,  
  **Então** a solicitação é exibida com status `SOLICITADA` e os dados permanecem recuperáveis mesmo após reinicialização da sessão.

---

### HU-02 — Análise e Decisão da Solicitação pelo Prestador
> **Como** prestador de serviços,  
> **quero** analisar as solicitações recebidas podendo aprová-las ou recusá-las com justificativa,  
> **para** gerenciar meus compromissos de forma transparente e documentada.  
> `[Origem: N3, confirmada em E2]`

- **CA-02.1 (Caminho principal — Aprovação da solicitação):**  
  **Dado** que o prestador visualiza uma solicitação no estado `SOLICITADA` e possui capacidade técnica,  
  **Quando** ele aciona a opção "Aprovar",  
  **Então** o sistema altera o estado da reserva para `APROVADA`, pré-bloqueia a data na agenda, grava em `HISTORICO_RESERVA` e notifica o organizador.
- **CA-02.2 (Recusa justificada — Motivo obrigatório):**  
  **Dado** que o prestador decide não atender à solicitação,  
  **Quando** ele aciona a opção "Recusar" e informa um motivo válido com no mínimo 10 caracteres,  
  **Então** o sistema muda a reserva para o estado terminal `RECUSADA`, persiste o `motivo_recusa`, registra o histórico imutável e notifica o organizador com a justificativa.
- **CA-02.3 (Recusa e limite — Tentativa de recusa sem motivo):**  
  **Dado** que o prestador tenta recusar uma solicitação sem preencher a justificativa,  
  **Quando** ele confirma o formulário de recusa,  
  **Então** o sistema bloqueia a operação, mantém a reserva no estado anterior e informa que o motivo de recusa é obrigatório (RN04).
- **CA-02.4 (Efeito persistente — Preservação da justificativa):**  
  **Dado** que uma reserva foi recusada com motivo,  
  **Quando** o organizador consulta o detalhe da reserva recusada a qualquer momento posterior,  
  **Então** o sistema apresenta a justificativa original fornecida pelo prestador.

---

### HU-03 — Confirmação Definitiva da Reserva
> **Como** organizador de eventos,  
> **quero** confirmar a contratação de uma reserva previamente aprovada,  
> **para** fechar o compromisso e garantir o bloqueio definitivo do fornecedor.  
> `[Origem: N4, confirmada em E1 e E2]`

- **CA-03.1 (Caminho principal — Confirmação e bloqueio):**  
  **Dado** que a reserva está no estado `APROVADA` dentro do prazo de tolerância,  
  **Quando** o organizador clica em "Confirmar Contratação",  
  **Então** o sistema atualiza o estado para `CONFIRMADA`, efetiva o bloqueio definitivo em `DISPONIBILIDADE_SERVICO` em transação atômica e grava a mudança em `HISTORICO_RESERVA`.
- **CA-03.2 (Recusa e limite — Janela de confirmação esgotada):**  
  **Dado** que a reserva está em `APROVADA` há 48 horas sem confirmação do organizador,
  **Quando** o organizador tenta confirmar,  
  **Então** o sistema recusa a confirmação, informa que o prazo expirou e a reserva transita para `EXPIRADA`, liberando o pré-bloqueio da agenda.
- **CA-03.3 (Efeito persistente — Bloqueio atômico):**  
  **Dado** que uma reserva foi confirmada,  
  **Quando** qualquer outro organizador tentar solicitar o mesmo serviço no mesmo período,  
  **Então** a agenda reporta ocupação e o sistema bloqueia qualquer nova sobreposição.

---

### HU-04 — Acompanhamento e Trilha de Auditoria
> **Como** organizador ou prestador,  
> **quero** consultar o histórico completo de transições de uma reserva,  
> **para** comprovar as etapas acordadas e auditar responsabilidades em caso de divergência.  
> `[Origem: N5, confirmada em E1 e E2]`

- **CA-04.1 (Caminho principal — Consulta da trilha de auditoria):**  
  **Dado** que uma reserva possui uma ou mais transições realizadas,  
  **Quando** o usuário autorizado acessa os detalhes da reserva,  
  **Então** o sistema exibe cronologicamente cada transição com status anterior, novo status, data/hora e o autor da mudança.
- **CA-04.2 (Recusa e limite — Acesso indevido a reservas alheias):**  
  **Dado** que um usuário autenticado tenta acessar a trilha de uma reserva que não pertence a ele nem aos seus serviços,  
  **Quando** ele requisita a visualização,  
  **Então** o sistema recusa a visualização com código de acesso negado (403 Forbidden).
- **CA-04.3 (Efeito persistente — Imutabilidade):**  
  **Dado** que registros existem em `HISTORICO_RESERVA`,  
  **Quando** qualquer rotina da aplicação é executada,  
  **Então** nenhuma operação de UPDATE ou DELETE é permitida sobre esses registros.

---

### HU-12 — Anexos de Imagem e Documentos do Serviço
> **Como** prestador de serviços,
> **quero** anexar imagens e documentos ao meu serviço,
> **para** apresentar informações e especificações úteis aos organizadores.
> `[Origem: N1, D07]`

- **CA-12.1 (Caminho principal — Anexo válido):**
  **Dado** que o prestador autenticado gerencia o serviço e seleciona um arquivo JPEG, PNG, WebP, PDF ou DOCX de até 10 MB (10.000.000 bytes),
  **Quando** envia o anexo,
  **Então** o sistema valida o tipo MIME e o tamanho, armazena o conteúdo em storage externo e registra os metadados e a URL em `ARQUIVO`.
- **CA-12.2 (Recusa e limite — Tipo ou tamanho inválido):**
  **Dado** que o arquivo excede 10 MB ou não pertence aos tipos permitidos,
  **Quando** o prestador tenta enviá-lo,
  **Então** o sistema rejeita o arquivo, informa o motivo e não cria metadados nem disponibiliza o conteúdo.
- **CA-12.3 (Efeito persistente — Acesso e remoção):**
  **Dado** que o anexo foi registrado,
  **Quando** um organizador consulta o serviço,
  **Então** pode acessar o anexo, enquanto o prestador responsável pode removê-lo por exclusão lógica.

---

### HU-13 — Gerenciamento de Contas e Moderação
> **Como** administrador da plataforma,
> **quero** gerenciar contas e moderar serviços e conteúdos publicados,
> **para** manter a plataforma íntegra sem assumir as ações de organizadores ou prestadores.
> `[Origem: D1, DP04]`

- **CA-13.1 (Caminho principal — Conta):**
  **Dado** que o administrador está autenticado,
  **Quando** desativa ou reativa uma conta,
  **Então** o sistema atualiza o estado lógico da conta e impede operações de usuários inativos.
- **CA-13.2 (Caminho principal — Moderação):**
  **Dado** que o administrador identifica serviço ou conteúdo que deve ser moderado,
  **Quando** desativa ou restaura a publicação,
  **Então** o sistema oculta ou restaura a publicação no catálogo, sem excluir dados nem cancelar ou alterar reservas existentes.
- **CA-13.3 (Recusa e limite — Ação fora do papel):**
  **Dado** que um usuário sem papel de administrador tenta executar uma ação administrativa,
  **Quando** envia a solicitação,
  **Então** o sistema a recusa com código 403 e mantém os dados inalterados.

---

## 4. Caso de Uso Estruturado (UC-01)

### UC-01 — Solicitar e Tratar Reserva de Serviço
- **Ator principal:** Organizador de Eventos
- **Atores secundários:** Prestador de Serviços, Sistema (background)
- **Pré-condição:** Organizador autenticado, possuindo ao menos um evento cadastrado e serviço ativo no catálogo.
- **Garantia de sucesso (Pós-condição):** Reserva criada, analisada pelo prestador, confirmada com agenda bloqueada e todo o ciclo auditado em histórico imutável.

#### Fluxo Principal
1. O organizador localiza o serviço desejado no catálogo e aciona "Solicitar Reserva".
2. Seleciona o evento e informa o período (`dataInicio` e `dataFim`).
3. O sistema valida se o período está contido no evento e se o serviço está disponível na agenda.
4. O sistema cria a reserva no estado `SOLICITADA` e registra o evento em `HISTORICO_RESERVA`.
5. O prestador acessa a solicitação em sua fila de trabalho e inicia a análise (transição para `EM_ANALISE`).
6. O prestador decide aprovar a solicitação; o sistema atualiza o estado para `APROVADA`, grava histórico e pré-bloqueia a agenda.
7. O organizador toma ciência da aprovação e aciona "Confirmar Contratação".
8. O sistema valida que a confirmação está dentro do prazo de SLA, atualiza o estado para `CONFIRMADA`, consolida o bloqueio definitivo da agenda e emite o comprovante/voucher com dados da contratação.
9. Após a realização do evento e decurso da `dataFim`, o Sistema executa rotina automática alterando a reserva para `FINALIZADA` e habilitando a avaliação.

#### Fluxos Alternativos
- **3a. Serviço indisponível no período solicitado:** O sistema informa o conflito de agenda, não cria a reserva e sugere outros períodos ou serviços similares.
- **3b. Período incompatível com o evento:** O sistema informa que o horário do serviço excede os limites de início/término do evento e solicita correção.
- **4a. Prestador não inicia a análise em 48 horas:** O Sistema altera a reserva de `SOLICITADA` para `EXPIRADA`, notifica as partes e libera o intervalo da agenda.
- **6a. Prestador recusa a solicitação:** O prestador clica em "Recusar" e digita o motivo obrigatório. O sistema valida o preenchimento da justificativa (RN04), altera o estado para `RECUSADA`, grava o motivo no histórico e notifica o organizador. O fluxo encerra sem bloqueio de agenda.
- **5a. Cancelamento precoce pelo organizador:** O organizador desiste da solicitação antes da decisão do prestador e informa uma justificativa; o sistema muda o estado para `CANCELADA`, audita o cancelamento e libera a agenda.
- **6b. Prestador não responde em 48 horas:** A rotina do Sistema identifica o estouro de SLA em `EM_ANALISE`, altera o estado para `EXPIRADA`, notifica as partes e libera a agenda.
- **7a. Organizador desiste da reserva aprovada:** O organizador cancela a reserva antes da confirmação, informa uma justificativa e o sistema transita para `CANCELADA`, liberando o pré-bloqueio da agenda.
- **7b. Organizador não confirma em 48 horas:** O Sistema altera a reserva de `APROVADA` para `EXPIRADA`, liberando a agenda para outros clientes.
- **8a. Cancelamento de reserva confirmada:** Antes do início do evento, o organizador ou prestador informa uma justificativa; o Sistema altera para `CANCELADA`, registra o ator e o motivo no histórico e libera a agenda.

---

## 5. Requisitos Funcionais Gerais

Os 20 requisitos funcionais consolidados do EventFy são apresentados a seguir:

- **RF01 — Cadastro de usuário:** O sistema deve permitir o cadastro de usuários com nome, e-mail único, senha protegida por hash e papel (`Organizador` ou `Prestador`). O papel `Administrador` é atribuído pela equipe responsável, não por auto cadastro. `[Origem: D1, DP01]`
- **RF02 — Autenticação:** O sistema deve autenticar usuários por credenciais válidas e oferecer encerramento seguro de sessão (logout). `[Origem: D1]`
- **RF03 — Gerenciamento de perfil:** O sistema deve permitir consulta e edição de dados cadastrais, impedindo a alteração indevida de privilégios. `[Origem: D1]`
- **RF04 — Cadastro de serviço:** O sistema deve permitir que prestadores cadastrem serviços com nome, descrição, categoria, preço, regras de disponibilidade e anexos conforme RF19. `[Origem: N1, E2, D1]`
- **RF05 — Consulta de serviços:** O sistema deve disponibilizar catálogo público/pesquisável de serviços ativos. `[Origem: N1, E1, O1]`
- **RF06 — Busca e filtragem:** O sistema deve filtrar serviços por categoria, faixa de preço, localização e disponibilidade na data. `[Origem: N1, E1, O1]`
- **RF07 — Detalhes do serviço:** O sistema deve exibir os dados do serviço, seus anexos permitidos e as condições de atendimento. `[Origem: N1, E1, E2, D1]`
- **RF08 — Gerenciamento de serviços:** O sistema deve permitir ao prestador atualizar dados descritivos de seus serviços. Enquanto houver reserva ativa (`SOLICITADA`, `EM_ANALISE`, `APROVADA` ou `CONFIRMADA`), deve impedir alterações de preço, disponibilidade ou condições de atendimento e impedir a desativação; após o encerramento das reservas, a desativação será lógica. `[Origem: E2, D1, DP08]`
- **RF09 — Cadastro de evento:** O sistema deve permitir que organizadores cadastrem eventos com nome, datas de início/fim e local. `[Origem: N2, E1, D1]`
- **RF10 — Solicitação de reserva:** O sistema deve permitir a solicitação de reserva vinculada a um evento e período, iniciando em `SOLICITADA`. `[Origem: N2, E1]`
- **RF11 — Visualização de solicitações:** O sistema deve apresentar ao prestador a fila de solicitações recebidas. `[Origem: N3, E2]`
- **RF12 — Análise da solicitação:** O sistema deve permitir ao prestador aprovar (`APROVADA`) ou recusar (`RECUSADA` com justificativa obrigatória) solicitações. `[Origem: N3, E2]`
- **RF13 — Confirmação de reserva:** O sistema deve permitir ao organizador confirmar reservas aprovadas, transitando para `CONFIRMADA` e bloqueando a agenda. `[Origem: N4, E1, E2, O1]`
- **RF14 — Cancelamento de reserva:** O sistema deve permitir que o organizador cancele reservas em `SOLICITADA`, `EM_ANALISE`, `APROVADA` ou `CONFIRMADA`, e que o prestador cancele reservas `CONFIRMADA`, desde que o evento ainda não tenha começado. Em todos os casos, exige justificativa, registra o ator e o motivo em `HISTORICO_RESERVA`, muda a reserva para `CANCELADA` e libera a agenda. `[Origem: E1, E2, D1, DP03]`
- **RF15 — Gerenciamento de eventos:** O sistema deve permitir ao organizador listar e editar seus eventos. Enquanto houver reserva ativa (`SOLICITADA`, `EM_ANALISE`, `APROVADA` ou `CONFIRMADA`), deve impedir alteração de período ou local e impedir a exclusão/desativação do evento; outras alterações descritivas são permitidas. `[Origem: N2, E1, D1, DP07]`
- **RF16 — Acompanhamento de reservas:** O sistema deve exibir o estado em tempo real de cada solicitação. `[Origem: N5, E1, E2]`
- **RF17 — Avaliação de serviços:** O sistema deve permitir ao organizador titular avaliar cada reserva após `FINALIZADA`, uma única vez, atribuindo uma nota inteira de 1 a 5, sem campo de comentário. `[Origem: D1, DP05]`
- **RF18 — Histórico e auditoria da reserva:** O sistema deve gravar registro imutável em `HISTORICO_RESERVA` em toda transição de estado. `[Origem: N5, E1, E2]`
- **RF19 — Anexos de serviço:** O sistema deve permitir ao prestador anexar imagens JPEG/PNG/WebP e documentos PDF/DOCX de até 10 MB (10.000.000 bytes) ao próprio serviço, validar o tipo MIME, armazenar os binários em storage externo e manter metadados em `ARQUIVO`. `[Origem: D07, D1]`
- **RF20 — Administração e moderação:** O sistema deve permitir ao administrador desativar/reativar contas e ocultar/restaurar publicações de serviços e conteúdos no catálogo, preservando as reservas existentes e sem permitir que organizadores ou prestadores executem essas ações. `[Origem: D1, DP04]`

---

## 6. Requisitos Não Funcionais Verificáveis (ISO/IEC 25010)

Os requisitos não funcionais foram quantificados no formato **Planguage** (Gilb, 2005) e cobrem as características de qualidade da norma **ISO/IEC 25010:2023** conforme o Capítulo 5 (Tabela 5.7).

As fontes identificam necessidades (`N`), entrevistas (`E`), observações (`O`) e decisões de domínio/projeto (`D`/`DP`) descritas em `DESCOBERTA.md` e `PROJETO.md`.

### RNF-01 — Segurança no Armazenamento de Credenciais
- **Origem:** `D1`
- **Característica ISO/IEC 25010:** Segurança (Confidencialidade)
- **Grandeza:** Algoritmo e derivação de chave das senhas no banco de dados.
- **Condição:** Em todas as operações de cadastro, alteração e persistência de usuários.
- **Aceitável:** Senhas protegidas com salt e algoritmo de derivação lento (bcrypt fator de custo >= 10 ou Argon2id); nenhuma senha em texto puro.
- **Pretendido:** Hash via Argon2id com tempo de computação controlado de ~200ms.
- **Como verificar:** Inspecionar os registros da tabela `USUARIO` no banco de dados de teste e verificar a ausência de texto puro e o padrão do hash gerado.

### RNF-02 — Integridade Concorrente da Agenda (Conflito de Datas)
- **Origem:** `N4, E1, E2, O1`
- **Característica ISO/IEC 25010:** Confiabilidade / Integridade
- **Grandeza:** Taxa de reservas confirmadas simultâneas sobre o mesmo período em um mesmo serviço.
- **Condição:** Requisições concorrentes disparadas para o mesmo serviço no mesmo intervalo de datas.
- **Aceitável:** **Zero** reservas com conflito de agenda confirmadas; o sistema deve rejeitar ou pré-bloquear transacionalmente.
- **Pretendido:** Bloqueio atômico em menos de 100 ms via transação relacional com lock de linha.
- **Como verificar:** Teste de integração automatizado executando duas chamadas simultâneas para o mesmo serviço e intervalo, confirmando que a segunda recebe código HTTP 409 (Conflict).

### RNF-03 — Eficiência de Desempenho na Consulta ao Catálogo
- **Origem:** `N1, E1, E2`
- **Característica ISO/IEC 25010:** Eficiência de Desempenho (Comportamento temporal)
- **Grandeza:** Tempo decorrido entre a requisição de busca/filtro e a renderização completa dos resultados.
- **Condição:** Base com até 200 serviços cadastrados, consultada em conexão de rede local padrão.
- **Aceitável:** até 3,0 segundos.
- **Pretendido:** até 1,0 segundo.
- **Como verificar:** Medição no navegador (painel Network do DevTools), três execuções consecutivas com a base de teste de 200 registros, adotando o maior valor medido.

### RNF-04 — Capacidade de Interação e Responsividade Móvel
- **Origem:** `O1, E1, E2`
- **Característica ISO/IEC 25010:** Capacidade de Interação (Usabilidade e Acessibilidade)
- **Grandeza:** Realização dos fluxos sem necessidade de rolagem horizontal em telas móveis.
- **Condição:** Visualização em viewport de 360 pixels de largura (smartphone comum).
- **Aceitável:** 100% dos fluxos de solicitação, aprovação e recusa concluíveis em tela de 360px de largura sem rolagem horizontal.
- **Pretendido:** Interface adaptativa fluida com feedback imediato para toques e formulários.
- **Como verificar:** Teste de usabilidade nas ferramentas de desenvolvedor em emulação de tela móvel de 360px × 640px.

### RNF-05 — Rastreabilidade e Auditoria Imutável de Estados
- **Origem:** `N5, E1, E2`
- **Característica ISO/IEC 25010:** Confiabilidade / Não repúdio
- **Grandeza:** Taxa de transições de estado que geram registro correspondente em auditoria.
- **Condição:** Em todas as mudanças de status da reserva (`SOLICITADA` a `FINALIZADA`).
- **Aceitável:** 100% das transições registradas com status anterior, novo status, timestamp ISO 8601 e identificador do executor.
- **Pretendido:** Inserção em transação atômica única no banco de dados.
- **Como verificar:** Inspecionar a tabela `HISTORICO_RESERVA` após a execução de cada operação do ciclo de vida, conferindo integridade cronológica.

### RNF-06 — Manutenibilidade e Isolamento de Políticas de Prazo
- **Origem:** `D1, DP03`
- **Característica ISO/IEC 25010:** Manutenibilidade (Modificabilidade / Critério de Parnas)
- **Grandeza:** Número de arquivos afetados por alteração nas regras de tolerância de SLA e cancelamento.
- **Condição:** Alteração do prazo de tolerância de análise (ex.: de 48h para 24h).
- **Aceitável:** No máximo 1 módulo do backend alterado (`PoliticaCancelamento` / `ServicoDisponibilidade`).
- **Pretendido:** 1 único arquivo alterado sem impacto em telas, controladores ou esquema relacional.
- **Como verificar:** Teste do critério de Parnas: contagem de arquivos modificados em pull request que simula a alteração do prazo.

### RNF-07 — Autorização por Papel e Propriedade
- **Origem:** `D1, DP01, DP04`
- **Característica ISO/IEC 25010:** Segurança (controle de acesso)
- **Grandeza:** Proporção de operações protegidas que são autorizadas somente para o papel e titular corretos.
- **Condição:** Requisições de leitura ou alteração de eventos, serviços, reservas, anexos e contas.
- **Aceitável:** 100% das tentativas sem papel ou propriedade necessários são recusadas com HTTP 403, sem alteração persistida; 100% das operações autorizadas são limitadas ao escopo definido em RF01, RF08, RF14, RF15 e RF20.
- **Pretendido:** Cobertura automatizada de todos os pares operação/papel e dos casos de acesso a recurso alheio.
- **Como verificar:** Testes de autorização para cada papel, incluindo acesso a recurso alheio e ação administrativa, verificando resposta 403 e ausência de efeitos persistentes.

> **Cobertura das nove características da ISO/IEC 25010 (Seção 5.7.1 do livro):**
>
> | Característica | Cobertura no EventFy |
> |---|---|
> | Adequação funcional | RF01–RF20 e seus critérios de aceitação |
> | Eficiência de desempenho | RNF-03 |
> | Compatibilidade | RE-01 (API REST/JSON) |
> | Capacidade de interação | RNF-04 |
> | Confiabilidade | RNF-02 e RNF-05 |
> | Segurança | RNF-01 e RNF-07 |
> | Manutenibilidade | RNF-06 |
> | Flexibilidade | RE-01 (frontend desacoplado da API) |
> | Segurança de operação física (safety) | Não aplicável: o sistema não controla dispositivos ou riscos físicos |

---

## 7. Restrições e Regras de Negócio

### 7.1 Restrições do Sistema (RE)
- **RE-01 (Arquitetura Web):** A aplicação deve operar sob o modelo cliente-servidor web, com frontend desacoplado consumindo backend por API REST JSON. `[Origem: D1]`
- **RE-02 (Persistência Relacional):** O armazenamento deve utilizar banco de dados relacional com suporte a chaves estrangeiras e transações atômicas (ACID). `[Origem: D1]`
- **RE-03 (Privacidade e LGPD):** O sistema deve coletar exclusivamente dados operacionais estritamente necessários para contato e agendamento (Princípio da Necessidade, art. 6º, III, Lei 13.709/2018). `[Origem: D1]`
- **RE-04 (Anexos):** Anexos de serviço devem usar os tipos MIME permitidos em RF19, ter no máximo 10 MB (10.000.000 bytes) e ser armazenados fora do banco relacional, mantendo somente metadados e URL em `ARQUIVO`. `[Origem: D07, D1]`

### 7.2 Regras de Negócio (RN)
- **RN01 — Responsabilidade sobre eventos:** Um evento pertence a um único organizador responsável, que é o único autorizado a gerenciá-lo. `[Origem: D1]`
- **RN02 — Responsabilidade sobre serviços:** Um serviço pertence ao prestador que o cadastrou; apenas ele pode alterar dados e decidir sobre solicitações. `[Origem: D1]`
- **RN03 — Vínculo da reserva:** Uma reserva relaciona obrigatoriamente um organizador, um evento, um serviço, um prestador e um intervalo de datas. `[Origem: D1]`
- **RN04 — Obrigatoriedade do motivo de recusa:** Nenhuma reserva pode ser alterada para `RECUSADA` sem que uma justificativa textual seja registrada. `[Origem: E1, E2]`
- **RN05 — Máquina de estados estrita:** A reserva deve seguir rigorosamente a máquina de estados oficial com 8 estados, sem caminhos órfãos e sem transições não mapeadas. `[Origem: D1]`
- **RN06 — Incompatibilidade de agenda:** Um serviço não pode ter duas reservas com períodos concorrentes no estado `CONFIRMADA`. `[Origem: E2, O1]`
- **RN07 — Imutabilidade da auditoria:** O histórico de transições de uma reserva é permanente e imutável; nenhuma linha de histórico pode ser alterada ou apagada. `[Origem: D1]`
- **RN08 — Períodos de disponibilidade:** O serviço só pode ser solicitado em períodos de atendimento sem bloqueio ou sobreposição com reservas ativas; a aprovação pré-bloqueia o intervalo e a confirmação o bloqueia definitivamente. `[Origem: D1, DP02]`
- **RN09 — Cancelamento justificado:** O organizador pode cancelar em `SOLICITADA`, `EM_ANALISE`, `APROVADA` ou `CONFIRMADA`; o prestador pode cancelar em `CONFIRMADA`. O cancelamento exige justificativa, ocorre antes do início do evento e libera o bloqueio da agenda. `[Origem: D1, DP03]`
- **RN10 — Integridade de eventos com reservas:** Havendo reserva ativa (`SOLICITADA`, `EM_ANALISE`, `APROVADA` ou `CONFIRMADA`), o organizador pode editar dados descritivos, mas não pode alterar período ou local nem excluir/desativar o evento. `[Origem: D1, DP07]`
- **RN11 — Integridade de serviços com reservas:** Havendo reserva ativa (`SOLICITADA`, `EM_ANALISE`, `APROVADA` ou `CONFIRMADA`), o prestador pode editar dados descritivos, mas não pode alterar preço, disponibilidade ou condições de atendimento nem desativar o serviço. `[Origem: D1, DP08]`
- **RN12 — Avaliação de reserva:** Somente o organizador titular pode registrar uma nota inteira de 1 a 5, sem comentário, uma única vez após `FINALIZADA`. `[Origem: D1, DP05]`
- **RN13 — Escopo do administrador:** Somente o administrador pode desativar/reativar contas e ocultar/restaurar publicações; a moderação remove a oferta de novas buscas sem excluir ou alterar reservas existentes, e não permite operar reservas em nome das partes. `[Origem: D1, DP04]`

---

## 8. Decisões de Escopo (DP01–DP08)

As decisões abaixo foram fechadas com a equipe e usadas na especificação desta versão:

| ID | Decisão | Registro na especificação |
|---|---|---|
| DP01 | Papéis: organizador, prestador e administrador; o administrador é provisionado pela equipe. | RF01, RF20, RNF-07 |
| DP02 | Disponibilidade é composta por intervalos e bloqueios; aprovação pré-bloqueia e confirmação bloqueia definitivamente. | HU-01 a HU-03, RF13, RN08 |
| DP03 | Organizador cancela antes do início do evento nos estados permitidos; prestador pode cancelar reserva confirmada; ambos informam justificativa. | RF14, RN09, `estados-reserva.md` |
| DP04 | Administrador gerencia contas e oculta/restaura publicações para novas buscas, sem alterar reservas existentes ou operar reservas das partes. | RF20, RN13 |
| DP05 | Avaliação única por reserva finalizada, nota inteira de 1 a 5 e sem comentário. | RF17, RN12 |
| DP06 | Histórico imutável registra estado anterior/novo, data/hora, executor e justificativa quando houver. | RF18, RN07, RNF-05 |
| DP07 | Com reserva ativa, evento mantém período/local; descrição pode mudar; exclusão/desativação fica bloqueada. | RF15, RN10 |
| DP08 | Com reserva ativa, serviço mantém preço/disponibilidade/condições; descrição pode mudar; desativação fica bloqueada. | RF08, RN11 |

---

## 9. Matriz de Rastreabilidade Unificada

A cadeia liga cada necessidade do `DESCOBERTA.md` aos requisitos, regras e modelos:

| Necessidade | Requisito Funcional | Regra de Negócio | Entidade de Domínio | Tabela de Banco |
|:---:|:---:|:---:|:---:|:---:|
| **N1** | RF05, RF06, RF07, RF19 | RN02 | `Servico`, `Arquivo` | `SERVICO`, `ARQUIVO` |
| **N2** | RF10 | RN01, RN03, RN06 | `Reserva`, `Evento` | `RESERVA`, `EVENTO` |
| **N3** | RF11, RF12 | RN02, RN04, RN05 | `Reserva` | `RESERVA` |
| **N4** | RF13 | RN05, RN06 | `DisponibilidadeServico` | `DISPONIBILIDADE_SERVICO` |
| **N5** | RF16, RF18 | RN05, RN07 | `HistoricoReserva` | `HISTORICO_RESERVA` |
| **D1** | RF01, RF20 | RN13 | `Usuario`, `Servico` | `USUARIO`, `SERVICO` |

---

## 10. Validações Realizadas

### Sessão V1 — 01/10/2026, com Organizador Autônomo (Perfil de Carlos, E1)

A sessão de validação foi realizada com o protótipo navegável de baixa/média fidelidade seguindo o procedimento da Seção 5.11.2 do livro didático (situar a tarefa sem explicar a tela, observar em silêncio e registrar o que o teste derrubou):

| Achado na Validação | Efeito no Requisito / Projeto | Item Alterado |
|---|---|---|
| O usuário procurou um campo para explicar necessidades especiais ao solicitar o serviço | O campo de observações adicionais era opcional e estava pouco visível na tela de solicitação | `RF10` e tela `prototipo/reserva.html` atualizados para destacar observações |
| O usuário tentou recusar uma reserva sem digitar nada para ver se o sistema permitia | A validação visual precisava bloquear o botão de envio enquanto o motivo estivesse em branco | `CA-02.3` reforçado e validação no script de `recusada.html` |
| O usuário perguntou se o prestador podia sugerir outra data quando recusasse | Sugestão de reagendamento não estava prevista na recusa simples | Registrado fora do escopo atual (`HU-14`) |
| O usuário elogiou poder ver o status exato da reserva sem precisar mandar mensagem no WhatsApp | Confirmou o valor central da máquina de estados visível | `HU-04` e `RF16` validados com o usuário |

---

## 11. Lista de Verificação da Revisão (Checklist de Fagan)

Inspeção formal de requisitos conduzida segundo a Listagem 5.7 do livro-texto:

### Para cada História / Requisito:
- [x] Tem origem declarada, e a origem existe no `DESCOBERTA.md` (`N1..N5`).
- [x] O benefício declarado nomeia claramente quem se beneficia (*"para..."*).
- [x] Tem critérios de aceitação para o caminho principal, para recusa/limite e para o efeito que persiste.
- [x] Nenhum critério descreve elementos de tela (botão azul, cor) em vez do comportamento.
- [x] Cabe em uma iteração de 2 semanas, na avaliação de quem vai construir.

### Para o Conjunto dos Requisitos:
- [x] Nenhum par de requisitos se contradiz, e todo termo do domínio está no glossário.
- [x] As nove características da ISO/IEC 25010 foram percorridas e registradas.
- [x] As ações por papel e propriedade têm critérios mensuráveis de autorização.
- [x] Anexos, cancelamentos, disponibilidade e edição com reservas têm limites verificáveis.
- [x] Toda necessidade confirmada do `DESCOBERTA.md` possui item correspondente ou motivo para ficar fora.
- [x] Todo item possui posição na ordem do backlog com critério declarado.
- [x] Os itens obrigatórios consomem no máximo 60% do esforço previsto até a review parcial.

---

## 12. Histórico de Revisão e Linha de Base do Marco 1

- **2026-09-03:** Linha de base inicial dos requisitos e regras de negócio.
- **2026-10-21:** Reconciliação dos RFs com a máquina de estados de 8 estados e inclusão da auditoria imutável.
- **2026-10-28:** **Linha de Base do Marco 1 (Encontro 5):** Inclusão do Glossário formal, Backlog ordenado com MoSCoW e risco técnico, Histórias de Usuário INVEST com Dado-Quando-Então, Caso de Uso UC-01, RNFs em Planguage (ISO 25010), registro de validação V1 e checklist de Fagan.
- **2026-10-28:** Fechamento das decisões DP01–DP08; especificação de anexos, permissões por papel, cancelamento e limites de alteração de eventos/serviços com reservas; revisão da avaliação e RNFs.
