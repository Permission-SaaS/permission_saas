# 📋 Planejamento — Arquiteturas avançadas de software com microsserviços e Spring Framework

**Aluno:** Jairo Williams Guedes Lopes Neto
**Disciplina:** Arquiteturas avançadas de software com microsserviços e Spring Framework
**Prazo:** 05/10/2026 23:59 (entrega única no Moodle)
**Disponibilidade:** ~1h/dia nos dias úteis; 3–4h nos fins de semana (26–27/09 e 03–04/10)
**Base:** projeto Permission SaaS, na versão entregue em 31/08/2026 (tag `etapa-4`)

> ⚠️ Este arquivo é o plano **desta** disciplina. Os planos anteriores
> (`docs/clean_code_e_padroes_de_projeto/PLAN.md` e
> `docs/desenvolvimento_de_aplicacoes_java_com_spring_boot/PLAN.md`) são evidência já
> submetida e **não devem ser alterados**.

---

## Contexto

O Permission SaaS chega nesta disciplina como um **monolito modular** com cinco módulos
(`shared`, `identity`, `billing`, `permission`, `project`, `audit`), persistência em PostgreSQL
via Flyway, CRUD REST completo, Swagger e fronteiras verificadas pelo Spring Modulith.

A disciplina pede o caminho seguinte: sair do monolito para uma solução distribuída — extrair um
serviço, comunicar por HTTP com OpenFeign, externalizar configuração, containerizar tudo e
introduzir mensageria e processamento em lote.

Três itens que estavam registrados como *trabalho futuro* no `docs/` entram agora no escopo:
**OpenFeign** (cortado na disciplina anterior), **mensageria assíncrona para a trilha de
auditoria** e **bancos separados por serviço**. É a evolução aditiva que o `CLAUDE.md` pede — nada
do que já foi entregue é reescrito.

### Lacunas medidas contra a rubrica (estado em 21/09/2026)

| Item da rubrica                                                                   | Estado hoje                                                                                                                                            |
| --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1 — Controller/Service/Repository separados, sem regra de negócio no controller | ✅ atendido (`api` → `application` → `domain` ← `infrastructure`)                                                                           |
| 2 — módulos do domínio identificáveis                                         | ✅ no código; ❌ falta a apresentação dos módulos no`README.md` como a Etapa 1 pede                                                              |
| 3 — Bean Validation, tratamento de exceções, consultas Spring Data, Swagger    | ⚠️ parcial: validação e`GlobalExceptionHandler` ✅; consultas derivadas existem mas são poucas; anotações Swagger em apenas 5 dos controllers |
| 4 — dependências entre módulos + candidata à separação                      | ❌ análise não escrita                                                                                                                               |
| 5 — funcionalidade extraída para um serviço Spring Boot independente           | ❌ inexistente                                                                                                                                         |
| 6 — API REST do novo serviço com DTOs e Swagger                                 | ❌ inexistente                                                                                                                                         |
| 7 — OpenFeign + endereço externalizado                                          | ❌ inexistente (cortado na disciplina anterior)                                                                                                        |
| 8 — tratamento da indisponibilidade do serviço remoto                           | ❌ inexistente                                                                                                                                         |
| 9 — Profiles + variáveis de ambiente                                            | ⚠️ parcial: há`${VAR:default}` no `application.yml`, mas **nenhum** `application-dev`/`application-prod`                              |
| 10 — banco relacional, cada serviço dono dos próprios dados                    | ⚠️ PostgreSQL ✅, mas há um único banco para tudo                                                                                                  |
| 11 — imagens Docker das duas aplicações                                        | ⚠️ só a aplicação principal tem`Dockerfile`                                                                                                     |
| 12 — Docker Compose integrando os componentes                                    | ⚠️ compose atual sobe app + Postgres apenas                                                                                                          |
| 13, 14 — produtor, fila e consumidor de mensagens                                | ❌ inexistente (hoje o Observer é síncrono, em processo)                                                                                             |
| 15 — Job Spring Batch com chunks                                                 | ❌ inexistente                                                                                                                                         |
| 16 — quando usar REST, mensageria ou Batch                                       | ❌ reflexão não escrita                                                                                                                              |
| Tags de marco                                                                     | ✅ `arq-etapa-1` … `arq-etapa-4` — ver Decisão 4 |

---

## Decisões

1. **Política de IA (🟢).** Esta disciplina incentiva o uso de IA, exigindo citação. O modo de
   trabalho muda em relação à anterior: a IA pode escrever código, e não só plano e documentação.
   Em contrapartida, o `README.md` ganha uma seção **Uso de IA** declarando ferramenta
   (Claude Code / Opus 5), em que partes foi usada e o que foi revisado pelo aluno.
   A regra registrada no `CLAUDE.md` para a disciplina anterior deixa de valer aqui.
2. **Serviço a extrair: `audit`.** É a escolha coerente com o domínio, não uma extração para
   cumprir requisito:

   - a trilha de auditoria é *append-only* e ninguém do fluxo principal lê dela para decidir nada;
   - já é consumida por evento (`PermissionValidatedEvent` → `AuditLogListener`), ou seja, o
     acoplamento com o resto já é o mais fraco do projeto;
   - tem dados próprios (`audit_events`) e sem FK para as tabelas dos outros módulos (ADR-004) —
     separar o banco não quebra integridade referencial;
   - cresce em volume por um motivo diferente do resto (uma validação de permissão gera um evento;
     um projeto criado gera um), então escala de forma independente.

   Extrair `billing` seria o oposto: `ApiKeyValidationHandler` depende dele **dentro** da
   requisição de validação, e a separação transformaria uma chamada de método em ponto de falha no
   caminho crítico.
3. **Layout do repositório: pastas irmãs, não multi-módulo Maven.** Um repositório só, com cada
   aplicação na sua pasta e `pom.xml` próprio, sem `pom` agregador:

   ```
   permission_saas/
   ├── permission-service/  aplicação principal
   ├── audit-service/       serviço extraído
   ├── config-server/       Spring Cloud Config Server
   └── docker-compose.yml   orquestra todos
   ```

   **Revisada em 28/09/2026.** A primeira versão mantinha a aplicação principal na raiz, para não
   "sujar o diff" movendo `src/`. O Git registra o movimento como renomeação, sem linha alterada,
   e as tags antigas seguem intactas; já o serviço aninhado dentro da aplicação principal
   confundia a leitura do repositório e a IDE. Decisão, revisão e alternativa descartada no
   **ADR-008** de `docs/ARCHITECTURE.md`.
4. **Nome das tags — há conflito.** A disciplina pede `etapa-1` … `etapa-4`, mas essas tags **já
   existem** apontando para a disciplina de Spring Boot. Mover qualquer uma delas destrói a
   evidência já avaliada.

   - **Aprovado pelo professor em 28/09/2026:** `arq-etapa-1` … `arq-etapa-4`, com uma tabela no `README.md`
     ligando cada tag ao marco correspondente da disciplina. `arq-etapa-1` foi a primeira criada.
   - As tags antigas `etapa-1` … `etapa-4` nunca são reapontadas.
5. **A consulta de auditoria continua exposta pela aplicação principal, como proxy Feign.** Ao
   extrair o `audit`, a aplicação principal mantém um `GET /audit-events` que **não toca banco**:
   delega ao `audit-service` pelo `AuditClient`. É o desenho que a Etapa 2 pede
   (`Controller → Service → Feign Client → HTTP → Microsserviço`) e resolve três coisas de uma vez:

   - **mantém os itens 7 e 8 vivos na tag final.** Na Etapa 4 a *gravação* migra para a fila; sem
     este endpoint, o `@FeignClient` ficaria sem nenhum chamador em `arq-etapa-4` — justamente a
     tag que o professor abre — e o OpenFeign viraria código morto;
   - **dá a demonstração de indisponibilidade** que o item 9 da Etapa 2 exige: com o
     `audit-service` parado, a consulta degrada com resposta amigável enquanto o
     `POST /validate-permission` continua respondendo;
   - **é barato**: um controller fino, sem banco, sem projeto novo.
6. **Mensageria: RabbitMQ** (confirmado com o professor em 28/09/2026). Produtor na aplicação
   principal, fila `audit.events`, consumidor no `audit-service`. **Quem publica na fila é a aplicação
   principal, direto no RabbitMQ** — e não o `audit-service` enfileirando o que recebe por HTTP: com
   a fila atrás do serviço, a aplicação principal continuaria esperando a resposta HTTP e perderia o
   evento com o serviço fora do ar; com o broker entre os dois, a mensagem espera na fila até o
   consumidor voltar. Na Etapa 2 a gravação de
   auditoria passa por Feign (síncrona); na Etapa 4 ela migra para a fila, e o Feign permanece
   para a **consulta** (`GET /audit-events`). Isso dá à Etapa 4 uma comparação real entre os dois
   estilos dentro do mesmo domínio, em vez de dois mecanismos desconexos. A reflexão da Etapa 4
   parte do que a Etapa 2 mostrar na prática — com o `audit-service` fora do ar, a validação espera
   o timeout do Feign e o evento de auditoria se perde —, e a fila entra como a evolução que resolve
   essa dor, não como requisito cumprido.
7. **Batch: importação de rotas por CSV.** Um cliente que migra sua API para o SaaS precisa
   cadastrar dezenas de rotas de uma vez — é a operação do domínio que naturalmente é lote, e não
   requisição. `Job` → `Step` (chunk 10) → `FlatFileItemReader` → processor que normaliza
   `httpMethod`/`path` e descarta duplicadas → writer que persiste via o repositório do módulo
   `project`.

---

## Arquitetura alvo

### Hoje (tag `etapa-4` da disciplina anterior)

```
Cliente HTTP
↓
Aplicação Spring Boot (monolito modular)
├── identity ├── billing ├── permission ├── project ├── audit
↓
PostgreSQL (permissions_saas)
```

### Ao final da Etapa 2

```
Cliente HTTP ──▶ Aplicação Principal
                 ├── permission / project / billing / identity
                 └── AuditClient ──Feign──▶ audit-service
                                            └── audit_events (grava e consulta)
```

### Ao final da Etapa 4

```
Config Server
  ↓ (configuração)
Aplicação Principal ──Feign──▶ audit-service        (consulta)
        │                          ▲
        └──mensagem──▶ RabbitMQ ───┘                (gravação)
        │
        └── Spring Batch: CSV de rotas → Job → project

Aplicação Principal → permissions_saas      audit-service → audit_db
```

---

## Cronograma

### Etapa 1 — Organização Arquitetural (22–24/09)

| Dia | Data      | Horas | Entrega                                                                                                                                                                                                                                                                      |
| --- | --------- | ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 ✅ | Ter 22/09 | 1h    | **Feito em 23/09.** `README.md`: apresentação dos módulos e responsabilidades, análise de dependências (ex.: `permission → project` via `RouteAccessChecker`, `permission → billing` via `ApiKeyValidator`) e justificativa do `audit` como candidato a serviço independente |
| 2 ✅ | Qua 23/09 | 1h    | **Feito em 28/09, com ajuste de escopo.** Duas consultas JPQL no `audit` — `search` (tipo, projeto, período) e `searchDenied` (negadas por projeto e período) —, com a filtragem saindo da memória para o banco (**ADR-009**); verificadas contra o PostgreSQL real. Ficaram de fora: a consulta de rotas por método/`path` (as rotas vivem dentro do agregado `Project`, ADR-006, e um repositório só de rotas quebraria esse desenho), o teste de integração das consultas (vai para o `audit-service`) e a varredura dos `@Size` que faltam em `RegisterClientRequest`/`RegisterPlanRequest` (buffer do dia 14). De carona: Queries separadas dos Commands em `application/query/` (`docs/PATTERNS.md`) |
| 3 ✅ | Qui 24/09 | 1h    | **Feito em 25/09.** Anotações Swagger (`@Tag`, `@Operation`, `@ApiResponse`) nos controllers que faltavam; **ADR-008** (layout de vários projetos no mesmo repositório). **Tag `arq-etapa-1`** criada no fechamento do dia 2, em 28/09                                                                           |

### Etapa 2 — Separação e Comunicação (25–28/09)

| Dia | Data       | Horas | Entrega                                                                                                                                                                                                                                                                                                                                                                                    |
| --- | ---------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 4 ✅ | Sex 25/09  | 1h    | **Feito em 28/09.** Esqueleto do `audit-service/`: `pom.xml` (Spring Boot 4.1.0, sem Security), classe `@SpringBootApplication`, `application.yml` na porta 8081; cópia do `audit/domain`, do mapeamento JPA e das consultas JPQL do ADR-009 |
| 5 ✅ | Sáb 26/09 | 3h    | **Feito em 28/09, com ajuste.** `GET /audit-events` (com os filtros da etapa 1) e `POST /audit-events/permission-checks` — o caminho é específico do tipo porque o corpo só serve para validações de permissão —, DTOs de contrato próprios, Bean Validation, `GlobalExceptionHandler`, Swagger, migration `V1`; pasta `audit-service (8081)` na coleção do Postman e seção no `docs/API.md` |
| 6 ✅ | Dom 27/09  | 3h    | **Feito em 28–30/09** (passos 6 a 10 de "Onde parou" abaixo): BOM Spring Cloud `2025.1.3` + `spring-cloud-starter-openfeign`, `AuditClient`, gravação e consulta pelo Feign com timeout, `try/catch` e `503`, persistência local do `audit` removida (ADR-010). Aplicação principal:`AuditClient` (`@FeignClient`) no lugar do `AuditEventRepositoryAdapter`; `AuditLogListener` passa a chamar o cliente; `GET /audit-events` da aplicação principal vira proxy Feign (Decisão 5); **tratamento de indisponibilidade** (falha do Feign não pode derrubar a validação de permissão nem vazar stack trace); URL em `audit.service.url`; remoção do `audit` do módulo principal (controller e adapter JPA) |
| 7 ✅ | Seg 28/09  | 1h    | **Feito em 01/10.** Pasta `audit-service fora do ar` no Postman, com o roteiro da demonstração de indisponibilidade; seções "Serviço independente: `audit-service`" (nome, responsabilidade, o que saiu do monolito, motivo) e "Reflexões arquiteturais → Etapa 2" no `README.md` → **tag `arq-etapa-2`**                                                                                                                    |

### Etapa 3 — Configuração e Execução (29/09–02/10)

| Dia | Data      | Horas | Entrega                                                                                                                                                                                                                                                  |
| --- | --------- | ----- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 8 ✅ | Ter 29/09 | 1h    | **Feito em 02/10** (passo 13 de "Onde parou"): `application-dev`/`application-prod` nos dois serviços, variáveis `DB_URL`, `DB_USERNAME`, `DB_PASSWORD`, `AUDIT_SERVICE_URL`, `SERVER_PORT`; `.env.example` só com o que o Compose repassa (ADR-011) |
| 9 ✅ | Qua 30/09 | 1h    | **Metade feita em 28/09:** o `audit-service` já nasceu com banco próprio (`audit_db`, container `audit-postgres`, usuário `audit`, porta 5433). **Resto em 30/09:** migration `V10` na aplicação principal removendo `audit_events`, junto com a persistência local do `audit` (ADR-010) |
| 10 ✅ | Qui 01/10 | 1h    | **Feito em 02/10** (passo 14): `config-server/` com backend `native` lendo `config-repo/`; os dois serviços buscam nele, no `prod`, os endereços e o log de SQL (ADR-012) |
| 11 ✅ | Sex 02/10 | 1h    | **Feito em 02/10** (passos 12 e 15): `Dockerfile` do `audit-service` e do `config-server`; `docker-compose.yml` com os cinco containers na rede do Compose, sem `localhost` entre eles; reflexão da Etapa 3 no `README.md` → **tag `arq-etapa-3`** |

### Etapa 4 — Assíncrono e Batch (03–05/10)

| Dia | Data       | Horas | Entrega                                                                                                                                                                                                                                                             |
| --- | ---------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 12 ✅ | Sáb 03/10 | 4h    | **Feito em 03/10** (passo 16 de "Onde parou"): RabbitMQ no Compose; a aplicação principal publica cada validação na fila `audit.events` num envelope genérico; o `audit-service` consome e grava; fila de mensagens mortas; demonstração com o consumidor parado no Postman (ADR-013) |
| 13 ✅ | Dom 04/10  | 4h    | **Feito em 04/10** (passo 17 de "Onde parou"): importação de rotas por CSV com Spring Batch: `Job` → `Step` (chunk 10) → `FlatFileItemReader` → processor que normaliza e descarta → writer pelo `AddRouteToProjectUseCase`; CSV de exemplo com 16 linhas (ADR-014). Reflexão REST × mensageria × Batch e tag `arq-etapa-4` ficam para o passo 18 |
| 14  | Seg 05/10  | 1–2h | Buffer:`./mvnw verify` nos quatro projetos, `docker compose up --build` do zero, coleção Postman atualizada, seção **Uso de IA**, PDF e postagem no Moodle                                                                                            |

Total planejado: **~24h em 14 dias**. O caminho crítico é o fim de semana de 26–27/09 (extração +
Feign): sem ele caem de uma vez os itens 5, 6, 7 e 8 da rubrica, e as Etapas 3 e 4 ficam sem o
segundo serviço para configurar, containerizar e alimentar por fila.

### Replanejamento em 28/09

A Etapa 1 fechou com quatro dias de atraso e o fim de semana de 26–27/09 não entregou a extração.
Os dias restantes ficam assim; as tabelas acima continuam valendo como descrição do conteúdo de
cada dia.

| Data | Dias do plano | Entrega |
|---|---|---|
| Seg 28/09 | 2 | Consultas do `audit`, documentação, tag `arq-etapa-1` |
| ~~Ter 29 – Qua 30/09~~ Seg 28/09 ✅ | 4, 5 e 9 (metade) | `audit-service`: esqueleto, `POST`/`GET`, banco próprio — adiantado. De carona, a aplicação principal saiu da raiz para `permission-service/` (ADR-008 revisado) |
| Ter 29/09 – Qui 01/10 | 6, 7 e 9 (resto) | Feign (gravação e consulta), indisponibilidade, remoção do `audit` do monolito, testes pelo Postman/Swagger, tag `arq-etapa-2` — a folga ganha no `audit-service` vai para cá. **Situação em 01/10:** a terça não rendeu código e consumiu a folga; os passos 6 a 10 fecharam na quarta (30/09) e o 11 na quinta (01/10), com a tag `arq-etapa-2`. Em dia com este replanejamento, sem margem |
| Sex 02/10 | 8 e 11 | Profiles, variáveis de ambiente, `Dockerfile` e Compose, tag `arq-etapa-3`. É o dia mais apertado: proposta de divisão — Claude faz a parte mecânica (`Dockerfile` do `audit-service`, Compose, profiles), Jairo as decisões e a reflexão. **Situação em 02/10:** feito, com o Config Server (dia 10) adiantado do fim de semana; Jairo decidiu que o Claude escrevesse a parte de Docker e explicasse depois |
| Sáb 03 – Dom 04/10 | 12 e 13 | RabbitMQ e Batch, tag `arq-etapa-4`; Config Server (dia 10) só se sobrar tempo |
| Seg 05/10 | 14 | Buffer, seção **Uso de IA**, entrega |

O banco próprio do `audit-service` (dia 9) sobe para a criação do serviço: nascer com `audit_db`
custa menos do que migrar depois. **Testes automatizados** das partes novas saem do caminho
crítico — a rubrica não pontua testes JUnit, e as demonstrações que ela pede (Postman/Swagger,
serviço fora do ar, fila com consumidor parado) são manuais. Ficam como trabalho futuro, a começar
pelo teste de integração das consultas do ADR-009.

### Onde parou (atualizado em 04/10)

**Etapa 4 em andamento.** A mensageria fechou em 03/10 e o Spring Batch em 04/10; falta o **passo 18** (reflexão, Uso de IA, tag e entrega). A
sequência até a tag `arq-etapa-4`:

| Passo | Quem | Entrega |
|---|---|---|
| 16 ✅ | Claude (a decisão do envelope genérico foi do Jairo) | **Mensageria (ADR-013).** A gravação da auditoria sai do Feign e vai por mensagem. A porta `AuditEventPublisher` e o adapter `RabbitAuditEventPublisher` publicam na fila `audit.events`, num envelope `{source, type, occurredAt, payload}`. O `AuditMessageListener` do `audit-service` consome e grava pelo mesmo caso de uso do `POST`. A fila é durável e declarada pelos dois lados; o que não pode ser gravado vai para a `audit.events.dlq`, depois de 3 tentativas. O `AuditLogListener` virou `@Async`: com o broker parado, a resolução do nome demorava 5,5s e prendia a validação. A porta `AuditTrail` ficou só com a consulta (Feign). RabbitMQ no Compose (painel na 15672) e o endereço dele no `config-repo/`. A pasta `audit-service fora do ar` do Postman passou a mostrar a mensagem esperando na fila e chegando depois. Testado em 03/10: `clean verify` nos três projetos; consumidor parado (3 mensagens esperaram e foram gravadas na volta); 3 mensagens inválidas na `.dlq`; broker parado (validação em 0,4s, evento perdido com `WARN`); newman com a coleção inteira (63 requisições, 102 asserções) e o roteiro isolado (22 requisições, 39 asserções). Na revisão, achei um import errado (`MessageConverter` do Logback) que a IDE trocou porque ainda não tinha recarregado o `pom.xml`, e uma asserção do Postman que lia contagens atrasadas do painel; os dois foram corrigidos |
| 17 ✅ | Claude (o Jairo ia escrever o Batch, mas, sem tempo e sem ter mexido com Batch antes, pediu que o Claude escrevesse tudo e explicasse; o estudo fica para a semana seguinte à entrega) | **Spring Batch (ADR-014).** `POST /projects/{projectId}/routes/import` recebe o CSV pelo `RouteImportRequest` (`@NotNull`; o arquivo temporário fica no adapter, não no controller, como o Jairo apontou na revisão). O `ImportRoutesUseCase` confere o projeto e chama a porta `RouteImporter`, implementada pelo `BatchRouteImporter`, que dispara o `importRoutesJob`. O job tem `FlatFileItemReader<RouteCsvLine>` (`@StepScope`, pula o cabeçalho), o `RouteImportProcessor` (normaliza método e path; descarta nome ou path vazio, método inválido, rota repetida no arquivo ou já existente no projeto), o `RouteImportWriter` (grava pelo `AddRouteToProjectUseCase`), chunk de 10 e linha malformada pulada, até 10. Tabelas `BATCH_*` pela migration `V11`. CSV de exemplo em `docs/postman/rotas-exemplo.csv` e pasta `Importacao de rotas (Spring Batch)` no Postman. Testado em 04/10: `clean verify`; 16 lidas, 12 importadas e 4 descartadas, e 0 importadas ao repetir; 2 commits (um por lote) em `batch_step_execution`; CSV com 2 linhas quebradas (1 importada, 2 puladas); newman com a coleção inteira, na ordem e com a queda do consumidor (68 requisições, 113 asserções) |
| 18 | Jairo + Claude | Reflexão da Etapa 4 no `README.md` (6 perguntas, mais a diferença entre mensageria e Batch), seção **Uso de IA**, tag `arq-etapa-4` |

A Etapa 3 fechou em 02/10 com a tag `arq-etapa-3`. A sequência que levou à tag, para registro:

| Passo | Quem | Entrega |
|---|---|---|
| 12 ✅ | Claude (rascunho do `Dockerfile` do `audit-service` pelo Jairo) | `audit-service/Dockerfile` (multi-stage, como o da aplicação principal) e `.dockerignore` nos dois projetos. O agente de debug (JDWP) saiu das duas imagens e passou a ser ligado pelo Compose, via `JAVA_TOOL_OPTIONS` (portas 5005 e 5006): o enunciado pede só o necessário para executar. O healthcheck troca `curl` por `wget`, porque a imagem `eclipse-temurin:21-jre-alpine` não tem `curl` e o container da aplicação principal ficava `unhealthy` para sempre. O `audit-service` entrou no Compose com `audit-postgres:5432` e a aplicação principal recebe `AUDIT_SERVICE_URL=http://audit-service:8081`, sem `localhost` entre containers. Volume `audit_logs` para o `logs/audit-events.txt` e `POSTGRES_HOST_PORT` para publicar o banco principal fora da 5432. Testado em 02/10: `docker compose up -d --build` do zero, os 4 containers `healthy`; newman contra os containers com 29 requisições e 54 asserções, incluindo derrubar e religar o `audit-service`; evento no `audit_db` e no arquivo do volume |
| 13 ✅ | Claude | `application.yml` comum + `application-dev.yml` (padrão; valores para `localhost`, SQL no log, nenhuma variável obrigatória) + `application-prod.yml` (tudo de variável, **sem valor padrão**, SQL fora do log) nos dois serviços (**ADR-011**). Variáveis `DB_URL`, `DB_USERNAME`, `DB_PASSWORD`, `AUDIT_SERVICE_URL`, `SERVER_PORT`; o Compose ativa `prod`; o `.env` fica só com os segredos que o Compose repassa e `POSTGRES_HOST_PORT`. Testado em 02/10: `clean verify` (22 + 9 testes); os dois serviços em `dev` sem `.env`, com porta, banco e URL trocados por variável; os dois em `prod` sem variáveis recusam subir; Compose em `prod` com newman, 30 requisições e 55 asserções, sem SQL no log e Swagger exigindo senha |
| 14 ✅ | Claude | `config-server/` (porta 8888, backend `native` lendo `config-repo/` montado como volume); no `prod`, os dois serviços importam `configserver:${CONFIG_SERVER_URL}` e recebem dele os endereços (banco, `audit-service`) e o log de SQL; segredos seguem em variáveis; `dev` e `test` desligam o cliente (**ADR-012**). `spring.application.name` da aplicação principal vira `permission-service`. Pasta `config-server (8888)` no Postman. Testado em 02/10: `clean verify`; `dev` sobe sem o Config Server; Compose com 5 containers `healthy`; newman com 30 requisições e 55 asserções, mais 7 asserções na pasta nova; `show-sql` trocado só no `config-repo/` valeu depois de `docker compose restart`, sem rebuild; com o Config Server parado, o `audit-service` não sobe (`ConfigClientFailFastException`) |
| 15 ✅ | Jairo + Claude | Reflexão da Etapa 3 no `README.md` (perguntas 1 e 2 a partir do que foi feito; 3 a 6 com as respostas do Jairo, redação do Claude). De carona, o `README.md` foi enxugado de 625 para ~420 linhas: o guia de ambiente (profiles, variáveis, Config Server, rodar fora do Docker, debug, testes) foi para o novo `docs/RUNNING.md`, e o fluxo em `curl` desatualizado deu lugar à pasta `Fluxo completo` do Postman. Tag `arq-etapa-3` |

A Etapa 2 fechou em 01/10 com a tag `arq-etapa-2`. A sequência que levou à tag, para registro:

| Passo | Quem | Entrega |
|---|---|---|
| 6 ✅ | Jairo + Claude | BOM Spring Cloud `2025.1.3` (a última GA para Spring Boot 4.0–4.1, conferida no Initializr e no Maven Central), `spring-cloud-starter-openfeign`, `@EnableFeignClients`, `audit.service.url: ${AUDIT_SERVICE_URL:http://localhost:8081}`. Commit `611aa53` |
| 7 ✅ | Jairo + Claude | `AuditClient` (`@FeignClient(name = "audit-service", url = "${audit.service.url}")`) em `audit/infrastructure/client/`, com `registerPermissionCheck` (POST) e `searchAuditEvents` (GET); DTOs de contrato espelhados em `client/dto/` (`RegisterPermissionCheckRequest`, `AuditEventResponse`, sem Bean Validation). Nomes explícitos em cada `@RequestParam`, `required = false` (nulo omite o filtro) e `from`/`to` como `Instant`, para não mandar `+` na URL |
| 8 ✅ | Jairo + Claude | Gravação: o `AuditLogListener` traduz o evento e chama a porta `AuditTrail` (adapter `AuditTrailClientAdapter` sobre o `AuditClient`), com timeout de 1s/2s no cliente `audit-service` e `try/catch` — com o serviço fora do ar a validação responde normalmente e o evento se perde (limitação que a fila resolve na etapa 4). Testado em 30/09: serviço ligado (evento no `audit_db`), desligado (200 em 0,4s + `WARN`) e travado (200 em 2,5s) |
| 9 ✅ | Jairo + Claude | Consulta: o `GET /audit-events` da aplicação principal vira repasse ao serviço pela porta `AuditTrail` (modelo de leitura `AuditTrailEntry`); período invertido e filtro inválido seguem `400` locais; serviço fora do ar responde `503` (`ServiceUnavailableException` no `shared`). Testado em 30/09: 8080 devolve o mesmo que a 8081, filtros `projectId`/`onlyDenied`/`type` minúsculo/`from` com fuso `+02:00`, os dois `400` e o `503` |
| 10 ✅ | Claude | Persistência do `audit` apagada do monolito (entidades, repositórios, adapter, portas antigas, `AuditDemoRunner`, file writer, `ProjectLifecycleEvent`) e migration `V10` apagando `audit_events` (ADR-010) — fecha o dia 9. Testado em 30/09: `clean verify` (22 + 9 testes) e as 10 migrations num PostgreSQL vazio. Commit `a48c658` |
| 11 ✅ | Jairo + Claude | Pasta `audit-service fora do ar` no Postman e as seções do `audit-service` e da reflexão da etapa 2 no `README.md` — respostas do Jairo, redação do Claude, revisada pelo Jairo. De carona, o `README.md` passa a dizer Spring Boot 4.1.0, a versão dos dois `pom.xml`. Tag `arq-etapa-2` |

A pasta nova do Postman tem cinco requisições: com o serviço parado, a validação segue respondendo
`200` (e o log mostra `Audit event lost: ...`) e a consulta devolve `503` sem detalhe interno; com o
serviço religado, a trilha mostra que o evento do período fora do ar se perdeu e que a gravação voltou.
Verificada em 01/10 com o newman, em bancos e portas descartáveis: 40 de 40 asserções, contando a
pasta `Fluxo completo`.

Pendências menores fora da sequência:

- O `git stash` "IT do audit (plano futuro)" ficou obsoleto: testa o `AuditEventRepositoryAdapter` do
  monolito, apagado no passo 10, e está no layout antigo (`src/` na raiz). O teste de integração das
  consultas faz sentido no `audit-service`, como trabalho futuro.
- **Proposta para a etapa 4 (dia 12), a confirmar com o Jairo:** desenhar a mensagem do RabbitMQ como
  envelope genérico (`source`, `type`, `occurredAt`, `payload`), alinhado à direção futura do
  `audit-service` registrada em `docs/ARCHITECTURE.md` → "Direção futura". Mesmo custo de um formato
  específico.

### Ordem de corte, se atrasar

Cortar de baixo para cima, nunca as tags:

1. **Filtros do `GET /audit-events`** no serviço novo — entregar a consulta sem query params. Não
   há item de rubrica sobre filtros, e o endpoint continua provando a comunicação Feign.
2. **Config Server** (dia 10) — **cai por último**: não tem item de rubrica próprio (o item 9 é
   coberto por Profiles + variáveis de ambiente), mas é **exigência escrita do enunciado da
   Etapa 3** (`ETAPA3.md`, "Configuração centralizada"). Só cortar se a Etapa 4 estiver em risco;
   nesse caso vira "trabalho futuro" documentado e a reflexão da Etapa 3 responde o *porquê* da
   centralização mesmo sem o serviço no ar.

Se a Etapa 4 não fechar até 04/10, o dia 05/10 deixa de ser buffer e vira dia de execução, com a
postagem no Moodle na última hora.

---

## Reaproveitamento (não reinventar)

- `audit/domain/` e `audit/infrastructure/` — vão quase inteiros para o `audit-service`; o trabalho
  é de recorte e contrato, não de modelagem nova.
- `shared/api/GlobalExceptionHandler.java` — copiar para o serviço novo mantém o mesmo mapeamento
  de status HTTP nos dois lados.
- `shared/domain/Mapper.java` — mesma interface para os mappers do serviço extraído.
- `permission/domain/event/PermissionValidatedEvent` — já é o contrato do que vai para a fila na
  Etapa 4; a carga da mensagem sai dele.
- `permission-service/Dockerfile` — modelo para os `Dockerfile` dos projetos novos.
- `audit/api/` — o controller atual é o molde do `GET /audit-events` que vira proxy Feign
  (Decisão 5) e do controller equivalente dentro do `audit-service`.

---

## Não incluído

- **Service discovery (Eureka) e API Gateway.** Não há item de rubrica; o Compose resolve os nomes
  dos serviços na rede interna, que é o suficiente para a solução desta entrega.
- **Resiliência avançada (Resilience4j, circuit breaker, retry).** A própria Etapa 2 dispensa
  ("não será obrigatório utilizar mecanismos avançados de resiliência"); o tratamento será o
  `try/catch` do Feign com resposta de indisponibilidade.
- **Quebrar `billing`, `identity` ou `project` em serviços.** A Etapa 2 pede uma única
  responsabilidade extraída, e nenhum dos três tem o desacoplamento que o `audit` já tem.
- **Aplicação consumidora externa (`permission-client-demo`).** Estava prevista como demonstração
  do SaaS pelo lado de quem o compra, e foi **cortada do escopo em 23/09/2026**: nenhum item de
  rubrica depende dela (o item 7 pede a *aplicação principal* consumindo o serviço extraído), a
  Etapa 2 aceita Postman/Swagger UI como "Testes da comunicação" (item 10) e o enunciado
  desaconselha múltiplas extrações ("Será suficiente extrair uma única funcionalidade"). Um
  terceiro projeto custaria o dia 7 inteiro sem pontuar. Fica registrada como **trabalho futuro**
  no `README.md`.
- **Spring Security / JWT real e front-end.** Continuam fora, como nas disciplinas anteriores.
- **Migração dos eventos de auditoria já gravados** para o banco do serviço novo. O histórico local
  não é evidência de nada avaliado; o serviço começa com a tabela vazia.

---

## Citação de IA (exigida pela política 🟢)

Registrar no `README.md`, antes da entrega:

- **Ferramenta:** Claude Code (modelo Opus 5), usado como par de programação e revisor.
- **Onde foi usada:** planejamento, divisão do enunciado, configuração de Feign/RabbitMQ/Batch,
  `Dockerfile` e Compose, documentação e revisão de código.
- **O que foi verificado pelo aluno:** toda a solução roda localmente via
  `docker compose up --build`, com os testes do repositório passando — a checagem descrita em
  "Verificação".

---

## Verificação

Ao final de cada dia, nos projetos tocados:

```bash
./mvnw test                       # inclui verifiesModularStructure()
./mvnw clean package -DskipTests
```

A partir da Etapa 2:

```bash
docker compose up --build -d
curl http://localhost:8080/ping
curl http://localhost:8081/audit-events                     # serviço novo, isolado
curl -X POST http://localhost:8080/validate-permission ...  # deve gerar evento no serviço novo
docker compose stop audit-service                           # a validação deve continuar respondendo
```

A partir da Etapa 4:

```bash
docker compose stop audit-service    # publicar eventos com o consumidor parado
# conferir a fila audit.events no painel do RabbitMQ (15672)
docker compose start audit-service   # as mensagens devem ser consumidas ao religar
curl -X POST http://localhost:8080/routes/import -F 'file=@routes.csv'
```

Antes da tag final:

```bash
git tag -l    # deve listar as quatro tags desta disciplina, sem tocar em etapa-1..etapa-4
```
