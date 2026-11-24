## O que muda

<!-- Em 1 a 3 frases: o que mudou e por quê. -->

## Item de backlog

<!-- Um único item por PR. Troque pelo número da issue. -->
Closes #

Requisitos afetados: <!-- ex.: HU-02, RF01, RN02, RNF-05 -->

## Como testar

<!-- Passos que outra pessoa consiga repetir, com os comandos executados e o resultado obtido. -->

1.
2.

**Resultado esperado:**

## Antes de pedir a revisão (autor)

- [ ] Todos os critérios de aceitação da issue foram atendidos.
- [ ] O PR trata de um único item de backlog e pode ser revisado em 15 a 20 minutos.
- [ ] Os testes automatizados foram criados ou atualizados e passam localmente.
- [ ] Requisitos, regras de negócio, modelos, contrato da API (`docs/API.md`) e `CHANGELOG.md` afetados foram atualizados.
- [ ] Não há senha, chave, token nem dado pessoal real no código, nos testes ou nos dados de exemplo.
- [ ] Os requisitos não funcionais aplicáveis foram verificados.
- [ ] A funcionalidade pode ser demonstrada no ambiente local, quando aplicável.

## Revisão (revisor)

<!-- Marque cada lente conferida. Nos comentários, use [Bloqueia], [Sugere], [Pergunta] ou [Elogia] (CONTRIBUTING.md, seção 6). -->

- [ ] **Independência:** a conferência foi feita por alguém que não escreveu a mudança.
- [ ] **Item:** a mudança atende aos critérios de aceitação da issue, sem faltar nem sobrar.
- [ ] **Legibilidade:** os nomes seguem o glossário do domínio e o fluxo é entendido na primeira leitura.
- [ ] **Manutenibilidade:** a regra de negócio está no backend, sem duplicação, e trata os casos de zero, um e muitos.
- [ ] **Contrato:** rotas, respostas JSON e códigos de erro seguem `docs/API.md`.
- [ ] **Testes:** há testes para o caminho principal, para os erros e para os valores limite.
- [ ] **Segurança e dados:** o servidor confere papel e titularidade; não há segredo nem dado pessoal real.
- [ ] **Rastreabilidade:** o PR e os commits citam a issue e os requisitos.
- [ ] Todo defeito encontrado e não corrigido neste PR virou issue (rótulo `bug`) ou dívida técnica (rótulo `divida-tecnica`).
