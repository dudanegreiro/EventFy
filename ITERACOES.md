# Iterações

Este arquivo registra, por iteração, **o que a equipe planejou, o que concluiu e o que aprendeu**. O `PROCESSO.md` diz como a equipe trabalha; este arquivo diz o que aconteceu de fato (livro, Capítulo 8, seção 8.11).

**Como ler os números**

- **Concluído** é o item que cumpre a Definição de Pronto (`PROCESSO.md`, seção 4): integrado ao **`main`** por Pull Request revisado e aprovado por outra pessoa. Item com PR aberto, ou integrado só em ramo intermediário, **não conta**.
- **Velocidade** é a soma dos pontos dos itens concluídos na iteração.
- Todo número tem a fonte ao lado, para outra pessoa conferir.
- Datas e horários estão em UTC, como o GitHub exibe. Dados coletados em **24/11/2026, por volta de 17h30 UTC**.
- Quem atualiza: Thalita (@thalist), com apoio de todos (issues #31 e #67). Toda alteração entra por Pull Request revisado por outra pessoa.

> **Estado deste arquivo:** primeira versão. Itens marcados com **[A CONFIRMAR]** dependem de uma resposta da equipe e não foram preenchidos por suposição. A retrospectiva da Iteração 1 está completa; a da Iteração 2 ainda não existe, porque ela termina em 26/11.

---

## Replanejamento até a demonstração de 03/12 (proposta)

Faltam 9 dias para a apresentação do sistema funcionando. O livro (cap. 8) manda que o que não terminou **volte ao backlog sem mudar a duração da iteração**, então o replanejamento ordena o que falta pelo que a demonstração precisa. A ordem abaixo é uma **proposta para a equipe decidir**.

A demonstração precisa mostrar o fluxo principal funcionando de ponta a ponta: o organizador cria um evento e solicita uma reserva, o prestador analisa e aprova ou recusa, e o organizador confirma (HU-01 a HU-04, `docs/REQUISITOS.md`).

| Prioridade | O que precisa acontecer | Itens | Quem (proposta) | Prazo-alvo |
|---|---|---|---|---|
| 1 | **Levar a API e os testes ao `main`**: resolver os três comentários [Bloqueia] do Igor e integrar o ramo `feat/service-catalog-management` ao `main` | #23 a #26 (EVT-03 a 06) | Gustavo, revisão do Igor | 26/11 |
| 2 | **Tela ligada à API**: eventos, solicitação, análise, confirmação e histórico | #27 (EVT-07), #34, #35, #37 | José | 28/11 |
| 3 | **Testes e verificação automática no GitHub** | #29, #30, #43, #47 | Thalita, Igor, Gustavo | 29/11 |
| 4 | **Sistema no ar**, com verificação de saúde e a versão | #53 a #57 | Igor, Gustavo | 01/12 |
| 5 | **Documentação de entrega e versão v1.0.0** | #32, #44, #59, #64, #65, #66, #68 | Eduarda, Thalita | 02/12 |
| 6 | Retrospectiva e dívida técnica | #63, #67 | Thalita | 02/12 |

**Candidatos a ficar de fora, para a equipe decidir [A CONFIRMAR]:** #38 avaliação, #39 anexos de serviço, #40 moderação administrativa, #41 expiração automática, #36 cancelamento justificado. O que for cortado deve aparecer como "não entregue" na matriz de escopo (#66), não escondido. O livro valoriza dizer com honestidade o que não ficou pronto.

**Risco principal:** o item 1 bloqueia os itens 2, 3 e 4. Sem a API no `main`, não há o que ligar à tela, testar na integração contínua ou colocar no ar.

---

## Iteração 2 (23 a 26 de novembro)

**Meta:** [A CONFIRMAR]. Sugestão: a API do fluxo principal está no `main`, e o organizador consegue criar um evento e solicitar uma reserva pela tela.

**Capacidade:** [A CONFIRMAR] pessoas equivalentes; previsão de [A CONFIRMAR] pontos.

| Item | Responsável | Pontos | Situação em 24/11 |
|---|---|---:|---|
| #33 EVT-13 Cadastro de contas e perfil | Gustavo | sem estimativa | Em progresso |
| #34 EVT-14 Criação e gerenciamento de eventos | José | sem estimativa | A fazer |
| #35 EVT-15 Fila e detalhe das solicitações do prestador | José | sem estimativa | A fazer |
| #36 EVT-16 Cancelamento justificado | Gustavo | sem estimativa | A fazer |
| #37 EVT-17 Acompanhamento do estado e histórico | José | sem estimativa | A fazer |
| #38 EVT-18 Avaliação única após finalização | José | sem estimativa | A fazer |
| #39 EVT-19 Anexos de serviço | Gustavo | sem estimativa | A fazer |
| #40 EVT-20 Moderação administrativa | Gustavo | sem estimativa | A fazer |
| #41 EVT-21 Expiração automática por SLA de 48 horas | Gustavo | sem estimativa | A fazer |

Fonte: quadro "EventFy - Desenvolvimento", campo Iteração.

**Resultado:** preencher ao fim da iteração, com a observação do usuário na demonstração.

---

## Iteração 1 (19 a 23 de novembro)

**Meta:** [A CONFIRMAR]. O `docs/BACKLOG.md` liga os itens EVT-01 a EVT-08 ao "Marco 2: Review parcial" e EVT-09 a EVT-12 ao "Marco 3: Qualidade verificada".

**Planejado:** 76 pontos (12 itens, EVT-01 a EVT-12). Fonte: quadro, campo Iteração, e estimativas do `docs/BACKLOG.md`.

**Concluído até o fim da iteração (23/11):** **0 pontos**. Nenhum PR de EVT havia sido integrado ao `main`. Fonte: `git log --first-parent origin/main`.

**Concluído em 24/11 (já na Iteração 2):** **13 pontos**, EVT-01 (PR #83, 5 pontos) e EVT-02 (PR #77, 8 pontos). Pela regra do livro, esses pontos contam na velocidade da Iteração 2, e não da 1.

**Devolvido ao backlog / continua:** 10 itens, 63 pontos.

| Item | Responsável | Pontos | Situação em 24/11 |
|---|---|---:|---|
| #21 EVT-01 Tecnologias, arquitetura e ambiente local | Igor | 5 | Concluído (PR #83 no `main`) |
| #22 EVT-02 Banco, migrações e dados de demonstração | Gustavo | 8 | Concluído (PR #77 no `main`) |
| #23 EVT-03 API REST do fluxo principal | Gustavo | 8 | PR #78 integrado só em ramo intermediário; **não está no `main`**; 1 [Bloqueia] |
| #24 EVT-04 Autenticação e autorização por papel | Gustavo | 5 | PR #79 integrado só em ramo intermediário; **não está no `main`** |
| #25 EVT-05 Catálogo, filtros e gerenciamento de serviços | Gustavo | 8 | PR #80 integrado só em ramo intermediário; **não está no `main`** |
| #26 EVT-06 Máquina de estados e agenda concorrente | Gustavo | 8 | PR #81 integrado só em ramo intermediário; **não está no `main`**; 2 [Bloqueia] |
| #27 EVT-07 Eventos e solicitações no frontend | José | 8 | A fazer |
| #28 EVT-08 Preparar review parcial executável | Eduarda | 3 | Em revisão (PR #85 aberto) |
| #29 EVT-09 Testes unitários e de integração | Thalita | 8 | A fazer |
| #30 EVT-10 Integração contínua e proteção do `main` | Igor | 5 | A fazer |
| #31 EVT-11 Checklist de revisão e evidências | Thalita | 5 | Parcial: PR #82 no `main`; falta este arquivo e as estimativas das dívidas |
| #32 EVT-12 Documentação operacional e linha de base | Eduarda | 5 | Em progresso |

### Retrospectiva

**Evidências**

| Evidência | Valor | Fonte |
|---|---|---|
| Itens planejados | 12 itens, 76 pontos | Quadro e `docs/BACKLOG.md` |
| Itens concluídos até 23/11 | 0 | `git log --first-parent origin/main` |
| Itens concluídos até 24/11 | 2 itens, 13 pontos (EVT-01 e EVT-02) | PRs #83 e #77, no `main` |
| Itens como "Finalizadas" no quadro | 6 itens, 42 pontos (EVT-01 a 06) | Quadro, 24/11 |
| Itens "Finalizadas" sem o código no `main` | 4 itens, 29 pontos (EVT-03 a 06) | `git ls-tree -r origin/main` sem `api/` nem `tests/`; PRs #78 a #81 têm base diferente de `main` |
| Pull Requests abertos de 20 a 24/11 | 9 (#77 a #85) | `gh pr list --state all` |
| Integrados no `main` | 3 (#77, #82, #83) | Página de cada PR |
| Integrados só em ramo intermediário | 4 (#78 a #81) | Campo "base" de cada PR |
| Ainda abertos | 2 (#84, #85) | Página de cada PR |
| Espera até a primeira revisão | #77: 107 h 52 min; #78: 107 h 31 min; #79: 53 h 7 min; #80: 107 h 7 min; #81: 106 h 52 min; #82: 53 h 7 min | Página de cada PR |
| Meta de revisão do `CONTRIBUTING.md` | até 24 h; **nenhum dos 6 PRs revisados cumpriu** | `CONTRIBUTING.md`, seção 4, item 4 |
| Horário das revisões do Igor | seis revisões enviadas entre 14:57:24 e 14:57:35 de 24/11 | Páginas dos PRs #77 a #82 |
| Revisões feitas | 7 (6 do Igor, 1 da Thalita) | Páginas dos PRs |
| Revisões que usaram as etiquetas do `CONTRIBUTING.md` | 3 de 7 (as duas com pedido de mudança do Igor e a da Thalita) | Corpo de cada revisão |
| Comentários [Bloqueia] | 3, sobre 2 problemas: testes que falham na segunda execução (#78 e #81) e fila de reservas que não concorda com o detalhe na expiração (#81) | Revisões do Igor em #78 e #81 |
| Comentários da revisão do PR #79 pela Thalita | 0 Bloqueia, 4 Sugere, 2 Pergunta, 3 Elogia | Revisão de @thalist, 22/11 08:42 |
| PR integrado no `main` sem revisão registrada | 1 de 3 (#83) | Página do PR #83 |
| Defeitos achados depois da integração | ainda não medido | Só há 3 itens integrados no `main` |
| Issues com estimativa em pontos | 12 de 48 | `docs/BACKLOG.md`; as demais issues não têm pontos |
| Cartões em "A fazer" | 38 de 48 | Quadro, 24/11 |

**Leitura**

- Os dados mostram que **o código foi escrito em 20/11 e revisado só em 24/11**, depois do fim da iteração. Nenhum PR foi revisado dentro de 24 horas. A revisão ocorreu em bloco, não de forma contínua.
- Os dados mostram que **o quadro e o `main` não contam a mesma história**: quatro cartões estão em "Finalizadas", mas o código deles ainda não está no `main`. Pela Definição de Pronto, eles não estão concluídos. Isso importa porque a demonstração depende da API.
- Os dados mostram que dois PRs foram integrados em ramo intermediário com pedido de mudança aberto. Eu **não verifiquei** se os três [Bloqueia] já foram corrigidos depois.
- Os dados **não mostram** por que as revisões demoraram. Pode ser falta de aviso, de tempo ou de clareza sobre quem revisa. Isso precisa ser perguntado ao grupo.
- Os dados também **não mostram** a eficácia da revisão, porque há poucos itens no `main` para medir defeitos que escapam depois da integração.
- Só 12 de 48 issues têm estimativa, então não dá para planejar a Iteração 2 por pontos, como o livro pede.
- O `PROCESSO.md` (seção 2) descreve iterações de **duas semanas**, mas o quadro tem quatro iterações de 3 a 4 dias (19/11 a 03/12). Essa diferença deve ser tratada na retrospectiva final (#67).

**Decisões (no máximo duas, cada uma com dono e forma de conferir)**

> **Propostas para discussão com a equipe.** Ninguém aceitou ainda. Só passam a valer depois que o grupo concordar e o dono for confirmado.

| Mudança | Dono | Como conferir | Quando conferir |
|---|---|---|---|
| Levar a API e os testes ao `main` e, daqui em diante, todo PR ter como base o `main` | [A CONFIRMAR] | `git ls-tree -r origin/main` lista `api/` e `tests/`; PRs novos mostram base `main` | Fim da Iteração 2 (26/11) |
| Todo PR abre já com revisor pedido, e a primeira revisão sai em até 24 h | [A CONFIRMAR] | Tempo entre a abertura do PR e a primeira revisão, lido na página de cada PR | Retrospectiva da Iteração 2 |

**Observação do usuário na demonstração:** [A PREENCHER] (ainda não houve demonstração).

**Riscos revisados:** [A PREENCHER], com o `DESCOBERTA.md`.

---

## Histórico de alterações deste arquivo

- **2026-11-24:** criação, com o replanejamento até 03/12, o plano da Iteração 2 e a retrospectiva da Iteração 1. Autora: Thalita Menezes (@thalist).
