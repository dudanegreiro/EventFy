# 🔍 Conferência Cruzada — EventFy

Este documento registra a conferência cruzada formal realizada entre os artefatos de **Requisitos**, **Modelo de Domínio**, **Modelo de Dados**, **Diagrama de Estados** e **Protótipo**, conforme estabelecido no **Capítulo 6** (Tabela 6.8 e Seção 6.8.3) da disciplina de Engenharia de Software.

A revisão foi realizada em duplas trocadas: quem participou da modelagem revisou o protótipo e os requisitos, e quem participou da prototipação revisou os modelos.

---

## 1. Verificação das 6 Questões Fundamentais (Tabela 6.8)

| # | Pergunta da Conferência | Artefatos Comparados | Defeito Investigado | Situação no EventFy | Correção Realizada |
|:---:|---|---|---|:---:|---|
| **1** | Todo campo que aparece na tela existe no modelo? | Protótipo e Modelo de Domínio | Campo inventado no desenho da tela, sem dado que o sustente | 🟢 Conforme | Campos de data de início/fim, valor total, descrição do serviço e justificativa de recusa possuem atributos correspondentes em `Servico` e `Reserva`. |
| **2** | Todo atributo do modelo aparece em alguma tela ou regra? | Modelo de Domínio e Protótipo | Dado que ninguém usa, que vai ser preenchido e nunca lido | 🟢 Conforme | Atributos como `motivoRecusa` foram incorporados à tela `prototipo/recusada.html` e `HistoricoReserva` reflete a auditoria exigida na regra RN07. |
| **3** | Todo critério de aceitação tem o dado de que precisa? | REQUISITOS.md e Modelo de Dados | Critério que não poderá ser verificado por falta de coluna | 🟢 Conforme | CA04.4 (motivo obrigatório) mapeado em `RESERVA.motivo_recusa`; RNF02 (conflitos) sustentado por `DISPONIBILIDADE_SERVICO`; RNF05 por `HISTORICO_RESERVA`. |
| **4** | Todo passo do caso de uso tem tela ou mensagem projetada? | UC-01 e Protótipo | Fluxo alternativo sem tratamento que vira decisão de quem implementa | 🟢 Conforme | Criada a tela `recusada.html` para tratar o fluxo alternativo 4b (recusa justificada) e tela `aprovada.html`/`confirmada.html` para o avanço da contratação. |
| **5** | Toda situação do diagrama de estados é alcançável e tem saída? | Diagrama de Estados e Backlog | Estado sem transição de entrada ou situação em que o usuário fica preso | 🟢 Conforme | Os 8 estados (`SOLICITADA`, `EM_ANALISE`, `APROVADA`, `CONFIRMADA`, `RECUSADA`, `CANCELADA`, `EXPIRADA`, `FINALIZADA`) possuem entradas e saídas válidas sem *deadlocks*. |
| **6** | Todo item do backlog da fatia tem modelo correspondente? | Backlog e Modelo de Domínio | Item que será implementado sem estrutura decidida | 🟢 Conforme | Itens prioritários da fatia do MVP (solicitar, analisar, aprovar, recusar e confirmar) possuem entidades (`Reserva`, `Servico`, `DisponibilidadeServico`) estruturadas. |

---

## 2. Registro da Revisão por Pares

| Data | Artefato Revisado | Autor | Revisor | Inconsistência Encontrada | Ação / Correção Efetuada | Status |
|:---:|---|---|---|---|---|:---:|
| 21/10/2026 | `REQUISITOS.md` | Equipe | Pessoa 3 | Critérios de aceitação sem especificação do efeito persistente de histórico | Atualizada RN05, RN07 e critérios CA10 a CA18 | ☑ Aprovado |
| 21/10/2026 | Modelo de domínio | Igor (Pessoa 4) | Pessoa 3 | Ausência de representação de agenda dinâmica e auditoria de estados | Inclusão de `DisponibilidadeServico` e `HistoricoReserva` | ☑ Aprovado |
| 21/10/2026 | Modelo de dados | Igor (Pessoa 4) | Pessoa 3 | Faltavam decisões sobre exclusão lógica e granularidade de horário | Inclusão da coluna `ativo` em todas as tabelas e tipos `DATETIME` | ☑ Aprovado |
| 21/10/2026 | Estados da reserva | Igor (Pessoa 4) | Pessoa 3 | Estados terminais não previam cancelamento em todas as fases pré-evento | Máquina expandida para 8 estados contemplando `CANCELADA` e `EXPIRADA` | ☑ Aprovado |
| 21/10/2026 | Diagrama de sequência | Igor (Pessoa 4) | Pessoa 3 | Falta de clareza sobre quem valida conflitos de agenda | Inclusão do componente de domínio `ServicoDisponibilidade` (Parnas) | ☑ Aprovado |
| 21/10/2026 | Protótipo | Equipe | Pessoa 4 | Falta da tela de recusa com campo obrigatório de justificativa | Criada tela `prototipo/recusada.html` com input obrigatório de motivo | ☑ Aprovado |
| 28/10/2026 | Fontes Mermaid | Igor (Pessoa 4) | Equipe | Diagramas existiam apenas embutidos no markdown | Criados arquivos `.mmd` em `docs/diagrams/` | ☑ Aprovado |
