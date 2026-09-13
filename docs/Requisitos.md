# Requisitos — EventFy

**Fatia do primeiro marco (Tabela 1):** Gestão de Reservas — solicitação e acompanhamento de agendamento entre Organizador e Prestador/Fornecedor.

---

## 1. Glossário do domínio

| Termo | Definição | Fonte |
|---|---|---|
| Organizador | Usuário responsável por planejar um evento e solicitar itens do catálogo (profissionais ou estruturas). | README do projeto — seção "Sobre o Projeto" |
| Prestador | Profissional que oferece serviço avulso para eventos (ex.: garçom, segurança, DJ). | README — seção "Problema"/"Solução" |
| Fornecedor | Responsável por estruturas físicas ofertadas para eventos (ex.: som, iluminação, espaço). | README — seção "Solução" |
| Item do catálogo | Registro publicado por um Prestador ou Fornecedor, contendo descrição, preço e disponibilidade. | README — seção "Funcionalidades", item "Catálogo Unificado" |
| Reserva | Vínculo criado quando um Organizador solicita um item do catálogo para uma data específica. | Apresentação da equipe — Tabela 1 |
| Solicitação de reserva | Ação do Organizador que dá origem a uma Reserva, antes de haver confirmação do Prestador/Fornecedor. | Apresentação da equipe — Tabela 1 |
| Status da reserva | Estado atual do vínculo: *pendente*, *confirmada*, *recusada* ou *cancelada*. | Definição da equipe, validada em sessão de validação (ver seção 7) |
| Disponibilidade | Condição declarada pelo Prestador/Fornecedor indicando se o item pode ser reservado em determinada data. | README — seção "Funcionalidades" |
| Painel do Organizador | Área onde o Organizador acompanha o status de todas as reservas solicitadas para um evento. | README — seção "Funcionalidades" |

---

## 2. Backlog ordenado

| # | Item | Origem | Classificação | Dependência |
|---|---|---|---|---|
| 1 | Cadastro e autenticação de usuário (Organizador / Prestador / Fornecedor) | Apresentação da equipe | Funcional | Nenhuma |
| 2 | Publicação de item no catálogo (Prestador/Fornecedor) | README — "Catálogo Unificado" | Funcional | Item 1 |
| 3 | Busca e filtragem de itens do catálogo | README — "Catálogo Unificado" | Funcional | Item 2 |
| 4 | **Solicitar reserva de um item para uma data** | Apresentação da equipe — Tabela 1 | Funcional | Item 3 |
| 5 | **Prestador/Fornecedor aceitar ou recusar solicitação de reserva** | Apresentação da equipe — Tabela 1 | Funcional | Item 4 |
| 6 | **Organizador acompanhar status das reservas no painel** | README — "Painel do Organizador" | Funcional | Item 4 |
| 7 | Cancelamento de reserva já confirmada | Sessão de validação (achado da equipe) | Funcional | Item 5 |
| 8 | Notificação de mudança de status de reserva | Sessão de validação (achado da equipe) | Funcional | Item 5 |
| 9 | Tempo de resposta do sistema em operações de reserva | Requisito não funcional definido pela equipe | Não funcional | Item 4 |
| 10 | Disponibilidade do sistema (uptime) | Requisito não funcional definido pela equipe | Não funcional | Nenhuma |

*Itens 4, 5 e 6 (em destaque) compõem a fatia escolhida para este marco: Gestão de Reservas.*

---

## 3. Histórias de usuário da fatia escolhida

### HU-01 — Solicitar reserva
**Como** Organizador,
**quero** solicitar a reserva de um item do catálogo para uma data do meu evento,
**para** garantir o serviço/estrutura sem precisar negociar por canais externos.

- **Benefício declarado:** elimina a necessidade de contato manual (WhatsApp, e-mail) para reservar cada item, centralizando o pedido na plataforma.
- **Origem:** README — seção "Problema" (dispersão de fornecedores) e "Solução" (solicitações diretamente pelo sistema).

### HU-02 — Responder a uma solicitação de reserva
**Como** Prestador ou Fornecedor,
**quero** aceitar ou recusar uma solicitação de reserva recebida,
**para** controlar minha agenda e evitar conflitos de data.

- **Benefício declarado:** dá ao Prestador/Fornecedor controle sobre sua disponibilidade sem depender de mensagens trocadas manualmente.
- **Origem:** README — seção "Solução" (negociação e gestão de reservas pelo sistema).

### HU-03 — Acompanhar status das reservas
**Como** Organizador,
**quero** visualizar o status de todas as reservas solicitadas para o meu evento em um único painel,
**para** saber rapidamente o que já está confirmado e o que ainda depende de resposta.

- **Benefício declarado:** reduz o tempo gasto verificando manualmente cada prestador, centralizando a visão do evento.
- **Origem:** README — seção "Funcionalidades", item "Painel do Organizador".

---

## 4. Critérios de aceitação

### HU-01 — Solicitar reserva

**Caminho principal**
```
Dado que estou autenticado como Organizador e visualizo um item disponível no catálogo
Quando eu seleciono uma data disponível e confirmo a solicitação de reserva
Então a reserva é criada com status "pendente"
E o Prestador/Fornecedor correspondente passa a visualizar a solicitação
```

**Recusa (caminho negativo)**
```
Dado que estou autenticado como Organizador
Quando eu tento solicitar uma reserva para uma data marcada como indisponível
Então o sistema impede a solicitação
E exibe uma mensagem informando que a data não está disponível
```

**Efeito persistente**
```
Dado que uma reserva foi solicitada com sucesso
Quando eu recarrego a página ou acesso o sistema em outro momento
Então a reserva continua registrada com status "pendente"
E permanece vinculada ao evento e ao item originalmente selecionado
```

### HU-02 — Responder a uma solicitação de reserva

**Caminho principal**
```
Dado que sou Prestador/Fornecedor e tenho uma reserva com status "pendente"
Quando eu aceito a solicitação
Então o status da reserva muda para "confirmada"
E a data correspondente deixa de estar disponível para novas solicitações
```

**Recusa**
```
Dado que sou Prestador/Fornecedor e tenho uma reserva com status "pendente"
Quando eu recuso a solicitação
Então o status da reserva muda para "recusada"
E a data volta a ficar disponível no catálogo
```

**Efeito persistente**
```
Dado que uma reserva foi confirmada
Quando o Organizador acessa o item novamente em outro momento
Então a data confirmada continua indisponível para outras solicitações
```

### HU-03 — Acompanhar status das reservas

**Caminho principal**
```
Dado que sou Organizador e possuo reservas solicitadas para um evento
Quando eu acesso o painel do evento
Então visualizo a lista de reservas com seus respectivos status (pendente, confirmada, recusada, cancelada)
```

**Recusa (caso sem dados)**
```
Dado que sou Organizador e ainda não solicitei nenhuma reserva para o evento
Quando eu acesso o painel
Então o sistema exibe uma mensagem indicando que não há reservas registradas
```

**Efeito persistente**
```
Dado que uma reserva teve seu status alterado por um Prestador/Fornecedor
Quando eu acesso o painel em um momento posterior
Então o status exibido reflete a alteração mais recente
```

---

## 5. Caso de uso do fluxo principal

**Nome:** Solicitar Reserva
**Ator principal:** Organizador
**Atores secundários:** Prestador/Fornecedor
**Pré-condição:** Organizador autenticado; item do catálogo com disponibilidade cadastrada.

**Fluxo principal**
1. O Organizador acessa a página de um item do catálogo.
2. O sistema exibe as datas disponíveis para o item.
3. O Organizador seleciona uma data e confirma a solicitação de reserva.
4. O sistema registra a reserva com status "pendente".
5. O sistema notifica o Prestador/Fornecedor sobre a nova solicitação.
6. O caso de uso é encerrado com sucesso.

**Fluxos alternativos**

- **A1 — Data indisponível (passo 3):**
  3a. O sistema identifica que a data selecionada não está mais disponível.
  3b. O sistema exibe mensagem de erro e retorna à listagem de datas atualizada.
  3c. O fluxo retorna ao passo 2.

- **A2 — Prestador/Fornecedor recusa (após o passo 5, fora deste caso de uso, mas como continuação do processo):**
  5a. O Prestador/Fornecedor recusa a solicitação.
  5b. O sistema altera o status da reserva para "recusada" e libera a data.
  5c. O sistema notifica o Organizador sobre a recusa.

- **A3 — Sessão expirada (passo 3):**
  3a. O sistema identifica que a sessão do Organizador expirou.
  3b. O sistema solicita nova autenticação.
  3c. Após autenticar, o fluxo retorna ao passo 1.

**Pós-condição:** Reserva registrada com status "pendente" e visível tanto para o Organizador quanto para o Prestador/Fornecedor.

---

## 6. Requisitos não funcionais aplicáveis

| Grandeza | Condição | Valor aceitável | Forma de verificação |
|---|---|---|---|
| Tempo de resposta ao solicitar reserva | Sob carga normal de uso (até 50 usuários simultâneos) | Resposta em até 2 segundos | Teste de carga com ferramenta de medição de tempo de resposta (ex.: k6, JMeter) |
| Disponibilidade do sistema | Em operação contínua | Uptime mínimo de 99% mensal | Monitoramento de uptime via ferramenta de observabilidade |
| Consistência de status de reserva | Após alteração por qualquer ator | Status refletido para todos os atores em até 5 segundos | Teste manual comparando telas do Organizador e do Prestador após alteração |
| Usabilidade do painel de reservas | Para usuário sem treinamento prévio | Localização do status de uma reserva em até 3 cliques | Teste de usabilidade com usuário real, cronometrado |

---

## 7. Restrições e regras de negócio

| Regra/Restrição | Documento de origem |
|---|---|
| Uma reserva só pode ser solicitada para datas marcadas como disponíveis pelo Prestador/Fornecedor. | Apresentação da equipe — Tabela 1 |
| Uma reserva confirmada bloqueia automaticamente a data para novas solicitações do mesmo item. | Sessão de validação (achado da equipe) |
| Apenas o Prestador/Fornecedor dono do item pode aceitar ou recusar uma solicitação recebida. | README — seção "Perfil de Prestador/Fornecedor" |
| O sistema deve ser desenvolvido com controle de versão via Git/GitHub, conforme prática adotada pela equipe. | README — seção "Tecnologias Utilizadas" |
| O projeto é de natureza acadêmica, vinculado à disciplina de Engenharia de Software da UFT — Câmpus Palmas. | README — seção "Sobre o Projeto" |

---
