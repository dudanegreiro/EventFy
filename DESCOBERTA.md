# 🔍 Descoberta do Problema e Engenharia de Requisitos — EventFy

Este documento consolida os resultados da etapa de descoberta do problema, partes interessadas, personas, necessidades e riscos do projeto **EventFy**, estruturado segundo o **Capítulo 4** da disciplina de Engenharia de Software.

---

## 1. O Problema

A contratação de serviços para eventos de pequeno e médio porte em Palmas–TO é realizada de forma dispersa e informal, por meio de conversas soltas no WhatsApp, buscas pontuais no Instagram e anotações manuais em cadernos ou planilhas.

Essa dinâmica causa perda de orçamentos, demora para saber se a data está livre, duplo agendamento para o mesmo fornecedor e desentendimento sobre o que foi combinado entre as partes.
`[Fontes: E1, E2, O1]`

---

## 2. Partes Interessadas (Stakeholders)

| Parte Interessada | Categoria | O que busca no sistema (Interesse) | Poder de Decisão | Contato |
|---|---|---|:---:|---|
| **Organizador autônomo** | Decide e usa | Encontrar opções em um só lugar, checar disponibilidade de data e formalizar reservas sem retrabalho. | **Alto** | `Duda Negreiro (representante)` |
| **Prestador / Fornecedor** | Usa | Receber pedidos estruturados, evitar conflito de datas na agenda e responder formalmente com motivo de recusa. | **Médio** | `Igor Oliveira (representante)` |
| **Convidado do evento** | Afetado | Usufruir de serviços pontuais e sem imprevistos causados por falha de fornecedor. | **Baixo** | `Alunos da turma` |
| **Administrador da plataforma** | Opera e mantém | Monitorar conformidade dos cadastros, auditoria de transições e integridade operacional. | **Alto** | `Equipe técnica` |
| **Infraestrutura / Servidor** | Opera e mantém | Sistema estável, leve, sem consumo abusivo de armazenamento e sem dependências externas incertas. | **Alto** | `Prof. Jackson / Laboratório` |

---

## 3. Personas

### Persona 1: Carlos, organizador autônomo
- **Contexto:** 24 anos, estudante universitário, organiza recepções de formatura e confraternizações para amigos e familiares em Palmas. `[Fonte: E1]`
- **Objetivo:** Encontrar espaço e som para o evento, comparar preços e garantir a data sem precisar mandar mensagem para dez perfis no Instagram. `[Fonte: E1]`
- **Dificuldade atual:** Espera até três dias por respostas de orçamento no WhatsApp e já teve caso em que o fornecedor esqueceu que a data já estava prometida. `[Fonte: E1, O1]`
- **Condição de uso:** Acessa prioritariamente pelo celular, à noite ou em intervalos de aula. `[Fonte: O1]`
- **O que ele NÃO precisa:** Gerenciar lista de convidados ou emitir ingressos dentro do sistema. `[Fonte: E1]`

### Persona 2: Juliana, prestadora de serviços (Som e Iluminação)
- **Contexto:** 31 anos, dona de microempresa de sonorização em Palmas, atende de 3 a 5 eventos por final de semana. `[Fonte: E2]`
- **Objetivo:** Ter um canal organizado para receber solicitações e bloquear na agenda as datas já confirmadas. `[Fonte: E2]`
- **Dificuldade atual:** Mensagens de orçamento misturam-se com conversas pessoais; quando precisa recusar um cliente por falta de equipamento, o cliente insiste por falta de um canal formal. `[Fonte: E2]`
- **Condição de uso:** Acessa pelo computador no escritório durante a semana e pelo celular no local dos eventos aos sábados. `[Fonte: E2]`
- **O que ela NÃO precisa:** Sistema contábil completo ou emissão de nota fiscal pela plataforma. `[Fonte: E2]`

---

## 4. Fontes Consultadas

- **E1:** Entrevista semiestruturada com organizador autônomo em Palmas, realizada em 25/08/2026, duração 40 min, conduzida por Duda Negreiro.
- **E2:** Entrevista semiestruturada com prestador local de serviços de som/iluminação, realizada em 26/08/2026, duração 45 min, conduzida por Igor Oliveira.
- **O1:** Observação direta da rotina de fechamento de reservas em grupos de WhatsApp e perfis comerciais, realizada em 27/08/2026, duração 60 min.
- **D1:** Análise de contratos de prestação de serviços padrão e tabelas de preços de fornecedores locais.

---

## 5. Tabela de Necessidades Levantadas

| Id | Necessidade | Parte Interessada | Fonte | Situação |
|:---:|---|---|:---:|:---:|
| **N1** | Consultar serviços disponíveis por categoria e filtros em um catálogo único | Organizador | E1, O1 | **Confirmada** |
| **N2** | Solicitar reserva vinculada a um evento com indicação de data/horário | Organizador | E1 | **Confirmada** |
| **N3** | Receber solicitações em fila e poder aprovar ou recusar com motivo obrigatório | Prestador | E2 | **Confirmada** |
| **N4** | Bloqueio automático de data na disponibilidade após confirmação da reserva | Prestador / Organizador | E1, E2, O1 | **Confirmada** |
| **N5** | Histórico imutável de mudanças de estado para comprovar o que foi acordado | Ambas as partes | E1, E2 | **Confirmada** |
| **N6** | Pagamento online integrado com split automático | Prestador | E2 | **Bloqueada (fora de escopo, ver R2)** |

---

## 6. Conflitos entre Partes Interessadas e Decisões

| Conflito | Entre quem | Critério aplicado | Decisão tomada |
|---|---|---|---|
| **Tempo de resposta da solicitação** (organizador quer aprovação rápida vs prestador precisa avaliar cronograma) | Organizador e Prestador | Dinamismo do processo e redução de bloqueio | Estabelecimento de prazo de SLA de 48h para análise: se o prestador não responder, a solicitação expira automaticamente (`EXPIRADA`), liberando o organizador. |
| **Recusa de pedido** (prestador prefere apenas não responder vs organizador quer saber por que não deu certo) | Prestador e Organizador | Princípio de respeito e regra de negócio do domínio | Recusa exige preenchimento obrigatório de justificativa (`motivo_recusa`), garantindo transparência ao organizador. |
| **Meio de pagamento** (prestador quer sinal antecipado na plataforma vs equipe técnica) | Prestador e Equipe | Restrição de acesso e viabilidade semestral (Critério 5 da Tabela 1.5) | Pagamentos ficam fora da plataforma nesta versão; negociação de pagamento ocorre externamente entre as partes. |

---

## 7. Cenário Atual vs Cenário Pretendido

### 7.1 Cenário Atual (Sem o EventFy)
1. O organizador pesquisa fornecedores abrindo perfis manuais no Instagram. `[O1]`
2. Envia mensagens individuais no WhatsApp de cada um perguntando se a data está livre. `[E1, O1]`
3. O prestador leva horas ou dias para verificar sua agenda manual e responder se tem disponibilidade. `[E2]`
4. Caso a data esteja ocupada, a conversa se encerra sem histórico e o organizador recomeça a busca do zero. `[E1]`
5. Quando fecham acordo, combinam informalmente por mensagem; se houver cancelamento de última hora, não há histórico auditável nem registro formal do cancelamento. `[E1, E2]`

### 7.2 Cenário Pretendido (Com o EventFy)
1. O organizador acessa o EventFy, filtra os serviços por categoria e visualiza a disponibilidade na data do evento.
2. Submete a solicitação de reserva diretamente pela plataforma com os dados do evento e período.
3. O prestador recebe a notificação estruturada, analisa a viabilidade e clica em "Aprovar" ou "Recusar" (informando o motivo).
4. O organizador recebe a confirmação e formaliza a contratação, provocando o bloqueio automático definitivo na agenda do serviço.
5. Todo o histórico de transições é registrado com data, hora e responsável na auditoria.

---

## 8. Escopo do Sistema

### 8.1 Entra nesta versão (Escopo Ativo)
- Cadastro e autenticação de usuários (Organizador e Prestador).
- Cadastro, edição e catálogo de serviços.
- Gestão de disponibilidade e bloqueios de agenda.
- Gerenciamento de eventos do organizador.
- Fluxo de solicitação, análise, aprovação, recusa com motivo e confirmação de reserva.
- Máquina de estados completa com 8 estados (`SOLICITADA` a `FINALIZADA`).
- Trilha de auditoria imutável das reservas (`HISTORICO_RESERVA`).

### 8.2 Fora de escopo nesta versão (com justificativa)
- **Processamento de pagamentos e transações financeiras:** Dependeria de credenciamento bancário/gateway terceiro, violando o critério 5 da Tabela 1.5.
- **Gestão operacional da festa (convidados, ingressos, cronograma interno):** O problema central do EventFy é a contratação e garantia de agenda de serviços; a execução do evento é responsabilidade de outros softwares.
- **Chat em tempo real interno:** Cria complexidade de infraestrutura desnecessária no semestre; o contato preliminar é suprido pelos canais diretos já habituais dos usuários.

---

## 9. Produto Mínimo Viável (MVP — Fatia Vertical)

O MVP foi selecionado aplicando os **três critérios** do livro (Seção 4.13):
1. **Necessidade confirmada por múltiplas fontes:** A reserva sem duplicidade e com acompanhamento claro (`N2`, `N3`, `N4`).
2. **Risco técnico prioritário:** Concorrência temporal na disponibilidade e transições da máquina de estados.
3. **Demonstrabilidade:** Um fluxo completo navegável e executável de ponta a ponta (Organizador solicita -> Prestador analisa/aprova/recusa -> Confirmação).

*Contagem de iterações:* Entre o Encontro 4 e o Marco 2 (Encontro 9) cabem exatamente **2 iterações e meia** (5 semanas), tempo suficiente para implementar a fatia vertical completa.

---

## 10. Riscos Iniciais e Respostas

| Id | Risco | Prob. | Impacto | Resposta | Ação e Responsável |
|:---:|---|:---:|:---:|:---:|---|
| **R1** | Prestadores demorarem para responder solicitações, gerando insatisfação | Alta | Médio | **Mitigar** | Implementar regra de SLA no backend com expiração automática (`EXPIRADA`) após 48h. *Responsável: Equipe de backend.* |
| **R2** | Inviabilidade de integrar gateway de pagamento | Alta | Médio | **Evitar** | Declarar pagamentos fora de escopo no MVP; pagamento direto entre as partes. *Responsável: Duda Negreiro.* |
| **R3** | Concorrência de duas pessoas solicitando a mesma data no mesmo minuto | Média | Alto | **Mitigar** | Controle de concorrência com transação atômica no banco de dados e pré-bloqueio em `APROVADA`. *Responsável: Igor Oliveira.* |
| **R4** | Membros da equipe terem semanas de provas concomitantes reduzindo a capacidade | Alta | Médio | **Aceitar** | Planejar capacidade com folga de 20% e tarefas SMART curtas de 1 dia. *Responsável: Equipe.* |
| **R5** | Regras de tolerância de cancelamento mudarem durante o desenvolvimento | Média | Alto | **Mitigar** | Isolar a política de cancelamento em módulo único (critério de Parnas). *Responsável: Igor Oliveira.* |

---

## 11. Histórico de Revisão

- **2026-08-27:** Versão inicial de descoberta (Capítulo 4).
- **2026-10-21:** Reconciliação dos riscos e do escopo do MVP com o modelo de estados do Capítulo 6.
