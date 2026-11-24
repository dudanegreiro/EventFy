# 🎬 EVT-08 — Review parcial executável

> **Issue:** [#28 — EVT-08: Preparar review parcial executável](https://github.com/dudanegreiro/EventFy/issues/28)
>
> **Baseline de demonstração:** tag anotada `review-parcial-evt08`, criada sobre o commit que contém este roteiro e o script de restauração.

Este roteiro congela as instruções de ambiente, as fixtures do banco e a sequência de demonstração da fatia vertical descrita na Seção 9 de [`DESCOBERTA.md`](../DESCOBERTA.md): o organizador solicita, o prestador analisa e decide, e o organizador confirma. Ele separa o que é executável do que o protótipo apenas simula; não apresenta a interface como um sistema de reservas integrado.

## 1. Baseline e preparação

| Item | Baseline da review |
|---|---|
| Commit demonstrado | O commit apontado pela tag anotada `review-parcial-evt08`; registre o SHA na tabela de execução. |
| Sistema e ferramentas | Windows, Python 3.14 e PostgreSQL 17; dependências Python fixadas em [`dev/requirements.txt`](../dev/requirements.txt). |
| Interface demonstrada | Protótipo estático em `prototipo/`, servido pelo Uvicorn conforme a seção **Execução** do [`README.md`](../README.md). |
| Banco de demonstração | Banco local isolado `eventfy_demo`, criado e restaurado por [`scripts/restore-demo-data.ps1`](../scripts/restore-demo-data.ps1). |
| API executável | `GET /api/ambiente` consulta a versão do PostgreSQL; não implementa operações de catálogo ou reserva. |

Antes de apresentar:

1. Obtenha o código exatamente na tag `review-parcial-evt08` e confirme o commit com `git show -s --format=%H review-parcial-evt08`.
2. Inicie o serviço PostgreSQL 17 e verifique se `psql` e `createdb` estão no `PATH`.
3. Execute `.\scripts\restore-demo-data.ps1`. Confirme a operação quando o PowerShell solicitar; o script atua apenas em `eventfy_demo` ou em um nome de teste com prefixo `eventfy_demo_`.
4. Verifique as fixtures no banco:

   ```powershell
   psql -d eventfy_demo -c "SELECT status, count(*) FROM public.reserva GROUP BY status ORDER BY status;"
   ```

   O resultado esperado são três reservas: uma `APROVADA`, uma `FINALIZADA` e uma `SOLICITADA`.
5. Configure a URL local do banco no `.env` para apontar a `eventfy_demo`, inicie o Uvicorn conforme o README e confira `http://127.0.0.1:8000/api/ambiente`. A resposta deve indicar `EventFy` e PostgreSQL `17.x`.
6. Abra `http://127.0.0.1:8000/`. Use dados fictícios apenas; não inclua credenciais ou informações pessoais reais na demonstração.

Para repetir a apresentação, execute novamente o script de restauração. Ele confirma a migração de esquema e substitui, em uma transação, o conteúdo das tabelas de demonstração. Não use `-Confirm:$false` durante uma apresentação manual.

## 2. Roteiro da demonstração

Siga os passos na ordem. A coluna **Tela/evidência** identifica o que deve estar visível; **Critério** liga cada passo ao backlog e aos requisitos. Registre o resultado real na tabela da Seção 5, sem marcar uma etapa como aprovada se não tiver sido executada.

| Passo | Ação de demonstração | Tela / evidência observável | Critério relacionado |
|---|---|---|---|
| 1. Baseline | Mostrar a tag e o SHA do commit em execução. | Terminal: saída de `git show -s --format=%H review-parcial-evt08`. | Issue #28: commit demonstrado possui tag anotada. |
| 2. Dados | Restaurar as fixtures; consultar a contagem por estado. | Terminal: sucesso do script e três estados no banco. | Issue #28: script restaura dados de demonstração; fixtures de `db/migrations/V2__seed_demo_data.sql`. |
| 3. Ambiente | Consultar `GET /api/ambiente`. | Navegador em `/api/ambiente`, com aplicação e versão do PostgreSQL. | Issue #28: ambiente congelado e demonstrável; diagnóstico descrito em `ARQUITETURA.md`. |
| 4. Catálogo | Partir da página inicial, abrir o catálogo e localizar um serviço adequado. | `prototipo/index.html`, `catalogo.html` e `servico.html`; os serviços desta tela são fixtures JavaScript. | HU-05, RF05/RF06 (a especificação não traz CA específico para HU-05); filtro por data, preço e localização não é demonstrado. |
| 5. Solicitação | Para uma festa de aniversário, preencher o serviço, evento e um período futuro e enviar o pedido. | `reserva.html` seguido do resumo `solicitada.html`, com estado `SOLICITADA`. | HU-01, RF10, CA-01.1. |
| 6. Análise | Acionar a transição de demonstração e aprovar o pedido como prestador. | `em-analise.html` e `aprovada.html`; o prestador e sua decisão são simulados. | HU-02, RF12, CA-02.1. A fila real do prestador (RF11) não é demonstrada. |
| 7. Confirmação | Confirmar a contratação aprovada. | `confirmada.html`, com estado `CONFIRMADA`. | HU-03, RF13, CA-03.1. |
| 8. Histórico | Abrir e percorrer os registros da solicitação. | `historico.html`, com estados, ator, data/hora e justificativa quando aplicável. | HU-04, RF16, RF18, CA-04.1. O histórico é transportado na URL, não persistido no servidor. |

**Ramos opcionais, se houver tempo:** refazer o fluxo para demonstrar recusa e justificativa em `em-analise.html` → `recusada.html` (HU-02, RF12, CA-02.2–CA-02.4), ou cancelar uma solicitação confirmada em `confirmada.html` → `cancelar.html` → `cancelada.html` (RF14, RN09). O critério CA-02.2 exige justificativa com pelo menos 10 caracteres; o protótipo atual só bloqueia justificativa vazia, portanto não declare esse limite validado.

## 3. Limitações e elementos simulados

- O catálogo, o formulário, as transições e o histórico são telas estáticas com dados de demonstração mantidos entre páginas pela URL.
- O botão **Simular início da análise** e as decisões de aprovação/recusa não chamam uma fila nem um usuário real do papel de prestador.
- O formulário não autentica um organizador, verifica a disponibilidade real do serviço ou persiste uma solicitação; CA-01.1 é demonstrado somente como sequência visual.
- A aplicação FastAPI oferece somente `GET /api/ambiente`; o catálogo, as reservas e o histórico não consomem a API.
- O banco `eventfy_demo` e o protótipo são demonstrações separadas. A fixture SQL contém buffet, enquanto o catálogo estático apresenta som e iluminação, espaço e equipe de apoio.
- Não há login, autorização de papéis, persistência de reservas feitas no navegador, agenda concorrente, notificações nem auditoria real na interface.
- O script restaura apenas os dados sintéticos da base isolada; não cria anexos binários reais. A URL do anexo na fixture é fictícia.
- Busca por preço, localização e disponibilidade por data não está implementada no catálogo. A justificativa de recusa não aplica o mínimo de 10 caracteres do CA-02.2.

Estas limitações não devem ser apresentadas como funcionalidades concluídas. Um resultado visual do protótipo não comprova persistência, autorização ou execução de uma operação de negócio no backend.

## 4. Plano de falha

### Antes da apresentação

- Restaurar as fixtures e executar a consulta da Seção 1.
- Confirmar o SHA da tag, a resposta de `/api/ambiente` e a abertura da página inicial.
- Preparar uma segunda máquina com a mesma tag, versões de Python/PostgreSQL, dependências instaladas, `.env` configurado localmente e acesso ao PostgreSQL. Não copie credenciais entre máquinas.
- Manter capturas ou uma gravação local do fluxo da mesma tag como último recurso. A gravação é evidência de interface, não substitui uma demonstração ao vivo nem a consulta ao banco.

### Se algo falhar durante a apresentação

1. **Interface ou Uvicorn indisponível:** interromper a etapa, reiniciar o servidor com o comando do README e tentar uma vez. Registrar o erro e o resultado da nova tentativa.
2. **Banco ou `/api/ambiente` indisponível:** verificar o serviço PostgreSQL e a URL no `.env`; depois de restabelecer a conexão, executar novamente o script de restauração e repetir a consulta. Não afirmar que a API está conectada se retornar HTTP 503.
3. **Máquina principal indisponível:** continuar na segunda máquina somente após confirmar a mesma tag/SHA e restaurar suas fixtures.
4. **Demonstração ao vivo não recuperável:** mostrar a gravação/capturas como fallback, declarar que se trata de registro anterior e marcar as etapas de execução ao vivo como não realizadas. Não substituir silenciosamente o resultado.

### Registro da execução

| Data | Apresentador / observador | Máquina e versões | Tag e SHA | Resultado da restauração | Passos executados / evidências | Falha, recuperação ou desvio | Resultado final |
|---|---|---|---|---|---|---|---|
| A preencher após a demonstração | A preencher | A preencher | `review-parcial-evt08` / SHA a preencher | Pendente | Pendente | Nenhum registrado / descrever | Pendente |

## 5. Conferência dos critérios da issue

| Critério de aceite #28 | Evidência neste repositório |
|---|---|
| Script restaura dados de demonstração. | `scripts/restore-demo-data.ps1`, com confirmação e banco isolado. |
| Commit demonstrado possui tag anotada. | Tag `review-parcial-evt08`; confirme com `git cat-file -t review-parcial-evt08` (resultado esperado: `tag`). |
| Roteiro liga passo, tela e critério. | Tabela da Seção 2. |
| Limitações e elementos simulados declarados. | Seção 3. |
| Plano de falha documentado. | Seção 4, incluindo reinício, segunda máquina, fallback e registro da execução. |

O documento prepara a demonstração. Preencha o registro da execução somente após ensaiar ou apresentar o fluxo; não há resultados de demonstração registrados antecipadamente.
