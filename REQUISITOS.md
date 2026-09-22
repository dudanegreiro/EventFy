# REQUISITOS — EventFy

> Documento consolidado para a entrega incremental 6.14.
>

## 1. Objetivo

O EventFy é uma plataforma web para centralizar a busca, contratação e gestão de serviços e estruturas para eventos, conectando organizadores a prestadores de serviços e fornecedores.

## 2. Requisitos funcionais

### RF01 — Cadastro de usuário
O sistema deverá permitir o cadastro de usuários com nome, e-mail, senha e tipo de perfil.

### RF02 — Autenticação
O sistema deverá permitir que usuários cadastrados realizem login e logout.

### RF03 — Perfil de usuário
O sistema deverá permitir visualizar e atualizar os dados básicos do perfil.

### RF04 — Cadastro de serviço ou estrutura
O prestador/fornecedor deverá poder cadastrar itens disponibilizados para eventos, informando nome, categoria, descrição, preço, disponibilidade e imagens.

### RF05 — Edição e remoção de serviço
O prestador/fornecedor deverá poder editar os dados dos itens cadastrados e solicitar sua remoção.

### RF06 — Catálogo unificado
O sistema deverá apresentar os serviços e estruturas disponíveis em um catálogo.

### RF07 — Busca e filtragem
O sistema deverá permitir pesquisar e filtrar itens por categoria, preço e disponibilidade.

### RF08 — Visualização de detalhes
O sistema deverá apresentar os detalhes de um serviço ou estrutura, incluindo descrição, preço, imagens e informações do fornecedor.

### RF09 — Solicitação de reserva
O organizador deverá poder solicitar a reserva de um serviço ou estrutura para determinado evento, informando data e demais dados necessários.

### RF10 — Análise da solicitação
O prestador/fornecedor deverá poder analisar uma solicitação de reserva.

### RF11 — Aceitar solicitação
O prestador/fornecedor deverá poder aceitar uma solicitação de reserva.

### RF12 — Recusar solicitação
O prestador/fornecedor deverá poder recusar uma solicitação de reserva, registrando um motivo para a recusa.

### RF13 — Acompanhar reserva
O organizador deverá poder consultar o estado de suas solicitações e reservas.

### RF14 — Cancelar reserva
O organizador ou o prestador/fornecedor deverá poder cancelar uma reserva conforme as regras de negócio definidas.

### RF15 — Painel do organizador
O sistema deverá disponibilizar um painel para o organizador acompanhar os serviços contratados e suas reservas.

### RF16 — Histórico
O sistema deverá manter histórico das reservas e de seus estados para fins de acompanhamento.

### RF17 — Avaliação
Após a conclusão de uma contratação, o sistema poderá permitir avaliação entre as partes, conforme a regra de negócio definida para a versão do projeto.

### RF18 — Notificação de mudança de estado
O sistema deverá informar ao usuário quando houver alteração relevante no estado de uma solicitação ou reserva.

## 3. Requisitos não funcionais

### RNF01 — Segurança
As credenciais de acesso deverão ser armazenadas de forma segura, sem exposição de senhas em texto puro.

### RNF02 — Integridade
O sistema deverá impedir reservas incompatíveis com a disponibilidade registrada.

### RNF03 — Usabilidade
As telas principais deverão apresentar navegação clara e feedback para ações de sucesso, erro, recusa e cancelamento.

### RNF04 — Consistência de dados
Datas e horários deverão seguir um padrão único de armazenamento e apresentação.

### RNF05 — Rastreabilidade
Cada reserva deverá possuir identificador único e manter seu histórico de estados.

### RNF06 — Disponibilidade de arquivos
Imagens e outros arquivos associados a serviços deverão possuir referência persistente e acessível.

## 4. Regras de negócio

### RN01 — Identificação
Usuários, serviços, eventos e reservas possuirão identificadores únicos.

### RN02 — Reserva
Uma reserva representa a solicitação de contratação de um serviço/estrutura para um evento e período determinados.

### RN03 — Estados da reserva
Uma reserva poderá assumir os estados:

`SOLICITADA → EM_ANÁLISE → APROVADA → CONFIRMADA → FINALIZADA`

Também poderá seguir para:

`EM_ANÁLISE → RECUSADA`

e:

`CONFIRMADA → CANCELADA`

### RN04 — Recusa
Uma recusa deverá possuir um motivo registrado e apresentado ao solicitante.

### RN05 — Exclusão
Registros que possuam histórico relevante de reservas não deverão ser apagados fisicamente de forma a eliminar a rastreabilidade. Quando necessário, deverá ser utilizada desativação/exclusão lógica.

### RN06 — Imagens
O banco de dados deverá armazenar a referência do arquivo (por exemplo, caminho ou URL), e não necessariamente o conteúdo binário da imagem.

### RN07 — Tempo
Datas e horários deverão ser armazenados em tipos próprios (`DATE`, `TIME`, `DATETIME`/equivalente), evitando datas como texto livre.

## 5. Rastreabilidade inicial

| Elemento do domínio | Requisitos relacionados |
|---|---|
| Usuario | RF01, RF02, RF03, RN01 |
| Evento | RF09, RF15, RN01 |
| Servico | RF04, RF05, RF06, RF07, RF08, RN06 |
| Reserva | RF09–RF16, RN02–RN07 |
| Avaliacao | RF17 |
| Arquivo/Imagem | RF04, RF08, RN06 |

