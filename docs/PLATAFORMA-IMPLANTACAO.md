# ☁️ Escolha da Plataforma de Implantação — EventFy

> **Issue relacionada:** [`#54` — EVT-34: Escolher e registrar plataforma de implantação](https://github.com/dudanegreiro/EventFy/issues/54)
>
> **Responsável:** Igor Anicezio Oliveira (`@IgorAnicezioOliveira`) · **Apoio:** Eduarda Negreiro (`@dudanegreiro`)
>
> **Referências:** Capítulo 14 (Implantação e Operação), [`ARQUITETURA.md`](../ARQUITETURA.md) (`ADR-03` e `ADR-05`), [`docs/AMBIENTES.md`](./AMBIENTES.md).

---

## 1. Decisão Registrada

- **Modelo escolhido:** **PaaS (Platform-as-a-Service)** compatível com a capacidade de manutenção de uma equipe acadêmica de 5 estudantes sem equipe dedicada de infraestrutura.
- **Provedor escolhido:** **Render** (`https://render.com`).
- **URLs convencionadas (provisionamento executado na `EVT-35`, `#55`):**
  - **Produção:** `https://eventfy-api.onrender.com` (health check em `https://eventfy-api.onrender.com/api/health`)
  - **Homologação:** `https://eventfy-homolog.onrender.com` (health check em `https://eventfy-homolog.onrender.com/api/health`)
  - *Nota de transparência:* caso o subdomínio `eventfy-api` já esteja reservado no momento do provisionamento na `EVT-35`, a URL definitiva será atualizada nesta tabela e em `OPERACAO.md` antes da review final (`EVT-45`).

---

## 2. Critérios de Avaliação e Comparativo de Alternativas

Os critérios foram definidos conforme a capacidade da equipe (`PROCESSO.md`), a arquitetura (`ARQUITETURA.md`) e as restrições do projeto (`RE-01` a `RE-04`):

| Critério | **Render (PaaS — Escolhido)** | Railway (PaaS) | Fly.io (PaaS/Containers) | VPS / IaaS Manual (EC2 / Droplet) | Vercel / Serverless Puro |
|---|---|---|---|---|---|
| **Custo** | Baixo/previsível; permite homologação em camada gratuita e produção acessível com banco + disco. | Crédito inicial limitado; cobrança por uso pode gerar surpresa se banco ficar ativo 24/7. | Exige cartão e configuração fina de máquinas/volumes; risco de cobrança inesperada. | Custo previsível, porém exige custo oculto alto de horas de configuração e manutenção. | Gratuito para estático, mas exige serviços terceiros pagos para Postgres + storage + cron. |
| **Manutenção** | **Baixa:** TLS automático, deploy conectado ao Git/tag, logs centralizados e Postgres gerenciado. | Baixa, interface simples, porém menor padronização declarativa de cron + disco persistente. | Média: exige domínio de `fly.toml`, CLI `flyctl` e gerenciamento manual de volumes/Postgres. | **Alta:** exige configurar Nginx, Certbot TLS, firewall, systemd, patches de SO e backups manuais. | Média/alta para FastAPI transacional (limites de timeout e pool de conexões SQL). |
| **Privacidade e Segurança** | Banco PostgreSQL em rede privada interna, TLS fim a fim, variáveis/secrets isolados por ambiente, região configurável (ex.: Ohio/Oregon EUA — registrada no inventário LGPD `EVT-32`). | Rede privada interna e secrets por ambiente; transparência menor de compliance acadêmico. | Rede privada WireGuard e secrets; maior chance de erro de configuração por inexperiência. | Controle total da região, porém alto risco de erro humano em firewall, SSH e hardening. | Dados fragmentados entre múltiplos provedores (Vercel + Neon/Supabase + S3). |
| **Suporte à Stack EventFy** | **Completo:** Python 3.12+/3.14, FastAPI/Uvicorn, **PostgreSQL 17 gerenciado com `btree_gist` e `pgcrypto`**, Persistent Disk (`LOCAL_DOS_ARQUIVOS`) e Cron Jobs nativos. | Bom suporte a Python e Postgres; volumes e cron menos lineares que Render Blueprints. | Bom suporte via Dockerfile, mas Postgres não é totalmente gerenciado sem custo/esforço extra. | Suporta tudo, mas toda a instalação e automação ficam por conta da equipe. | **Inadequado:** sistema de arquivos efêmero (quebra `ADR-03`) e cold starts em conexões `psycopg`. |

---

## 3. Cobertura dos Quatro Pilares Operacionais

| Pilar | Como é coberto no Render | Detalhes técnicos |
|---|---|---|
| **Banco de dados** | **Render Managed PostgreSQL 17** | Instância dedicada por ambiente (`homologacao` e `producao`) acessível via `Internal Database URL` (rede privada, sem exposição pública desnecessária), com suporte nativo às extensões `btree_gist` e `pgcrypto` usadas em `V1__create_relational_schema.sql` e backup automático. |
| **Armazenamento de anexos** | **Render Persistent Disk** montado em `/var/data/eventfy/uploads` | Atende diretamente a `ADR-03` e `RE-04`, apontando `LOCAL_DOS_ARQUIVOS=/var/data/eventfy/uploads` com validação de MIME e limite de 10 MB no backend. Em evolução futura multi-instância, o adaptador permite migrar para Object Storage S3/R2 sem alterar rotas ou banco. |
| **Jobs agendados** | **Render Cron Job** (ou fallback via workflow agendado no GitHub Actions) | Executa periodicamente a rotina autenticada `POST /api/jobs/reservas/expiracoes` (SLA de 48h, `EVT-21`) e a rotina de finalização (`EVT-38`) utilizando credencial de serviço armazenada exclusivamente em variável secreta. |
| **Variáveis e segredos** | **Render Environment Groups / Environment Variables** | Cada ambiente (`homologacao` e `producao`) recebe conjunto próprio e isolado (`URL_DO_BANCO`, `CHAVE_SECRETA_JWT`, `AMBIENTE`, `VERSAO_APP`, `LOCAL_DOS_ARQUIVOS`, `CORS_ORIGINS`, `NIVEL_LOG`), nunca commitados no repositório (`EVT-28`, `EVT-33`). |

---

## 4. Alternativas Descartadas (Resumo do ADR-05)

1. **IaaS / VPS manual (AWS EC2, DigitalOcean Droplet):** descartada porque a equipe de 5 estudantes sem perfil dedicado de SysAdmin gastaria tempo crítico configurando proxy reverso, renovação TLS, firewall, systemd e backups de PostgreSQL, aumentando o risco operacional às vésperas da entrega final.
2. **Serverless puro (Vercel / AWS Lambda):** descartada por incompatibilidade com disco persistente local (`ADR-03`), sobrecarga de gerenciamento de conexões PostgreSQL transacionais (`psycopg` com `FOR UPDATE`) e fragmentação de provedores.
3. **Fly.io:** descartada pela curva operacional maior para manutenção de PostgreSQL e volumes em comparação ao PaaS totalmente gerenciado.
4. **Railway:** descartada como opção principal por modelo de cobrança variável por uso contínuo e menor padronização declarativa de disco persistente + cron jobs no mesmo blueprint.

---

## 5. Consequências Aceitas e Mitigações

- **Instância única enquanto houver disco persistente (`ADR-03`):** o Persistent Disk do Render acopla o serviço web a 1 instância ativa. *Mitigação:* suficiente para a escala do MVP acadêmico e demonstração final; caso o sistema escale horizontalmente, o armazenamento de anexos migra para S3/Cloudflare R2.
- **Hibernação / cold start no plano gratuito:** serviços web gratuitos no Render entram em repouso após inatividade (~15 min), causando atraso na primeira requisição. *Mitigação:* usar plano básico contínuo em produção na semana da demonstração final (ou aquecer o serviço previamente via `GET /api/health` antes da apresentação da `EVT-45`).
- **Retenção de banco gratuito (30 dias):** bancos gratuitos no Render têm prazo limitado de vida. *Mitigação:* manter backups lógicos (`pg_dump`) conforme `OPERACAO.md` (`EVT-39`) e utilizar migrações versionadas `V1..Vn` + scripts de seed para reconstrução completa em minutos.
- **Dependência do provedor PaaS:** mitigada mantendo a aplicação 100% padrão (Python/FastAPI/Uvicorn + PostgreSQL 17 + variáveis de ambiente, sem SDK proprietário do Render no código-fonte).
