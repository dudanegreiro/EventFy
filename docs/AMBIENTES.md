# 🌐 Ambientes de Desenvolvimento, Homologação e Produção — EventFy

> **Issue relacionada:** [`#53` — EVT-33: Definir ambiente desenvolvimento, homologação e produção](https://github.com/dudanegreiro/EventFy/issues/53)
>
> **Responsável:** Igor Anicezio Oliveira (`@IgorAnicezioOliveira`) · **Apoio:** Gustavo Leite Bringel (`@GustavoBringel`)
>
> **Referências:** Capítulo 14 (Implantação e Operação), [`ARQUITETURA.md`](../ARQUITETURA.md), [`docs/DATABASE.md`](./DATABASE.md) e [`docs/API.md`](./API.md).

---

## 1. Finalidade e Separação dos Três Ambientes

O **EventFy** opera com **três ambientes isolados** — desenvolvimento, homologação e produção — compartilhando **exatamente o mesmo artefato de código** (sem `if ambiente == "producao"` alterando regras de negócio) e variando exclusivamente por variáveis de ambiente e infraestrutura.

| Dimensão | Desenvolvimento (`desenvolvimento`) | Homologação (`homologacao`) | Produção (`producao`) |
|---|---|---|---|
| **Finalidade** | Construção local, depuração rápida, execução de testes automatizados e validação de PRs em CI. | Ensaio de implantação, validação de migrações/rollback, conferência de volume realista e plano de contingência da demonstração final. | Uso real e demonstração final em ambiente público estável (`v1.0.0`, `EVT-45`). |
| **Código implantado** | Branch curta de trabalho ou `main` local (`--reload` permitido apenas aqui). | Mesmo artefato/commit candidato à release do `main` (sem alterações manuais em servidor). | Exatamente o commit anotado pela tag de release no `main` (ex.: `v1.0.0`), imutável. |
| **Banco de dados** | PostgreSQL 17 local (`eventfy`, `eventfy_test`, `eventfy_demo`) ou container efêmero do GitHub Actions. | PostgreSQL 17 gerenciado dedicado, mesmas extensões (`btree_gist`, `pgcrypto`), esquema `V1..Vn` e volume sintético próximo da produção. | PostgreSQL 17 gerenciado dedicado em rede privada, TLS obrigatório e backup automatizado. |
| **Armazenamento de anexos** | Diretório local `./uploads` (`LOCAL_DOS_ARQUIVOS`). | Volume persistente dedicado ao ambiente de homologação (espelhando permissões e limite de 10 MB). | Volume persistente dedicado à produção incluído na rotina de backup (`ADR-03`). |
| **Dados permitidos** | Exclusivamente dados fictícios (`V2__seed_demo_data.sql`) e fixtures temporárias de teste. | Exclusivamente dados sintéticos gerados por script (incluindo massa de ~200 serviços para validar `RNF-03`). | Dados reais ou sintéticos controlados para a demonstração, sob regras de `RE-03` (LGPD). |
| **Acesso e exposição** | `127.0.0.1` / `localhost` apenas. | URL separada da produção, restrita à equipe e ensaios (com credenciais próprias). | URL pública HTTPS com `GET /api/health` monitorado e rate limit de login (`#89`). |

---

## 2. Regra de Paridade de Código e Fluxo de Promoção

1. **Mesmo código nos três ambientes:** toda diferença entre desenvolvimento, homologação e produção é injetada via variáveis de ambiente (Twelve-Factor App, fator III). Nenhuma funcionalidade de negócio, validação de permissão ou regra de agenda pode ser desabilitada por variável de ambiente.
2. **Ordem obrigatória de promoção:**
   ```text
   Branch curta (PR + CI verde) ──▶ main ──▶ Homologação (validação de deploy e migração) ──▶ Tag vX.Y.Z ──▶ Produção
   ```
3. **Sem edição manual em servidor:** toda alteração em homologação ou produção precisa nascer em commit revisado no `main` e passar pelo procedimento repetível de implantação (`EVT-35`, `#55`).

---

## 3. Regra de Isolamento de Dados (Dados Reais Nunca Descem)

Para atender à privacidade (`RE-03`, LGPD) e evitar exposição acidental de credenciais ou dados pessoais:

- **Proibição absoluta de cópia descendente:** dumps de banco de dados ou arquivos de anexo da **produção nunca podem ser copiados para homologação ou desenvolvimento**.
- **População de homologação e desenvolvimento:** utiliza somente as migrações versionadas (`db/migrations/V*__*.sql`), o seed fictício (`V2__seed_demo_data.sql`) e scripts de geração de massa sintética.
- **Segredos distintos por ambiente:** `CHAVE_SECRETA_JWT`, senhas de banco (`URL_DO_BANCO`) e tokens de agendamento de jobs devem ser **únicos e independentes** em cada ambiente — um vazamento em desenvolvimento jamais compromete homologação ou produção.
- **Contas administrativas separadas:** contas `ADMINISTRADOR` de desenvolvimento (`admin.demo@eventfy.local`) não podem usar a mesma senha em homologação ou produção.

---

## 4. Matriz de Variáveis de Ambiente

Todas as configurações sensíveis ou específicas de ambiente são lidas de variáveis de ambiente (`api/eventfy_api/config.py`):

| Variável | Obrigatória | Desenvolvimento | Homologação | Produção |
|---|:---:|---|---|---|
| `AMBIENTE` | Não (padrão `desenvolvimento`) | `desenvolvimento` | `homologacao` | `producao` |
| `VERSAO_APP` | Não (padrão `0.2.0`) | `0.2.0-dev` | SHA/tag candidata | Tag exata da release (ex.: `1.0.0`) |
| `URL_DO_BANCO` | Sim | `postgresql://eventfy_dev:...@127.0.0.1:5432/eventfy` | URL privada do Postgres 17 de homologação (TLS) | URL privada do Postgres 17 de produção (TLS) |
| `CHAVE_SECRETA_JWT` | Sim (>= 32 chars) | Segredo aleatório local no `.env` | Secret exclusivo de homologação | Secret exclusivo de produção |
| `DURACAO_TOKEN_MINUTOS` | Não (padrão `30`) | `30` | `30` | `30` |
| `LOCAL_DOS_ARQUIVOS` | Não (padrão `./uploads`) | `./uploads` | `/var/data/eventfy/uploads` (disco homolog) | `/var/data/eventfy/uploads` (disco prod) |
| `NIVEL_LOG` | Não (padrão `INFO`) | `DEBUG` ou `INFO` | `INFO` | `INFO` (ou `WARNING`, sempre sem PII) |
| `CORS_ORIGINS` | Não | `http://localhost:5500,http://127.0.0.1:5500,http://localhost:5173,http://127.0.0.1:5173` | Origem HTTPS exata da homologação | Origem HTTPS exata da produção |
| `PORTA` | Não (padrão `8000`) | `8000` | Injetada pela plataforma (`PORT`) | Injetada pela plataforma (`PORT`) |

> Nenhum valor real deve ser gravado em `.env.example` ou no repositório. A política completa de proteção de segredos está em [`EVT-28` (`#48`)](https://github.com/dudanegreiro/EventFy/issues/48).

---

## 5. Paridade de Homologação com a Produção

Para que o ambiente de homologação antecipe defeitos reais antes da publicação em produção (e sirva como **plano de contingência** na review final `EVT-45`):

1. **Mesmo SGBD e extensões:** PostgreSQL **17** com `btree_gist` e `pgcrypto`, mesmas restrições `EXCLUDE USING gist` e trigger de imutabilidade de `historico_reserva`.
2. **Mesma topologia lógica:** API FastAPI sob HTTPS, banco em rede privada, volume persistente para anexos e rotina agendada de expiração/finalização (`EVT-38`).
3. **Volume aproximado de dados sintéticos:** base populada com pelo menos **200 serviços sintéticos**, múltiplos organizadores/prestadores e reservas em diferentes estados, permitindo verificar o desempenho do catálogo (`RNF-03` <= 3,0s) e o comportamento das migrações em escala semelhante à da produção.
4. **Ensaio obrigatório de migração:** toda nova migração `V<n>__*.sql` é aplicada primeiro em homologação antes de ser promovida à produção.
