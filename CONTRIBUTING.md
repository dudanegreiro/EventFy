# 🤝 Guia de Contribuição — EventFy

Este documento estabelece as convenções, padrões de versionamento, fluxo de trabalho e práticas de qualidade adotadas pela equipe no desenvolvimento do **EventFy**, em estrita conformidade com os fundamentos de Gerência de Configuração e Qualidade de Processo e Produto.

---

## 🌿 1. Ramos e Integração (Branches)

O ramo principal `main` representa a linha de base estável do software em funcionamento. **Nenhuma alteração é enviada diretamente ao `main`.**

Todo trabalho deriva de um item de backlog, é desenvolvido em um ramo curto e integrado exclusivamente via **Pull Request (PR)** revisado.

### 1.1 Nomenclatura de Ramos

Os ramos devem ser nomeados com o prefixo correspondente ao tipo de trabalho, seguido de descrição curta em minúsculas separada por hífens:

- `feat/<descricao-curta>` — Nova funcionalidade ou história de usuário
- `fix/<descricao-curta>` — Correção de defeito/bug
- `docs/<descricao-curta>` — Criação ou alteração de documentação e requisitos
- `test/<descricao-curta>` — Criação ou alteração de testes automatizados
- `refactor/<descricao-curta>` — Refatoração de código sem alteração de comportamento externo
- `chore/<descricao-curta>` — Tarefas de configuração, dependências e infraestrutura

*Exemplos no EventFy:*
- `feat/solicitar-reserva`
- `feat/analise-solicitacao-prestador`
- `fix/bloqueio-conflito-agenda`
- `docs/especificacao-requisitos`
- `test/validacao-disponibilidade`

### 1.2 Regras de Trabalho com Ramos

1. **Vida Curta:** O ramo deve viver poucos dias (máximo de 1 a 3 dias), evitando divergências longas em relação ao `main`.
2. **Atualização Contínua:** Antes de iniciar o trabalho e antes de abrir o PR, sincronize seu ramo com o `main` atualizado:
   ```bash
   git switch main
   git pull origin main
   git switch -c feat/nome-da-tarefa
   ```
3. **Exclusão pós-merge:** Após a aprovação e integração do PR no GitHub, o ramo correspondente deve ser excluído do repositório remoto e local.

---

## 💬 2. Convenção de Commits (Conventional Commits)

Cada commit representa uma **unidade de mudança atômica, coerente e completa**. Commits gigantes ("commit-depósito") ou commits fragmentados com código quebrado são proibidos.

Adota-se a especificação **Conventional Commits 1.0.0**:

```text
tipo(escopo): resumo no imperativo

Corpo detalhando o porquê da alteração e o contexto da decisão técnica (quando não óbvio).

Closes #<número-da-issue>
```

### 2.1 Tipos Permitidos

- `feat`: nova funcionalidade do sistema
- `fix`: correção de defeito
- `docs`: alterações em documentação e requisitos
- `test`: adição ou ajuste de testes
- `refactor`: reestruturação de código preservando o comportamento
- `chore`: configurações, build ou ajustes de dependências

### 2.2 Exemplos Contextualizados ao EventFy

```text
feat(reserva): permitir que o prestador recuse solicitacao com motivo

A regra de negocio RN04 exige que nenhuma reserva seja recusada sem motivo
explicito. A tela de recusa passa a validar o preenchimento de justificativa
antes de enviar a requisicao ao servidor.

Closes #18
```

```text
fix(agenda): impedir aprovacao de reservas com datas sobrepostas

Corrige validacao de conflito em DisponibilidadeServico para bloquear a
confirmacao quando ja existir outra reserva no mesmo intervalo de horas.

Closes #23
```

---

## 🔀 3. Fluxo de Pull Requests (PR)

A integração de qualquer alteração no `main` segue três princípios:

1. **Pull Request Pequeno:** Um item de backlog por PR. Alterações devem ser compreensíveis e revisáveis em 15 a 20 minutos.
2. **Descrição Completa:** Todo PR deve preencher o template em `.github/pull_request_template.md` com o que muda, como testar e a issue vinculada (`Closes #12`).
3. **Revisão Obrigatória:** Nada entra no `main` sem a aprovação de ao menos um integrante diferente do autor do código.
4. **SLA de Revisão:** O tempo máximo para revisão e resposta de um PR aberto é de **até 24 horas**.

---

## ⚖️ 4. Resolução de Divergência Técnica

Discordâncias técnicas durante a revisão de código e de documentação são naturais no processo de engenharia. Para evitar atrasos no fluxo da equipe:

1. A discussão técnica é realizada e registrada publicamente no próprio Pull Request.
2. Caso não haja consenso em até **dois turnos de comentários**, o responsável técnico pelo módulo ou papel de arquitetura (`Pessoa 4 / Igor`) toma a decisão final.
3. A decisão e a justificativa adotada são registradas no próprio PR antes da conclusão do merge.

---

## 📋 5. Definição de Pronto (Definition of Done - DoD)

Um item do backlog só é considerado **concluído (Pronto)** e computado na velocidade da iteração quando cumprir integralmente o seguinte checklist:

- [ ] **Critérios de Aceitação:** Todos os critérios de aceitação foram verificados e atendidos.
- [ ] **Independência de Verificação:** A conferência foi realizada por alguém que **não escreveu** o código do item.
- [ ] **Revisão de Código:** O código foi integrado ao `main` por Pull Request revisado e aprovado.
- [ ] **Acesso e Demonstração:** A funcionalidade está acessível no ambiente local/demonstração da equipe.
- [ ] **Requisitos Não Funcionais:** Os requisitos não funcionais aplicáveis ao item foram validados.
- [ ] **Rastreabilidade Preservada:** A issue correspondente referencia a história de usuário, os commits citam a issue (`Closes #numero`) e o PR vincula a issue.

---

## 🔍 6. Diretrizes para Revisão de Código (Code Review)

A revisão moderna tem como objetivo principal a **difusão de conhecimento e a melhoria da qualidade do código**, e não a avaliação de pessoas.

### 6.1 Classificação dos Comentários de Revisão

Para dar clareza à intenção, todo comentário de revisão deve receber uma das quatro etiquetas:

| Tipo | Quando usar | Ação esperada |
|---|---|---|
| **`[Bloqueia]`** | O PR fere requisitos, regras de negócio, contrato ou quebra o sistema. | O autor deve corrigir antes do merge. |
| **`[Sugere]`** | Proposta de melhoria de legibilidade, simplificação ou estilo. | O autor decide se acata agora ou em dívida técnica. |
| **`[Pergunta]`** | Dúvida sobre contexto, premissa ou regra de negócio. | O autor esclarece antes da decisão. |
| **`[Elogia]`** | Solução elegante, boa clareza ou cobertura de teste relevante. | Reconhece boas práticas no código. |

### 6.2 As Três Lentes de Avaliação

Todo revisor deve ler a contribuição através de três perspectivas:

1. **Legibilidade:** Os nomes utilizam o vocabulário do glossário do domínio (`Reserva`, `Servico`, `Disponibilidade`)? Uma pessoa que não escreveu a função compreende o fluxo na primeira leitura?
2. **Manutenibilidade:** A regra de negócio está no backend e isolada conforme as decisões de projeto (critério de Parnas)? A alteração duplica código? Trata os casos de multiplicidade (zero, um e muitos)?
3. **Rastreabilidade:** O PR e os commits referenciam a issue e os requisitos que motivaram a mudança?
