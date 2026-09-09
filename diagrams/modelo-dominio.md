# Modelo de domínio — EventFy

O modelo de domínio abaixo relaciona as principais entidades do EventFy e os requisitos que justificam suas responsabilidades.

```mermaid
classDiagram
    class Usuario {
        +int id_usuario
        +string nome
        +string email
        +string senha_hash
        +TipoUsuario tipo_usuario
        +bool ativo
    }

    class Evento {
        +int id_evento
        +int id_organizador
        +string nome
        +string descricao
        +date data_inicio
        +date data_fim
        +string local
    }

    class Servico {
        +int id_servico
        +int id_prestador
        +string nome
        +string categoria
        +string descricao
        +decimal preco
        +string disponibilidade
        +bool ativo
    }

    class Arquivo {
        +int id_arquivo
        +int id_servico
        +string nome_original
        +string url
        +string tipo_mime
        +int tamanho
    }

    class Reserva {
        +int id_reserva
        +int id_evento
        +int id_servico
        +int id_solicitante
        +StatusReserva status
        +datetime data_inicio
        +datetime data_fim
        +string observacao
        +string motivo_recusa
    }

    class Avaliacao {
        +int id_avaliacao
        +int id_reserva
        +int id_avaliador
        +int nota
        +string comentario
    }

    Usuario "1" --> "0..*" Evento : organiza
    Usuario "1" --> "0..*" Servico : oferece
    Servico "1" --> "0..*" Arquivo : possui
    Evento "1" --> "0..*" Reserva : possui
    Servico "1" --> "0..*" Reserva : recebe
    Usuario "1" --> "0..*" Reserva : solicita
    Reserva "1" --> "0..1" Avaliacao : gera
    Usuario "1" --> "0..*" Avaliacao : realiza
```

## Rastreabilidade

- `Usuario` → RF01, RF02, RF03, RN01
- `Evento` → RF09, RF15, RN01
- `Servico` → RF04–RF08, RN06
- `Reserva` → RF09–RF16, RN02–RN07
- `Avaliacao` → RF17
- `Arquivo` → RF04, RF08, RN06
