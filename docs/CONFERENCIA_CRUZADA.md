# Conferência cruzada — Entrega Incremental 6.14

## Objetivo

Registrar a conferência dos artefatos produzidos para a entrega incremental. Cada artefato deve ser revisado por uma pessoa diferente de quem o produziu.

## Checklist

### Requisitos
- [ ] Todos os requisitos possuem identificador.
- [ ] Requisitos estão claros e testáveis.
- [ ] Regras de negócio estão separadas dos requisitos funcionais.
- [ ] Lacunas descobertas pela modelagem foram incorporadas.

### Modelo de domínio
- [ ] Todas as entidades importantes estão representadas.
- [ ] Relacionamentos possuem cardinalidades coerentes.
- [ ] Cada classe possui rastreabilidade para requisitos.

### Modelo de dados
- [ ] Todas as entidades persistentes possuem chave primária.
- [ ] Chaves estrangeiras correspondem às relações do domínio.
- [ ] Campos de data/hora estão tipados.
- [ ] Arquivos possuem estratégia de armazenamento definida.

### Estados
- [x] O objeto central está definido (Reserva).
- [x] Todas as transições principais estão representadas.
- [x] Todo estado é alcançável e possui saída válida (sem deadlocks).
- [x] Cancelamento a partir de SOLICITADA, EM_ANALISE, APROVADA e CONFIRMADA.
- [x] Expiração por inatividade/SLA representada (EXPIRADA).
- [x] Executor da finalização definido (rotina automática do Sistema após data_fim).
- [x] O motivo da recusa é preservado obrigatoriamente.

### Diagrama de sequência
- [x] Fluxo principal detalhado ponta a ponta (solicitação, análise, aprovação, confirmação, finalização).
- [x] Fluxos alternativos contemplados (recusa com motivo, conflito de agenda, cancelamento e expiração).
- [x] Interação com componentes lógicos, serviço de disponibilidade e histórico de auditoria.

### Protótipo
- [ ] O fluxo principal é navegável.
- [ ] Existe tela de detalhes.
- [ ] Existe solicitação.
- [ ] Existe aprovação.
- [ ] Existe recusa.
- [ ] A tela de recusa apresenta o motivo.
- [ ] Os links de retorno funcionam.

## Registro da revisão

| Data | Artefato | Autor | Revisor | Correção solicitada | Correção realizada | Aprovação |
|---|---|---|---|---|---|---|
| 21/10/2026 | REQUISITOS.md | Equipe | Pessoa 3 | Alinhamento de RN05 e critérios de aceitação | Atualizada RN05 e RF14 | ☑ |
| 21/10/2026 | PROJETO.md | Igor (Pessoa 4) | Pessoa 3 | Fichas CRC, Parnas, substantivos, rastreabilidade | Consolidado nas seções 6, 7, 10, 13, 15, 16 | ☑ |
| 21/10/2026 | Modelo de domínio | Igor (Pessoa 4) | Pessoa 3 | DisponibilidadeServico, ativo, estados | Inclusão de agenda e auditoria | ☑ |
| 21/10/2026 | Modelo de dados | Igor (Pessoa 4) | Pessoa 3 | HISTORICO_RESERVA, DISPONIBILIDADE, ativo, DATETIME | Atualizado diagrama ER e observações | ☑ |
| 21/10/2026 | Estados da reserva | Igor (Pessoa 4) | Pessoa 3 | Cancelamentos amplos, expiração, finalização | Atualizado diagrama e matriz de estados | ☑ |
| 21/10/2026 | Sequência da reserva | Igor (Pessoa 4) | Pessoa 3 | Fluxo principal e 4 alternativos | Criado diagrams/sequencia-reserva.md | ☑ |
| 21/10/2026 | Processos de negócio | Equipe / Igor (Pessoa 4) | Pessoa 3 | Reconciliar RF19-29 e RN08-15 inexistentes | docs/PROCESSOS-NEGOCIO.md 100% alinhado | ☑ |
| 21/10/2026 | Protótipo | Pessoa 5 | Pessoa 4 | Correspondência de telas com requisitos | Telas navegáveis validadas | ☐ |

