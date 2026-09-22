# PROJETO — Entrega Incremental 6.14 — EventFy

## 1. Identificação

**Projeto:** EventFy  
**Disciplina:** Engenharia de Software  
**Instituição:** Universidade Federal do Tocantins (UFT) — Câmpus Palmas  
**Objetivo da entrega:** consolidar a modelagem, decisões de projeto, rastreabilidade de requisitos e protótipo navegável.

O README público do projeto descreve o EventFy como uma plataforma web para conectar organizadores de eventos a prestadores de serviços e fornecedores de infraestrutura, centralizando catálogo, busca, contratação e gestão de reservas.

## 2. Escopo da entrega

Esta entrega consolida:

1. modelo de domínio;
2. rastreabilidade entre classes e requisitos;
3. modelo de dados derivado;
4. decisões de identidade;
5. decisões de apagamento;
6. representação de tempo;
7. armazenamento de arquivos;
8. diagrama de estados da reserva;
9. lacunas de requisitos encontradas pela modelagem;
10. distribuição de responsabilidades;
11. decisões de projeto;
12. conferência cruzada;
13. protótipo navegável do fluxo principal, incluindo recusa.

## 3. Modelo de domínio

As entidades centrais são:

- `Usuario`: representa organizadores e prestadores/fornecedores.
- `Evento`: representa o evento para o qual serviços/estruturas são necessários.
- `Servico`: representa um serviço ou estrutura disponibilizado no catálogo.
- `Reserva`: representa a solicitação/contratação de um serviço para um evento.
- `Avaliacao`: representa avaliação após uma contratação, quando habilitada.
- `Arquivo`: representa a referência de arquivos associados a serviços.

### 3.1 Rastreabilidade

| Classe | Requisitos que justificam a classe |
|---|---|
| Usuario | RF01, RF02, RF03, RN01 |
| Evento | RF09, RF15, RN01 |
| Servico | RF04, RF05, RF06, RF07, RF08, RN06 |
| Reserva | RF09, RF10, RF11, RF12, RF13, RF14, RF15, RF16, RN02–RN07 |
| Avaliacao | RF17 |
| Arquivo | RF04, RF08, RN06 |

O diagrama completo está em `diagrams/modelo-dominio.md`.

## 4. Modelo de dados derivado

O modelo relacional proposto contém:

### USUARIO
- `id_usuario` — PK
- `nome`
- `email` — único
- `senha_hash`
- `tipo_usuario`
- `ativo`
- `criado_em`
- `atualizado_em`

### EVENTO
- `id_evento` — PK
- `id_organizador` — FK → USUARIO
- `nome`
- `descricao`
- `data_inicio`
- `data_fim`
- `local`
- `criado_em`

### SERVICO
- `id_servico` — PK
- `id_prestador` — FK → USUARIO
- `nome`
- `categoria`
- `descricao`
- `preco`
- `disponibilidade`
- `ativo`
- `criado_em`
- `atualizado_em`

### ARQUIVO
- `id_arquivo` — PK
- `id_servico` — FK → SERVICO
- `nome_original`
- `url`
- `tipo_mime`
- `tamanho`
- `criado_em`

### RESERVA
- `id_reserva` — PK
- `id_evento` — FK → EVENTO
- `id_servico` — FK → SERVICO
- `id_solicitante` — FK → USUARIO
- `status`
- `data_inicio`
- `data_fim`
- `observacao`
- `motivo_recusa`
- `criado_em`
- `atualizado_em`

### AVALIACAO
- `id_avaliacao` — PK
- `id_reserva` — FK → RESERVA
- `id_avaliador` — FK → USUARIO
- `nota`
- `comentario`
- `criado_em`

O diagrama está em `diagrams/modelo-dados.md`.

## 5. Decisões de identidade

| Entidade | Identificador | Decisão |
|---|---|---|
| Usuario | `id_usuario` | Chave primária única |
| Evento | `id_evento` | Chave primária única |
| Servico | `id_servico` | Chave primária única |
| Arquivo | `id_arquivo` | Chave primária única |
| Reserva | `id_reserva` | Chave primária única |
| Avaliacao | `id_avaliacao` | Chave primária única |

Além da chave técnica, `Usuario.email` deverá ser único.

## 6. Decisões de apagamento

### Usuários
Não deverão ser apagados fisicamente quando possuírem histórico relevante. A opção preferencial é desativação lógica com `ativo = false`.

### Serviços
Um serviço que já participou de reservas deverá ser desativado em vez de ter seu histórico destruído.

### Reservas
Reservas não deverão ser apagadas fisicamente após possuírem histórico. O registro deverá permanecer para rastreabilidade.

### Arquivos
Arquivos sem referência poderão ser removidos conforme política de manutenção. Arquivos necessários para preservar histórico deverão permanecer disponíveis.

## 7. Representação de tempo

A decisão é separar data e hora quando o domínio exigir essa distinção.

- `DATE`: datas sem horário.
- `TIME`: horário isolado, quando necessário.
- `DATETIME`/equivalente: criação e atualização de registros.
- Para reservas, recomenda-se registrar início e fim.

O sistema não deverá armazenar datas e horários como texto livre.

## 8. Armazenamento de arquivos

Imagens de serviços e estruturas serão armazenadas em armazenamento de arquivos/servidor, enquanto o banco manterá apenas seus metadados e referência:

`url`, `nome_original`, `tipo_mime`, `tamanho`.

Essa decisão reduz o acoplamento do banco ao conteúdo binário dos arquivos e facilita sua entrega ao frontend.

## 9. Diagrama de estados do objeto central

O objeto central escolhido é `Reserva`, pois concentra o fluxo de solicitação e contratação.

Estados:

`SOLICITADA → EM ANÁLISE → APROVADA → CONFIRMADA → FINALIZADA`

Fluxo alternativo:

`EM ANÁLISE → RECUSADA`

Fluxo de cancelamento:

`CONFIRMADA → CANCELADA`

Uma recusa exige motivo registrado. O diagrama completo está em `diagrams/estados-reserva.md`.

## 10. Distribuição de responsabilidades

| Responsabilidade | Papel principal | Apoio |
|---|---|---|
| Levantamento e revisão de requisitos | Equipe | Todos |
| Modelo de domínio | Equipe de modelagem | Todos |
| Modelo de dados | Responsável por dados | Equipe |
| Diagrama de estados | Responsável por modelagem | Equipe |
| Protótipo navegável | Responsável por interface | Equipe |
| Conferência cruzada | Revisor diferente do autor | Equipe |
| Integração por PR | Autor da alteração | Revisor |

### 10.1 Equipe registrada no README

- Eduarda Negreiro
- Gustavo Leite Bringel
- Igor Anicezio Oliveira
- Thalita Teixeira Menezes
- José Guilherme Costa Oliveira

## 11. Tabela de decisões do projeto

| ID | Decisão | Motivo | Consequência aceita |
|---|---|---|---|
| D01 | Identificadores próprios para entidades | Evitar ambiguidade | Cada entidade possui PK |
| D02 | E-mail único para usuário | Evitar duplicidade de conta | Restrição de unicidade |
| D03 | Exclusão lógica para registros históricos | Preservar rastreabilidade | Registros permanecem no banco |
| D04 | Reserva com estados | Representar ciclo de contratação | Campo `status` e regras de transição |
| D05 | Motivo obrigatório na recusa | Dar transparência ao solicitante | Campo `motivo_recusa` |
| D06 | Data/hora em tipos próprios | Evitar inconsistências | Campos temporais estruturados |
| D07 | Arquivo externo + URL no banco | Evitar BLOB desnecessário | Banco guarda metadados |
| D08 | Histórico de reserva preservado | Auditoria e rastreabilidade | Não apagar fisicamente reservas |

## 12. Conferência cruzada

A conferência cruzada deve ser realizada por integrante diferente do autor do artefato.

| Artefato | Autor | Revisor | Verificações | Resultado |
|---|---|---|---|---|
| REQUISITOS.md | Equipe | Integrante diferente do autor | IDs, regras e lacunas | A realizar pela equipe |
| Modelo de domínio | Equipe de modelagem | Integrante diferente do autor | Classes, relações e rastreabilidade | A realizar |
| Modelo de dados | Responsável por dados | Integrante diferente do autor | PK, FK e cardinalidade | A realizar |
| Estados da reserva | Responsável por modelagem | Integrante diferente do autor | Transições e recusas | A realizar |
| Protótipo | Responsável por interface | Integrante diferente do autor | Fluxo e telas de recusa | A realizar |


## 13. Fluxo principal do protótipo

O protótipo implementa o seguinte fluxo:

`Início → Catálogo → Detalhes do serviço → Solicitação → Em análise → Aceitar OU Recusar`

No caminho de recusa:

`Recusar → Motivo da recusa → Solicitação recusada → Voltar ao catálogo`

No caminho de aprovação:

`Aceitar → Reserva aprovada → Confirmar → Reserva confirmada`

## 14. Relação entre artefatos

```text
REQUISITOS.md
      │
      ├──────────────► Modelo de domínio
      │                      │
      │                      ▼
      │               Modelo de dados
      │
      └──────────────► Diagrama de estados
                             │
                             ▼
                       Protótipo navegável
```

A modelagem deve retroalimentar os requisitos. Quando um diagrama revelar uma regra necessária que não esteja documentada, `REQUISITOS.md` deverá ser atualizado.

## 15. Estrutura da entrega

```text
/
├── PROJETO.md
├── REQUISITOS.md
├── diagrams/
│   ├── modelo-dominio.md
│   ├── modelo-dados.md
│   └── estados-reserva.md
├── prototipo/
│   ├── index.html
│   ├── catalogo.html
│   ├── servico.html
│   ├── reserva.html
│   ├── recusada.html
│   ├── aprovada.html
│   ├── confirmada.html
│   ├── css/style.css
│   └── js/script.js
└── CONFERENCIA_CRUZADA.md
```
