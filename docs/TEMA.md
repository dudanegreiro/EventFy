# 🎯 Tema — EventFy

> Página do tema do projeto: quem é o usuário real, por que o software precisa existir e a verificação do tema contra os critérios da Tabela 1.5 (Aula 1).

**Estado deste documento:** rascunho para revisão da equipe. Trechos marcados com ⚠️ dependem de informação que a equipe ainda precisa confirmar (conversa com usuário real, critérios da Tabela 1.5).

---

## 📑 Sumário

- [1. Usuário real e como falar com ele](#1-usuário-real-e-como-falar-com-ele)
- [2. Razão do software existir](#2-razão-do-software-existir)
- [3. Verificação contra a Tabela 1.5](#3-verificação-contra-a-tabela-15)

---

## 1. Usuário real e como falar com ele

### 1.1 Usuário principal

> ⚠️ **Hipótese de trabalho.** A descrição abaixo foi construída a partir do problema documentado no [`README.md`](../README.md) e do contexto da equipe (Palmas–TO). Ela só deixa de ser hipótese depois que a conversa registrada na seção 1.4 for realizada.

| Campo | Descrição |
|---|---|
| **Quem é** | Pessoa que organiza, por conta própria e sem agência, eventos de pequeno e médio porte em Palmas: formaturas, confraternizações de empresa, aniversários, casamentos e eventos de associações ou igrejas. |
| **Papel no sistema** | **Organizador** (ver [`REQUISITOS.md`](./REQUISITOS.md), RN01) |
| **Frequência** | Organiza poucos eventos por ano. Não é um profissional da área, então não conhece de antemão os fornecedores da cidade. |
| **O que precisa contratar** | Espaço, som e iluminação, equipe de apoio (as categorias do protótipo em [`prototipo/catalogo.html`](../prototipo/catalogo.html)), além de itens como buffet e tendas. |
| **Como procura hoje** | Indicação de conhecidos, Instagram dos fornecedores, grupos e conversas de WhatsApp. |
| **Dor principal** | Não tem um lugar único para ver o que existe, comparar opções, saber se a data está livre e acompanhar o que já foi pedido. |

### 1.2 Usuário secundário

| Campo | Descrição |
|---|---|
| **Quem é** | Prestador ou fornecedor local (dono de espaço, técnico de som, equipe de apoio). Normalmente é um negócio pequeno, que atende pelo WhatsApp e divulga no Instagram. |
| **Papel no sistema** | **Prestador** (RN02) |
| **Dor principal** | Recebe pedidos soltos em conversas, perde o controle de quais datas já prometeu e responde o mesmo orçamento várias vezes. |

### 1.3 Como falar com o usuário

**Canal.** Conversa presencial ou por chamada curta. Quando não for possível, usar o WhatsApp, porque é o canal que o próprio usuário já usa para organizar eventos.

**Tom.** Informal e curioso, de colega. O usuário não é da área de tecnologia.

- Falar em "evento", "fornecedor", "orçamento", "data" e "pedido". Evitar "reserva", "requisição", "módulo" e "plataforma" até o usuário usar essas palavras.
- Perguntar sobre o que **já aconteceu** ("conta como foi o último evento que você organizou"), e não sobre o que ele "gostaria". Comportamento passado é mais confiável que opinião sobre algo que não existe.
- Não apresentar a solução antes de ouvir o problema. Só mostrar o protótipo depois das perguntas.
- Anotar as palavras exatas que o usuário usa e reaproveitá-las nos rótulos das telas.

**Roteiro de conversa (15 a 20 minutos).**

1. Qual foi o último evento que você organizou? Quando foi e de que tamanho?
2. O que você precisou contratar? Como achou cada fornecedor?
3. Quantos fornecedores você contatou até fechar cada um? Por quais canais?
4. Teve algum que respondeu tarde, não respondeu ou disse que a data já estava ocupada? O que você fez?
5. Como você acompanhava o que já estava combinado e o que ainda estava pendente?
6. Alguma vez alguém deixou de comparecer ou mudou o combinado de última hora?
7. O que foi mais cansativo em todo o processo?
8. *(Mostrar o protótipo)* Em qual tela você não saberia o que fazer? O que está faltando?

**Para o prestador**, trocar as perguntas 2 a 6 por: como chegam os pedidos, como controla as datas já ocupadas, quantos pedidos viram contrato e o que faz quando precisa recusar.

### 1.4 Registro das conversas

> ⚠️ **A preencher pela equipe.** Até este registro ter ao menos uma linha, o usuário da seção 1.1 continua sendo hipótese.

| Data | Entrevistado (perfil, sem dados pessoais) | Quem conduziu | Principais achados | O que mudou no projeto |
|---|---|---|---|---|
| ____/____/______ | | | | |
| ____/____/______ | | | | |
| ____/____/______ | | | | |

---

## 2. Razão do software existir

### 2.1 O problema, de forma concreta

O organizador hoje monta o evento juntando conversas soltas. Para cada serviço ele precisa descobrir quem oferece, perguntar preço e data, esperar resposta e guardar de cabeça (ou em anotações) o que foi combinado. O prestador, do outro lado, recebe pedidos misturados com conversas pessoais e controla a agenda na memória.

Cada ferramenta usada hoje resolve uma parte e deixa o resto descoberto:

| Alternativa atual | Onde ajuda | Onde falha para este problema | Requisito do EventFy que cobre a falha |
|---|---|---|---|
| **WhatsApp** | Resposta rápida, todos já usam | Pedido, orçamento e confirmação ficam misturados na mesma conversa. Não há estado do pedido nem histórico estruturado. | RF16, RF18, RN05, RN07 |
| **Instagram** | Vitrine visual dos fornecedores | Não há busca por categoria, preço ou data. Comparar exige abrir perfil por perfil. | RF05, RF06, RF07 |
| **Planilha** | O organizador controla o que contratou | Atualização manual. Não sabe se o prestador aceitou. Não impede dois pedidos para a mesma data. | RF15, RF16, RNF02, RN06 |
| **Indicação de conhecidos** | Confiança | Alcance limitado. Não há avaliação registrada. | RF17 |

### 2.2 O que o EventFy muda

- O organizador encontra serviços **em um só lugar**, com busca e filtro (RF05, RF06).
- Cada pedido tem **um estado visível** (Solicitada, Em análise, Aprovada, Confirmada etc.), e o organizador não precisa perguntar "e aí, deu certo?" (RF16, RN05).
- O prestador responde de forma estruturada, e uma **recusa sempre vem com motivo** (RF12, RN04).
- O sistema **impede conflito de datas** para o mesmo serviço (RNF02, RN06).
- Tudo fica registrado em **histórico** (RF18, RN07).

### 2.3 Como saber se o software está resolvendo o problema

> ⚠️ As metas numéricas só podem ser definidas depois que a equipe medir a situação atual nas conversas da seção 1.4. Até lá, os indicadores abaixo são o que será medido, não promessas.

| Indicador | Como medir hoje (linha de base) | Como medir com o EventFy | Sentido esperado |
|---|---|---|---|
| Nº de canais usados para contratar um serviço | Perguntar na conversa (pergunta 3) | Fixo em 1 (a plataforma) | ↓ |
| Nº de contatos até fechar um serviço | Perguntar na conversa (pergunta 3) | Nº de solicitações enviadas até uma ser Aprovada | ↓ |
| Tempo entre pedir e saber se foi aceito | Perguntar na conversa (pergunta 4) | Diferença entre os registros `SOLICITADA` e `APROVADA`/`RECUSADA` no histórico (RF18) | ↓ |
| Conflitos de data descobertos tarde | Perguntar na conversa (pergunta 6) | Conflitos bloqueados pelo sistema (CA-RNF02.1) | ↓ |

### 2.4 O que o EventFy **não** pretende resolver

Limites deste tema, para evitar crescimento de escopo (ver também [`PROJETO.md`](./PROJETO.md), seção 5):

- Não é um sistema de pagamento.
- Não substitui a negociação direta quando o usuário quiser conversar com o prestador.
- Não gerencia a execução do evento (cronograma, convidados, ingressos).

> ⚠️ A equipe deve confirmar esta lista. Se algum item for, na verdade, desejado, ele precisa entrar em [`REQUISITOS.md`](./REQUISITOS.md) antes de aparecer aqui como escopo.

---

## 3. Verificação contra a Tabela 1.5

Abaixo apresenta-se a verificação explícita do tema **EventFy** contra os seis critérios para escolha do tema definidos na **Tabela 1.5** do livro-texto da disciplina (p. 29–30).

### 3.1 Verificação

Legenda: ✅ atende · 🟡 atende em parte · ❌ não atende

| # | Critério (Tabela 1.5 do livro) | Atende? | Evidência no repositório | Observação |
|---|---|:---:|---|---|
| 1 | **Usuário real e acessível**<br>*(Elicitação e validação exigem alguém para conversar; usuário imaginário produz requisito imaginário)* | ✅ | Seção 1 deste documento, [`REQUISITOS.md`](./REQUISITOS.md) e [`DESCOBERTA.md`](../DESCOBERTA.md) | Organizadores de eventos locais autônomos e pequenos fornecedores de Palmas–TO (espaço, som, buffet) acessíveis para entrevistas e testes do protótipo. |
| 2 | **Regra de negócio, e não apenas cadastro**<br>*(Sem regra, não há o que modelar, decidir nem testar de forma interessante)* | ✅ | [`REQUISITOS.md`](./REQUISITOS.md) (RN01 a RN07), [`PROJETO.md`](./PROJETO.md) (Seção 13) e [`diagrams/estados-reserva.md`](./diagrams/estados-reserva.md) | O sistema possui regras críticas de domínio: bloqueio de colisão de datas (RN06/RNF02), máquina de estados estrita com 8 estados (RN05), obrigatoriedade de motivo em recusa (RN04) e auditoria imutável (RN07). |
| 3 | **Dado que justifique persistência**<br>*(Consulta, alteração e histórico são o que exercita modelagem e camada de dados)* | ✅ | [`diagrams/modelo-dados.md`](./diagrams/modelo-dados.md) e [`PROJETO.md`](./PROJETO.md) (Seção 8 e 10) | Persistência com integridade relacional, histórico de auditoria imutável (`HISTORICO_RESERVA`), controle de agenda (`DISPONIBILIDADE_SERVICO`) e exclusão lógica (`ativo`). |
| 4 | **Escopo cabível em um semestre**<br>*(O objetivo é atravessar o ciclo inteiro, não construir o sistema mais ambicioso)* | ✅ | Seção 2.4 deste documento e [`PROJETO.md`](./PROJETO.md) (Seção 5) | Escopo estritamente delimitado no fluxo de ponta a ponta (solicitar, analisar, aprovar/recusar, confirmar). Pagamentos e gestão de convidados foram declarados fora de escopo. |
| 5 | **Sem dependência de acesso incerto**<br>*(Integração que depende de credencial ou autorização externa costuma inviabilizar o projeto no meio do caminho)* | ✅ | [`PROJETO.md`](./PROJETO.md) (Seção 16.1, D-05) e [`DESCOBERTA.md`](../DESCOBERTA.md) | O sistema funciona de forma autônoma sem depender de homologações burocráticas de APIs bancárias ou órgãos externos. |
| 6 | **Sem dado pessoal sensível**<br>*(Coletar menos evita risco que a equipe ainda não tem repertório para tratar)* | ✅ | [`REQUISITOS.md`](./REQUISITOS.md) (RF01) e [`diagrams/modelo-dados.md`](./diagrams/modelo-dados.md) | O EventFy coleta apenas dados cadastrais estritamente necessários para contato e operação (nome, e-mail comercial, telefone). Nenhum dado sensível (LGPD art. 5º, II) é coletado. |

### 3.2 Lacunas e Ações

| Critério | Situação | Ação mitigadora | Responsável | Prazo |
|---|---|---|---|---|
| Validação de campo com usuário real | Hipótese estruturada | Realizar sessão presencial/WhatsApp com roteiro da Seção 1.3 para confirmar premissas de tempo e atrito de agenda | Equipe | Iteração 2 |

### 3.3 Evidências disponíveis para citar

Para facilitar o preenchimento da coluna "Evidência", estes são os artefatos que já existem no repositório:

| Para evidenciar... | Cite |
|---|---|
| Problema e público | [`README.md`](../README.md) (seções Problema e Principais Usuários) e [`PROJETO.md`](./PROJETO.md) (seções 2 e 4) |
| Objetivos e escopo | [`PROJETO.md`](./PROJETO.md) (seções 3 e 5) |
| Funcionalidades verificáveis | [`REQUISITOS.md`](./REQUISITOS.md) (RF01 a RF18, com critérios de aceitação) |
| Qualidade e restrições | [`REQUISITOS.md`](./REQUISITOS.md) (RNF01 a RNF06) |
| Regras do domínio | [`REQUISITOS.md`](./REQUISITOS.md) (RN01 a RN07) |
| Fluxos de uso | [`PROCESSOS-NEGOCIO.md`](./PROCESSOS-NEGOCIO.md) |
| Domínio e dados | [`diagrams/modelo-dominio.md`](./diagrams/modelo-dominio.md) e [`diagrams/modelo-dados.md`](./diagrams/modelo-dados.md) |
| Ciclo de vida da reserva | [`diagrams/estados-reserva.md`](./diagrams/estados-reserva.md) |
| Interface | [`../prototipo/`](../prototipo) |
| Conferência entre artefatos | [`CONFERENCIA_CRUZADA.md`](./CONFERENCIA_CRUZADA.md) |
| Validação com usuário real | Seção 1.4 deste documento (ainda sem registros) |
