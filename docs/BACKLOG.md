# Backlog de Execucao — EventFy

Este backlog organiza as lacunas encontradas ao comparar os capitulos 1 a 10 da disciplina com o estado atual do repositório. Ele complementa `docs/REQUISITOS.md` e deve ser convertido em issues do GitHub no início da próxima iteração.

## Responsáveis sugeridos

| Integrante | Área principal | Responsabilidade no backlog |
|---|---|---|
| Eduarda Negreiro (@dudanegreiro) | Produto e requisitos | Priorização, validação com usuário, rastreabilidade e aceite |
| Gustavo Leite Bringel (@GustavoBringel) | Dados e backend | Banco, API, regras de domínio e persistência |
| Igor Anicezio Oliveira (@IgorAnicezioOliveira) | Arquitetura e integração | Arquitetura, decisões técnicas, consistência dos modelos e integrações |
| Thalita Teixeira Menezes (@thalist) | Processos e qualidade | Processos, auditoria, testes de qualidade e evidências de iteração |
| José Guilherme Costa Oliveira (@ZezinG14) | Interface e experiência | Telas, responsividade, protótipo executável e integração com API |

## Estado atual e lacunas

O repositório já possui requisitos, descoberta, processo, modelo de domínio, modelo de dados, estados, processos de negócio, protótipo navegável, rastreabilidade e conferência cruzada.

O que ainda falta para um sistema web completo:

- implementar frontend e backend;
- definir e documentar tecnologias e versões;
- criar esquema, migrações e dados de demonstração;
- implementar autenticação e autorização por papel;
- transformar o fluxo estático em API REST persistente;
- implementar testes automatizados e integração contínua;
- criar ambiente executável com instruções reais;
- preparar a review parcial com ambiente congelado e roteiro;
- registrar a qualidade do processo e da revisão de código com evidências;
- corrigir divergências futuras entre requisitos, modelos e código por conferência contínua.

Nenhuma issue aberta foi encontrada no GitHub no momento da organização deste backlog.

## Issues detalhadas criadas no GitHub

O backlog principal foi decomposto em issues pequenas. A criação atual cobre os capítulos 1 a 16 e distribui o trabalho entre todos os integrantes.

| Faixa | Issues | Conteúdo |
|---|---|---|
| Arquitetura e implementação central | #21–#32 | Tecnologias, banco, API, autenticação, catálogo, estados, frontend, review parcial, testes iniciais e documentação |
| Funcionalidades verticais menores | #33–#41 | Contas, eventos, fila, cancelamento, histórico, avaliação, anexos, administração e expiração |
| Verificação, qualidade e segurança | #42–#52 | Inspeção, casos de teste, validação externa, testes automatizados, CI local, segredos, dependências, autorização, entrada não confiável e LGPD |
| Implantação e operação | #53–#59 | Ambientes, plataforma, deploy, rollback, health check, jobs e manual de operação |
| Manutenção e evolução | #60–#63 | Evolução do prazo, implementação adaptativa, refatoração e pagamento da dívida técnica |
| Review final | #64–#68 | Changelog, versão v1.0.0, demonstração, matriz de escopo, retrospectiva e documentação de encerramento |

## Quadro sugerido

| Coluna | Conteúdo |
|---|---|
| `Backlog` | issues não refinadas ou dependentes de decisão |
| `Ready` | issue refinada, estimada e com critérios de aceitação |
| `In Progress` | issue em ramo curto e Pull Request não integrado |
| `Review` | Pull Request aguardando aprovação por integrante diferente do autor |
| `Done` | código ou artefato integrado ao `main` e confirmado pela Definition of Done |

Marcos sugeridos:

- **Marco 1 — Escopo e requisitos:** já concluído nos artefatos existentes.
- **Marco 2 — Review parcial:** issues `EVT-01` a `EVT-08`.
- **Marco 3 — Qualidade verificada:** issues `EVT-09` a `EVT-12`.
- **Marco 4 — Review final:** itens de implantação e evolução serão criados após a revisão parcial.

## Issues prontas para criação

### EVT-01 — Definir tecnologia, arquitetura executável e ambiente local

- **Responsável:** Igor
- **Apoio:** Gustavo e José
- **Prioridade:** P0
- **Estimativa:** 5 pontos
- **Marco:** Review parcial
- **Labels:** `architecture`, `setup`, `P0`

**Descrição**

Escolher tecnologias concretas para frontend, backend, banco de dados, autenticação, testes e armazenamento de arquivos. Registrar as versões e decisões em `ARQUITETURA.md` e remover o status de tecnologia indefinida do README.

**Critérios de aceitação**

- [ ] Frontend, backend e banco possuem tecnologias e versões documentadas.
- [ ] Existe diagrama das quatro vistas relevantes: lógica, desenvolvimento, processos e implantação.
- [ ] O monólito modular ou arquitetura escolhida está justificando as alternativas descartadas.
- [ ] Existe ADR para pelo menos banco, armazenamento e autenticação.
- [ ] Um novo colaborador consegue iniciar o projeto a partir do README.

### EVT-02 — Criar banco de dados, migrações e dados de demonstração

- **Responsável:** Gustavo
- **Apoio:** Igor
- **Prioridade:** P0
- **Estimativa:** 8 pontos
- **Marco:** Review parcial
- **Labels:** `backend`, `database`, `P0`

**Descrição**

Implementar o modelo relacional consistente com `docs/diagrams/dados.mmd` e `docs/PROJETO.md`, incluindo migrações e seed data.

**Critérios de aceitação**

- [ ] Todas as entidades principais possuem tabelas e restrições.
- [ ] Chaves estrangeiras e exclusão lógica são aplicadas.
- [ ] Existem dados mínimos para execução e demonstração.
- [ ] A criação do banco é reproduzível por comando.
- [ ] Migrações são versionadas e reversíveis ou compatíveis com a prática adotada.

### EVT-03 — Implementar API REST e contrato do fluxo principal

- **Responsável:** Gustavo
- **Apoio:** Igor e José
- **Prioridade:** P0
- **Estimativa:** 8 pontos
- **Marco:** Review parcial
- **Labels:** `backend`, `api`, `P0`

**Descrição**

Implementar o contrato cliente-servidor necessário para catálogo, eventos, solicitações, análise e confirmação.

**Critérios de aceitação**

- [ ] Operações REST usam recursos coerentes com o domínio.
- [ ] Respostas JSON e códigos HTTP estão definidos em contrato.
- [ ] Erros de validação e autorização possuem formato consistente.
- [ ] O servidor valida todas as regras críticas independentemente do frontend.
- [ ] Contrato de API cobre HU-01, HU-02, HU-03 e HU-04.

### EVT-04 — Implementar autenticação e autorização por papel

- **Responsável:** Gustavo
- **Apoio:** Igor
- **Prioridade:** P0
- **Estimativa:** 5 pontos
- **Marco:** Review parcial
- **Labels:** `security`, `backend`, `P0`

**Descrição**

Implementar cadastro, login, logout, hash de senha e controle de acesso por organizador, prestador e administrador.

**Critérios de aceitação**

- [ ] Senhas não são persistidas em texto puro.
- [ ] Operações recusam usuários sem papel ou propriedade correta com 403.
- [ ] Usuários inativos não podem operar.
- [ ] O administrador não pode alterar reservas alheias.
- [ ] Existem testes cobrindo os principais pares operação/papel.

### EVT-05 — Implementar catálogo, filtros e gerenciamento de serviços

- **Responsável:** Gustavo
- **Apoio:** José
- **Prioridade:** P0
- **Estimativa:** 8 pontos
- **Marco:** Review parcial
- **Labels:** `feature`, `backend`, `frontend`

**Descrição**

Implementar cadastro e consulta de serviços com categoria, preço, localização, disponibilidade e anexos permitidos.

**Critérios de aceitação**

- [ ] Somente o prestador titular altera seu serviço.
- [ ] Dados críticos ficam protegidos enquanto houver reserva ativa.
- [ ] Busca com 200 serviços atende RNF-03.
- [ ] Tipos MIME e tamanho máximo são validados.
- [ ] A interface mostra estados vazios e erros de validação.

### EVT-06 — Implementar máquina de estados e disponibilidade concorrente

- **Responsável:** Gustavo
- **Apoio:** Igor e Thalita
- **Prioridade:** P0
- **Estimativa:** 8 pontos
- **Marco:** Review parcial
- **Labels:** `domain`, `concurrency`, `P0`

**Descrição**

Implementar solicitações, pré-bloqueio, aprovação, recusa, confirmação, cancelamento, expiração e liberação da agenda.

**Critérios de aceitação**

- [ ] Apenas transições documentadas são permitidas.
- [ ] Motivo obrigatório é aplicado em recusa e cancelamento.
- [ ] Duas confirmações concorrentes não produzem conflito na agenda.
- [ ] Cada transição gera uma linha imutável em `HISTORICO_RESERVA`.
- [ ] Integração testa os fluxos principal e alternativos.

### EVT-07 — Implementar eventos e solicitações no frontend

- **Responsável:** José
- **Apoio:** Gustavo e Eduarda
- **Prioridade:** P0
- **Estimativa:** 8 pontos
- **Marco:** Review parcial
- **Labels:** `frontend`, `feature`, `P0`

**Descrição**

Conectar o protótipo navegável à API, preservando o fluxo principal e tornando os dados persistentes.

**Critérios de aceitação**

- [ ] Organizador cria evento e solicita reserva.
- [ ] Prestador visualiza, aprova ou recusa uma solicitação.
- [ ] Organizador confirma uma reserva aprovada.
- [ ] Histórico e estados são exibidos a partir da API.
- [ ] Fluxos principais funcionam em viewport de 360 × 640 px.

### EVT-08 — Preparar revisão parcial executável

- **Responsável:** Eduarda
- **Apoio:** José, Igor e Thalita
- **Prioridade:** P0
- **Estimativa:** 3 pontos
- **Marco:** Review parcial
- **Labels:** `review`, `demo`, `P0`

**Descrição**

Congelar um ambiente local, dados fictícios e roteiro para demonstrar o fluxo principal conforme o capítulo 9.

**Critérios de aceitação**

- [ ] Existe script para restaurar os dados de demonstração.
- [ ] Existe tag anotada do commit demonstrado.
- [ ] Roteiro liga ação, tela e critério de aceitação.
- [ ] Limitações e elementos simulados são declarados.
- [ ] Plano de falha contempla reinício, segunda máquina e registro da execução.

### EVT-09 — Automatizar testes unitários e de integração

- **Responsável:** Thalita
- **Apoio:** Gustavo e Igor
- **Prioridade:** P1
- **Estimativa:** 8 pontos
- **Marco:** Qualidade verificada
- **Labels:** `tests`, `quality`, `P1`

**Descrição**

Criar a suíte mínima para regras críticas do domínio e integrações da API.

**Critérios de aceitação**

- [ ] Conflitos de agenda são testados com concorrência.
- [ ] Autorização cobre papéis e recursos alheios.
- [ ] Transições de estado são testadas em caminho principal e recusa.
- [ ] Auditoria é testada junto a cada transição.
- [ ] Comandos de teste estão documentados no README.

### EVT-10 — Configurar integração contínua e proteção do main

- **Responsável:** Igor
- **Apoio:** Thalita
- **Prioridade:** P1
- **Estimativa:** 5 pontos
- **Marco:** Qualidade verificada
- **Labels:** `ci`, `devops`, `P1`

**Descrição**

Executar testes e verificações em toda contribuição antes da integração.

**Critérios de aceitação**

- [ ] Push e Pull Request executam o pipeline.
- [ ] Testes e build precisam passar antes do merge.
- [ ] O `main` exige revisão de outro integrante.
- [ ] Ramos não protegidos não podem ser usados como caminho de entrega.
- [ ] Falhas de pipeline são visíveis no Pull Request.

### EVT-11 — Implantar checklist de revisão e evidências de qualidade

- **Responsável:** Thalita
- **Apoio:** todos
- **Prioridade:** P1
- **Estimativa:** 5 pontos
- **Marco:** Qualidade verificada
- **Labels:** `quality`, `process`, `P1`

**Descrição**

Aplicar revisão por legibilidade, manutenibilidade e rastreabilidade e medir aderência e eficácia.

**Critérios de aceitação**

- [ ] Template de PR exige critérios de aceitação, testes e rastreabilidade.
- [ ] Comentários usam [Bloqueia], [Sugere], [Pergunta] ou [Elogia].
- [ ] Cada defeito encontrado gera issue ou dívida técnica registrada.
- [ ] O processo registra aderência e eficácia por iteração em `ITERACOES.md`.
- [ ] Dívidas técnicas possuem estimativa e vínculo com o backlog.

### EVT-12 — Completar documentação de operação e linha de base

- **Responsável:** Eduarda
- **Apoio:** Igor e Thalita
- **Prioridade:** P1
- **Estimativa:** 5 pontos
- **Marco:** Qualidade verificada
- **Labels:** `documentation`, `operations`, `P1`

**Descrição**

Atualizar README, changelog e documentação de entrega para o sistema que efetivamente está implementado.

**Critérios de aceitação**

- [ ] Pré-requisitos e versões são explicitados.
- [ ] Comandos de instalação, migração, testes e execução estão disponíveis.
- [ ] Variáveis de ambiente são documentadas sem revelar segredos.
- [ ] Changelog identifica baseline demonstrada.
- [ ] Arquitetura, requisitos e código passam por conferência cruzada atualizada.

## Dependências

```text
EVT-01 -> EVT-02 -> EVT-03 -> EVT-04
EVT-02 -> EVT-06 -> EVT-07
EVT-01 -> EVT-10
EVT-03 -> EVT-09
EVT-07 -> EVT-08
EVT-09 -> EVT-10
EVT-08 -> EVT-11
EVT-11 -> EVT-12
```

## Política de distribuição

Nenhum integrante deve acumular todos os itens críticos de uma iteração. As tarefas de integração devem ter revisor diferente do autor e o responsável pela arquitetura não pode aprovar sozinho todas as decisões.
