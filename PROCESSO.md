# 🔄 Processo de Desenvolvimento — EventFy

Este documento registra o processo de desenvolvimento de software adotado pela equipe no projeto **EventFy**, fundamentado nas diretrizes do **Capítulo 3** da disciplina de Engenharia de Software.

---

## 1. Escolha e Justificativa do Processo

A equipe adota o modelo **Iterativo e Incremental**, organizado em **iterações de duas semanas**.

A decisão baseia-se na avaliação dos cinco fatores de **Boehm e Turner (2003)**:

| Fator | Avaliação no Projeto | Direção | Justificativa |
|---|---|:---:|---|
| **Tamanho da equipe** | 5 pessoas | **Ágil** | Equipe pequena, comunicação direta e rápida entre todos os membros. |
| **Criticidade** | Baixa | **Ágil** | Sistema de agendamento de eventos, sem risco de vida ou dados financeiros sensíveis; falhas causam incômodo reparável. |
| **Dinamismo** | Alto | **Ágil** | Requisitos do domínio de eventos e prestadores evoluem à medida que protótipos e fluxos são validados. |
| **Pessoal** | Estudantes de 4º período | **Plano-dirigido** | Primeira experiência prática em equipe e tomada de decisões arquiteturais inéditas. |
| **Cultura** | Ambiente acadêmico | **Ágil** | Tolera ajustes no percurso, desde que formalmente registrados e justificados. |

### 1.1 Compensação para o fator "Pessoal"
Como o fator *Pessoal* aponta para plano-dirigido, a equipe adota salvaguardas explícitas para compensar a inexperiência:
1. **Artefatos escritos a cada marco:** Requisitos, modelos conceituais, diagrama de estados e contratos de API registrados antes da implementação definitiva.
2. **Revisão obrigatória (Code Review):** Nenhuma alteração é integrada ao `main` sem aprovação de outro membro em Pull Request.
3. **Definição de Pronto rigorosa:** Critérios claros para evitar itens dados como "prontos" apenas na máquina do autor.

---

## 2. Estrutura e Cadência das Iterações

As iterações têm duração fixa de **duas semanas** (10 dias úteis), sincronizadas com o cronograma de 16 encontros da disciplina:

- **Encontros 4 a 5:** Descoberta e Especificação (Marco 1: Escopo e Requisitos)
- **Encontros 6 a 8 (Iteração 1):** Modelagem de domínio, arquitetura e prototipação navegável
- **Encontros 8 a 10 (Iteração 2):** Implementação da fatia vertical do MVP (Marco 2: Review Parcial no Encontro 9)
- **Encontros 11 a 13 (Iteração 3):** Qualidade, testes automatizados e segurança (Marco 3)
- **Encontros 14 a 16 (Iterações 4 e 5):** Implantação, manutenção evolutiva e encerramento (Marco 4: Review Final)

### 2.1 Eventos da Iteração

1. **Planejamento da Iteração (30 min - Segunda-feira inicial):**
   - Definição da meta verificável da iteração.
   - Cálculo da capacidade da equipe (pessoas equivalentes e pontos).
   - Seleção dos itens do topo do backlog ordenado.
   - Reserva de capacidade técnica (dívidas técnicas e preparação de demonstrações).
2. **Acompanhamento Diário:**
   - Registro assíncrono no canal da equipe com 3 tópicos: o que fiz, o que farei hoje e o que está bloqueado.
3. **Demonstração (Sexta-feira final):**
   - Apresentação do software rodando para colegas e/ou usuários, com roteiro estruturado.
4. **Retrospectiva com Evidências (15 min):**
   - Análise de dados reais do repositório (tempo de PRs, defeitos escapados).
   - Resposta a 3 perguntas essenciais:
     - *O que funcionou?*
     - *O que atrapalhou?*
     - *O que muda na próxima iteração?* (com dono e forma de conferir).

---

## 3. Papéis e Responsabilidades

Seguindo o princípio ágil de responsabilidades explícitas:

- **Priorização do Backlog (Product Owner):** Duda Negreiro (garante valor de negócio e alinhamento com usuários).
- **Arquitetura, Modelagem e Integridade Técnica:** Igor Oliveira (governança de contratos, consistência dos modelos e isolamento de Parnas).
- **Condução da Demonstração:** Rodízio entre os membros a cada iteração, registrado no quadro de tarefas.
- **Decisões Técnicas de Tarefa:** O integrante responsável pela tarefa, respeitando o [CONTRIBUTING.md](./CONTRIBUTING.md) e [PROJETO.md](./docs/PROJETO.md).

---

## 4. Definição de Pronto (Definition of Done - DoD)

Um item é considerado pronto quando:

1. Todos os critérios de aceitação foram verificados e aprovados por alguém que **não escreveu** o código do item.
2. O código está integrado ao ramo `main` por Pull Request revisado e aprovado.
3. A funcionalidade está acessível e testável no ambiente de demonstração local da equipe.
4. Os requisitos não funcionais aplicáveis ao item foram conferidos contra os valores aceitáveis.
5. A issue correspondente referencia a história de usuário, com a rastreabilidade da necessidade preservada.

---

## 5. Práticas de Engenharia Adotadas (Extreme Programming)

Com base no histórico e na necessidade de qualidade contínua:

- **Integração Frequente:** Ramos curtos (1 a 3 dias) integrados continuamente ao `main` para evitar conflitos volumosos.
- **Propriedade Coletiva do Código:** Alternância de revisores e responsáveis para evitar que apenas uma pessoa entenda determinada camada do sistema.
- **Revisão Sistemática por Lentes:** Avaliação por legibilidade, manutenibilidade e rastreabilidade conforme Capítulo 10.

---

## 6. Histórico de Revisão do Processo

- **2026-08-20:** Versão inicial do processo de desenvolvimento (Capítulo 3).
- **2026-10-21:** Ajuste na Definição de Pronto e inclusão das práticas de revisão e rastreabilidade (Capítulo 5 e 10).
