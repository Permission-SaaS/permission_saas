# Permission SaaS

SaaS de gerenciamento de permissões por projeto — um cliente se cadastra, assina um
plano (pagamento simulado) e recebe uma **ApiKey**. Sistemas externos usam essa
ApiKey para validar, em um único endpoint, se uma requisição pode acessar uma rota
com determinado cargo.

Um **monolito modular** com um serviço extraído dele, em Java 21 / Spring Boot 4.1.0,
construído como projeto de longo prazo ao longo da Pós-Graduação: cada disciplina evolui
este mesmo código em vez de começar um projeto do zero. O que cada uma acrescentou está em
[Evolução](#evolução).

> **Repositórios.** Desde 05/10/2026, cada aplicação tem repositório próprio na organização
> [Permission-SaaS](https://github.com/Permission-SaaS), e este é o repositório guarda-chuva: fixa a
> versão de cada uma como submódulo, sobe o sistema inteiro e guarda a documentação do sistema e as
> tags (ADR-015). **As versões avaliadas continuam nas tags**, no layout de pasta única da época:
> [`etapa-4`](https://github.com/Permission-SaaS/permission_saas/tree/etapa-4) (Spring Boot) e [`arq-etapa-4`](https://github.com/Permission-SaaS/permission_saas/tree/arq-etapa-4) (Microsserviços).

**Stack:** Java 21 · Spring Boot 4.1.0 · Spring Data JPA · PostgreSQL 16 · Flyway · Spring Modulith · Spring Cloud OpenFeign · Spring Cloud Config · RabbitMQ · Spring Batch · Docker Compose · Maven

---

## Como rodar

Basta Docker com Docker Compose (v2): o build das aplicações acontece dentro das imagens.

```bash
git clone --recurse-submodules https://github.com/Permission-SaaS/permission_saas.git
cd permission_saas
cp .env.example .env
docker compose up -d --build
```

| Container            | Porta | Papel                                                        |
| -------------------- | ----- | ------------------------------------------------------------ |
| `permission-service` | 8080  | aplicação principal (monolito modular)                       |
| `audit-service`      | 8081  | trilha de auditoria, extraída como serviço                   |
| `config-server`      | 8888  | configuração centralizada, lida de `config-repo/`            |
| `postgres`           | 5432  | banco da aplicação principal                                 |
| `audit-postgres`     | 5433  | banco do `audit-service`                                     |
| `rabbitmq`           | 5672  | broker de mensagens; painel em http://localhost:15672 (`saas`/`saas123`) |

```bash
curl http://localhost:8080/ping                  # pong
docker compose ps                                # os seis como "healthy"
```

O caminho feliz completo (cliente → plano → ApiKey → projeto → validação → auditoria) está na pasta
`Fluxo completo` da coleção do Postman em [`docs/postman/`](docs/postman/); os endpoints estão no
`API.md` [da aplicação principal](https://github.com/Permission-SaaS/permission_saas_api/blob/main/docs/API.md) e [do `audit-service`](https://github.com/Permission-SaaS/permission_saas_audit/blob/main/docs/API.md). Profiles, variáveis de ambiente, rodar fora do Docker, debug,
testes e o que fazer com a porta 5432 ocupada: [`docs/RUNNING.md`](docs/RUNNING.md).

```
permission_saas/                guarda-chuva (este repositório)
├── permission_saas_api/        submódulo: aplicação principal (monolito modular)
├── permission_saas_audit/      submódulo: trilha de auditoria extraída como serviço
├── permission_saas_config/     submódulo: configuração centralizada (Spring Cloud Config)
├── permission_saas_front/      submódulo: front-end, ainda sem código
├── config-repo/                os arquivos de configuração que o config-server serve
├── docker-compose.yml          orquestra as aplicações e os bancos
├── docker/                     script de inicialização do Postgres da aplicação principal
└── docs/                       documentação do sistema e de cada disciplina
```

Cada aplicação é um projeto Maven independente, com seu próprio `pom.xml`, `mvnw` e `Dockerfile`, no
seu repositório: [`permission_saas_api`](https://github.com/Permission-SaaS/permission_saas_api), [`permission_saas_audit`](https://github.com/Permission-SaaS/permission_saas_audit) e
[`permission_saas_config`](https://github.com/Permission-SaaS/permission_saas_config) (ADR-008 e ADR-015 em [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)).

---

## Arquitetura

A aplicação principal é um monolito modular: um deploy só, organizado por módulo de domínio,
cada um com `domain` / `application` / `infrastructure` / `api`. Os módulos só conversam por use
cases ou eventos, nunca pelo repositório de outro módulo. Essa fronteira é verificada pelo Spring
Modulith: `./mvnw test` (em `permission_saas_api/`) falha se alguém importar um pacote interno de
outro módulo. Camadas e regras de comunicação: o [`ARCHITECTURE.md` da aplicação principal](https://github.com/Permission-SaaS/permission_saas_api/blob/main/docs/ARCHITECTURE.md);
visão do sistema e ADRs: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

### Módulos e responsabilidades

**`identity` — quem é o cliente.** Cadastra e consulta o `Client`, a empresa que
contrata o SaaS. É a porta de entrada: sem um cliente cadastrado não há assinatura,
e sem assinatura não há ApiKey. Não conhece plano, projeto nem permissão.

**`billing` — o que o cliente comprou.** Cuida de `Plan` e `Subscription` e é o único
lugar que emite e ativa uma `ApiKey`. Concentra também o pagamento, hoje simulado
atrás da porta `PaymentGateway`. Responde a uma pergunta que o resto do sistema faz o
tempo todo: *esta ApiKey existe e está ativa?*

**`project` — o que o cliente configurou.** Guarda o `Project` do cliente, seus
cargos (`Role`), suas rotas (`Route`) e, entre eles, o `RoleRoute` — a concessão que
diz quais rotas cada cargo alcança, com histórico de concessão e revogação. É aqui
que vive a regra de negócio que a validação consulta.

**`permission` — o núcleo.** Expõe o único endpoint que o cliente chama em produção
(`POST /validate-permission`) e decide se uma requisição passa. A decisão é uma
cadeia de responsabilidade: cada handler verifica uma preocupação e delega adiante.
Não tem tabela própria — pergunta aos outros módulos.

**`audit` — o que aconteceu.** Registra cada validação de permissão em uma trilha
append-only. Nasce de um evento publicado pelo `permission` e não devolve nada a
ninguém. Desde 30/09/2026 não guarda nada localmente: publica cada evento na fila
`audit.events` do RabbitMQ, consumida pelo `audit-service` (porta 8081, banco próprio), e
repassa cada consulta a ele via OpenFeign. Se o serviço cair, a validação de permissão
segue funcionando, o evento espera na fila até ele voltar, e a consulta responde `503`.

**`shared` — o que é de todos.** Configuração de segurança e Swagger, `Mapper<I,O>`,
`DomainException` e o `GlobalExceptionHandler` que centraliza o tratamento de erro.
Não tem regra de negócio.

### Dependências entre os módulos

Medido pelos imports entre pacotes de módulos diferentes:

```
identity   → shared
billing    → identity, shared
project    → shared
permission → billing, project, shared
audit      → permission (apenas o record do evento), shared
```

Duas dependências concretas, ambas no caminho crítico da validação de permissão:

**`permission` → `billing`.** Para aceitar uma requisição é preciso saber se a ApiKey
existe e está ativa. O `permission` não enxerga a tabela do `billing`: declara a porta
`ApiKeyValidator` no próprio domínio, e o adapter `BillingApiKeyValidator` chama o use
case `FindActiveApiKeyByPlainKeyUseCase`. Quem consome é o `ApiKeyValidationHandler`.

**`permission` → `project`.** Para decidir se o cargo alcança a rota é preciso
consultar as concessões do projeto. Mesmo desenho: porta `RouteAccessChecker` no
domínio, adapter `ProjectRouteAccessChecker` chamando `CheckRouteAccessUseCase`, e o
`RoleRouteValidationHandler` como consumidor.

As duas são **síncronas e acontecem dentro da requisição**: se qualquer uma falhar, a
validação não tem resposta para dar. É exatamente o que as separa do `audit`.

Uma terceira dependência, de natureza diferente: **`audit` → `permission`**. O
`ValidatePermissionUseCase` publica um `PermissionValidatedEvent` e segue seu caminho;
o `AuditLogListener` reage a ele. A seta aponta para dentro do `audit` e nada volta.

### Candidato a serviço independente: `audit`

> Análise da etapa 1. A extração foi feita na etapa 2: o `audit-service/` grava e
> consulta a trilha no próprio banco, e o módulo `audit` do monolito virou só um
> cliente dele (ADR-010 em [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)).

**Responsabilidade.** Registrar a trilha de auditoria das validações de permissão —
projeto, rota, cargo, data, resultado e motivo — e permitir consultá-la depois.

**Quem depende dele hoje.** Nenhum módulo. É a resposta incômoda e é justamente o
argumento: `grep` por imports de `com.saas.permissions.audit` fora do próprio módulo
não retorna nada. O acoplamento existe na direção oposta e por evento — um único
publisher (`ValidatePermissionUseCase`) e um único consumidor (`AuditLogListener`),
sem valor de retorno. Nenhuma regra de negócio lê da auditoria para decidir algo.

**Por que poderia rodar separado.**

- A trilha é *append-only*: grava-se muito e lê-se raramente, para conferência.
- O acoplamento já é o mais fraco do projeto — um evento assíncrono por natureza,
  hoje entregue em processo.
- Os dados são próprios (`audit_events`) e **sem chave estrangeira** para as tabelas
  dos outros módulos, então separar o banco não quebra integridade referencial.
- Cresce por um motivo diferente do resto: cada validação de permissão gera um
  registro, enquanto o cadastro de projetos é esporádico. Escala independente.

**Por contraste, o que não deve sair.** Extrair `billing` seria o oposto: o
`ApiKeyValidationHandler` depende dele *dentro* da requisição, e a separação
transformaria uma chamada de método em ponto de falha no caminho crítico.

### Consultas Spring Data

Além do CRUD do `JpaRepository`, as consultas que o domínio pede:

- **`project` — consultas derivadas.** Projetos ativos por nome
  (`findByDeletedAtIsNullAndNameContainingIgnoreCaseOrderByNameAsc`), por cliente
  (`findByClientIdAndDeletedAtIsNullOrderByCreatedAtAsc`) e a busca por id que
  ignora os excluídos (`findByIdAndDeletedAtIsNull`).
- **`audit` — JPQL com filtros opcionais** (desde 30/09/2026 no `audit-service`, para
  onde a trilha foi extraída). `search` filtra a trilha por tipo,
  projeto e período; `searchDenied` devolve só as validações negadas, por projeto e
  período, apoiada no índice parcial `idx_audit_events_denied`. Na disciplina anterior
  esses filtros rodavam em memória; como a trilha só cresce, desceram para o banco —
  decisão e detalhes no ADR-009 de [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

---

## Serviço independente: `audit-service`

A extração da etapa 2. O porquê da escolha está em
[Candidato a serviço independente: `audit`](#candidato-a-serviço-independente-audit).

|                                         |                                                                                                                                                                                                                                                                                                                       |
| --------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Nome**                                | `audit-service` — repositório [`permission_saas_audit`](https://github.com/Permission-SaaS/permission_saas_audit), porta 8081, banco próprio `audit_db` (porta 5433)                                                                                                                                                                                                                           |
| **Responsabilidade principal**          | Guardar a trilha de auditoria das validações de permissão e permitir consultá-la por tipo, projeto, período e resultado                                                                                                                                                                                              |
| **O que saiu da aplicação principal**   | A persistência da trilha: entidades JPA com herança `SINGLE_TABLE`, repositórios, consultas JPQL, o arquivo `logs/audit-events.txt` e a tabela `audit_events`, apagada pela migration `V10`. O módulo `audit` do monolito ficou só como cliente do serviço                                                       |
| **Motivo**                              | Nenhum módulo depende da auditoria para decidir algo: o `permission` avisa o que aconteceu e não espera resposta. Os dados não têm chave estrangeira para outras tabelas e crescem a cada validação, num ritmo próprio. E auditoria serve a qualquer sistema, não só a este — ver a [reflexão](#etapa-2--separação-do-audit-service) |

**API REST.** `POST /audit-events/permission-checks` registra uma validação (`201`/`400`) e
`GET /audit-events` consulta a trilha com filtros opcionais (`200`/`400`). O contrato são DTOs
próprios nos dois lados; nenhuma entidade JPA atravessa a rede. Swagger em
`http://localhost:8081/swagger-ui/index.html`; detalhes no [`API.md` do serviço](https://github.com/Permission-SaaS/permission_saas_audit/blob/main/docs/API.md).

**Comunicação.** Cada operação usa o estilo que combina com ela. A **consulta** é REST: a
aplicação principal chama o serviço pelo cliente OpenFeign `AuditClient`, atrás da porta
`AuditTrail`, porque quem consulta precisa da resposta na hora. A **gravação**, desde a etapa 4,
é uma mensagem na fila `audit.events` do RabbitMQ, atrás da porta `AuditEventPublisher`, porque
ninguém espera por ela. Nenhum controller conhece o Feign nem o RabbitMQ, e os endereços vêm da
configuração, nunca do código Java.

```
Cliente HTTP
↓
permission-service (8080)
├── PermissionController → ValidatePermissionUseCase → publica PermissionValidatedEvent
│                                                          ↓
├── AuditLogListener (Observer, @Async) → porta AuditEventPublisher → RabbitMQ: fila audit.events
│                                                                          ↓ mensagem
└── AuditEventController → SearchAuditEventsUseCase → porta AuditTrail → AuditClient (@FeignClient)
                                                                          ↓ HTTP
                                                     audit-service (8081)
                                                     ├── AuditMessageListener (consome a fila)
                                                     ├── AuditEventController (GET /audit-events)
                                                     └── use cases → AuditEventRepository → PostgreSQL audit_db
```

**Falha de comunicação.** Cada operação trata a falha de um jeito:

- **Gravação:** a validação de permissão responde normalmente, sem esperar a auditoria. Com o
  `audit-service` fora do ar, a mensagem **espera na fila** e é gravada quando ele volta. Só com o
  próprio RabbitMQ fora do ar o evento se perde, com `WARN ... Audit event lost: ...` no log.
- **Consulta:** o cliente desiste em 1s para conectar e 2s para ler, e o `GET /audit-events`
  responde `503` com `{"status":503,"error":"Service Unavailable","message":"Audit service is unavailable",...}`.
  O detalhe do Feign só vai para o log.

**Como testar** (coleção em [`docs/postman/`](docs/postman/)):

| Demonstração                         | Pasta do Postman                                     |
| ------------------------------------ | ---------------------------------------------------- |
| API do serviço isolada               | `audit-service (8081)`                               |
| Operação pela aplicação principal    | `Fluxo completo` (requisições 9 a 14) e `Audit`      |
| Serviço indisponível                 | `audit-service fora do ar` — o roteiro está na descrição da pasta |

---

## Reflexões arquiteturais

### Etapa 2 — separação do `audit-service`

**Qual funcionalidade foi separada da aplicação principal?** A trilha de auditoria:
registrar cada validação de permissão (projeto, rota, cargo, resultado e motivo) e
consultar esse histórico depois.

**Por que ela foi escolhida?** Era o módulo mais desacoplado do monolito: ninguém
depende dele, ele só recebe um evento e não devolve nada. Separar primeiro a parte mais
solta segue o *Strangler Fig*: tirar uma capacidade de cada vez do monolito, sem
reescrevê-lo inteiro. O `billing`, pelo contrário, está dentro da requisição de validação
e, se fosse separado, viraria um ponto de falha no caminho crítico.

**O que ficou mais complexo depois da separação?**

- A aplicação principal precisou ser reestruturada para atender o novo serviço. O código
  saiu da raiz para `permission-service/`. O módulo `audit` perdeu a persistência e virou
  cliente, com um `@FeignClient`, um adapter e DTOs que espelham o contrato do serviço.
  Esse contrato agora existe nos dois lados e precisa mudar junto.
- Passou a haver outro sistema para cuidar: dois projetos, dois bancos e duas aplicações
  para subir, depurar e manter.
- A aplicação principal precisa decidir o que fazer com o retorno ou a falha do serviço.
  Uma chamada de método virou chamada de rede, que pode demorar, falhar ou nem responder.
  Cada operação ganhou uma decisão própria: a gravação engole a falha, a consulta devolve
  `503`.
- Foi preciso configurar a aplicação principal para a indisponibilidade: URL externa,
  timeouts e tratamento de erro que não vaza detalhe interno.

**O que aconteceria com a funcionalidade principal caso o novo serviço ficasse
indisponível?** A validação de permissão, que é o produto, continua funcionando. Ela
responde normalmente, no máximo uns 3 segundos mais lenta por causa dos timeouts, mas o
evento daquela validação se perde. A consulta da trilha fica fora do ar e responde `503`.
A perda de eventos é a limitação aceita nesta etapa; a fila do RabbitMQ, na etapa 4,
existe para resolvê-la.

**A funcionalidade realmente precisa permanecer como um serviço independente?** Sim. Olhando
só para o Permission SaaS, o módulo `audit` dentro do monolito dava conta: funcionou assim
na disciplina anterior, e a separação trouxe os custos listados acima sem ganho funcional
para este sistema sozinho. O que justifica o serviço é ele servir de base para outros
projetos. Auditoria é útil para qualquer sistema: mostra o que acontece de certo e de errado
nas aplicações e apoia a conformidade com a LGPD, que pede o registro das operações de
tratamento de dados pessoais. Com esse horizonte, desacoplar a auditoria do projeto
principal foi uma escolha válida. A direção está registrada em
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) → "Direção futura".

### Etapa 3 — configuração e execução

**Quais configurações da aplicação podem variar entre ambientes?** O endereço, o usuário e a senha
de cada banco; o endereço do `audit-service`; a porta de cada aplicação; os segredos (usuário do
Swagger, chaves do Google e do JWT); e o comportamento de execução, como o log de SQL e o debug
remoto. O mesmo banco está em `localhost:5432` na máquina e em `postgres:5432` dentro do Compose.

**Quais dessas configurações foram externalizadas?** Todas. Nenhuma fica no código Java:

| Configuração                    | Onde fica                                                                                         |
| ------------------------------- | ------------------------------------------------------------------------------------------------- |
| Profile ativo                   | `SPRING_PROFILES_ACTIVE`: `dev` por padrão, `prod` no Compose                                     |
| Porta                           | `SERVER_PORT`, com valor padrão no `application.yml`                                              |
| Endereço do banco               | `dev`: `DB_URL`, com padrão `localhost`; `prod`: Config Server (`config-repo/<serviço>-prod.yml`) |
| Usuário e senha do banco        | `DB_USERNAME` / `DB_PASSWORD`; no `prod`, sem valor padrão                                        |
| Endereço do `audit-service`     | `dev`: `AUDIT_SERVICE_URL`; `prod`: Config Server                                                 |
| Log de SQL                      | `application-dev.yml` (ligado) e `config-repo/application-prod.yml` (desligado)                   |
| Segredos (Swagger, Google, JWT) | variáveis de ambiente; no Compose, vêm do `.env`                                                  |
| Debug remoto                    | `JAVA_TOOL_OPTIONS` no `docker-compose.yml`, fora da imagem                                       |

Ficaram de fora os timeouts do Feign, iguais em todo ambiente, e as senhas dos bancos de
desenvolvimento, escritas no `docker-compose.yml`; num ambiente real viriam de um cofre de segredos.

**Por que um serviço não deve acessar diretamente o banco de outro serviço?** Tecnicamente funciona,
mas é um erro de arquitetura:

- **Confiabilidade dos dados:** quem grava por fora pula as regras do dono, como a validação do
  `POST /audit-events/permission-checks`.
- **Dois serviços presos ao mesmo banco:** se a aplicação principal lesse `audit_events`, renomear
  uma coluna no `audit-service` a quebraria, e os dois deixariam de evoluir separados, que foi o
  motivo da extração.
- **Segurança:** com um dono só, a API é a barreira e os DTOs são o contrato. A aplicação principal
  nem tem a senha do `audit_db`.

**Qual problema o Docker resolve no projeto?** O "na minha máquina funciona". A imagem leva a
aplicação junto com o ambiente de que ela precisa (o Java 21 e o jar) e roda igual em qualquer
máquina, isolada no seu container. Na prática: o PostgreSQL instalado na máquina do autor ocupa a
5432 e os bancos do projeto rodam sem conflito com ele; e não é preciso ter JDK nem Maven para subir
a solução, porque o build acontece dentro da imagem.

**Qual é a função do Docker Compose?** Orquestrar os containers localmente. Um arquivo descreve a
solução inteira (os cinco containers, as variáveis, as portas, os volumes e a rede interna em que eles
se acham pelo nome, como `audit-service:8081`), e `docker compose up` sobe tudo na ordem certa: os
serviços só partem depois que o Config Server e o banco de cada um respondem ao healthcheck. O
Compose centraliza *como a solução roda*; *o que cada serviço configura* fica com o Config Server.

**Qual problema uma configuração centralizada procura resolver?** Um sistema tem vários ambientes
(desenvolvimento, testes, homologação, produção), cada um com sua configuração. Espalhada, mudar uma
integração exige mexer em cada serviço; centralizada, cada ambiente fica organizado em arquivos e
cada serviço busca a sua na subida. No projeto, `config-repo/application-prod.yml` configura os dois
serviços de uma vez, e uma mudança vale depois de reiniciar o serviço, sem imagem nova. O
desenvolvimento ficou de fora de propósito, para não exigir o Config Server na máquina (ADR-012), e
segredos não vão para lá, porque ele entrega a configuração em texto puro.

### Etapa 4 — comunicação assíncrona e processamento em lote

**Qual operação foi escolhida para comunicação assíncrona?** A gravação da trilha de auditoria. A
cada `POST /validate-permission`, a aplicação principal publica a validação na fila `audit.events` do
RabbitMQ, e o `audit-service` consome e grava.

**Por que essa operação não precisa necessariamente ser concluída durante a requisição original?**
Porque a auditoria não decide nada. Quem chamou a API precisa saber se o acesso foi permitido ou
negado, e essa resposta não depende de a validação já estar registrada. A auditoria é um subprocesso
independente: precisa acontecer, mas não antes da resposta. Por isso a validação responde sem esperar,
mesmo com o `audit-service` fora do ar.

**O que acontece com a mensagem caso o consumidor esteja temporariamente indisponível?** Ela fica na
fila `audit.events`, no estado *Ready* (pronta, esperando entrega). Quando o `audit-service` volta, o
broker entrega o que esperava e ele grava tudo. Na etapa 2, com a gravação por HTTP, esse evento se
perdia. A fila é durável e as mensagens são persistentes, então sobrevivem até a um restart do broker.
Uma mensagem que não pode ser gravada (tipo desconhecido, dados inválidos) é tentada 3 vezes e vai para
a fila `audit.events.dlq`, em vez de travar as outras.

**Qual funcionalidade foi escolhida para processamento em lote?** A importação das rotas de um projeto
a partir de um CSV (`POST /projects/{projectId}/routes/import`).

**Por que essa funcionalidade é adequada para Batch?** Um cliente com muitas rotas levaria muito tempo
cadastrando uma a uma. Se ele exporta as rotas do projeto dele para um CSV, o Batch importa todas de uma
vez: lê o arquivo linha a linha, normaliza e descarta o que não serve, e grava em lotes de 10, cada lote
numa transação. No fim, há um resumo (no arquivo de exemplo, 16 lidas, 12 importadas e 4 descartadas) e
o registro da execução nas tabelas do Spring Batch. É um conjunto de dados conhecido de antemão,
processado do começo ao fim: o caso típico de lote.

**Qual a diferença entre a mensageria e o Batch?** A mensageria é comunicação assíncrona entre
componentes: um evento por vez, enviado quando acontece, para outro serviço tratar quando puder. O
Batch é processamento estruturado sobre um conjunto de dados: a coleção inteira, lida e gravada em
pedaços controlados, com início, fim e resumo. A fila liga dois serviços; o Batch roda dentro de um.

**Em quais situações da aplicação seria mais adequado utilizar REST, mensageria ou Batch?**

- **REST** quando quem chama precisa da resposta na hora para seguir: a validação de permissão
  (`POST /validate-permission`), que diz se o acesso passa, e a consulta da trilha (`GET /audit-events`).
- **Mensageria** quando uma parte do sistema pode ser desacoplada e feita depois, por outro serviço: a
  gravação da auditoria. Pelo mesmo motivo, serviria para avisar o cliente por e-mail quando a
  assinatura vencer, sem segurar a requisição que originou o aviso.
- **Batch** para importar ou migrar dados em volume, lendo arquivos grandes: a importação de rotas, e a
  migração dos eventos antigos de auditoria para o `audit_db`, que o ADR-010 aponta como o caminho num
  sistema em produção.

---

## Padrões de projeto

| Padrão                 | Onde                                                                                   | Status |
| ----------------------- | -------------------------------------------------------------------------------------- | ------ |
| Factory Method          | `ApiKeyFactory` — centraliza a estratégia de geração da ApiKey                   | ✅     |
| Adapter                 | `FakePaymentGatewayAdapter` — adapta o gateway simulado à porta `PaymentGateway` | ✅     |
| Chain of Responsibility | Handlers de validação de permissão, um por preocupação                            | ✅     |
| Observer                | `AuditLogListener` — reage à validação de permissão sem acoplar os módulos       | ✅     |
| Builder                 | `ProjectBuilder` — descartado: `@Builder` do Lombok mais `addRole`/`addRoute` já cobrem o caso | ⛔     |

Onde cada padrão vive, por que foi escolhido e como estender:
[`PATTERNS.md` da aplicação principal](https://github.com/Permission-SaaS/permission_saas_api/blob/main/docs/PATTERNS.md). Mapeamento dos 5 princípios SOLID:
[`ARCHITECTURE.md` da aplicação principal](https://github.com/Permission-SaaS/permission_saas_api/blob/main/docs/ARCHITECTURE.md#princípios-solid).

---

## Escopo

**Implementado:** cadastro de cliente, assinatura de plano com pagamento simulado e
geração de ApiKey, middleware de validação de permissão aplicando a regra real
(o cargo precisa de uma concessão ativa sobre a rota), CRUD de projeto/cargo/rota com
histórico de concessão e revogação, e trilha de auditoria em banco e arquivo texto —
desde a etapa 2 no [`audit-service`](#serviço-independente-audit-service), chamado por
OpenFeign. Desde a etapa 3, as três aplicações rodam em containers com Docker Compose, com
profiles `dev`/`prod` e configuração centralizada num Config Server. Desde a etapa 4, a gravação
da auditoria vai por mensagem (RabbitMQ), e o evento espera na fila se o `audit-service` cair, e
um projeto pode importar rotas em lote a partir de um CSV, com Spring Batch
(`POST /projects/{projectId}/routes/import`).

**Limitações conhecidas:** o `TokenValidationHandler` é um stub documentado que sempre concede
(depende de um 2º fator de autenticação), e a validação da ApiKey não confere o dono do projeto nem
evita comparar a chave por bcrypt com todas as chaves ativas
([`DOMAIN.md` da aplicação principal](https://github.com/Permission-SaaS/permission_saas_api/blob/main/docs/DOMAIN.md) → "Limitações conhecidas").

**Trabalho futuro:** gateway de pagamento real, autenticação/JWT com Spring Security,
exportação CSV/JSON, front-end, `userId` no evento de auditoria, uma aplicação
cliente de demonstração consumindo o `POST /validate-permission` e a renomeação desse
endpoint para `POST /permissions/validate`, que alinharia o recurso ao restante da API
(ver a nota de contrato no [`API.md` da aplicação principal](https://github.com/Permission-SaaS/permission_saas_api/blob/main/docs/API.md)).

---

## Evolução

O mesmo código atravessa as disciplinas da Pós-Graduação. Cada uma tem sua pasta em
`docs/`, com o enunciado do professor e o plano daquela matéria — o que permite
distinguir o que já existia do que foi construído em cada momento.

| Disciplina                                                                                                             | Período        | O que acrescentou                                                                                                                                            | Marcos                                           |
| ---------------------------------------------------------------------------------------------------------------------- | --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------ |
| [Clean Code e Padrões de Projeto](docs/clean_code_e_padroes_de_projeto/PLAN.md)                                        | até 05/07/2026 | Módulos`shared`, `identity`, `billing` e `permission`; Factory Method, Adapter e Chain of Responsibility; fronteiras de módulo com Spring Modulith | —                                               |
| [Desenvolvimento de aplicações Java com Spring Boot](docs/desenvolvimento_de_aplicacoes_java_com_spring_boot/PLAN.md) | até 31/08/2026 | Módulos `project` e `audit`, CRUD REST completo, relacionamentos e herança JPA, leitura de arquivos texto | tags `etapa-1` … `etapa-4` |
| [Arquiteturas avançadas de software com microsserviços e Spring Framework](docs/arquiteturas_avancadas_de_software_com_microsservicos_e_spring_framework/PLAN.md) | até 05/10/2026 | `audit` extraído como serviço independente, OpenFeign, Config Server, banco por serviço, RabbitMQ e Spring Batch | tags `arq-etapa-1` … `arq-etapa-4` |

As tags desta disciplina usam o prefixo `arq-` porque `etapa-1` … `etapa-4` já
apontam para a evidência da disciplina anterior e não podem ser movidas.

Em 05/10/2026, entre uma disciplina e outra, cada aplicação ganhou repositório próprio (ADR-015).
Todas as tags acima ficam neste repositório e continuam apontando para o código como ele foi
entregue.

O relatório escrito da primeira disciplina foi entregue como PDF no Moodle e não está
versionado aqui.

---

## Documentação

A raiz de `docs/` guarda a documentação **do sistema como um todo** — cumulativa, descrevendo o
sistema como ele está hoje:

| Arquivo                                        | Conteúdo                                                                          |
| ---------------------------------------------- | --------------------------------------------------------------------------------- |
| [`docs/RUNNING.md`](docs/RUNNING.md)           | Como clonar, subir, configurar (profiles, variáveis, Config Server), depurar e testar |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Os repositórios, como os serviços conversam e o log de decisões (ADRs)            |
| [`docs/DER.pdf`](docs/DER.pdf)                 | Diagrama entidade-relacionamento                                                  |
| [`docs/postman/`](docs/postman/)               | Coleção Postman com todos os endpoints dos três serviços                          |

Cada aplicação documenta o próprio interior no seu repositório:

| Repositório                              | Documentação                                                                                                      |
| ---------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| [`permission_saas_api`](https://github.com/Permission-SaaS/permission_saas_api)       | `ARCHITECTURE.md` (módulos e camadas), `DOMAIN.md`, `API.md`, `PATTERNS.md` e `TEST-ARCHITECTURE.md`, em `docs/` |
| [`permission_saas_audit`](https://github.com/Permission-SaaS/permission_saas_audit)     | `ARCHITECTURE.md`, `DOMAIN.md` e `API.md` (endpoints e contrato da fila), em `docs/`                              |
| [`permission_saas_config`](https://github.com/Permission-SaaS/permission_saas_config)    | `README.md`                                                                                                       |
| [`permission_saas_front`](https://github.com/Permission-SaaS/permission_saas_front)      | `README.md` (front-end, stack a definir)                                                                          |

O que é específico de uma disciplina — enunciado e planejamento — fica na pasta dela,
listada em [Evolução](#evolução).

---

## Uso de IA

A disciplina incentiva o uso de IA, desde que citado. Usei o **Claude Code**, da Anthropic (modelos da
família Claude Opus), no terminal e no VS Code, como um par de programação. Ele me ajudou a tirar
dúvidas, a ver um exemplo antes de implementar algo que eu ainda não conhecia e a assumir as tarefas
mecânicas, enquanto eu me concentrava na arquitetura e no domínio do projeto.

| Parte | Como foi feito |
| ----- | -------------- |
| Arquitetura e decisões | As decisões foram minhas, discutidas com a IA: qual funcionalidade extrair (o `audit`), RabbitMQ como broker, o envelope genérico da mensagem, os nomes das tags e os cortes de escopo. A IA ajudou a confrontar o plano com a rubrica e registrou as decisões no `PLAN.md` e nos ADRs |
| Extração do `audit-service` | Delegada por ser mecânica: copiar o módulo, ajustar pacotes e imports. A IA executou e eu revisei |
| OpenFeign | Feito em conjunto: escrevi partes da integração e deixei com a IA os detalhes repetitivos |
| Dockerfiles e Compose | Eu já tinha um `Dockerfile` como base e deleguei a adaptação e o Compose, para me concentrar na arquitetura e no domínio. A IA explicou cada linha depois |
| Profiles e Config Server | Eu nunca tinha usado o Config Server. Li a documentação, tirei as dúvidas com a IA e, como a implementação é simples depois de entendida, pedi que ela a fizesse |
| RabbitMQ | A IA implementou o produtor e o consumidor. Acompanhei o fluxo no painel do RabbitMQ (conexões, fila e consumidor) até entender o papel de cada peça: produtor, broker, fila e consumidor |
| Spring Batch | Eu sabia como fazer uma importação em massa, porque já tinha feito em PHP, mas não conhecia o Spring Batch. A IA implementou o job e me explicou cada componente: reader, processor, writer, chunk e job |
| Reflexões arquiteturais | As respostas são minhas. A IA redigiu o texto a partir delas, e eu revisei |
| Testes e documentação | Testei o fluxo completo pela coleção do Postman. A IA rodou a coleção inteira (newman) contra a solução em containers, incluindo as quedas de serviço, e redigiu o README, os ADRs, o `API.md` e o `RUNNING.md` |

Revisei cada mudança antes do commit e levei à IA toda dúvida que tive, até entendê-la. Algumas
correções partiram dessa revisão, como tirar a validação do upload do controller (`RouteImportRequest`)
e enxugar este README. Como os resultados da IA podem ter erros, cada mudança também passou por build,
testes automatizados e pela coleção do Postman antes do commit.

---

## Autor

Jairo Williams Guedes Lopes Neto
