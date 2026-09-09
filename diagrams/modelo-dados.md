# Modelo de dados — EventFy

```mermaid
erDiagram
    USUARIO ||--o{ EVENTO : organiza
    USUARIO ||--o{ SERVICO : oferece
    SERVICO ||--o{ ARQUIVO : possui
    EVENTO ||--o{ RESERVA : possui
    SERVICO ||--o{ RESERVA : recebe
    USUARIO ||--o{ RESERVA : solicita
    RESERVA ||--o| AVALIACAO : gera
    USUARIO ||--o{ AVALIACAO : realiza

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
        date data_inicio
        date data_fim
        varchar local
        datetime criado_em
    }

    SERVICO {
        int id_servico PK
        int id_prestador FK
        varchar nome
        varchar categoria
        text descricao
        decimal preco
        varchar disponibilidade
        boolean ativo
        datetime criado_em
        datetime atualizado_em
    }

    ARQUIVO {
        int id_arquivo PK
        int id_servico FK
        varchar nome_original
        varchar url
        varchar tipo_mime
        bigint tamanho
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
        datetime criado_em
        datetime atualizado_em
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

## Observações

- As chaves primárias garantem identidade técnica.
- `USUARIO.email` deve possuir restrição de unicidade.
- `RESERVA.status` representa o ciclo de vida definido no diagrama de estados.
- `RESERVA.motivo_recusa` é preenchido quando o estado for `RECUSADA`.
- `ARQUIVO.url` referencia o armazenamento do arquivo.
