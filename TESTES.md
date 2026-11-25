# Plano de Testes do EventFy

## 1. Objetivo e leitura do documento

Este documento define **o que é testado no EventFy e com qual critério**. Ele não contém código de teste. Serve de referência para a automação (EVT-09, #29) e para a conferência pela equipe. Cada caso deriva de um critério de aceitação de [`docs/REQUISITOS.md`](./docs/REQUISITOS.md), o que permite rastrear a origem de qualquer teste a partir de sua linha.

Os casos são apresentados em tabelas com as seguintes colunas:

| Coluna | Conteúdo |
|---|---|
| **ID** | Identificador do caso. `TC` indica *Test Case*, e o sufixo indica a área (por exemplo, `EST` para estados da reserva). |
| **Requisito / Critério** | Origem do caso: requisito (por exemplo, RF12) e critério de aceitação (por exemplo, CA-02.3). |
| **Nível** | Camada em que o teste é executado (seção 2.1). |
| **Técnica** | Critério de escolha do caso: partição de equivalência ou valor limite (seção 2.2). |
| **Entrada** | Ação ou dado submetido ao sistema. |
| **Resultado esperado** | Comportamento exigido do sistema. Resposta diferente caracteriza falha do teste. |

Esta é uma primeira versão. Os casos devem ser conferidos pelo responsável pelo backend, quanto à viabilidade, e pela responsável pelos requisitos, quanto aos critérios de aceitação, antes de serem automatizados.

## 2. Estratégia

### 2.1 Níveis de teste

Os testes são divididos em quatro níveis, do mais isolado ao mais abrangente:

| Nível | Escopo | Exemplo no EventFy | Execução |
|---|---|---|---|
| **Unidade** | Uma regra isolada, sem banco de dados nem rede. | O motivo de recusa possui no mínimo 10 caracteres (RN04). | pytest |
| **Integração** | Componentes combinados: API e banco de dados. | Duas confirmações simultâneas para o mesmo período: a segunda recebe HTTP 409 (RNF-02). | pytest, HTTPX e PostgreSQL 17 |
| **Sistema** | Fluxo completo, de ponta a ponta. | Solicitação, aprovação e confirmação de uma reserva (HU-01 a HU-03). | pytest e HTTPX, com chamadas em sequência |
| **Aceitação** | Adequação ao uso pretendido, avaliada por um usuário. | Pessoa externa conclui o fluxo principal no protótipo. | Sessão com usuário externo (EVT-24, #44) |

As ferramentas seguem o [`ARQUITETURA.md`](./ARQUITETURA.md). Os testes de integração e de sistema utilizam o mesmo SGBD da aplicação, pois somente ele reproduz os conflitos reais de agenda.

### 2.2 Técnicas de seleção de casos

Como não é viável testar todas as entradas possíveis, os casos são selecionados por duas técnicas:

- **Partição de equivalência:** as entradas são divididas em classes que o sistema trata de forma equivalente, e um representante de cada classe é testado. Exemplo: o motivo de recusa possui duas classes, "menos de 10 caracteres" (recusa) e "10 ou mais" (aceita).
- **Valor limite:** são testados os valores nas fronteiras entre as classes, onde os defeitos são mais frequentes. Exemplo: motivos de 9 e de 10 caracteres.

### 2.3 Critério de escolha do nível

Cada caso é atribuído ao **nível de menor custo capaz de detectar o defeito**. Regras que podem ser verificadas em uma função isolada são testadas como unidade. A integração é reservada ao que depende da combinação de componentes, como a agenda concorrente. Os níveis de sistema e de aceitação cobrem os fluxos principais, em número reduzido de casos.

Um mesmo requisito pode ter casos em mais de um nível. Por exemplo, o tamanho da senha tem um caso de unidade (a regra) e um de integração (a resposta de erro da API).

### 2.4 Limitações

Este documento não define a frequência de execução nem o ambiente de execução dos testes, que pertencem à integração contínua (EVT-10, #30). Também não atesta que o código atual satisfaz os casos descritos: os testes existentes estão em ramos intermediários e ainda não constam no `main`.

## 3. Casos de teste

Os casos de aceitação (nível 4) são conduzidos na sessão com usuário externo (EVT-24, #44) e por isso não constam nas tabelas. Os demais níveis estão distribuídos entre as áreas.

### 3.1 Agenda concorrente

**Requisitos:** RF10, RF13, RN06, RN08, RNF-02. **Regra aplicada:** o banco impede intervalos sobrepostos entre reservas ativas do mesmo serviço, com intervalo semiaberto (início incluído, fim excluído). Conflito resulta em HTTP 409. **Referência:** reserva existente do serviço A, das 10h às 12h.

| ID | Requisito / Critério | Nível | Técnica | Entrada | Resultado esperado |
|---|---|---|---|---|---|
| TC-AGD-01 | RF10, RN08 / CA-01.1 | Integração | Partição: sem sobreposição | Solicitar o serviço A das 14h às 16h | Reserva criada em `SOLICITADA` |
| TC-AGD-02 | RN08 / CA-01.2 | Integração | Partição: com sobreposição | Solicitar o serviço A das 11h às 13h | HTTP 409; nenhuma reserva gravada |
| TC-AGD-03 | RN08 / CA-01.1 | Integração | Valor limite: início igual ao fim da existente | Solicitar o serviço A das 12h às 14h | Reserva criada (ver DA-02) |
| TC-AGD-04 | RNF-02 / CA-01.2 | Integração | Concorrência | Duas solicitações simultâneas ao serviço A, no mesmo período livre | Exatamente uma criada; a outra recebe HTTP 409 |
| TC-AGD-05 | RNF-02, RF13 / CA-03.1 | Integração | Concorrência | Duas confirmações simultâneas de reservas do serviço A no mesmo período | No máximo uma confirmada; a outra recebe HTTP 409 |

### 3.2 Autenticação

**Requisitos:** RF01, RF02, RNF-01.

| ID | Requisito / Critério | Nível | Técnica | Entrada | Resultado esperado |
|---|---|---|---|---|---|
| TC-AUT-01 | RF01, RNF-01 | Integração | Partição: dados válidos | Cadastrar organizador com e-mail novo e senha de 12 caracteres | Usuário criado; a senha é armazenada como hash bcrypt, nunca em texto puro |
| TC-AUT-02 | RF01 | Integração | Partição: e-mail repetido | Cadastrar `x@ex.test` e depois `  X@EX.TEST ` | Segundo cadastro recusado com HTTP 409 |
| TC-AUT-03 | RF01 | Unidade | Valor limite: um abaixo do mínimo | Validar senha de 11 caracteres | Recusada |
| TC-AUT-04 | RF02 | Integração | Partição: credenciais inválidas | Login com senha incorreta | Login recusado, sem informar qual dado está incorreto |
| TC-AUT-05 | RF02 | Integração | Efeito persistente | Realizar logout e reutilizar o mesmo token | Requisição recusada, pois a sessão foi revogada |

### 3.3 Autorização

**Requisitos:** RNF-07, RN01, RN02, RN13. Em todos os casos, o resultado inclui a ausência de alteração persistida.

| ID | Requisito / Critério | Nível | Técnica | Entrada | Resultado esperado |
|---|---|---|---|---|---|
| TC-AUZ-01 | RNF-07 | Integração | Partição: sem credencial | Chamar uma rota protegida sem token | Recusada |
| TC-AUZ-02 | RNF-07, RN02 / CA-02.1 | Integração | Partição: papel incorreto | Organizador tenta aprovar uma solicitação | HTTP 403 |
| TC-AUZ-03 | RN02, RF08 | Integração | Partição: recurso alheio | Prestador altera o serviço de outro prestador | HTTP 403 |
| TC-AUZ-04 | RNF-07 / CA-04.2 | Integração | Partição: recurso alheio | Usuário consulta o histórico de reserva que não é sua nem de seus serviços | HTTP 403 |
| TC-AUZ-05 | RN13, RF20 / CA-13.3 | Integração | Partição: papel incorreto | Usuário sem papel de administrador desativa uma conta | HTTP 403 |

### 3.4 Estados da reserva

**Requisitos:** RN04, RN05, RF12, RF13, transições T01 a T13 (`docs/diagrams/estados-reserva.md`).

| ID | Requisito / Critério | Nível | Técnica | Entrada | Resultado esperado |
|---|---|---|---|---|---|
| TC-EST-01 | HU-01 a HU-03 | Sistema | Fluxo principal | Solicitar, iniciar análise, aprovar e confirmar uma reserva | Estados `SOLICITADA`, `EM_ANALISE`, `APROVADA` e `CONFIRMADA`, em sequência |
| TC-EST-02 | RF12, RN04 / CA-02.3 | Unidade | Valor limite: um abaixo do mínimo | Recusar com motivo de 9 caracteres | Recusa bloqueada; a reserva permanece no estado anterior |
| TC-EST-03 | RF12, RN04 / CA-02.2 | Integração | Valor limite: mínimo aceito | Recusar com motivo de 10 caracteres | Reserva vai para `RECUSADA`; o motivo é persistido |
| TC-EST-04 | RN05 | Unidade | Partição: transição não mapeada | Tentar levar uma reserva `RECUSADA` para `APROVADA` | Transição recusada; o estado não muda |
| TC-EST-05 | RN05 / T04 | Integração | Valor limite: 47h59 sem ação | Executar a rotina de expiração sobre reserva `SOLICITADA` há 47h59 | Reserva permanece `SOLICITADA` |
| TC-EST-06 | RN05, RN06 / T04 | Integração | Valor limite: 48h01 sem ação | Executar a rotina de expiração sobre reserva `SOLICITADA` há 48h01 | Reserva vai para `EXPIRADA`; a agenda é liberada |

### 3.5 Anexos

**Requisitos:** RF19, RE-04, RN02. Tipos permitidos: JPEG, PNG, WebP, PDF e DOCX. Limite: 10.000.000 bytes.

| ID | Requisito / Critério | Nível | Técnica | Entrada | Resultado esperado |
|---|---|---|---|---|---|
| TC-ANX-01 | RF19 / CA-12.1 | Integração | Partição: arquivo válido | Prestador envia um JPEG de 1 MB ao próprio serviço | Aceito; metadados registrados em `ARQUIVO` |
| TC-ANX-02 | RE-04 / CA-12.1 | Integração | Valor limite: tamanho máximo | Enviar arquivo de 10.000.000 bytes | Aceito |
| TC-ANX-03 | RE-04 / CA-12.2 | Integração | Valor limite: um acima do máximo | Enviar arquivo de 10.000.001 bytes | Recusado; nenhum metadado criado |
| TC-ANX-04 | RF19 / CA-12.2 | Integração | Partição: tipo não permitido | Enviar um arquivo de texto simples | Recusado; nenhum metadado criado |
| TC-ANX-05 | RN02 | Integração | Partição: recurso alheio | Prestador envia anexo a serviço de outro prestador | HTTP 403 |

### 3.6 Auditoria

**Requisitos:** RF18, RN07, RNF-05.

| ID | Requisito / Critério | Nível | Técnica | Entrada | Resultado esperado |
|---|---|---|---|---|---|
| TC-AUD-01 | RF18, RNF-05 / CA-04.1 | Integração | Partição: transição bem-sucedida | Executar uma transição (por exemplo, aprovar) | Um registro em `HISTORICO_RESERVA` com estado anterior, novo estado, data/hora e executor |
| TC-AUD-02 | RN07 / CA-04.3 | Integração | Partição: tentativa de alteração | Executar `UPDATE` em uma linha do histórico | Operação rejeitada pelo banco |
| TC-AUD-03 | RN07 / CA-04.3 | Integração | Partição: tentativa de remoção | Executar `DELETE` em uma linha do histórico | Operação rejeitada pelo banco |
| TC-AUD-04 | RNF-05 | Integração | Partição: executor automático | Transição por expiração (sistema) | Registro com identificação do sistema como executor |
| TC-AUD-05 | RNF-05 | Integração | Partição: transição que falha | Confirmação recusada por conflito de agenda (HTTP 409) | Nenhum registro de histórico é criado e o estado não muda |

## 4. Omissões deliberadas

Os casos abaixo não foram incluídos nesta versão por limite de escopo e prazo. Todos podem ser acrescentados quando a EVT-09 (#29) for executada.

- **Agenda:** variações de sobreposição parcial (início, fim, contido, idêntico) pertencem à mesma classe de TC-AGD-02. Período inválido, limites do evento, concorrência entre serviços distintos e liberação por cancelamento também ficam de fora.
- **Autenticação:** limite superior da senha (72 bytes), senha com acento e limite de tentativas de login (dívidas técnicas #89, #90 e #91).
- **Autorização:** usuário inativo, escopo do administrador sobre reservas alheias e adulteração do papel no token.
- **Estados:** cancelamento sem justificativa, demais transições T01 a T13 isoladas e rotina de finalização (T12).
- **Anexos:** conteúdo incompatível com a extensão declarada, remoção lógica e acesso por organizadores.
- **Fora do escopo do sistema:** pagamento online e sugestão de nova data (HU-11 e HU-14).

## 5. Dúvidas em aberto

| ID | Dúvida | Divergência encontrada | Efeito nos casos | A decidir por |
|---|---|---|---|---|
| DA-01 | Quais reservas ocupam a agenda? | A RN06 restringe o conflito a reservas `CONFIRMADA`. O banco (`reserva_sem_sobreposicao_ativa`) e a RN08 consideram todas as reservas ativas. | TC-AGD-02 e TC-EST-06 usam a regra do banco. | Responsáveis pelo backend e pela arquitetura |
| DA-02 | A fronteira do intervalo inclui o instante final? | O banco usa intervalo semiaberto `[)`. O diagrama `sequencia-reserva.md` descreve o intervalo como fechado. | TC-AGD-03 usa o comportamento do banco; com intervalo fechado, o resultado seria HTTP 409. | Responsáveis pelo backend e pela arquitetura |
