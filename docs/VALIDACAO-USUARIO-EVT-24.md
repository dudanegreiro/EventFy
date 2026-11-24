# 🧪 EVT-24 — Roteiro e relatório de validação com usuário externo

> **Issue:** [#44 — EVT-24: Validar fluxo principal com usuário externo](https://github.com/dudanegreiro/EventFy/issues/44)
>
> **Estado do artefato:** roteiro preparado; sessão e resultados ainda pendentes.

Este documento orienta uma sessão exploratória de usabilidade e utilidade do fluxo principal do EventFy. O roteiro não pressupõe que o participante conheça a interface e não deve ser usado para ensinar como navegar.

## 📑 Sumário

- [1. Objetivo e escopo](#1-objetivo-e-escopo)
- [2. Preparação e condução](#2-preparação-e-condução)
- [3. Tarefas para o participante](#3-tarefas-para-o-participante)
- [4. Registro imparcial das observações](#4-registro-imparcial-das-observações)
- [5. Itens de validação e rastreabilidade](#5-itens-de-validação-e-rastreabilidade)
- [6. Defeitos](#6-defeitos)
- [7. Novas necessidades e mudanças de requisito](#7-novas-necessidades-e-mudanças-de-requisito)
- [8. Síntese da sessão e retorno ao backlog](#8-síntese-da-sessão-e-retorno-ao-backlog)

---

## 1. Objetivo e escopo

Observar se uma pessoa que não pertence à equipe de desenvolvimento consegue compreender o valor do fluxo de contratação e avançar, sem instruções sobre a interface, da busca de serviço até a confirmação. A sessão também pode revelar problemas de uso, defeitos em relação a critérios existentes e necessidades ainda não cobertas pelos requisitos.

O teste usa o [protótipo navegável](../prototipo/README.md), não uma versão de produção. Ele mantém dados de exemplo entre telas pela URL e simula as ações do prestador; não há autenticação, API de negócio, persistência real ou agenda real. Não classifique essas limitações conhecidas como defeitos do protótipo. Registre-as como contexto se afetarem a interpretação dos resultados.

**Limites identificados na preparação do roteiro**

- O catálogo permite busca textual e filtro por categoria; não permite filtrar por preço, localização ou disponibilidade por data. T1 observa a descoberta de serviços, mas não valida todo o RF06. Consulte [`catalogo.html`](../prototipo/catalogo.html) e [`RF06`](./REQUISITOS.md).
- O critério CA-02.2 exige motivo de recusa com pelo menos 10 caracteres. O protótipo atualmente bloqueia apenas o motivo vazio. Se T4 for executada antes de essa diferença ser corrigida, registre-a como divergência conhecida entre implementação e requisito, não como comportamento inesperado descoberto pelo participante. Consulte [`script.js`](../prototipo/js/script.js) e [`CA-02.2`](./REQUISITOS.md).

Uma sessão com uma pessoa fornece evidência qualitativa para investigação, não uma medida representativa de todos os usuários.

## 2. Preparação e condução

### 2.1 Participante e ambiente

- Convidar uma pessoa externa à equipe de desenvolvimento; priorizar alguém que organize ou possa vir a organizar eventos.
- Registrar apenas um código anônimo, como `U-01`, e uma descrição geral do perfil. Não registrar nome, telefone, e-mail ou dados pessoais do evento.
- Iniciar em `prototipo/index.html`, em navegador moderno, com uma janela limpa e sem parâmetros de fluxo na URL.
- Antes da sessão, escolher uma data futura e preencher esse valor no texto da Tarefa T1. O período deve ter início anterior ao fim.
- Obter consentimento para a participação e perguntar separadamente se a pessoa aceita gravação. Gravação é opcional; não coletar nem guardar dados pessoais sem necessidade.
- Planejar cerca de 15 a 20 minutos, conforme a conversa com o usuário descrita em [`TEMA.md`](./TEMA.md).

### 2.2 Abertura e postura do facilitador

Leia apenas a abertura e a tarefa correspondente. Não faça demonstração nem explique telas, rótulos, botões ou o caminho esperado antes da tarefa.

**Abertura sugerida**

> Obrigado por participar. Estamos avaliando o protótipo, não você; não há respostas certas ou erradas. Use-o como faria normalmente e, se puder, diga em voz alta o que está pensando. Algumas ações são demonstrações e os dados não são salvos em um sistema real. Você pode parar a qualquer momento.

Durante a execução:

- Leia cada tarefa como está escrita; não acrescente passos, nomes de controles ou sugestões de navegação.
- Não confirme que uma escolha está certa ou errada. Evite completar frases, apontar a tela ou mover o cursor pelo participante.
- Se a pessoa pedir ajuda, aguarde alguns segundos e use, no máximo, uma pergunta neutra, como **“O que você tentaria fazer normalmente?”** Registre a pergunta e a ajuda solicitada.
- Se houver problema técnico, interrompa o cronômetro, registre o ocorrido e restabeleça o mesmo ponto inicial; não transforme a correção em orientação de uso.
- Registre ações e falas observáveis. Separe a citação literal da interpretação da equipe.

Após cada tarefa, use perguntas abertas, sem sugerir uma resposta:

- “O que você esperava que acontecesse?”
- “Como essa experiência se compara ao que você faz hoje?”
- “O que ficou faltando para você decidir o que fazer?”
- “Em que situação você usaria ou não usaria algo assim?”

Não pergunte “Você gostou?”, “Foi fácil?” ou “Você achou útil?”, isoladamente: perguntas desse tipo favorecem respostas curtas e podem induzir aprovação.

## 3. Tarefas para o participante

Antes da sessão, substitua `[data e horário futuros]` por um período válido. Não leia a coluna **Referência interna** para o participante.

| ID | Texto a ser lido ao participante | Referência interna — não ler |
|---|---|---|
| **T1 — Encontrar serviço e fazer um pedido** | “Você está organizando uma festa de aniversário e precisa de som e iluminação para **[data e horário futuros]**. Encontre uma opção que pareça adequada e deixe o pedido encaminhado para esse evento.” | Começar na página inicial. Observar busca e consulta do catálogo, seleção de serviço e preenchimento do pedido. Resultado esperado para rastreabilidade: pedido exibido como `SOLICITADA`, com serviço, evento e período informados. Não indicar em qual tela ou controle fazer isso. |
| **T2 — Concluir a contratação** | “O fornecedor avaliou o pedido e informou que pode atender. Continue até que o compromisso fique confirmado.” | Continuar a partir do pedido de T1. O protótipo simula a análise e a aprovação do prestador; observar se o participante entende o estado e chega a `CONFIRMADA`. |
| **T3 — Conferir o que aconteceu** | “Você quer conferir como o pedido evoluiu e quem participou de cada mudança. Encontre essa informação.” | Usar o pedido confirmado de T2. Observar se o participante localiza e interpreta a sequência do histórico. |

### Tarefas opcionais

Use uma nova execução do fluxo para T4. T5 pode ser executada após T2, se houver tempo. Não substitua as tarefas principais por estas.

| ID | Texto a ser lido ao participante | Referência interna — não ler |
|---|---|---|
| **T4 — Comunicar uma recusa** | “Em outra solicitação, o fornecedor percebeu que não poderá atender ao período. Dê um retorno ao organizador e deixe claro o motivo.” | Nova solicitação; observar o caminho de recusa, a exigência de justificativa e a exibição do motivo. Não fornecer uma justificativa pronta. |
| **T5 — Encerrar um compromisso** | “Depois de confirmar a contratação, seus planos mudaram e você não precisará mais do serviço. Encerre esse compromisso e deixe o motivo registrado.” | Usar uma solicitação confirmada; observar se a pessoa encontra o cancelamento e compreende a exigência de justificativa. |

## 4. Registro imparcial das observações

### 4.1 Dados da sessão

| Campo | Registro |
|---|---|
| Código anônimo do participante | A preencher |
| Perfil geral relevante à tarefa (sem identificação pessoal) | A preencher |
| Confirmação de que não pertence à equipe de desenvolvimento | A preencher |
| Data e duração da sessão | A preencher |
| Facilitador / observador | A preencher |
| Dispositivo e navegador | A preencher |
| Consentimento para participação | A preencher |
| Consentimento separado para gravação, se aplicável | A preencher |

### 4.2 Resultado por tarefa

Registre o tempo aproximado e o apoio oferecido. Não use “concluída” como sinônimo de “fácil”; anote o que ocorreu.

| Tarefa | Resultado (sem ajuda / com pergunta neutra / não concluída / não executada) | Tempo | Pedidos de ajuda ou interrupções | Observação factual |
|---|---|---|---|---|
| T1 | A preencher | A preencher | A preencher | A preencher |
| T2 | A preencher | A preencher | A preencher | A preencher |
| T3 | A preencher | A preencher | A preencher | A preencher |
| T4 (opcional) | A preencher / não executada | A preencher | A preencher | A preencher |
| T5 (opcional) | A preencher / não executada | A preencher | A preencher | A preencher |

### 4.3 Log de observação

Use uma linha por ocorrência relevante. Registre a sequência, a fala literal entre aspas quando possível e o apoio do facilitador. Evite rótulos como “confuso” sem descrever o comportamento que levou a essa interpretação.

| Nº | Tarefa e horário aproximado | Ação observável ou fala literal | Contexto / tela | Pergunta ou ajuda oferecida | Evidência relacionada (V-xx) |
|---|---|---|---|---|---|
| O-01 | A preencher | A preencher | A preencher | Nenhuma / descrever | A preencher |

## 5. Itens de validação e rastreabilidade

Os itens abaixo definem o que a sessão pretende observar; **não são resultados**. Após o teste, preencha evidência e resultado. Toda conclusão deve apontar sua origem e o critério correspondente.

`N1` a `N5` são as necessidades descritas em [`DESCOBERTA.md`](../DESCOBERTA.md) e rastreadas em [`REQUISITOS.md`](./REQUISITOS.md).

| ID | Tarefa | Origem | Critério rastreável | Evidência a registrar | Resultado |
|---|---|---|---|---|---|
| V-01 | T1 | Necessidade N1 | HU-05 (item do backlog); RF05 e RF07. RF06 é observado somente quanto ao filtro por categoria disponível no protótipo | Busca utilizada, detalhes consultados, dúvidas e conclusão da tarefa | Pendente |
| V-02 | T1 | Necessidade N2; [`REQUISITOS.md`](./REQUISITOS.md) | HU-01; RF10; CA-01.1 — pedido vinculado ao evento e período, iniciado em `SOLICITADA` | Dados apresentados no resumo, estado exibido e eventuais tentativas inválidas | Pendente |
| V-03 | T2 | Necessidade N3; [`REQUISITOS.md`](./REQUISITOS.md) | HU-02; RF12; CA-02.1 — aprovação da solicitação. RF11 (fila do prestador) não é exercitado pelo protótipo | Compreensão dos estados e conclusão da transição simulada | Pendente |
| V-04 | T2 | Necessidade N4; [`REQUISITOS.md`](./REQUISITOS.md) | HU-03; RF13; CA-03.1 — confirmação da contratação aprovada | Se e como a pessoa confirma e entende o resultado | Pendente |
| V-05 | T3 | Necessidade N5; [`REQUISITOS.md`](./REQUISITOS.md) | HU-04; RF16, RF18; CA-04.1 — consulta cronológica do histórico | Se encontra a trilha e identifica estados, autoria e sequência | Pendente |
| V-06 | T4 (opcional) | Necessidade N3; [`REQUISITOS.md`](./REQUISITOS.md) | HU-02; RF12; CA-02.2, CA-02.3 e CA-02.4 — recusa com motivo obrigatório e visível | Validação do motivo, resultado da recusa e compreensão do texto exibido | Pendente / não executado |
| V-07 | T5 (opcional) | HU-08; [`REQUISITOS.md`](./REQUISITOS.md) | RF14; RN05 — cancelamento permitido e justificado conforme o estado | Estado antes/depois, justificativa e compreensão do resultado | Pendente / não executado |

**Resultado** pode ser `validado`, `parcial`, `não validado` ou `não observado`. Registre a evidência que sustenta a classificação; se a sessão ainda não ocorreu, mantenha `Pendente`.

## 6. Defeitos

Registre aqui somente comportamentos reproduzíveis que contrariem um requisito ou critério já definido. Se a observação revelar uma necessidade que não está coberta, registre-a na seção 7, não como defeito. Se houver as duas coisas, crie registros separados.

| ID | Tarefa | Defeito observado (esperado × ocorrido) | Origem / evidência | Critério violado | Ação no backlog (issue ou item, responsável e estado) |
|---|---|---|---|---|---|
| D-01 | A preencher | A preencher | A preencher | HU / RF / CA / RNF correspondente | Criar ou vincular issue; registrar ID |

Se nenhum defeito for observado, registre **“Nenhum defeito observado nesta sessão”** e não deixe a ausência de linhas parecer uma sessão ainda não realizada.

## 7. Novas necessidades e mudanças de requisito

Registre aqui oportunidades, expectativas ou necessidades que não estejam cobertas pelos critérios atuais. Descreva o objetivo do usuário sem converter imediatamente a sugestão em solução de interface. Se o item propõe alterar um requisito existente, identifique o requisito afetado e submeta a mudança à decisão do responsável pelo produto.

| ID | Tarefa | Necessidade expressa (citação ou síntese fiel) | Origem / evidência | Critério atual ou “novo critério a definir” | Requisito afetado / mudança proposta | Ação no backlog (issue ou item, responsável e estado) |
|---|---|---|---|---|---|---|
| N-01 | A preencher | A preencher | A preencher | A preencher | A preencher | Criar ou vincular issue; registrar ID |

Se nenhuma nova necessidade for identificada, registre **“Nenhuma nova necessidade ou mudança de requisito identificada nesta sessão”**.

## 8. Síntese da sessão e retorno ao backlog

### 8.1 Síntese

| Campo | Registro |
|---|---|
| O que funcionou para o participante (com evidência) | A preencher |
| Principal ponto de dificuldade (com evidência) | A preencher |
| Utilidade percebida nas palavras do participante | A preencher |
| Tarefas concluídas sem ajuda | A preencher |
| Limitações do protótipo que afetaram a sessão | A preencher |
| Conclusão da equipe e justificativa | A preencher |

### 8.2 Ações após a sessão

1. Conferir se cada item de validação tem origem, critério e evidência; itens sem evidência permanecem pendentes.
2. Classificar separadamente defeitos e novas necessidades. Não converter opinião isolada em requisito aprovado.
3. Para cada defeito ou necessidade que demande trabalho, criar ou atualizar um item no backlog do GitHub e registrar o número da issue na tabela correspondente.
4. Quando uma necessidade alterar o escopo ou critério de aceite, abrir item de backlog para a decisão do responsável pelo produto e, após aprovação, atualizar [`REQUISITOS.md`](./REQUISITOS.md) e a rastreabilidade relacionada.
5. Não alterar requisitos diretamente a partir da fala do participante; manter a citação e a decisão da equipe rastreáveis.
6. Manter o relatório sem dados pessoais e atualizar o estado deste documento de **roteiro preparado** para **sessão realizada** somente após registrar evidências reais.
