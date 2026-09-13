# Processo — EventFy

## Definição de Pronto (Definition of Done)

Um item do backlog é considerado **pronto** quando todos os critérios abaixo são atendidos:

1. **Requisitos**
   - A história de usuário possui critérios de aceitação registrados no `REQUISITOS.md`.
   - Os critérios de aceitação cobrem, no mínimo: caminho principal, um caminho de recusa/erro e o efeito persistente da ação.

2. **Implementação**
   - O código correspondente foi implementado em uma branch própria, seguindo o padrão de nomenclatura `feature/nome-da-funcionalidade`.
   - O código segue as convenções de estilo acordadas pela equipe (nomes descritivos, sem código comentado deixado por engano).

3. **Revisão**
   - A implementação foi submetida via pull request para a branch `main`.
   - O pull request foi revisado por, no mínimo, um outro membro da equipe.
   - Todos os comentários da revisão foram resolvidos antes do merge.

4. **Validação**
   - Os critérios de aceitação foram verificados manualmente (ou por teste automatizado, quando aplicável) antes do merge.
   - Requisitos não funcionais relacionados ao item (quando existirem) foram checados contra o valor aceitável definido.

5. **Documentação**
   - `REQUISITOS.md` está atualizado caso a implementação tenha gerado mudanças em relação ao que foi originalmente descrito.
   - Alterações de escopo identificadas durante a implementação são registradas na seção de registro de validação.

6. **Integração**
   - O merge para `main` foi realizado sem quebrar a build/execução do projeto.
   - A funcionalidade foi verificada em execução local após o merge.

---

## Fluxo de trabalho da equipe

1. Item selecionado do backlog (`REQUISITOS.md`, seção 2).
2. Criação de branch a partir da `main`.
3. Desenvolvimento + testes locais.
4. Abertura de pull request com descrição do que foi implementado e referência à história de usuário correspondente.
5. Revisão por outro(a) integrante da equipe.
6. Ajustes, se necessário.
7. Merge para `main` somente após aprovação e checklist de Definição de Pronto atendido.