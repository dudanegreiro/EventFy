# 🔐 Proteção de Segredos e Plano de Resposta a Vazamento — EventFy

> **Issue relacionada:** [`#48` — EVT-28: Proteger segredos e criar plano de vazamento](https://github.com/dudanegreiro/EventFy/issues/48)
>
> **Responsável:** Igor Anicezio Oliveira (`@IgorAnicezioOliveira`) · **Apoio:** Gustavo Leite Bringel (`@GustavoBringel`)
>
> **Referências:** Capítulo 13 (Segurança), `RNF-01`, `RE-03` e [`ARQUITETURA.md`](../ARQUITETURA.md).

---

## 1. Política de Configuração e Variáveis de Ambiente

Nenhum segredo (senhas de banco, chaves JWT, tokens de API, chaves privadas ou credenciais de armazenamento/implantação) pode ser gravado em código-fonte, testes, arquivos de documentação ou histórico Git.

### 1.1 Inventário de variáveis sensíveis

| Variável | Onde é lida | Restrição de segurança | Onde configurar |
|---|---|---|---|
| `URL_DO_BANCO` | `dev/ambiente.py` (`os.getenv`), `api/eventfy_api/config.py` (`Settings`) | Contém usuário e senha do PostgreSQL; nunca logar nem versionar. | `.env` local / Secrets do provedor de implantação |
| `CHAVE_SECRETA_JWT` | `api/eventfy_api/config.py` (`SecretStr`) | Mínimo de **32 caracteres aleatórios**; valores com prefixo `GERAR_` são rejeitados na inicialização. | `.env` local / Secrets do provedor |
| `LOCAL_DOS_ARQUIVOS` | `api/eventfy_api/config.py` | Caminho de disco local ou destino do storage; não contém segredo, mas varia por ambiente. | `.env` local / variáveis de ambiente |
| Credenciais de Object Storage / Deploy (futuro `EVT-34`/`EVT-35`) | Variáveis de ambiente / Secrets do CI | Chaves de bucket S3-compatível e tokens de deploy nunca entram no repositório. | **GitHub Actions Secrets** (`Settings → Secrets and variables → Actions`) e painel da plataforma |

### 1.2 Proteção no repositório local e remoto

- **`.gitignore`:** exclui explicitamente `.env`, `.env.*` (mantendo apenas `!.env.example`), `*.local` e `/uploads/`.
- **`.env.example`:** contém exclusivamente placeholders ilustrativos (`SUBSTITUA_LOCALMENTE`, campo `CHAVE_SECRETA_JWT=` vazio) e instruções de cópia local.
- **Geração segura de segredo JWT local:**
  ```powershell
  # PowerShell / Python
  python -c "import secrets; print(secrets.token_urlsafe(48))"
  ```

### 1.3 Uso de segredos em Integração Contínua (CI/CD)

1. **Segredos reais (deploy, homologação, produção, storage externo):** devem ser armazenados exclusivamente em **GitHub Actions Secrets** (por repositório ou *Environment* protegido) e referenciados somente como `${{ secrets.NOME_DO_SEGREDO }}`, nunca impressos em `echo` ou logs.
2. **Credenciais efêmeras de teste em CI:** os workflows de teste (`.github/workflows/ci.yml` e `.github/workflows/quality.yml`) sobem um container PostgreSQL 17 descartável dentro do runner isolado; suas credenciais fictícias existem apenas durante o job e jamais podem ser reutilizadas fora do CI.
3. **Verificação automática contínua:** o workflow [`.github/workflows/secrets-check.yml`](../.github/workflows/secrets-check.yml) executa em todo `push` e `pull_request` para bloquear arquivos `.env`, chaves privadas e padrões conhecidos de tokens antes do merge.

---

## 2. Plano de Resposta a Vazamento de Segredos

Caso qualquer credencial real, token ou arquivo `.env` seja exposto em um commit, Pull Request, log ou canal externo, **considere o segredo imediatamente comprometido** (mesmo se o repositório fosse privado ou o commit apagado minutos depois) e execute os **4 passos abaixo em ordem**:

### Passo 1 — Conter e Revogar (imediato, < 15 minutos)

1. **Revogar a credencial comprometida na origem** antes mesmo de limpar o Git:
   - **Token GitHub / PAT / chave de deploy:** revogar imediatamente em *GitHub Settings → Developer settings* ou no provedor de hospedagem.
   - **Chave de Object Storage / API externa:** desativar/revogar a chave no console do provedor.
   - **Senha do PostgreSQL:** bloquear/alterar a credencial do usuário afetado (`ALTER USER <usuario> WITH PASSWORD '<nova_senha>';`).
   - **Chave JWT (`CHAVE_SECRETA_JWT`):** preparar nova chave aleatória (>= 32 caracteres) e **revogar todas as sessões ativas** no banco:
     ```sql
     UPDATE public.sessao_autenticacao
     SET revogada_em = now()
     WHERE revogada_em IS NULL;
     ```

### Passo 2 — Rotacionar e Reconfigurar

1. Gerar novos segredos com alta entropia (nunca reutilizar nem derivar do segredo vazado).
2. Atualizar as variáveis nos ambientes afetados (`.env` local, GitHub Actions Secrets e variáveis de ambiente de homologação/produção).
3. Reiniciar o serviço da API e validar `GET /api/health` e login de teste.

### Passo 3 — Limpar o Histórico Git

1. Remover o arquivo ou segredo de **todo o histórico de commits e branches** usando `git filter-repo` (ferramenta recomendada pelo GitHub em substituição ao `filter-branch`):
   ```sh
   # Exemplo para remover um .env commitado acidentalmente de todo o histórico
   git filter-repo --invert-paths --path .env

   # Ou substituir um segredo literal usando um arquivo replacements.txt
   # (formato: SEGREDO_VAZADO==>REMOVIDO)
   git filter-repo --replace-text replacements.txt
   ```
2. Coordenar com toda a equipe o `git push --force --all` e `git push --force --tags`, orientando todos os integrantes a sincronizar/reclonar o repositório para evitar reintroduzir o commit antigo.
3. Caso o vazamento tenha ocorrido em um Pull Request já aberto no GitHub, solicitar limpeza de cache/objetos órfãos ao suporte do GitHub se necessário e confirmar que a busca de código não retorna mais o padrão.

### Passo 4 — Auditar e Registrar Lição Aprendida

1. **Auditar acessos no período de exposição:** verificar logs da API, tabela `public.sessao_autenticacao`, logs de autenticação do PostgreSQL e histórico de auditoria do provedor/GitHub em busca de acessos não autorizados.
2. **Avaliar impacto em dados pessoais (LGPD / `RE-03`):** se houve acesso potencial a dados de usuários em ambiente real, acionar a responsável pelo produto (`@dudanegreiro`) e registrar o incidente conforme `DADOS-PESSOAIS.md` (`EVT-32`, `#52`).
3. **Registrar o incidente e reforçar prevenção:** abrir issue de acompanhamento com a causa raiz e adicionar nova regra no `.github/workflows/secrets-check.yml` / `.gitignore` para impedir recorrência.

### Responsáveis pelo acionamento

| Papel | Integrante | Atuação no incidente |
|---|---|---|
| Arquitetura e Segurança / CI | Igor Anicezio Oliveira (`@IgorAnicezioOliveira`) | Coordenação da contenção, limpeza do histórico Git e revisão do CI |
| Dados e Backend | Gustavo Leite Bringel (`@GustavoBringel`) | Rotação de credenciais do PostgreSQL e revogação de sessões JWT |
| Produto / Administração do Repositório | Eduarda Negreiro (`@dudanegreiro`) | Permissões do repositório no GitHub, comunicação e conformidade LGPD |
| Qualidade e Processo | Thalita Teixeira Menezes (`@thalist`) | Registro de evidências na retrospectiva (`ITERACOES.md`) e atualização do checklist |

---

## 3. Evidência da Auditoria do Histórico do Repositório

**Data da auditoria:** 26/11/2026 · **Escopo:** todos os commits e todas as branches (`--all`) do repositório `dudanegreiro/EventFy` até o commit `5e15fa1` (incluindo a promoção do backend no PR `#94`).

### Verificações executadas

1. **Arquivos sensíveis no histórico completo** (`.env`, `.env.*` exceto `.env.example`, `.pem`, `.key`, `.p12`, `.pfx`, `.jks`, `.secret`, `.credentials`):
   - **Resultado:** `0` arquivos encontrados.
2. **Varredura de padrões de segredos em todos os diffs do histórico** (tokens GitHub `ghp_`/`github_pat_`, chaves AWS `AKIA...`, chaves privadas `BEGIN ... PRIVATE KEY`, tokens `sk-...`, Slack `xox...`, Google `AIza...`):
   - **Resultado:** `0` ocorrências encontradas.
3. **Inspeção das ocorrências de `URL_DO_BANCO` e `CHAVE_SECRETA_JWT` no histórico:**
   - **Resultado:** apenas valores fictícios ilustrativos em `.env.example` (ex.: `SUBSTITUA_LOCALMENTE`, `troque-esta-senha`, campo vazio).

### Comandos reproduzíveis para reauditoria

```powershell
# 1. Conferir se algum arquivo sensível já entrou no histórico Git
git log --all --name-only --pretty=format: | Sort-Object -Unique | Where-Object {
    $_ -match '(^|/)\.env($|\.(?!example))|\.(pem|key|p12|pfx|jks|secret|credentials)$'
}

# 2. Varrer histórico por padrões de tokens e chaves privadas
git log --all -E -G '(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----|sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|AIza[0-9A-Za-z_-]{35})' --oneline
```
