# Inspeção formal de requisitos — EVT-22 (#42)

**Data do registro:** 25/11/2026  
**Artefato inspecionado:** [`docs/REQUISITOS.md`](./docs/REQUISITOS.md) e sua rastreabilidade com [`DESCOBERTA.md`](./DESCOBERTA.md), [`docs/PROCESSOS-NEGOCIO.md`](./docs/PROCESSOS-NEGOCIO.md), [`ARQUITETURA.md`](./ARQUITETURA.md), modelos e protótipo.  
**Referência:** [Capítulo 11 — Verificação e validação](https://jacksongomesbr.github.io/uft-cc-es/chapters/11-verificacao-e-validacao.html), especialmente a seção 11.5 e a entrega incremental da seção 11.12.

## 1. Objetivo e escopo

Esta inspeção verifica se os requisitos estão corretos, completos, consistentes, não ambíguos e verificáveis. O escopo cobre todos os requisitos funcionais (`RF01–RF20`), regras de negócio (`RN01–RN13`), requisitos não funcionais (`RNF-01–RNF-07`) e histórias de usuário do backlog (`HU-01–HU-14`).

A inspeção é uma atividade de verificação. Ela não substitui a validação com usuário registrada em [`docs/VALIDACAO-USUARIO-EVT-24.md`](./docs/VALIDACAO-USUARIO-EVT-24.md), nem prova a implementação do comportamento.

## 2. Método e critério de encerramento

O ciclo segue as etapas do capítulo 11:

1. **Planejamento:** delimitação do artefato, distribuição de papéis e definição da lista de verificação.
2. **Preparação:** leitura individual por requisito, confrontando origem, benefício, critérios, limites, autorização, persistência e rastreabilidade.
3. **Reunião:** registro do local, característica violada, classificação, gravidade e decisão necessária.
4. **Retrabalho:** autor corrige o texto ou responde a pergunta aberta; o registro não é apagado.
5. **Acompanhamento/recheck:** moderador confere a alteração no requisito e nos artefatos derivados.
6. **Melhoria do processo:** dúvidas recorrentes retornam à checklist e ao backlog.

**Critério de encerramento:** todos os achados devem estar `Fechado`, `Aceito como risco` ou `Convertido em backlog`, com evidência de recheck. Achado `Aberto`, `Bloqueado` ou `Não rechecado` não autoriza declarar a inspeção concluída.

Classificações usadas neste registro:

| Classificação | Uso |
|---|---|
| **Defeito** | O texto contradiz outro artefato, regra ou comportamento já decidido. |
| **Ambiguidade** | Mais de uma interpretação é possível e cada interpretação pode gerar comportamento diferente. |
| **Lacuna** | Falta informação necessária para construir, verificar, aceitar ou rastrear o requisito. |
| **Melhoria** | O requisito funciona como especificação, mas pode ficar mais claro, mensurável ou fácil de manter. |

As gravidades seguem o capítulo 11: **Major** altera comportamento, impede teste ou exige decisão de negócio; **Minor** afeta redação, consistência local ou manutenção sem mudar o comportamento principal.

## 3. Papéis da inspeção

O autor esclarece e corrige; o revisor confronta o requisito com a origem e os artefatos relacionados; o leitor parafraseia o texto; o inspetor procura defeitos usando a checklist. O autor não acumula o papel de inspetor no mesmo item.

| Papel | Responsabilidade | Participantes da escala |
|---|---|---|
| Autor | Mantém o requisito e executa o retrabalho. | Eduarda Negreiro, Gustavo Leite Bringel, Igor Anicezio Oliveira, Thalita Teixeira Menezes, José Guilherme Costa Oliveira |
| Revisor | Compara requisito, origem, regra, modelo e critério de aceite. | Escala rotativa abaixo |
| Leitor | Reescreve o sentido do requisito com suas próprias palavras e aponta interpretações concorrentes. | Escala rotativa abaixo |
| Inspetor | Aplica a checklist, registra achado, classificação e gravidade. | Escala rotativa abaixo |
| Moderador | Controla a reunião, confere preparação, retrabalho e recheck. | Thalita Teixeira Menezes |

### 3.1 Matriz de atribuição — histórias de usuário

| ID | Autor | Revisor | Leitor | Inspetor |
|---|---|---|---|---|
| HU-01 | Eduarda | Gustavo | Igor | Thalita |
| HU-02 | Gustavo | Igor | Thalita | José |
| HU-03 | Igor | Thalita | José | Eduarda |
| HU-04 | Thalita | José | Eduarda | Gustavo |
| HU-05 | José | Eduarda | Gustavo | Igor |
| HU-06 | Eduarda | Gustavo | Igor | Thalita |
| HU-07 | Gustavo | Igor | Thalita | José |
| HU-08 | Igor | Thalita | José | Eduarda |
| HU-09 | Thalita | José | Eduarda | Gustavo |
| HU-10 | José | Eduarda | Gustavo | Igor |
| HU-11 | Eduarda | Gustavo | Igor | Thalita |
| HU-12 | Gustavo | Igor | Thalita | José |
| HU-13 | Igor | Thalita | José | Eduarda |
| HU-14 | Thalita | José | Eduarda | Gustavo |

### 3.2 Matriz de atribuição — requisitos funcionais

| ID | Autor | Revisor | Leitor | Inspetor |
|---|---|---|---|---|
| RF01 | Eduarda | Gustavo | Igor | Thalita |
| RF02 | Gustavo | Igor | Thalita | José |
| RF03 | Igor | Thalita | José | Eduarda |
| RF04 | Thalita | José | Eduarda | Gustavo |
| RF05 | José | Eduarda | Gustavo | Igor |
| RF06 | Eduarda | Gustavo | Igor | Thalita |
| RF07 | Gustavo | Igor | Thalita | José |
| RF08 | Igor | Thalita | José | Eduarda |
| RF09 | Thalita | José | Eduarda | Gustavo |
| RF10 | José | Eduarda | Gustavo | Igor |
| RF11 | Eduarda | Gustavo | Igor | Thalita |
| RF12 | Gustavo | Igor | Thalita | José |
| RF13 | Igor | Thalita | José | Eduarda |
| RF14 | Thalita | José | Eduarda | Gustavo |
| RF15 | José | Eduarda | Gustavo | Igor |
| RF16 | Eduarda | Gustavo | Igor | Thalita |
| RF17 | Gustavo | Igor | Thalita | José |
| RF18 | Igor | Thalita | José | Eduarda |
| RF19 | Thalita | José | Eduarda | Gustavo |
| RF20 | José | Eduarda | Gustavo | Igor |

### 3.3 Matriz de atribuição — regras e requisitos não funcionais

| ID | Autor | Revisor | Leitor | Inspetor |
|---|---|---|---|---|
| RN01 | Eduarda | Gustavo | Igor | Thalita |
| RN02 | Gustavo | Igor | Thalita | José |
| RN03 | Igor | Thalita | José | Eduarda |
| RN04 | Thalita | José | Eduarda | Gustavo |
| RN05 | José | Eduarda | Gustavo | Igor |
| RN06 | Eduarda | Gustavo | Igor | Thalita |
| RN07 | Gustavo | Igor | Thalita | José |
| RN08 | Igor | Thalita | José | Eduarda |
| RN09 | Thalita | José | Eduarda | Gustavo |
| RN10 | José | Eduarda | Gustavo | Igor |
| RN11 | Eduarda | Gustavo | Igor | Thalita |
| RN12 | Gustavo | Igor | Thalita | José |
| RN13 | Igor | Thalita | José | Eduarda |
| RNF-01 | Thalita | José | Eduarda | Gustavo |
| RNF-02 | José | Eduarda | Gustavo | Igor |
| RNF-03 | Eduarda | Gustavo | Igor | Thalita |
| RNF-04 | Gustavo | Igor | Thalita | José |
| RNF-05 | Igor | Thalita | José | Eduarda |
| RNF-06 | Thalita | José | Eduarda | Gustavo |
| RNF-07 | José | Eduarda | Gustavo | Igor |

## 4. Checklist aplicada

Para cada item, o inspetor respondeu:

- a origem existe e está ligada a uma necessidade, entrevista, observação ou decisão;
- o benefício, ator, ação e objeto estão explícitos;
- o texto usa termos do glossário sem sinônimos concorrentes;
- há caminho principal, recusa/limite e efeito persistente quando aplicável;
- o critério é verificável sem depender da implementação;
- papéis, propriedade, prazos, estados, valores-limite e exceções estão definidos;
- o requisito é consistente com regras, processos, arquitetura, modelos, protótipo e rastreabilidade;
- existe ou pode ser derivado um caso de teste;
- o retrabalho e o recheck estão registrados.

## 5. Achados registrados

Os achados abaixo são a saída da inspeção. O status inicial é `Aberto`; as colunas de retrabalho e recheck são obrigatórias e serão atualizadas pelo autor e pelo moderador.

| ID | Local | Classificação | Gravidade | Achado | Retrabalho do autor | Recheck do moderador | Rastreabilidade | Status |
|---|---|---|---|---|---|---|---|---|
| INS-01 | `HU-01 / CA-01.1`; `RF10` | Ambiguidade | Major | “Notifica o prestador” não define canal, momento nem evidência da notificação. | Definir canal, evento disparador e resultado persistido; alinhar `UC-01` e `RF16`. | Conferir critério atualizado e derivar caso de teste de notificação. | `N2 → HU-01/RF10 → CA-01.1 → TC-INS-01` | Aberto |
| INS-02 | `RN06`, `RN08`, `HU-01–HU-03` | Defeito | Major | `RN06` restringe conflito a `CONFIRMADA`, enquanto `RN08` trata reservas ativas, pré-bloqueio e confirmação como regras de disponibilidade. | Harmonizar estados que bloqueiam agenda e atualizar `RF10`, `RF13`, modelo de estados e banco. | Reexecutar conferência entre regra, processo, diagrama e restrição SQL; confirmar que a redação admite um único comportamento. | `RN06/RN08 → RF10/RF13 → HU-01/HU-03 → modelo-dados` | Aberto |
| INS-03 | `RNF-01`; `ARQUITETURA.md` ADR-04 | Defeito | Major | O aceitável admite bcrypt ou Argon2id, o pretendido exige Argon2id e a arquitetura registra bcrypt; não há decisão única. | Escolher um algoritmo para a baseline e alinhar aceitável, pretendido, arquitetura e forma de verificação. | Conferir que requisitos e ADR apresentam a mesma escolha e que o teste mede essa escolha. | `D1 → RNF-01 → ADR-04 → teste de credencial` | Aberto |
| INS-04 | `RNF-02` | Lacuna | Major | O requisito mede concorrência, mas não informa tamanho da massa, número de concorrências, ambiente, repetição ou critério estatístico para “menos de 100 ms”. | Definir cenário, ferramenta, quantidade de execuções, ambiente e métrica de decisão; preservar o zero conflito como critério de segurança. | Reproduzir o caso em ambiente identificado e conferir que o resultado tem versão e evidência. | `N4/E1/E2/O1 → RNF-02 → RF10/RF13 → TC-INS-04` | Aberto |
| INS-05 | `RNF-03` | Lacuna | Major | “Rede local padrão” e “renderização completa” não fixam navegador, dispositivo, hardware, dataset reproduzível ou ponto final da medição. | Especificar ambiente, navegador, base de 200 serviços, ponto inicial/final e número de repetições. | Conferir se outra pessoa consegue repetir a medição sem escolher parâmetros por conta própria. | `N1/E1/E2 → RNF-03 → RF05/RF06 → TC-INS-05` | Aberto |
| INS-06 | `RNF-06`; `ARQUITETURA.md` | Lacuna | Major | O requisito cita `PoliticaCancelamento` e `ServicoDisponibilidade`, mas esses módulos não estão identificados no código/estrutura atual. | Definir o módulo real ou registrar a decisão como arquitetura futura, sem prometer uma evidência inexistente. | Conferir a alteração contra a árvore do repositório e o critério de Parnas. | `D1/DP03 → RNF-06 → ADR/estrutura de módulos → TC-INS-06` | Aberto |
| INS-07 | `HU-03 / CA-03.2`; `RN05`, `DP03` | Ambiguidade | Major | “Dentro do prazo de tolerância” e “há 48 horas” não definem o instante de início do SLA nem o fuso usado no cálculo. | Definir evento inicial, relógio/fuso, precisão e transição automática para `EXPIRADA`; alinhar `UC-01`. | Aplicar casos nos limites de 47:59, 48:00 e 48:01 com a data de referência fixada. | `N4 → HU-03/CA-03.2 → RN05/DP03 → TC-INS-07` | Aberto |
| INS-08 | `HU-05` no backlog; `RF05`, `RF06` | Lacuna | Major | A história existe no backlog, mas não possui seção com texto INVEST e critérios Dado-Quando-Então no documento de requisitos. | Criar `HU-05` com caminho principal, filtros, limites, efeito persistente e critérios rastreáveis; revisar `RF05/RF06`. | Conferir cobertura da história e derivar casos para busca vazia, um resultado, limite e excesso. | `N1 → HU-05 → RF05/RF06 → TC-INS-08` | Aberto |
| INS-09 | `HU-06–HU-10` no backlog; `RF04`, `RF08`, `RF09`, `RF14`, `RF17` | Lacuna | Major | Há itens de backlog sem histórias completas e critérios de aceite equivalentes, dificultando verificar cadastro, eventos, cancelamento, expiração e avaliação. | Criar ou justificar cada história fora da fatia; para as que permanecerem no escopo, incluir critérios e rastreabilidade. | Conferir que cada item tem critério, origem, caso de teste ou decisão explícita de escopo. | `backlog → HU-06..HU-10 → RF04/RF08/RF09/RF14/RF17` | Aberto |
| INS-10 | `HU-12 / CA-12.3` | Defeito | Minor | O critério repete “Dado que o anexo foi registrado” e mistura acesso do organizador com remoção pelo prestador sem separar pré-condições e permissões. | Reescrever em condições distintas, incluindo autorização, exclusão lógica, metadados e efeito observado. | Leitor parafraseia o critério e inspetor confirma que não restam duas interpretações. | `D07 → HU-12/CA-12.3 → RF19/RE04/RNF-07` | Aberto |
| INS-11 | `RF20`, `HU-13`, `DP04`; `README.md` | Defeito | Major | `docs/REQUISITOS.md` trata administração/moderação como decisão fechada, mas o README ainda apresenta RF20 como decisão pendente do MVP. | Escolher a fonte de verdade e alinhar README, descoberta, requisitos, backlog e escopo do MVP. | Conferir busca cruzada por `RF20`, `HU-13` e `DP04`; não aceitar status divergentes. | `D1/DP04 → RF20/HU-13 → README/DESCOBERTA/BACKLOG` | Aberto |
| INS-12 | `RF17`, `RN12`, `HU-10` | Lacuna | Minor | A avaliação tem regra, mas não tem critérios de aceitação detalhados para nota inválida, segunda avaliação, titularidade e reserva não finalizada. | Criar critérios para os limites 0, 1, 5, 6, duplicidade, papel e estado. | Derivar casos de teste e conferir a matriz RF/RN/RNF/HU. | `D1/DP05 → RF17/RN12/HU-10 → TC-INS-12` | Aberto |

### 5.1 Contagem dos achados

| Classificação | Quantidade |
|---|---:|
| Defeito | 4 |
| Ambiguidade | 2 |
| Lacuna | 6 |
| Melhoria | 0 |
| **Total** | **12** |

Os achados classificados como melhoria permanecem como categoria disponível no método; nesta rodada, os itens encontrados têm impacto suficiente para serem tratados como defeito, ambiguidade ou lacuna.

## 6. Plano de retrabalho e recheck

| Fase | Responsável | Evidência de saída |
|---|---|---|
| Decidir regras abertas | Coordenação/Produto | Resposta registrada junto ao achado e requisito alterado |
| Corrigir requisitos | Autor indicado na matriz | Diff no `REQUISITOS.md` e artefatos derivados |
| Atualizar rastreabilidade | Autor + revisor | Origem, requisito, regra, modelo e caso de teste ligados |
| Derivar casos | Inspetor | `TC-INS-*` com preparo, passos e resultado esperado |
| Fazer recheck | Moderador | Status alterado para `Fechado`, `Aceito como risco` ou `Convertido em backlog`, com evidência |

Nenhum achado deve ser removido por ter sido corrigido. O texto corrigido deve manter a referência ao ID do achado no histórico de revisão.

## 7. Rastreabilidade da inspeção

| Origem | Requisito/HU/RN/RNF | Achado | Artefato que precisa acompanhar o retrabalho |
|---|---|---|---|
| N1, N2, N4, D1, D07 | HU-01, HU-03, HU-05, HU-12, RF05, RF06, RF10, RF13, RF19, RN06, RN08, RNF-02, RNF-03, RNF-07 | INS-01, INS-02, INS-04, INS-05, INS-08, INS-10 | [`docs/PROCESSOS-NEGOCIO.md`](./docs/PROCESSOS-NEGOCIO.md), modelos, protótipo e casos `TC-INS-*` |
| D1, DP03, DP04, DP05 | HU-10, HU-13, RF17, RF20, RN12, RNF-01, RNF-06 | INS-03, INS-06, INS-11, INS-12 | [`ARQUITETURA.md`](./ARQUITETURA.md), [`README.md`](./README.md), [`DESCOBERTA.md`](./DESCOBERTA.md), backlog |
| N4, DP03, E1, E2 | HU-03, RN05 | INS-07 | [`docs/diagrams/estados-reserva.md`](./docs/diagrams/estados-reserva.md), `UC-01` e casos de limite |

## 8. Registro de melhoria do processo

- Incluir na checklist a pergunta “qual é o evento inicial do prazo e qual relógio mede o limite?” para todo requisito temporal.
- Exigir que cada item do backlog marcado como importante ou obrigatório tenha uma história e ao menos um critério de aceitação antes de ser considerado pronto.
- Conferir divergências entre requisitos fechados e textos institucionais antes da revisão final.
- Manter o resultado do recheck no mesmo registro do achado, para evitar que uma correção sem evidência seja confundida com encerramento.

## 9. Estado da inspeção

**Status:** Aberta — retrabalho e recheck pendentes para INS-01 a INS-12.  
**Decisão de entrega:** não declarar a inspeção concluída até que os achados Major tenham decisão e recheck registrados.

