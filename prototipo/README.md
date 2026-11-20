# Protótipo Navegável — EventFy

Abra `index.html` em um navegador moderno. Não é necessário instalar dependências.

## Fluxo principal

1. Na página inicial, entre no catálogo.
2. Pesquise ou filtre os serviços por categoria, faixa de preço, localização e período disponível; faixas inválidas e buscas sem resultados exibem mensagens próprias.
3. Informe evento, início e fim do período e envie a solicitação.
4. Na confirmação `SOLICITADA`, use **Simular início da análise** para continuar.
5. Na análise demonstrativa, aprove ou recuse a solicitação. A recusa exige justificativa.
6. Após a aprovação, confirme a contratação para chegar ao estado `CONFIRMADA`.

## Histórico e cancelamento

- **Ver histórico** está disponível nas telas de solicitação, análise, aprovação, recusa, confirmação e cancelamento. A trilha exibe estado anterior e novo, data/hora, ator e justificativa quando aplicável.
- O organizador pode cancelar nos estados `SOLICITADA`, `EM_ANALISE`, `APROVADA` e `CONFIRMADA`, antes do início do evento.
- O prestador pode cancelar somente uma reserva `CONFIRMADA`, também antes do início do evento.
- O cancelamento exige justificativa e termina em `CANCELADA`. Recusas e cancelamentos encerram o fluxo; `CONFIRMADA` antecede a finalização do evento, que não é simulada neste protótipo.
- A política implementada segue RF14/RN09; não há decisão de equipe pendente para as permissões e condições aqui demonstradas.

## Limites da demonstração

O protótipo é estático: os dados de exemplo e o histórico são carregados entre telas pela URL. Os filtros do catálogo demonstram os estados vazio e de validação, mas não consultam a API. Não há autenticação, persistência de reservas, agenda real ou auditoria imutável no protótipo. A implementação de produção deve aplicar as regras no servidor; a trilha real deve ser persistida e protegida contra alteração.

Use os links da própria navegação para manter o contexto de serviço e solicitação. Abrir diretamente uma tela de estado sem os parâmetros do fluxo exibe uma mensagem de dados indisponíveis.
