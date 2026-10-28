# 📝 Registro de Mudanças (Changelog) — EventFy

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

---

## [0.2.0] - 2026-10-21

### Adicionado
- Especificação formal da arquitetura e decisões de isolamento por critérios de David Parnas em `PROJETO.md`.
- Consolidação dos 8 estados do ciclo de vida da reserva (`SOLICITADA`, `EM_ANALISE`, `APROVADA`, `CONFIRMADA`, `RECUSADA`, `CANCELADA`, `EXPIRADA`, `FINALIZADA`).
- Diagrama de sequência UML para o fluxo principal de reserva e recusa justificada.
- Protótipo navegável em HTML/CSS/JS cobrindo fluxo de solicitação, aprovação e tela de recusa com motivo obrigatório.
- Documentação do tema do projeto em `docs/TEMA.md`.

### Alterado
- Reconciliação dos requisitos em `REQUISITOS.md` com os novos diagramas e regras de negócio RN01 a RN07.
- Reestruturação de `PROCESSOS-NEGOCIO.md` com mapeamento detalhado dos fluxos P01 a P10.

---

## [0.1.0] - 2026-09-03

### Adicionado
- Estrutura inicial do repositório configurada.
- Documento `README.md` com apresentação da proposta do EventFy, atores e escopo inicial.
- Guia de contribuição `CONTRIBUTING.md` com convenções de ramos, commits e pull requests.
- Especificação inicial de requisitos e regras de negócio.
- Modelagem conceitual preliminar de domínio e dados.
