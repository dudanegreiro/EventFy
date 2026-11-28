# EVT-08 - Review parcial executavel

Issue: #28. Baseline: commit `5e15fa1`, merge da PR #94. A tag `review-parcial-evt08-v2` aponta para o commit desta correcao; registre o SHA antes da demonstracao.

## Preparacao

1. Use Windows, Python 3.14, PostgreSQL 17 e `requirements-dev.txt`.
2. Confirme `git show -s --format=%H` e a tag da demonstracao.
3. Garanta que `psql` esteja no `PATH` e execute `scripts/restore-demo-data.ps1` com confirmacao.
4. Confira os estados das reservas:

   ```powershell
   psql -d eventfy_demo -c "SELECT status, count(*) FROM public.reserva GROUP BY status ORDER BY status;"
   ```

   Resultado esperado: uma reserva `APROVADA`, uma `FINALIZADA` e uma `SOLICITADA`.
5. Confirme a integridade do bloqueio:

   ```sql
   SELECT r.status, d.id_reserva
   FROM public.reserva r
   JOIN public.disponibilidade_servico d ON d.id_reserva = r.id_reserva
   WHERE r.status = 'APROVADA';
   ```

   A reserva aprovada deve possuir `id_reserva` no bloqueio ativo.

## Roteiro

| Passo | Evidencia | Criterio |
|---|---|---|
| Baseline | tag e SHA exibidos no terminal | Issue #28 |
| Restauracao | sucesso do script e tres estados no banco | fixtures reproduziveis |
| API | `/api/health` e `/docs` respondem | ambiente atual |
| Catalogo | prototipo navegavel | HU-05, RF05/RF06 |
| Solicitacao | fluxo chega a `SOLICITADA` | HU-01, RF10 |
| Analise | decisao chega a `APROVADA` ou `RECUSADA` | HU-02, RF12 |
| Confirmacao | reserva aprovada pode ser confirmada sem `MISSING_SCHEDULE_BLOCK` | HU-03, RF13, V5 |
| Historico | transicoes e justificativa sao visiveis | HU-04, RF16/RF18 |

## Repetibilidade e falha

Execute o script duas vezes seguidas. Cada execucao deve concluir sem erro de FK, recriar as fixtures e manter o vinculo entre a reserva aprovada e seu bloqueio. O script atua apenas em `eventfy_demo` ou `eventfy_demo_*`, exige confirmacao e usa transacao.

Se banco ou API falhar, registre o comando, erro, tentativa de recuperacao e resultado. Nao apresente o fallback gravado como evidencia de execucao ao vivo. Uma segunda maquina deve usar a mesma tag, SHA, versoes e fixtures.

## Limites

O prototipo estatico nao substitui a API, autenticacao, autorizacao, persistencia ou concorrencia reais. O roteiro demonstra o que foi executado e nao declara como concluida uma funcionalidade apenas simulada.
