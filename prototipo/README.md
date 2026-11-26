# Interface web — EventFy

As telas em HTML, CSS e JavaScript consomem a API REST do EventFy (`docs/API.md`). Os dados, a autenticação, as regras de estado e o histórico vêm do servidor e ficam gravados no PostgreSQL.

## Como executar

Pré-requisito: o banco preparado e a API configurada conforme [`docs/DATABASE.md`](../docs/DATABASE.md) e [`docs/API.md`](../docs/API.md).

1. Inicie a API na porta 8000, na raiz do repositório:

   ```powershell
   .\.venv\Scripts\python.exe -m uvicorn eventfy_api.main:app --app-dir api --env-file .env
   ```

2. Em outro terminal, sirva esta pasta na porta 5500, que é a origem aceita pela API (CORS):

   ```powershell
   .\.venv\Scripts\python.exe -m http.server 5500 --bind 127.0.0.1 --directory prototipo
   ```

3. Abra <http://127.0.0.1:5500/>. Para usar outra API, defina `window.EVENTFY_API_URL` antes de carregar `js/api.js`.

As contas de demonstração e a senha local estão em `docs/DATABASE.md`. Para recarregar a página depois de alterar um arquivo, use `Ctrl+F5`: o navegador pode guardar cópias antigas dos scripts.

## Fluxo principal

1. **Entrar** com uma conta de organizador (`entrar.html`). O catálogo é público.
2. No catálogo, pesquise e filtre por texto, categoria, faixa de preço, localização e período disponível; o servidor faz a busca.
3. Abra um serviço e escolha **Solicitar reserva**. Selecione um evento existente ou crie um novo, informe o período (dentro do evento e da disponibilidade do serviço) e envie. A reserva nasce `SOLICITADA`.
4. Entre como prestador, abra **Solicitações**, inicie a análise e **aprove** ou **recuse**. A recusa exige justificativa de pelo menos 10 caracteres.
5. Como organizador, abra **Minhas reservas**, entre na reserva `APROVADA` e **confirme a contratação** em até 48 horas. O estado passa a `CONFIRMADA` e a agenda é bloqueada.

## Histórico, estados e cancelamento

- **Ver histórico** mostra a trilha gravada pelo servidor: estado anterior e novo, data e hora, responsável com o papel e justificativa. Os registros não podem ser alterados nem apagados.
- O organizador cancela nos estados `SOLICITADA`, `EM_ANALISE`, `APROVADA` e `CONFIRMADA`; o prestador, somente em `CONFIRMADA`. O servidor exige justificativa, confere que o evento ainda não começou e libera a agenda (RF14 e RN09).
- Reservas `RECUSADA`, `CANCELADA`, `EXPIRADA` e `FINALIZADA` encerram o fluxo. A expiração por prazo de 48 horas e a finalização são feitas pelo servidor.

## Limites

- O prestador não vê o nome do evento, apenas o número, porque a API só deixa o organizador listar eventos.
- O token de sessão fica em `sessionStorage` e dura 30 minutos. A tela decide quais botões mostrar a partir do papel, mas é o servidor que autoriza cada operação.
- Não há telas de cadastro de conta, de avaliação, de anexos nem de administração; esses fluxos pertencem a outras entregas.
- As telas foram conferidas em largura de 360 px, sem rolagem horizontal.
