# Banco de dados local — EventFy

O banco relacional de desenvolvimento usa PostgreSQL 17. A API REST do fluxo principal usa FastAPI e Psycopg 3; sua configuracao, contrato e testes estao descritos em [`API.md`](./API.md).

O modelo implementa as entidades descritas em [`diagrams/dados.mmd`](./diagrams/dados.mmd) e [`PROJETO.md`](./PROJETO.md). Datas e horas usam `timestamptz`; exclusoes logicas usam `ativo`; chaves estrangeiras impedem a remocao fisica de registros referenciados. Uma restricao de exclusao do PostgreSQL impede intervalos sobrepostos para reservas ativas do mesmo servico. Os historicos de reservas e moderacao rejeitam `UPDATE` e `DELETE`. Migracoes incrementais adicionam sessao de autenticacao, localizacao, referencia de reservas aos pre-bloqueios de agenda e moderacao com visibilidade independente das publicacoes.

## Pre-requisitos

- PostgreSQL 17 instalado e servidor em execucao;
- `psql` e `createdb` no `PATH`;
- permissao para criar o banco `eventfy` e as extensoes `btree_gist` e `pgcrypto`.

No Windows, o instalador oficial do PostgreSQL pode adicionar `C:\Program Files\PostgreSQL\17\bin` ao `PATH`. Alternativamente, abra o terminal nessa pasta ou adicione-a temporariamente:

```powershell
$env:Path += ';C:\Program Files\PostgreSQL\17\bin'
```

O script usa `PGUSER`, `PGHOST` e `PGPORT` quando definidos. Os padroes sao `postgres`, `localhost` e `5432`. Quando a autenticacao exigir senha, o `psql`/`createdb` solicitara a senha; nao a passe como argumento de linha de comando.

## Criar ou atualizar o banco

Na raiz do repositorio:

```powershell
.\scripts\db-setup.ps1
```

O comando cria `eventfy` se ainda nao existir, cria o controle de migracoes e aplica, em ordem, as migracoes pendentes de `db/migrations/`. Pode ser executado novamente: versoes aplicadas nao sao repetidas e alteracoes em migracoes ja aplicadas sao reportadas como erro. Para mudar o esquema, adicione uma nova migracao `V<numero>__<descricao>.sql`; nao edite uma versao que ja foi aplicada.

Para usar outra conexao:

```powershell
$env:PGHOST = 'localhost'
$env:PGPORT = '5432'
$env:PGUSER = 'postgres'
.\scripts\db-setup.ps1 -Database eventfy
```

## Restaurar o banco de demonstração

Para a review parcial, use o banco isolado `eventfy_demo`. O script de restauração prepara as migrações e substitui apenas as fixtures desse banco pela seed versionada. Ele pede confirmação e recusa outros nomes de banco; não use `-Confirm:$false` em uma execução manual.

```powershell
.\scripts\restore-demo-data.ps1 -Confirm
```

O banco de demonstração pertence ao usuário indicado por `PGUSER` (por padrão, `postgres`). Para verificar os dados restaurados:

```powershell
psql -d eventfy_demo -c "SELECT status, count(*) FROM public.reserva GROUP BY status ORDER BY status;"
```

O resultado esperado é uma reserva em cada estado `APROVADA`, `FINALIZADA` e `SOLICITADA`. O roteiro completo da apresentação está em [`REVIEW-PARCIAL-EVT-08.md`](./REVIEW-PARCIAL-EVT-08.md).

## Acessar pelo pgAdmin

No pgAdmin, registre um servidor com:

| Campo | Valor local padrao |
|---|---|
| Host name/address | `localhost` |
| Port | `5432` |
| Maintenance database | `eventfy` |
| Username | o valor de `PGUSER`, normalmente `postgres` |
| Password | a senha local configurada no PostgreSQL |

As tabelas ficam no schema `public`. O historico de aplicacao das migracoes fica em `schema_migrations`.

## Dados de demonstracao

A segunda migracao inclui organizador, prestador, administrador, servico, evento, disponibilidade, anexo com URL ficticia, reservas em diferentes estados, historico e avaliacao.

Novos servicos exigem localizacao. O campo foi adicionado pela migracao V4; servicos anteriores permanecem sem localizacao ate o titular atualizar seus dados. A migracao V5 adiciona `disponibilidade_servico.id_reserva`, associa os pre-bloqueios existentes pela reserva correspondente e impede mais de um bloqueio ativo por reserva.

A migracao V6 adiciona `servico.visivel_catalogo`, que permite moderar uma publicacao sem alterar o estado da conta do prestador ou as reservas existentes. Tambem cria `historico_moderacao`, com ator, alvo, acao, motivo e instante; a tabela e imutavel.

Contas locais:

| Papel | E-mail | Senha de demonstracao |
|---|---|---|
| Organizador | `organizador.demo@eventfy.local` | `EventFyDemo123!` |
| Prestador | `prestador.demo@eventfy.local` | `EventFyDemo123!` |
| Administrador | `admin.demo@eventfy.local` | `EventFyDemo123!` |

As senhas sao armazenadas como hashes bcrypt gerados pelo `pgcrypto`. Essas contas e dados sao exclusivamente ficticios para desenvolvimento; nao os use em producao.

## Validacao rapida

```powershell
psql -d eventfy -c "SELECT version, applied_at FROM schema_migrations ORDER BY version;"
psql -d eventfy -c "SELECT status, count(*) FROM reserva GROUP BY status ORDER BY status;"
```
