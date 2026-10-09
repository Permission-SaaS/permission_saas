# Arquitetura — Permission SaaS

## Ideia central

O sistema é **um monolito modular mais serviços extraídos dele**, cada aplicação no seu repositório da organização [Permission-SaaS](https://github.com/Permission-SaaS). Este repositório é o guarda-chuva: fixa a versão de cada aplicação como submódulo, sobe o sistema inteiro pelo Docker Compose (com o `config-repo/` que o Config Server serve) e guarda a visão do sistema e o log de decisões abaixo (ADR-015).

| Repositório | Aplicação (`spring.application.name`) | Porta | O que é | Interior documentado em |
|---|---|---|---|---|
| [`permission_saas_api`](https://github.com/Permission-SaaS/permission_saas_api) | `permission-service` | 8080 | A aplicação principal: monolito modular com `identity`, `billing`, `project`, `permission` e o cliente de `audit` | [`docs/ARCHITECTURE.md`](https://github.com/Permission-SaaS/permission_saas_api/blob/main/docs/ARCHITECTURE.md) |
| [`permission_saas_audit`](https://github.com/Permission-SaaS/permission_saas_audit) | `audit-service` | 8081 | A trilha de auditoria, com banco próprio | [`docs/ARCHITECTURE.md`](https://github.com/Permission-SaaS/permission_saas_audit/blob/main/docs/ARCHITECTURE.md) |
| [`permission_saas_config`](https://github.com/Permission-SaaS/permission_saas_config) | `config-server` | 8888 | O Config Server; os arquivos que ele serve ficam no `config-repo/` daqui | [`README.md`](https://github.com/Permission-SaaS/permission_saas_config#readme) |
| [`permission_saas_front`](https://github.com/Permission-SaaS/permission_saas_front) | — | — | O front-end: React, TypeScript, Vite e Tailwind CSS (ADR-016), ainda sem funcionalidades. Fica fora do Docker Compose por enquanto | [`README.md`](https://github.com/Permission-SaaS/permission_saas_front#readme) |

A extração segue o padrão *Strangler Fig* — uma capacidade de cada vez, começando pela mais desacoplada — em vez de reescrever o monolito inteiro em serviços. O primeiro serviço extraído foi o `audit` (ADR-008 e ADR-010). Desde a etapa 3 da disciplina de microsserviços, o `config-server` serve a configuração de ambiente dos dois serviços no profile `prod` (ADR-011 e ADR-012), e as aplicações sobem juntas pelo Docker Compose, com um banco por serviço e o RabbitMQ.

---

## Como os serviços conversam

| De → para | Como | Para quê | Decisão |
|---|---|---|---|
| `permission-service` → `audit-service` | RabbitMQ, fila `audit.events`, assíncrono | Gravar cada validação de permissão na trilha | ADR-013 |
| `permission-service` → `audit-service` | HTTP, OpenFeign | Consultar a trilha (`GET /audit-events`) | ADR-010 |
| `permission-service`, `audit-service` → `config-server` | HTTP, só na subida e só no profile `prod` | Receber endereços e log de SQL | ADR-012 |

Os contratos são os DTOs e a mensagem documentados no [`API.md` do `audit-service`](https://github.com/Permission-SaaS/permission_saas_audit/blob/main/docs/API.md). Não há biblioteca compartilhada entre os repositórios: o que os dois lados têm em comum é copiado (ADR-008, "Duplicação consciente").

### A trilha de auditoria entre os dois serviços

**Extração concluída (30/09/2026).** A gravação e a consulta passam pelo serviço, e o monolito não guarda mais nada da trilha. Na gravação, o `AuditLogListener` do monolito traduz o `PermissionValidatedEvent` em `PermissionCheckEvent` e o entrega à porta `AuditTrail`, implementada por `AuditTrailClientAdapter` sobre o cliente OpenFeign `AuditClient` (`audit/infrastructure/client/`). O listener roda na thread da validação de permissão, então duas proteções impedem que a auditoria derrube a validação: timeout curto no cliente `audit-service` (1s para conectar, 2s para responder, no `application.yml`; o default do Feign é 60s) e um `try/catch` no listener. O adapter só traduz a `FeignException` para a `AuditTrailUnavailableException` da porta; quem decide que perder o evento é aceitável e quebrar a validação não é, é a camada `application`. Com o serviço fora do ar, a validação responde normalmente e o evento **se perde**, com um `WARN` no log — a limitação que a etapa 4 resolve trocando o Feign da gravação por uma fila no RabbitMQ. Na consulta, o `GET /audit-events` do monolito valida os filtros e o período (os `400` saem daqui, sem chamar a rede) e repassa ao serviço pela mesma porta `AuditTrail`, que devolve o modelo de leitura `AuditTrailEntry` — a resposta do serviço não traz dados para reconstruir um `PermissionCheckEvent`. Serviço fora do ar vira `503`: a `AuditTrailUnavailableException` estende a `ServiceUnavailableException` do `shared`, mapeada pelo `GlobalExceptionHandler` (o `shared` não pode importar do `audit`, que depende dele). A persistência local do módulo — entidades JPA, consultas do ADR-009, arquivo texto, `AuditDemoRunner` — foi apagada e a migration `V10` removeu a tabela `audit_events` do banco principal (ADR-010).

**Gravação pela fila (03/10/2026, etapa 4, ADR-013).** A gravação deixou o Feign: o `AuditLogListener` agora entrega o evento à porta `AuditEventPublisher`, implementada por `RabbitAuditEventPublisher` (`audit/infrastructure/messaging/`), que publica a mensagem na fila `audit.events`. O `AuditMessageListener` do serviço consome e grava pelo mesmo `RegisterPermissionCheckUseCase` do `POST`. Com o serviço fora do ar, a mensagem **espera na fila** e é gravada quando ele volta: a perda do parágrafo acima deixou de existir. O listener passou a rodar em segundo plano (`@Async`), então a validação não espera nem o broker. A porta `AuditTrail` ficou só com a consulta, que continua por OpenFeign, porque quem consulta precisa da resposta na hora.

A direção futura do `audit-service`, tornar-se um serviço de auditoria genérico, está no [`ARCHITECTURE.md` dele](https://github.com/Permission-SaaS/permission_saas_audit/blob/main/docs/ARCHITECTURE.md#direção-futura).

---

## Decisões (ADRs)

Os ADRs registram as decisões na ordem em que foram tomadas, com a numeração única do sistema inteiro. Os caminhos que eles citam (`docs/API.md`, `src/`, `permission-service/`, `audit-service/`...) são os do repositório na época. Desde o ADR-015, o código e a documentação interna de cada aplicação ficam no repositório dela, e a versão de cada ADR como foi entregue numa disciplina está na tag correspondente.

---

## ADR-001: quem gera o ID da entidade — domínio ou Hibernate

**Decisão:** métodos de fábrica no domínio (`Subscription.pendingFor()`, etc.) **não** atribuem `id` manualmente quando a entidade JPA correspondente usa `@GeneratedValue(strategy = GenerationType.UUID)`. O `id` fica `null` até o primeiro `save()`; o adapter lê o valor gerado de volta (`toDomain(saved)`) e o use case reatribui a variável (`subscription = subscriptionRepository.save(subscription)`).

**Por quê:** o Spring Data `SimpleJpaRepository.save()` decide entre `persist()` e `merge()` checando se o `id` está `null` (`isNew()`). Se o domínio já atribui um UUID antes do primeiro save, o repositório assume que a entidade **já existe** e chama `merge()` — que faz um `SELECT` pra achar a linha, não encontra (ela ainda não existe) e o Hibernate lança `StaleObjectStateException` (`ObjectOptimisticLockingFailureException`), mesmo sem `@Version` na entidade. Foi exatamente o bug corrigido em `SubscribeToPlanUseCase`/`Subscription.pendingFor()` — `Client` e `ApiKey` nunca tiveram esse problema porque já seguiam essa regra.

**Como aplicar:** qualquer entidade nova com `@GeneratedValue(strategy = GenerationType.UUID)` (ex: futuras entidades de `project`, `permission`, `audit`) deve deixar o Hibernate gerar o `id` — nunca pré-atribuir no domínio. Se um fluxo salvar a mesma entidade mais de uma vez na mesma transação (como a subscription: pending → paid/rejected → active), sempre reatribuir a variável local ao retorno de `save()`.

> ⚠️ **Exceção deliberada:** `Project`, `Role` e `Route` continuam gerando o próprio `id` no domínio. O ADR-003 explica por quê isso deixou de conflitar com este ADR quando a persistência JPA entrou na etapa 4. `AuditEvent` segue este ADR: quem atribui o `id` é o Hibernate (`@GeneratedValue(strategy = GenerationType.UUID)` na `AuditEventJpaEntity`).

---

## ADR-003: `Project`/`Role`/`Route` geram o próprio `id` — desvio do ADR-001

**Status:** aceito nas etapas 1-3 como temporário; **mantido em definitivo na etapa 4** — ver "Resolução na etapa 4" no fim deste ADR.

**Contexto:** `Project.addRole()` e `Project.addRoute()` fecham a referência de volta do filho para o pai (`role.setProjectId(this.id)`) — é o que materializa o relacionamento 1-N exigido pela rubrica. Isso só funciona se `this.id` já existir no momento da chamada.

Nas etapas 1-3 não há banco: a persistência é um `Map` in-memory e a demonstração monta o grafo em memória. Se o `id` só fosse atribuído no `save()`, todo `Role`/`Route` sairia com `projectId = null` — o relacionamento não apareceria nem no `toString()` da demo, nem no arquivo de auditoria.

**Decisão:** enquanto a persistência for in-memory, as três entidades do módulo `project` inicializam `id` com `UUID.randomUUID()` via `@Builder.Default`.

**Conflito conhecido com o ADR-001:** o ADR-001 determina o oposto — o domínio **não** deve pré-atribuir `id` quando a entidade JPA usa `@GeneratedValue(strategy = GenerationType.UUID)`, porque o `SimpleJpaRepository.save()` decide entre `persist()` e `merge()` checando `id == null`. Um `id` pré-atribuído faz o Spring Data chamar `merge()` em uma entidade que ainda não existe, e o Hibernate lança `ObjectOptimisticLockingFailureException`. Foi exatamente o bug corrigido em `SubscribeToPlanUseCase`.

Ou seja: **manter o `@Builder.Default` do `id` na etapa 4 reintroduz um bug já corrigido neste projeto.**

### Consequência para o `@EqualsAndHashCode(of = "id")`

`Project`, `Role` e `Route` são anotadas com `@EqualsAndHashCode(of = "id")` — igualdade por identidade, não por valor. Dois objetos são a mesma entidade se têm o mesmo `id`, independentemente dos demais campos. É a semântica correta para uma **entidade** (ao contrário de um value object, que se compara por conteúdo), e é o padrão seguido por todo o domínio do projeto: `Client`, `Plan`, `Subscription` e `ApiKey` usam a mesma anotação.

Hoje isso é seguro **por causa do ADR-003**, e não por acaso. O `@Builder.Default` garante duas propriedades das quais o `equals`/`hashCode` depende:

| Propriedade | Por que importa |
|---|---|
| `id` nunca é `null` | duas entidades distintas nunca colidem como "ambas nulas" |
| `id` nunca muda durante a vida do objeto | o `hashCode()` é estável, então o objeto continua achável dentro de um `HashSet`/`HashMap` |

**O item 1 do checklist abaixo destrói as duas.** Com `private UUID id;` sem default, o `id` fica `null` até o primeiro `save()`, e aí:

1. **Duas entidades novas diferentes passam a ser "iguais".** Ambas têm `id == null`, então `equals()` devolve `true`. Dois `Role` recém-criados num `Set` viram um só, silenciosamente — sem exceção, sem log. O risco é concreto na etapa 4: se a coleção `@OneToMany` for mapeada como `Set` (item 3), o Hibernate vai usar `equals`/`hashCode` para gerenciá-la.
2. **O `hashCode()` muda depois do `save()`.** De `null` para um UUID. Se o objeto já estava dentro de um `HashSet` ou era chave de um `HashMap`, ele passa a morar no bucket errado e não é mais encontrado — nem por `contains()`, nem por `remove()`. É a armadilha clássica de `equals`/`hashCode` com entidades JPA.

**As três saídas possíveis na etapa 4** (decidir antes de escrever a `ProjectJpaEntity`):

| Opção | Como | Custo |
|---|---|---|
| **A — `Persistable`** | manter o UUID gerado no domínio e implementar `Persistable<UUID>.isNew()` para o Spring Data saber que a entidade é nova sem consultar o `id` | resolve o conflito ADR-001 × ADR-003 na raiz; `equals`/`hashCode` continuam válidos sem alteração |
| **B — chave natural** | comparar por chave de negócio em vez de `id`. `Role` já tem uma: `projectId` + `name` (o invariante de unicidade). `Route`: `projectId` + `httpMethod` + `path` | dispensa Lombok, exige `equals`/`hashCode` à mão; `Project` não tem chave natural óbvia |
| **C — `equals` null-safe** | `id != null && id.equals(other.id)`, com `hashCode()` retornando constante (`getClass().hashCode()`) | o Lombok não expressa isso — `equals`/`hashCode` passam a ser escritos à mão nas três classes |

A opção **A** é a preferida: ela preserva tudo que já está escrito e elimina o desvio em vez de administrá-lo. As opções B e C existem aqui para o caso de a `ProjectJpaEntity` acabar exigindo `@GeneratedValue`.

> Os eventos do módulo `audit` seguem regra diferente e proposital: `AuditEvent` usa `@EqualsAndHashCode(of = "id")`, mas `PermissionCheckEvent` e `ProjectLifecycleEvent` usam `@EqualsAndHashCode(callSuper = true)`, incluindo os campos próprios de cada subclasse. Revisar essa escolha ao mapear a herança `SINGLE_TABLE` na etapa 4 — herança e igualdade por identidade interagem mal quando duas subclasses diferentes podem compartilhar o mesmo `id` de tabela única.

**O que fazer na etapa 4 (checklist obrigatório):**

1. Remover o `@Builder.Default` de `id` em `Project`, `Role` e `Route` — voltar a `private UUID id;`. **Só fazer isto junto com o item 2.**
2. Escolher e aplicar uma das três opções de `equals`/`hashCode` acima. Um `id` nulo com `@EqualsAndHashCode(of = "id")` é bug silencioso, não erro de compilação — nenhum teste existente falha por isso.
3. Mapear a coleção como `@OneToMany(mappedBy = "project", cascade = ALL, orphanRemoval = true)` na `ProjectJpaEntity`, deixando o JPA ser dono da FK. `Role.projectId`/`Route.projectId` no domínio passam a ser valor derivado, preenchido pelo adapter em `toDomain()`.
4. Remover as chamadas `role.setProjectId(this.id)` / `route.setProjectId(this.id)` de `addRole`/`addRoute`, que deixam de ter função.
5. Conferir que `ProjectRepositoryAdapter` reatribui a variável ao retorno do `save()` (`project = projectRepository.save(project)`), como manda o ADR-001.

**Por que aceitar o desvio em vez de evitá-lo:** a alternativa seria a rotina de demonstração atribuir os `id` manualmente antes de montar o grafo, deixando o domínio limpo. Isso empurraria uma responsabilidade de infraestrutura para dentro da demo e tornaria o `addRole` inseguro por padrão (silenciosamente gravando `null` se alguém esquecesse). Como a troca para JPA já está isolada atrás da porta `ProjectRepository` — o use case não muda —, o custo de reverter é o checklist acima, contido em três arquivos de domínio e um adapter.

---

### Resolução na etapa 4

O desvio **não foi revertido** — deixou de ser um desvio. O que mudou é que a persistência JPA usa
classes próprias (`ProjectJpaEntity`, `RoleJpaEntity`, `RouteJpaEntity`), separadas das classes de
domínio. O conflito descrito acima só existiria se a entidade de domínio *fosse* a entidade JPA.

**Por que o conflito com o ADR-001 não se materializa:**

| Condição do bug original | Situação na etapa 4 |
|---|---|
| entidade JPA com `@GeneratedValue` recebendo `id` pré-atribuído | `ProjectJpaEntity` usa `@Id` **atribuído**, sem `@GeneratedValue` — a coluna tem `DEFAULT gen_random_uuid()` só para quem inserir por SQL |
| `save()` decidindo `persist`/`merge` às cegas | o `ProjectRepositoryAdapter` faz `findById` antes de gravar: se existe, muta a entidade **gerenciada**; se não, monta uma nova |
| `@Version` disparando `ObjectOptimisticLockingFailureException` | nenhuma das três entidades tem `@Version`, então `merge()` sobre uma linha inexistente resolve para `SELECT` + `INSERT`, não para um `UPDATE` de zero linhas |

**Sobre a opção A (`Persistable`), que este ADR elegia como preferida:** foi implementada, avaliada e
removida. Ela só economiza o `SELECT` que o `merge()` faz antes de inserir, e cobra por isso um campo
`@Transient isNew` mais callbacks `@PostLoad`/`@PostPersist` — ou seja, um segundo lugar guardando
"esta linha já existe?", que o adapter já sabe porque acabou de consultar. Estado duplicado em troca
de uma consulta: não compensa. Se um dia o custo do `SELECT` extra pesar (inserção em lote, por
exemplo), `Persistable` volta como otimização localizada na entidade JPA, sem tocar em domínio nem
use case.

**Consequência para `equals`/`hashCode`:** o risco descrito acima **desapareceu**, porque o item 1 do
checklist (remover o `@Builder.Default` do `id`) não foi executado — e não precisa ser. O `id` do
domínio continua nunca sendo nulo e nunca mudando, que são exatamente as duas propriedades de que o
`@EqualsAndHashCode(of = "id")` depende.

**Checklist original, item a item:**

| Item | Situação |
|---|---|
| 1. remover `@Builder.Default` do `id` | ❌ não executado — deliberadamente, ver acima |
| 2. escolher uma das três opções de `equals`/`hashCode` | ✅ nenhuma foi necessária; a semântica atual segue válida |
| 3. mapear `@OneToMany(mappedBy, cascade = ALL, orphanRemoval = true)` | ✅ feito na `ProjectJpaEntity` |
| 4. remover `role.setProjectId(this.id)` de `addRole`/`addRoute` | ❌ mantido de propósito: `Role.projectId`/`Route.projectId` são o que a resposta JSON usa para referenciar o pai sem referência circular. O adapter repreenche esse campo em `toDomain()` a partir de `entity.getProject().getId()`, então o valor nunca diverge do dono real da FK |
| 5. adapter reatribuindo a variável ao retorno de `save()` | ✅ `save()` devolve `toDomain(jpa.save(entity))` |

> A ressalva sobre herança e igualdade no `audit` também se resolveu: as subclasses de
> `AuditEventJpaEntity` compartilham a tabela, mas não o `id` — cada linha é um evento distinto, e o
> `id` é gerado pelo banco, nunca pelo domínio.

---

## ADR-005: sem `Map` in-memory, sem seed e sem loader de arquivo texto no código final

**Status:** aceito na etapa 4 da disciplina de Spring Boot.

**Contexto:** as etapas 1-3 pediam explicitamente um `Map` simulando o banco (itens 7 e 8 da rubrica) e
classes *loader* lendo arquivos texto (itens 4 e 5). O enunciado da Etapa 4 autoriza a remoção do
`Map`: *"A implementação com Map não precisa permanecer no código final, pois estará preservada no
marco etapa-3."*

**Decisão:** removidos do código final o `InMemoryProjectRepository`, o `InMemoryAuditEventRepository`,
o `ProjectFileLoader`, o `SeedFileException`, o `ProjectSeedRunner` e os arquivos
`src/main/resources/data/*.txt`. A aplicação passa a depender exclusivamente do banco.

**Motivo:** o seed automático fazia a subida da aplicação depender de três arquivos de classpath e
gravava dados de demonstração em qualquer ambiente onde a tabela `projects` estivesse vazia —
inclusive produção. Como a arquitetura final é `Controller → Service → Repository → Banco`, um
carregador de texto no caminho de inicialização é um segundo dono do estado inicial, sem dono claro.

**Consequência a registrar:** os itens 4, 5, 7 e 8 da rubrica passam a ser evidenciados **apenas pelas
tags** `etapa-1`, `etapa-2` e `etapa-3`, não pelo `HEAD`. Isso é coerente com a estrutura de avaliação
por marcos combinada com o professor, mas é uma escolha consciente: quem olhar só a versão final não
encontra o `Map` nem os loaders.

Para inspecionar essas evidências:

```bash
git show etapa-3:src/main/java/com/saas/permissions/project/infrastructure/InMemoryProjectRepository.java
git show etapa-3:src/main/java/com/saas/permissions/project/infrastructure/ProjectFileLoader.java
git show etapa-3:src/main/resources/data/projects.txt
```

---

## ADR-006: submódulos por entidade dentro de cada camada do `project`

**Status:** aceito na etapa 4 da disciplina de Spring Boot.

**Contexto:** o `billing` já dividia cada camada em `plan/` e `subscription/`. O `project` tinha essa
divisão apenas no `domain` (`project/`, `role/`, `route/`); `application`, `infrastructure` e `api`
eram planos, com 40 classes misturadas.

**Decisão:** replicar a divisão do `domain` nas outras três camadas. Cada camada do `project` tem
`project/`, `role/` e `route/`, e `ProjectController` deixou de acumular os sub-recursos: `/roles` e
`/routes` passaram para `RoleController` e `RouteController`, com as mesmas URLs de antes.

**Consequências:**

- As URLs e os contratos não mudaram — a coleção Postman roda igual, sem edição.
- `RoleJpaEntity`, `RouteJpaEntity` e `ProjectJpaEntity` tiveram de virar `public`: elas se referenciam
  entre subpacotes. `JpaProjectRepository` e `ProjectRepositoryAdapter` seguem restritos ao subpacote.
- O `@NamedInterface` do `project` desceu de `project.application` para `project.application.project`,
  que é o subpacote de onde o `permission` consome o `CheckRouteAccessUseCase`. Subpacote de um pacote
  anotado **não** herda a anotação no Spring Modulith — por isso a anotação precisa estar exatamente
  onde está a classe consumida.

---

## ADR-007: `RoleRoute` é entidade associativa com histórico, não tabela de junção

**Status:** aceito na etapa 4 da disciplina de Spring Boot (migration `V9`).

**Contexto:** até então o modelo tinha `Project 1─N Role` e `Project 1─N Route`, sem nada ligando cargo a rota. A validação de permissão conseguia dizer no máximo "cargo e rota existem no mesmo projeto", o que na prática libera qualquer cargo para qualquer rota — o oposto do que um sistema de permissões vende.

**Decisão:** modelar

```
Project 1 ──── N Role  1 ──── N RoleRoute
Project 1 ──── N Route 1 ──── N RoleRoute
```

com `RoleRoute` carregando `grantedAt` e `revokedAt` além das duas FKs.

**Por que não `@ManyToMany` com `@JoinTable`:** o `@ManyToMany` esconde a tabela de junção e não deixa espaço para atributos próprios. Revogar viraria `role.getRoutes().remove(route)` — um `DELETE`, e a informação de que aquele cargo já teve acesso some. Com entidade associativa explícita, revogar é preencher `revokedAt`: a linha permanece e a trilha de auditoria consegue responder **quando** o cargo perdeu o acesso, que é o motivo pelo qual a associação existe.

**Decisões de detalhe:**

| Decisão | Motivo |
|---|---|
| índice único **parcial** `WHERE revoked_at IS NULL` | garante no banco no máximo uma concessão ativa por par, e ao mesmo tempo permite empilhar histórico: conceder → revogar → conceder gera duas linhas |
| `isActive()` derivado de `revokedAt == null`, sem coluna booleana | um booleano mais a data poderiam divergir; com um campo só, o estado é sempre consistente |
| `@OneToMany` com cascata no `Role`, inverso somente leitura no `Route` | dois caminhos de cascata gravariam a mesma linha; o `Role` é o dono porque é por ele que o agregado navega. A relação `Route 1─N RoleRoute` continua existindo no mapeamento e no banco (FK com `ON DELETE CASCADE`) |
| `Project` é quem concede e revoga, não `Role` | só o agregado raiz enxerga cargos e rotas ao mesmo tempo, e é isso que permite validar que ambos pertencem ao mesmo projeto antes de criar a concessão |

**Consequência no adapter — `save()` em duas etapas.** `RoleRouteJpaEntity.route` é um `@ManyToOne` **sem cascata**: a rota precisa já estar gerenciada pelo `EntityManager` quando a concessão a referencia. Num projeto recém-criado a rota ainda é transiente, e o Hibernate tentava resolvê-la por id no banco, onde a linha ainda não existia — `ObjectRetrievalFailureException`. Por isso `ProjectRepositoryAdapter.save()` grava primeiro o esqueleto (projeto + cargos + rotas) e só então aplica as concessões, num segundo `save()` dentro da mesma transação. O caso só aparece na primeira gravação de um agregado que já nasce com concessões — foi um teste de integração que o pegou, não o teste manual pela API, onde rota e concessão vêm em requisições separadas.

---

## ADR-002: `@Data` no domínio quebra o encapsulamento — refactor planejado

**Status:** aceito como dívida técnica consciente. Refactor não agendado (ver "trabalho futuro").

**Contexto:** todas as entidades de domínio do projeto (`Client`, `Plan`, `Subscription`, `Project`, `Role`, `Route`, `AuditEvent`) usam `@Data` do Lombok, que gera getter **e setter públicos para todo campo**. Isso entrou no projeto pela conveniência de escrever entidades rápido, antes de qualquer entidade ter regra de negócio própria.

**Problema:** quando o domínio passa a guardar invariantes, o `@Data` os torna opcionais. `Project.addRole()` valida `maxRoles`, mas o `@Data` também expõe `getRoles()` e `setRoles()` — então:

```java
project.addRole(role);           // valida o limite
project.getRoles().add(role);    // fura o limite, mesma classe, mesmo efeito
project.setRoles(outraLista);    // troca a coleção inteira
```

O encapsulamento hoje é **convenção, não garantia**: o invariante só vale se todo chamador lembrar de usar o método certo. É a mesma classe de problema que o ADR-001 descreve — comportamento correto dependendo de disciplina do chamador em vez de estar imposto pelo tipo.

**Decisão para agora:** manter `@Data` e documentar a limitação. Trocar em todas as entidades é um refactor transversal que atinge use cases, adapters e mappers dos cinco módulos; fazer isso no meio da disciplina de Spring Boot competiria com as etapas e não tem item de rubrica correspondente.

**Refactor planejado (trabalho futuro):** por entidade que tenha invariante, substituir `@Data` por:

1. `@Getter` + `@EqualsAndHashCode(of = "id")` — sem `@Setter` de classe.
2. Coleções expostas como cópia imutável (`List.copyOf(roles)`) e mutáveis só pelos métodos de domínio (`addRole`, `removeRole`).
3. Setters pontuais só onde a infraestrutura exigir (mappers JPA), preferencialmente substituídos por construtor/builder.

Entidades sem regra de negócio própria (`Plan`, hoje) podem continuar com `@Data` — o critério é ter ou não invariante a proteger, não uniformidade.

**Ordem sugerida:** `Project` primeiro (é quem tem o invariante mais claro, `maxRoles`), depois `Subscription` (máquina de estados), depois as demais.

---

## ADR-004: schema dos módulos `project` e `audit` — fronteiras de FK e herança

**Status:** aceito na etapa 4 da disciplina de Spring Boot (migrations `V5`–`V8`).

> Desde 30/09/2026 (ADR-010), a tabela `audit_events`, a herança `SINGLE_TABLE` e os `CHECK` abaixo existem só no `audit_db` do `audit-service` (a `V1` dele é cópia da `V8`). A `V10` do monolito apagou a tabela do banco principal.

### Onde há FK e onde não há

> A migration `V9` acrescentou `role_routes`, com FK para `roles` **e** para `routes`, ambas `ON DELETE CASCADE` — as duas pontas são do mesmo agregado, então valem as mesmas razões de `roles` e `routes`. Ver ADR-007.

| Referência | FK no banco | Por quê |
|---|---|---|
| `roles.project_id` → `projects` | ✅ com `ON DELETE CASCADE` | mesmo módulo e mesmo agregado; acompanha o `cascade = ALL` / `orphanRemoval = true` do `@OneToMany` da `ProjectJpaEntity` |
| `routes.project_id` → `projects` | ✅ com `ON DELETE CASCADE` | idem |
| `projects.client_id` → `clients` | ❌ só índice | ver abaixo |
| `audit_events.project_id` → `projects` | ❌ só índice | ver abaixo |

`subscriptions` (V3) referencia `clients` e `plans` com FK, então a ausência delas aqui é desvio consciente do precedente, por dois motivos distintos:

- **`projects.client_id`** — `CreateProjectUseCase` não valida o cliente contra o módulo `identity`: a FK transformaria um `clientId` inexistente em erro 500 do driver, sem exceção de domínio mapeada pelo `GlobalExceptionHandler`. Validar o cliente de verdade exigiria o `identity` expor um `@NamedInterface` de consulta — trabalho futuro; aí a FK passa a fazer sentido.

  > Quando esta decisão foi escrita havia um segundo motivo: o seed de `ProjectFileLoader` referenciava clientes fictícios inexistentes em `clients`, e a FK quebraria o carregamento. Esse motivo caiu com a remoção do seed (ADR-005); o primeiro continua valendo sozinho.
- **`audit_events.project_id`** — a trilha de auditoria precisa sobreviver ao projeto que descreve, e o módulo `audit` não é dono da tabela `projects`. A coluna é **nullable** porque `PermissionValidatedEvent` ainda não carrega o projeto (mesma lacuna do `httpMethod`, achado 3 de 29/08).

### Herança do `audit`: `SINGLE_TABLE`

`AuditEvent` → `PermissionCheckEvent` / `ProjectLifecycleEvent` foi mapeada como tabela única discriminada por `event_type`, com valores iguais aos devolvidos por `AuditEvent.type()`. A alternativa `JOINED` foi descartada porque a trilha é *append-only* e sempre lida pela superclasse (`SearchAuditEventsUseCase` devolve `List<AuditEvent>`) — pagar um JOIN por leitura não se justifica.

O preço é que as colunas de cada subclasse precisam ser `NULL`-áveis. A obrigatoriedade volta como `CHECK` condicionado ao discriminador (`audit_events_permission_check_fields`, `audit_events_lifecycle_fields`), o que também protege `granted` e `duration_ms`, primitivos no domínio (`boolean`/`double`) que não aceitam `null`.

### O schema espelha os invariantes do domínio

As regras que hoje só existem em Java foram repetidas como constraint, para que dados inseridos fora da API — o seed dos `.txt`, por exemplo — respeitem a mesma regra:

| Constraint | Regra de domínio correspondente |
|---|---|
| `uq_roles_project_name` (`project_id`, `LOWER(name)`) | `Project.addRole()` → `RoleAlreadyExistsException` |
| `uq_routes_project_method_path` (`project_id`, `UPPER(http_method)`, `LOWER(path)`) | `Project.addRoute()` → `RouteAlreadyExistsException` |
| `projects_max_roles_check` | `Project.update()` → `InvalidProjectDataException`; `@Min(1)` de `CreateProjectRequest` |
| `routes_http_method_check`, `routes_path_check` | `@Pattern` de `AddRouteRequest` |

Dois índices são parciais, cobrindo exatamente os filtros que os use cases aplicam: `idx_projects_active` (`WHERE deleted_at IS NULL`) para o soft delete que `FindAllProjectsUseCase`/`FindProjectByIdUseCase` tratam como inexistência, e `idx_audit_events_denied` (`WHERE granted = FALSE`) para o filtro `onlyDenied` de `SearchAuditEventsUseCase`.

`updated_at` é *nullable* nas três tabelas novas, ao contrário de `clients`/`subscriptions`, que usam `DEFAULT NOW()`: `Project`, `Role` e `Route` só preenchem `updatedAt` na primeira alteração, e um default reescreveria essa semântica.

**Verificado em 30/08/2026:** as oito migrations aplicam em sequência num Postgres 16 limpo; o seed dos três `.txt` entra íntegro (3 projetos, 8 cargos, 10 rotas) e 16 casos de constraint se comportam como o domínio.

---

## ADR-008: projetos irmãos no mesmo repositório, não multi-módulo Maven

**Status:** aceito na etapa 1 da disciplina de microsserviços; **revisado na etapa 2 (28/09/2026)**
— a aplicação principal saiu da raiz para `permission-service/`. A versão original e o motivo da revisão estão no
fim deste ADR. **Substituído pelo ADR-015 em 05/10/2026:** cada aplicação passou a ter
repositório próprio.

**Contexto:** a disciplina exige extrair o `audit` para uma aplicação Spring Boot independente e,
depois, acrescentar um Config Server. Passam a existir três `pom.xml` onde havia um. O caminho
idiomático do Maven seria converter a raiz em um `pom` agregador (`<packaging>pom</packaging>`) com
`permission-service/`, `audit-service/` e `config-server/` como módulos.

Há uma restrição que vem de fora do Maven: este repositório é a evidência avaliada de três
disciplinas da Pós-Graduação, e as tags `etapa-1` … `etapa-4` apontam para o código como ele foi
entregue em 31/08/2026.

**Decisão:** um único repositório, com **cada aplicação em uma pasta irmã** e a raiz reservada para
o que é de todas elas — orquestração e documentação. Cada aplicação tem seu próprio `pom.xml`,
`mvnw` e `Dockerfile`; não há `pom` agregador:

```
permission_saas/
├── permission-service/  aplicação principal (monolito modular)
├── audit-service/       serviço extraído
├── config-server/       Spring Cloud Config Server
├── docker-compose.yml   orquestra todos
└── docs/  README.md
```

Cada projeto compila sozinho (`./mvnw` dentro da pasta) e o `docker-compose.yml` da raiz é o que
integra os três.

Desde 02/10/2026, a raiz também guarda o `config-repo/`: a configuração de todas as aplicações,
servida pelo `config-server` (ADR-012). Fica fora de `config-server/` porque não é código do servidor;
num ambiente real seria um repositório Git à parte.

**Alternativa descartada — `pom` agregador na raiz.** Um agregador só se paga quando há build único
ou código compartilhado entre os módulos, e aqui não há nenhum dos dois (ver "Duplicação
consciente" abaixo). Acrescentaria um `pom.xml` na raiz e a tentação de um módulo `common`, que
voltaria a acoplar os deploys.

**Consequências:**

- **Não há build único.** Compilar tudo é rodar `./mvnw` em cada pasta, ou `docker compose build`.
  Aceitável porque os projetos não compartilham código-fonte — o que é comum entre eles (DTOs de
  contrato, `Mapper`, `GlobalExceptionHandler`) é copiado deliberadamente, não extraído para uma
  biblioteca compartilhada.
- **Duplicação consciente.** Uma lib compartilhada voltaria a acoplar os dois deploys: mudar o
  contrato exigiria versionar e publicar a lib antes de subir qualquer um dos lados. Para dois
  serviços com um contrato pequeno, copiar custa menos do que acoplar.
- O `verifiesModularStructure()` do Spring Modulith continua valendo só para a aplicação principal.
  A fronteira entre ela e o `audit-service` deixa de ser verificada por teste e passa a ser
  verificada pela rede: não há como importar o pacote do outro.
- Se uma disciplina futura precisar de build único, basta acrescentar um `pom` agregador na raiz
  listando as pastas como módulos — o layout já é o de um multi-módulo.
- **Qualquer serviço pode virar repositório próprio depois**, sem perder o histórico:
  `git subtree split --prefix=audit-service` gera um branch só com a história daquela pasta. Um
  repositório por serviço desde já foi descartado porque separaria as tags `etapa-*` e
  `arq-etapa-*` — a evidência das disciplinas — em repositórios diferentes.

**Revisão de 28/09/2026 — a aplicação principal saiu da raiz.** A versão original deste ADR mantinha
a aplicação principal na raiz (`src/`, `pom.xml`, `Dockerfile`) e acrescentava o `audit-service`
como pasta dentro dela. O argumento era que mover `src/` para `permission-service/src/` faria o diff da entrega ser
"dominado por milhares de linhas de arquivo movido". O argumento não se sustenta: o Git registra a
mudança como renomeação (`{src => permission-service/src}/…`, sem linha alterada), e as tags antigas continuam
apontando para o layout antigo, intactas.

Na prática, o layout original teve dois custos que não estavam previstos:

- **Parecia que o serviço fazia parte do monolito.** Com o `audit-service/` dentro da pasta da
  aplicação principal, quem abre o repositório vê um serviço aninhado em outro — o oposto do que a
  etapa 2 quer demonstrar, duas aplicações independentes.
- **A IDE concordava com essa leitura.** A extensão Java do VS Code importava o `pom.xml` da raiz e
  tratava o `audit-service/` como uma pasta do projeto principal, sem classpath próprio. Com a raiz
  sem `pom.xml`, cada pasta é importada como projeto independente.

A mudança foi feita antes da etapa 2 ganhar Feign, Dockerfiles e Config Server, quando só o
`docker-compose.yml` e os comandos do `README.md` precisavam de ajuste.

---

## ADR-009: a consulta da trilha de auditoria desce para o banco, em JPQL

**Status:** aceito na etapa 1 da disciplina de microsserviços. Desde 30/09/2026 as consultas existem só no `audit-service`, copiadas na extração; o monolito as removeu junto com a tabela (ADR-010).

**Contexto:** até aqui, `GET /audit-events` carregava todos os eventos (ou todos os de um projeto)
e o use case filtrava `type` e `onlyDenied` num stream — a regra geral "a porta é burra" da seção
*Adapter Pattern na infrastructure*. Para o `audit` essa regra custa caro: a trilha é *append-only*,
ganha uma linha a cada validação de permissão e nunca é podada. A etapa 1 também pede consultas
Spring Data coerentes com o domínio, e a busca por período era a que faltava.

**Decisão:** a porta ganha dois métodos com os filtros como parâmetros explícitos, e o adapter os
resolve em duas consultas `@Query` (JPQL):

| Porta | Consulta | Filtros |
|---|---|---|
| `search(type, projectId, from, to)` | `JpaAuditEventRepository.search` sobre `AuditEventJpaEntity` | tipo, projeto, período |
| `searchDenied(projectId, from, to)` | `JpaPermissionCheckEventRepository.searchDenied` sobre `PermissionCheckEventJpaEntity` | `granted = false`, projeto, período |

Cada filtro segue o padrão `(:param IS NULL OR campo = :param)`: parâmetro nulo significa "não
filtrar", a mesma convenção dos DTOs de busca. O use case `SearchAuditEventsUseCase` fica só com a
regra de negócio: rejeita período invertido (`InvalidAuditPeriodException`, 400), normaliza o tipo
para maiúsculas e escolhe entre `search` e `searchDenied`.

Três detalhes de implementação que não são óbvios:

- **`searchDenied` tem repositório próprio.** O JPQL navega por classes, não por tabelas: `granted`
  é declarado só na subclasse, então a consulta precisa partir de `PermissionCheckEventJpaEntity`,
  mesmo que as duas classes gravem na mesma tabela (ADR-004, `SINGLE_TABLE`).
- **O discriminador é mapeado como atributo somente leitura** (`eventType`, com
  `insertable = false, updatable = false`), para o filtro de tipo comparar texto. Quem grava a coluna
  continua sendo o `@DiscriminatorValue`. A alternativa `TYPE(e) IN :types` foi descartada porque
  exigiria passar uma coleção de `Class` como parâmetro.
- **As datas levam `cast(:from as OffsetDateTime)` no lado do `IS NULL`.** Para uma data nula, o
  driver do PostgreSQL não informa o tipo do parâmetro — `timestamp` e `timestamptz` são ambos
  candidatos —, e o banco recusa `$5 is null` com *could not determine data type of parameter*.
  `String` e `UUID` não precisam do `cast` porque o driver informa o tipo mesmo com valor nulo. O H2
  dos testes infere o tipo sozinho, então esse erro só aparece no PostgreSQL.

**Alternativas descartadas:**

- **Consultas derivadas, uma por combinação** (`findByGrantedFalseAndOccurredAtBetween…`): cinco
  filtros opcionais geram dezenas de combinações, e cada uma viraria um método.
- **`Specification` (Criteria API):** é o caminho idiomático para filtros realmente dinâmicos, mas
  com cinco filtros fixos o JPQL fica legível numa tela e não exige montar predicados em código.
  Continua sendo a saída se os filtros crescerem.

**Consequências:**

- O adapter JPA e um eventual adapter em memória deixam de ter o mesmo custo de implementação:
  filtrar passou a ser responsabilidade do adapter. Aceitável porque o `audit` não tem adapter em
  memória desde o ADR-005.
- O índice parcial `idx_audit_events_denied` (`occurred_at DESC WHERE granted = FALSE`), criado na
  `V8`, passa a ser usado de fato — antes existia, mas a filtragem acontecia no Java.
- **Sem teste automatizado das consultas por enquanto.** Foram verificadas contra o PostgreSQL real
  com a aplicação no ar (sem filtro, período, tipo em minúsculas, `onlyDenied` com
  `PROJECT_LIFECYCLE` e período invertido). O teste de integração ficou para o `audit-service`, que é
  onde esse código passa a morar na etapa 2.

---

## ADR-010: a persistência do `audit` sai do monolito

**Status:** aceito em 30/09/2026, na etapa 2 da disciplina de microsserviços (migration `V10`).

**Contexto:** com a gravação e a consulta da trilha passando pelo `audit-service`, a tabela
`audit_events` do banco principal parou de receber eventos e de ser lida. O código que a servia virou
código morto:
- as entidades JPA da herança `SINGLE_TABLE`;
- os repositórios JPQL do ADR-009 e o adapter;
- as portas `AuditEventRepository` e `AuditEventJournal`;
- o `AuditEventFileWriter` e o `AuditDemoRunner`.

**Decisão:** apagar esse código e a tabela. É o último passo do Strangler Fig para o `audit`. Enquanto o
caminho antigo existir, não fica claro qual dos dois vale, e quem mexer depois pode religá-lo sem
perceber. No monolito fica só o necessário para falar com o serviço:
- o `AuditLogListener`;
- a consulta (`SearchAuditEventsUseCase` e o controller);
- a porta `AuditTrail`, com o modelo de leitura `AuditTrailEntry`;
- o cliente OpenFeign.

- A migration é nova (`V10__drop_audit_events_table.sql`). A `V8` não é editada nem apagada: o Flyway
  guarda o checksum de cada migration aplicada e acusaria a diferença em todo banco que já a rodou.
- `AuditEvent` e `PermissionCheckEvent` ficam, porque são o evento que o listener monta e a porta
  recebe. `ProjectLifecycleEvent` e `LifecycleAction` saem do monolito, porque só o `AuditDemoRunner`
  os criava. Continuam no `audit-service`.

**Os eventos antigos não foram copiados para o `audit_db`.** O banco principal só tinha dados de
desenvolvimento: 6 validações de teste na máquina do autor. Num sistema em produção, a ordem seria
outra: primeiro copiar as linhas para o banco do serviço, com um job de migração (o Spring Batch da
etapa 4 serve para isso), e só depois rodar o `DROP`.

**O que a disciplina de Spring Boot entregou continua acessível.** A herança `SINGLE_TABLE`, o
`AuditDemoRunner` e o arquivo texto foram entregas daquela disciplina. A evidência dela é a tag
`etapa-4`, que continua apontando para o código como foi entregue. A herança JPA e o arquivo texto
continuam funcionando no `audit-service`, para onde foram copiados na extração.

**Consequências:**

- O `permission-service` não guarda dado de auditoria nenhum. Toda consulta depende do `audit-service`
  no ar e responde `503` quando ele não está.
- O índice parcial do ADR-009 e os `CHECK` do ADR-004 passam a existir só no `audit_db`.
- O `docs/DER.pdf` ainda mostra `audit_events` no banco principal; precisa ser corrigido quando o
  diagrama for refeito.

---

## ADR-011: profiles `dev` e `prod`, com `prod` sem valor padrão

**Status:** aceito em 02/10/2026, na etapa 3 da disciplina de microsserviços. **Revisado no mesmo dia pelo ADR-012:** no `prod`, os endereços (`DB_URL`, `AUDIT_SERVICE_URL`) deixaram de ser variáveis de ambiente e passaram a vir do Config Server; o resto continua valendo.

**Contexto:** até a etapa 2, cada aplicação tinha um só `application.yml`, com
`${SPRING_DATASOURCE_URL:localhost...}` e valores padrão de desenvolvimento. Isso trazia dois problemas:

- o mesmo arquivo servia à máquina do desenvolvedor e ao container, e um container sem a variável subia
  apontando para `localhost`, que dentro dele é o próprio container;
- o `.env` misturava os segredos do Compose com endereços para rodar na máquina. Como o Spring liga
  `SPRING_DATASOURCE_*` direto a `spring.datasource.*`, exportar o `.env` num terminal fazia o
  `audit-service` conectar no banco da aplicação principal.

**Decisão:** três arquivos por aplicação.

- `application.yml` guarda o que é igual em todo ambiente e declara `spring.profiles.default: dev`.
- `application-dev.yml` tem valor padrão para tudo, apontando para `localhost`, e liga o log de SQL.
  Rodar na máquina não exige nenhuma variável.
- `application-prod.yml` lê tudo de variável de ambiente, **sem valor padrão**, e desliga o log de
  SQL. O Compose ativa esse profile e fornece as variáveis.

As variáveis passam a se chamar `DB_URL`, `DB_USERNAME` e `DB_PASSWORD`, os nomes do enunciado, e o
`.env` fica só com o que o Compose repassa: os segredos e `POSTGRES_HOST_PORT`.

**Por que `prod` sem valor padrão:** uma variável esquecida deve impedir a subida, e não fazer o
serviço subir apontando para o lugar errado. O custo é a mensagem de erro, que nem sempre nomeia a
variável. Sem `DB_URL`, o Hikari acusa `'url' must start with "jdbc"`; sem `AUDIT_SERVICE_URL`, o
Feign acusa `http://${AUDIT_SERVICE_URL} is malformed`.

**Por que o Compose roda `prod`:** é o ambiente que simula a execução real, com a mesma imagem e a
configuração vinda de fora. O debug remoto continua ligado ali, mas pelo `JAVA_TOOL_OPTIONS` do
`docker-compose.yml`, e não pela imagem ou pelo profile. Num deploy de verdade, basta não definir a
variável.

**Consequências:**

- O profile `test` (testes com H2) não herda nada de `dev`. O `application-test.yml` traz o que os
  testes precisam: o usuário do Swagger e o `audit.service.url`.
- As senhas dos bancos continuam escritas no `docker-compose.yml`, ao lado dos containers Postgres que
  as definem. São credenciais locais; num ambiente real viriam de um cofre de segredos, e o Config
  Server da etapa 3 centraliza o restante da configuração.

---

## ADR-012: Config Server com backend em arquivos, só no profile `prod`

**Status:** aceito em 02/10/2026, na etapa 3 da disciplina de microsserviços.

**Contexto:** o enunciado da etapa 3 pede configuração centralizada com Spring Cloud Config Server.
Depois do ADR-011, a configuração de ambiente do `prod` (endereço do banco, do `audit-service`, log de
SQL) estava espalhada em variáveis do `docker-compose.yml`, uma por serviço.

**Decisão:**

- **Projeto irmão `config-server/`** (porta 8888, `@EnableConfigServer`), no mesmo layout do ADR-008.
- **Backend `native`, lido do disco**, a partir do `config-repo/` na raiz. O Compose monta a pasta como
  volume somente leitura, então mudar um arquivo e reiniciar o serviço basta, sem rebuild. O backend
  Git, o padrão do Spring Cloud Config, exigiria um repositório à parte ou o `.git` dentro do
  container; para um projeto só, o versionamento já vem do repositório do código.
- **O que vai para o `config-repo/`:** o que muda com o ambiente e não é segredo. São os endereços
  (`spring.datasource.url`, `audit.service.url`) em `<serviço>-prod.yml` e o que vale para os dois
  serviços (log de SQL desligado) em `application-prod.yml`, um arquivo que configura os dois de uma
  vez.
- **O que não vai:** senhas e segredos. O Config Server devolve a configuração em texto puro para
  quem pedir (`GET /permission-service/prod`); usuário e senha do banco, Swagger, Google e JWT
  continuam em variáveis de ambiente, como no ADR-011.
- **Só o `prod` usa o Config Server.** O `application-prod.yml` de cada serviço importa
  `configserver:${CONFIG_SERVER_URL}`, sem `optional:`. Se o servidor não responder, o serviço não
  sobe (`ConfigClientFailFastException`). O `dev` e o `test` desligam o cliente
  (`spring.cloud.config.enabled: false`) e seguem com os arquivos locais. Rodar na máquina não exige
  um terceiro processo.
- **Nome da aplicação principal:** `spring.application.name` passou de `permission_saas` para
  `permission-service`, porque é por esse nome que o Config Server escolhe o arquivo.

**Consequências:**

- O Config Server vira dependência de partida no `prod`: o Compose só sobe os dois serviços depois que
  ele está `healthy`. Com os serviços já no ar, a queda dele não afeta nada, porque a configuração só é
  lida na subida.
- Mudança de configuração exige reiniciar o serviço. Atualizar sem reiniciar (`@RefreshScope` com
  `/actuator/refresh`, ou Spring Cloud Bus) fica como trabalho futuro.
- O Config Server não tem autenticação. Ele só é alcançável pela rede do Compose e pela porta 8888 da
  máquina local, e não guarda segredo.
- A configuração do `dev` continua dentro de cada projeto. Centralizar também o `dev` obrigaria quem
  desenvolve a subir o Config Server antes de qualquer serviço.

---

## ADR-013: a gravação da auditoria vai pela fila; a consulta continua HTTP

**Status:** aceito em 03/10/2026, na etapa 4 da disciplina de microsserviços. Implementa a Decisão 6 do
plano da disciplina.

**Contexto:** desde a etapa 2, a aplicação principal gravava cada validação no `audit-service` por
OpenFeign, dentro da thread da validação. Com o serviço fora do ar, o evento se perdia, e com ele travado
a validação esperava o timeout. A auditoria é efeito colateral: quem pediu a validação não precisa que
ela já esteja gravada para receber a resposta.

**Decisão:**

- **Produtor na aplicação principal, direto no RabbitMQ.** O `AuditLogListener` entrega o evento à porta
  `AuditEventPublisher`, e o `RabbitAuditEventPublisher` publica na fila `audit.events` pela exchange
  padrão. Se o `audit-service` recebesse por HTTP e só depois enfileirasse, a aplicação principal
  continuaria dependendo dele no ar.
- **Consumidor no `audit-service`.** O `AuditMessageListener` grava pelo mesmo
  `RegisterPermissionCheckUseCase` do `POST`. O `POST` continua existindo para uso direto.
- **Envelope genérico:** `{source, type, occurredAt, payload}`. O consumidor lê o `type` antes de
  converter o `payload`, o que prepara a direção futura de um serviço de auditoria genérico.
- **O consumidor escolhe o tipo pelo parâmetro do método** (`setAlwaysConvertToInferredType`), e não
  pelo cabeçalho `__TypeId__` do produtor. O nome da classe Java de um lado não existe do outro.
- **Fila durável, declarada pelos dois lados com os mesmos argumentos.** O produtor também declara a
  fila. Sem isso, uma mensagem publicada antes da primeira subida do `audit-service` iria para uma fila
  que não existe, e o broker a descartaria.
- **Fila de mensagens mortas `audit.events.dlq`.** O consumidor rejeita sem devolver à fila o que nunca
  vai ser gravável: tipo desconhecido, payload inválido ou JSON quebrado. Uma falha de gravação, como o
  banco fora, é tentada 3 vezes com intervalo crescente antes de ir para lá. Assim, nada trava a fila
  num laço de reentrega, e nada some sem deixar rastro.
- **O listener roda em segundo plano (`@Async`).** Com o broker parado, o nome `rabbitmq` deixa de
  existir no DNS do Compose, e a resolução leva ~5s para falhar. O `connection-timeout` de 1s não
  cobre essa etapa. Na thread da validação, isso custava 5,5s a cada requisição; em segundo plano, a
  validação responde no tempo de sempre (~0,4s).
- **A consulta continua OpenFeign.** Quem consulta a trilha precisa da resposta na hora, então REST é o
  estilo certo para ela. É também o que mantém o cliente Feign das etapas 2 e 3 vivo na versão final
  (Decisão 5 do plano).

**Consequências:**

- **Consumidor fora do ar:** a mensagem espera na fila e é gravada quando ele volta. Verificado: 3
  validações com o `audit-service` parado ficaram na fila e foram gravadas na volta.
- **Broker fora do ar:** a publicação falha, o evento se perde e fica um `WARN Audit event lost` no log,
  mas a validação responde normalmente. Resolver isso pede uma *outbox* (gravar o evento no banco
  principal na mesma transação e publicar depois), que fica como trabalho futuro.
- **Ordem e duplicidade:** a entrega é *at-least-once*. Se o consumidor cair depois de gravar e antes
  de confirmar, a mensagem volta e o evento é gravado duas vezes. Para uma trilha de auditoria isso é
  tolerável; uma chave de idempotência no envelope resolveria.
- **As tentativas também valem para o que nunca vai dar certo:** uma mensagem de tipo desconhecido
  passa pelas 3 tentativas antes da fila de mensagens mortas. O custo é de poucos segundos por mensagem
  inválida.
- **A fila assíncrona perde a ordem garantida em relação à resposta:** logo depois do `200`, a trilha
  pode ainda não mostrar o evento. A diferença é de milissegundos com o serviço no ar.

---

## ADR-014: importação de rotas em lote com Spring Batch, dentro do módulo `project`

**Status:** aceito em 04/10/2026, na etapa 4 da disciplina de microsserviços. Implementa a Decisão 7 do
plano da disciplina.

**Contexto:** um cliente que migra a API para o SaaS precisa cadastrar dezenas de rotas de uma vez.
Uma requisição por rota é lenta para ele e frágil: se parar no meio, não há registro do que entrou.
É o caso típico de processamento em lote, e não de REST nem de mensageria: um conjunto de dados
conhecido de antemão, processado do começo ao fim, com um resumo no final.

**Decisão:**

- **Endpoint `POST /projects/{projectId}/routes/import`**, que recebe o CSV e dispara o job
  `importRoutesJob` pelo `JobOperator`. O controller só repassa: valida a presença do arquivo pelo
  `RouteImportRequest` e chama o `ImportRoutesUseCase`, que confere o projeto e chama a porta
  `RouteImporter`. O `BatchRouteImporter` (adapter da porta) copia o conteúdo para um arquivo
  temporário, porque o reader do Batch lê do disco.
- **Um step com chunk de 10:** `FlatFileItemReader` (uma linha por vez, sem carregar o arquivo na
  memória) → `RouteImportProcessor` (normaliza a linha e descarta o que não serve, devolvendo `null`) →
  `RouteImportWriter`. Cada chunk é uma transação.
- **O writer grava pelo `AddRouteToProjectUseCase`.** A rota importada passa pelo mesmo
  `Project.addRoute` de uma rota criada pela API, e a regra de criação continua num lugar só.
- **O processor descarta antes o que o agregado recusaria.** A rota repetida no arquivo ou já existente
  no projeto viraria `RouteAlreadyExistsException` no writer e desfaria o chunk inteiro. O processor
  carrega as rotas do projeto uma vez por execução (`@StepScope`) e vai acrescentando as que aceita.
- **Linha com o número errado de colunas é pulada** (`faultTolerant().skip(FlatFileParseException)`), até
  10 por execução.
- **Histórico das execuções no banco** (`spring-boot-starter-batch-jdbc`): as tabelas `BATCH_*` vêm da
  migration `V11`, cópia do `schema-postgresql.sql` do Spring Batch 6.0.4, porque o schema é do Flyway
  (`spring.batch.jdbc.initialize-schema: never`). Os jobs não rodam na subida (`spring.batch.job.enabled:
  false`).
- **Execução síncrona:** o job roda na thread da requisição, e a resposta traz os contadores. O arquivo
  é pequeno e quem importa quer o resumo na hora.
- **No `permission-service`, e não num serviço novo:** a importação grava no agregado `Project`, que é
  da aplicação principal. Um serviço de importação separado teria que gravar por HTTP ou pela fila,
  regra por regra, e não ganharia nada com isso.

**Consequências:**

- Importar o mesmo arquivo de novo não duplica nada: todas as linhas são descartadas e a resposta vem
  com `imported: 0`. Verificado em 04/10: 16 lidas, 12 importadas e 4 descartadas na primeira vez; 16
  descartadas na segunda.
- Um arquivo muito grande prenderia a requisição. O próximo passo seria disparar o job em segundo plano
  (`TaskExecutorJobOperator`), devolver `202` com o `executionId` e consultar o andamento depois.
- O job não é reiniciável de onde parou: cada upload gera um arquivo temporário novo, apagado no fim, e
  um parâmetro `requestedAt` único. Reiniciar exigiria guardar o arquivo enquanto a execução não
  terminasse.
- Sem teste automatizado próprio. O teste de contexto (`PermissionSaasApplicationTests`) garante que o
  job monta, com as tabelas do Batch criadas no H2. O comportamento foi verificado pela pasta
  `Importacao de rotas (Spring Batch)` do Postman.

---

## ADR-015: um repositório por aplicação, com este como guarda-chuva

**Status:** aceito em 05/10/2026, entre uma disciplina e outra: é manutenção do projeto, fora do escopo
de qualquer disciplina. Substitui o ADR-008.

**Contexto:** o ADR-008 manteve as três aplicações como pastas irmãs de um único repositório. Ele
descartou um repositório por serviço porque isso espalharia as tags `etapa-*` e `arq-etapa-*`, a
evidência das disciplinas, por repositórios diferentes. Depois da entrega da disciplina de
microsserviços, duas coisas mudaram:

- o projeto vai ganhar um front-end, com outra linguagem e outro ciclo de build. Dentro de um
  repositório Java, ele misturaria ferramentas e históricos sem ganho nenhum;
- o autor criou a organização Permission-SaaS no GitHub para reunir os repositórios do produto, e quer
  cada aplicação versionada e publicada por conta própria. Isso vale também para o `audit-service`, que
  tem a direção futura de virar um serviço de auditoria genérico, usado por outros projetos.

**Decisão:**

- **Um repositório por aplicação** na organização: `permission_saas_api` (`permission-service`),
  `permission_saas_audit` (`audit-service`), `permission_saas_config` (`config-server`) e, quando
  existir, `permission_saas_front`. Cada um foi extraído com o histórico da sua pasta
  (`git filter-repo`). O do `permission_saas_api` inclui o período em que a aplicação ficava na raiz,
  antes de 28/09/2026.
- **Este repositório vira o guarda-chuva** e é transferido para a organização, com o mesmo nome. Ele
  guarda o histórico completo e **todas as tags**, que continuam apontando para os mesmos commits. Os
  repositórios extraídos não levam as tags `etapa-*` nem `arq-etapa-*`, para não haver duas versões da
  mesma evidência. O GitHub redireciona o endereço antigo (`JairoNetoDev/permission_saas`), que está
  nos documentos de entrega.
- **Submódulos Git** ligam o guarda-chuva às aplicações. Cada commit daqui fixa o commit de cada
  aplicação, então uma tag aqui é a fotografia do sistema inteiro, que é o formato das entregas das
  próximas disciplinas. As URLs do `.gitmodules` são HTTPS, para qualquer pessoa clonar sem chave SSH.
- **O `config-repo/` fica no guarda-chuva**, ao lado do `docker-compose.yml`, e não no repositório do
  Config Server. Os dois descrevem a mesma topologia: os nomes `postgres`, `rabbitmq` e `audit-service`
  dos arquivos são os serviços do Compose, e renomear um deles continua sendo um commit só. O padrão
  `file:../config-repo` do Config Server segue valendo, porque a pasta dele fica ao lado do
  `config-repo/`.
- **Os nomes internos não mudam.** `spring.application.name`, os serviços do Compose, os arquivos do
  `config-repo/`, o cliente Feign `audit-service` e o `source` da mensagem continuam
  `permission-service`, `audit-service` e `config-server`. Só mudam os nomes de repositório e de pasta.
  Renomear as aplicações tocaria configuração, DNS do Compose e dados já gravados, sem ganho.
- **A documentação acompanha o código.** Cada repositório documenta o próprio interior: o
  `permission_saas_api` tem `ARCHITECTURE.md` (módulos e camadas), `DOMAIN.md`, `API.md`, `PATTERNS.md`
  e `TEST-ARCHITECTURE.md`; o `permission_saas_audit`, `ARCHITECTURE.md`, `DOMAIN.md` e `API.md`. Aqui
  ficam a visão do sistema, este log de ADRs com a numeração única, o `RUNNING.md`, a coleção Postman,
  o DER e as pastas das disciplinas.

**Alternativa descartada: pastas ignoradas e um script de clone.** Cada aplicação seria um clone comum
dentro desta pasta, ignorado pelo `.gitignore`, e um script clonaria todos. É mais simples no dia a dia,
mas nenhuma versão fica registrada: reproduzir uma entrega exigiria a mesma tag em cada repositório.

**Consequências:**

- **Clonar exige `--recurse-submodules`**, ou `git submodule update --init` depois. Sem isso, as pastas
  das aplicações vêm vazias.
- **Uma mudança passa a ter dois commits:** o do repositório da aplicação e, quando o conjunto deve
  ficar registrado, o que atualiza o ponteiro aqui. `push.recurseSubmodules=check` impede publicar um
  ponteiro para um commit que ainda não está no GitHub. O fluxo está no `RUNNING.md`.
- **HEAD destacado:** depois de um `git submodule update`, o submódulo fica parado num commit, fora de
  qualquer branch. É preciso `git switch main` antes de commitar nele.
- **Uma mudança de contrato**, como um campo novo na mensagem da fila, vira um commit em cada
  aplicação e um ponteiro atualizado aqui. Como no ADR-008, a duplicação dos contratos continua
  consciente: não há biblioteca compartilhada.
- **O motivo do ADR-008 para descartar esta opção deixou de valer:** as tags continuam todas aqui,
  intactas, e as entregas futuras ganham tag neste repositório, que fixa todas as aplicações de uma vez.
- O `docs/DER.pdf` fica aqui porque desenha o modelo do sistema inteiro, de antes da separação dos
  bancos.

---

## ADR-016: o front-end usa React, TypeScript, Vite e Tailwind CSS, e não o Create React App

**Status:** aceito em 07/10/2026, no início da disciplina de Desenvolvimento de aplicações interativas
com React.

**Contexto:** a disciplina pede um CRUD em React. O `permission_saas_front` existe desde o ADR-015,
ainda sem stack. O item 2 da rubrica pergunta se a aplicação foi criada com o Create React App (CRA),
mas o time do React descontinuou o CRA em 14/02/2025, e ele não recebe mais manutenção.

**Decisão:**

- **React** na versão mais recente (19.3 em 07/10/2026);
- **TypeScript**;
- **Vite** como ferramenta de build, no lugar do CRA;
- **Tailwind CSS** para os estilos.

**Consequência:** o item 2 da rubrica não é seguido ao pé da letra, e o relatório da disciplina cita
esta decisão.
