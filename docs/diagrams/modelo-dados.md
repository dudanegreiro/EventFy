# Modelo de dados — EventFy

```mermaid
erDiagram
    USUARIO ||--o{ EVENTO : organiza
    USUARIO ||--o{ SERVICO : oferece
    SERVICO ||--o{ ARQUIVO : possui
    SERVICO ||--o{ DISPONIBILIDADE_SERVICO : possui
    EVENTO ||--o{ RESERVA : possui
    SERVICO ||--o{ RESERVA : recebe
    USUARIO ||--o{ RESERVA : solicita
    RESERVA ||--o| AVALIACAO : gera
    USUARIO ||--o{ AVALIACAO : realiza
    RESERVA ||--o{ HISTORICO_RESERVA : registra
    USUARIO ||--o{ HISTORICO_RESERVA : executa

    USUARIO {
        int id_usuario PK
        varchar nome
        varchar email UK
        varchar senha_hash
        varchar tipo_usuario
        boolean ativo
        datetime criado_em
        datetime atualizado_em
    }

    EVENTO {
        int id_evento PK
        int id_organizador FK
        varchar nome
        text descricao
        datetime data_inicio
        datetime data_fim
        varchar local
        boolean ativo
        datetime criado_em
        datetime atualizado_em
    }

    SERVICO {
        int id_servico PK
        int id_prestador FK
        varchar nome
        varchar categoria
        text descricao
        decimal preco
        boolean ativo
        datetime criado_em
        datetime atualizado_em
    }

    DISPONIBILIDADE_SERVICO {
        int id_disponibilidade PK
        int id_servico FK
        datetime data_inicio
        datetime data_fim
        varchar tipo
        varchar motivo
        boolean ativo
        datetime criado_em
    }

    ARQUIVO {
        int id_arquivo PK
        int id_servico FK
        varchar nome_original
        varchar url
        varchar tipo_mime
        bigint tamanho
        boolean ativo
        datetime criado_em
    }

    RESERVA {
        int id_reserva PK
        int id_evento FK
        int id_servico FK
        int id_solicitante FK
        varchar status
        datetime data_inicio
        datetime data_fim
        text observacao
        text motivo_recusa
        boolean ativo
        datetime criado_em
        datetime atualizado_em
    }

    HISTORICO_RESERVA {
        int id_historico PK
        int id_reserva FK
        int id_usuario FK
        varchar status_anterior
        varchar status_novo
        datetime data_hora
        text observacao
        text motivo
    }

    AVALIACAO {
        int id_avaliacao PK
        int id_reserva FK
        int id_avaliador FK
        int nota
        text comentario
        datetime criado_em
    }
```

## Observações de Modelagem e Consistência

- **Identidade técnica:** Todas as entidades possuem chaves primárias inteiras autoincrementais (`PK`), assegurando identidade única (RNF04).
- **Unicidade de credencial:** `USUARIO.email` possui restrição de unicidade (`UK`) para evitar contas duplicadas (RF01, D02).
- **Histórico e auditoria da reserva (RF18, RNF05):** A tabela `HISTORICO_RESERVA` armazena de forma imutável cada mudança de estado da reserva, preservando o estado anterior, novo estado, data/hora, observação/motivo e o usuário responsável (ou nulo quando a transição for disparada pelo sistema).
- **Estruturação de disponibilidade (Decisão DP02):** A coluna textual `disponibilidade` de `SERVICO` foi substituída pela tabela relacional `DISPONIBILIDADE_SERVICO`. Esta modelagem permite registrar múltiplos períodos de atendimento, bloqueios manuais pelo prestador e reservas confirmadas, viabilizando consultas eficientes por sobreposição de intervalos temporais e prevenindo conflitos (RN06, RNF02).
- **Exclusão lógica e consistência histórica (Seção 10 do PROJETO.md):** As tabelas `USUARIO`, `EVENTO`, `SERVICO`, `RESERVA`, `DISPONIBILIDADE_SERVICO` e `ARQUIVO` contam com a coluna `ativo` (`boolean`), garantindo que registros vinculados a contratações e históricos não sejam fisicamente excluídos, preservando a integridade referencial.
- **Tipagem temporal do Evento e Reserva (Seção 11 do PROJETO.md):** As colunas `data_inicio` e `data_fim` de `EVENTO` utilizam `datetime` (alinhando-se com `RESERVA` e permitindo granularidade de data e horário para reservas precisas de serviços).
- **Ciclo de vida e estados da reserva:** A coluna `RESERVA.status` reflete a máquina de estados oficial (`SOLICITADA`, `EM_ANALISE`, `APROVADA`, `CONFIRMADA`, `FINALIZADA`, `RECUSADA`, `CANCELADA`, `EXPIRADA`).
- **Motivo de recusa e cancelamento:** `RESERVA.motivo_recusa` é obrigatório quando o estado for `RECUSADA` (RN04) e é replicado no registro correspondente em `HISTORICO_RESERVA`.
- **Armazenamento de mídia (D07):** A tabela `ARQUIVO` armazena apenas metadados técnicos e a `url` do arquivo armazenado em storage externo seguro.
