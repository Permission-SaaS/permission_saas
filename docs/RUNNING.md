# Como rodar e desenvolver

Guia do ambiente: como subir a solução, como cada aplicação é configurada em cada ambiente, como
rodar fora do Docker, depurar e testar. A visão geral e o comando para subir tudo estão no
[`README.md`](../README.md).

## Pré-requisitos

- Docker + Docker Compose (v2, comando `docker compose`). Basta isso para subir a solução: o build
  das aplicações acontece dentro das imagens.
- Para rodar fora do Docker: JDK 21. O Maven Wrapper (`./mvnw`) já está em cada projeto e baixa a
  versão certa do Maven sozinho.

Cada aplicação é um projeto Maven independente, com seu próprio `pom.xml`, `mvnw` e `Dockerfile`:
os comandos `./mvnw` rodam **dentro** da pasta do projeto (ADR-008 em
[`ARCHITECTURE.md`](ARCHITECTURE.md)).

## Subir tudo com o Docker Compose

```bash
cp .env.example .env
docker compose up -d --build
```

Sobem seis containers, na rede que o Compose cria para o projeto:

| Container            | Imagem                          | Porta na máquina            | Fala com                                                    |
| -------------------- | ------------------------------- | --------------------------- | ----------------------------------------------------------- |
| `config-server`      | `config-server/Dockerfile`      | 8888                        | — (lê `config-repo/`, montado como volume)                  |
| `permission-service` | `permission-service/Dockerfile` | 8080                        | `config-server:8888`, `postgres:5432`, `audit-service:8081`, `rabbitmq:5672` |
| `audit-service`      | `audit-service/Dockerfile`      | 8081                        | `config-server:8888`, `audit-postgres:5432`, `rabbitmq:5672` |
| `postgres`           | `postgres:16`                   | 5432 (`POSTGRES_HOST_PORT`) | —                                                           |
| `audit-postgres`     | `postgres:16`                   | 5433                        | —                                                           |
| `rabbitmq`           | `rabbitmq:4-management`         | 5672 · 15672 (painel)       | —                                                           |

- As duas aplicações sobem com o profile `prod`, e só depois que o `config-server`, o banco de cada
  uma e o `rabbitmq` estão `healthy`.
- Entre containers, o endereço é o **nome do serviço** e a porta de dentro, nunca `localhost`: num
  container, `localhost` é o próprio container.
- As migrations do Flyway de cada aplicação rodam na subida, cada uma no seu banco.
- Os dados ficam em volumes (`permission_saas_pgdata`, `audit_pgdata`); o arquivo
  `logs/audit-events.txt` do `audit-service` fica no volume `audit_logs`, e as mensagens do RabbitMQ
  no `rabbitmq_data`. Tudo isso sobrevive a
  `docker compose down`; só `down -v` apaga.

```bash
curl http://localhost:8080/ping                  # pong
curl http://localhost:8081/actuator/health       # {"status":"UP",...}
docker compose ps                                # os seis como "healthy"
```

**Porta 5432 ocupada** por um PostgreSQL instalado na máquina: publique o banco em outra porta com
`POSTGRES_HOST_PORT=5434 docker compose up -d --build`, ou ponha `POSTGRES_HOST_PORT=5434` no `.env`.
Isso só muda o acesso de fora: entre containers, o banco continua em `postgres:5432`.

## Profiles e variáveis de ambiente

Cada aplicação tem três arquivos de configuração em `src/main/resources/` (ADR-011):

| Arquivo                | Quando vale                                      | O que tem                                                                                                    |
| ---------------------- | ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------ |
| `application.yml`      | sempre                                           | O que não muda entre ambientes: Flyway, `ddl-auto: validate`, timeouts do Feign, actuator, porta via `SERVER_PORT` |
| `application-dev.yml`  | profile `dev`, o padrão quando nenhum é ativado | Banco e `audit-service` em `localhost`, SQL no log, segredos de mentira. **Toda variável tem valor padrão** |
| `application-prod.yml` | profile `prod`, ativado pelo Docker Compose      | A importação do Config Server e os segredos, de variável de ambiente **sem valor padrão**. Endereços e log de SQL vêm do Config Server |

O profile é escolhido por `SPRING_PROFILES_ACTIVE`. Na máquina, sem nada definido, vale o `dev`: não
precisa de `.env` nem de `export`. O Compose define `prod` e passa a cada container os segredos dele;
o resto, cada serviço busca no Config Server.

Em `prod`, se faltar uma variável ou o Config Server não responder, o serviço não sobe, de propósito:
é melhor do que subir apontando para o banco errado. Com o Config Server fora do ar, o erro é
`ConfigClientFailFastException: Could not locate PropertySource and the resource is not optional`.

| Variável                                                   | Quem lê   | `dev` (valor padrão)                                          | No Compose (`prod`)                                               |
| ---------------------------------------------------------- | --------- | ------------------------------------------------------------- | ----------------------------------------------------------------- |
| `SPRING_PROFILES_ACTIVE`                                   | os dois   | não definida, vale `dev`                                      | `prod`                                                            |
| `CONFIG_SERVER_URL`                                        | os dois   | não usada: o `dev` não fala com o Config Server               | `http://config-server:8888`                                       |
| `DB_URL`                                                   | os dois   | `localhost:5432/permissions_saas` · `localhost:5433/audit_db` | não usada: o endereço vem do Config Server                       |
| `DB_USERNAME` / `DB_PASSWORD`                              | os dois   | `saas`/`saas123` · `audit`/`audit123`                         | os mesmos, definidos no `docker-compose.yml`                     |
| `SERVER_PORT`                                              | os dois   | `8080` · `8081`                                               | não definida (vale o padrão)                                      |
| `AUDIT_SERVICE_URL`                                        | principal | `http://localhost:8081`                                       | não usada: o endereço vem do Config Server                       |
| `RABBITMQ_HOST`                                            | os dois   | `localhost`                                                   | não usada: o endereço vem do Config Server                       |
| `RABBITMQ_USERNAME` / `RABBITMQ_PASSWORD`                  | os dois   | `saas`/`saas123`                                              | os mesmos, definidos no `docker-compose.yml`                     |
| `SWAGGER_USERNAME` / `SWAGGER_PASSWORD`                    | principal | `admin`/`admin123`                                            | vêm do `.env`                                                     |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` / `JWT_SECRET` | principal | valores de mentira                                            | vêm do `.env` (\*)                                                |
| `POSTGRES_HOST_PORT`                                       | o Compose | —                                                             | `5432`: porta da **máquina** em que o banco principal é publicado |

(\*) OAuth2 e JWT não são usados pelo fluxo implementado: o `SecurityConfig` desabilita o
`oauth2Login`, e login/JWT é trabalho futuro. Mesmo assim, o client do Google precisa de um valor não
vazio para o contexto subir. Não é preciso criar credencial no Google Cloud Console.

O `.env` serve só ao Compose, que o lê sozinho e repassa aos containers apenas os segredos. O Spring
Boot não lê `.env`. Não o exporte num terminal: uma variável `SPRING_DATASOURCE_*` que tenha sobrado
num `.env` antigo ganha de qualquer profile.

## Configuração centralizada (Config Server)

No `prod`, cada serviço pede a sua configuração ao `config-server` na subida, pelo próprio nome e
profile. Os arquivos ficam em [`config-repo/`](../config-repo/) (ADR-012):

| Arquivo                                   | Vale para                        | O que tem                              |
| ----------------------------------------- | -------------------------------- | -------------------------------------- |
| `config-repo/application-prod.yml`        | todos os serviços em `prod`      | log de SQL desligado, endereço do RabbitMQ |
| `config-repo/permission-service-prod.yml` | a aplicação principal em `prod`  | endereço do banco e do `audit-service` |
| `config-repo/audit-service-prod.yml`      | o `audit-service` em `prod`      | endereço do banco                      |

Senhas e segredos não ficam no `config-repo/`: o Config Server entrega a configuração em texto puro.
Para ver o que cada serviço recebe (ou pela pasta `config-server (8888)` do Postman):

```bash
curl http://localhost:8888/permission-service/prod
curl http://localhost:8888/audit-service/prod
```

Para mudar uma configuração, edite o arquivo em `config-repo/` e reinicie só o serviço afetado, por
exemplo `docker compose restart audit-service`. Não é preciso rebuild, porque o `config-repo/` entra
no container como volume.

## Mensageria (RabbitMQ)

A gravação da auditoria vai por mensagem: a aplicação principal publica cada validação de permissão
na fila `audit.events`, e o `audit-service` consome e grava (ADR-013; o formato da mensagem está em
[`API.md`](API.md) → "Mensageria").

- **Painel:** http://localhost:15672, usuário `saas`, senha `saas123`. Na aba *Queues* estão a
  `audit.events` e a `audit.events.dlq`, para onde vão as mensagens que não puderam ser gravadas.
- **Ver as mensagens sem tirá-las da fila:** na fila, *Get messages* com *Ack mode* = "Nack message
  requeue true". As contagens da fila (*Ready*, *Consumers*) são atualizadas a cada 5 segundos, então
  logo depois de uma mudança podem estar atrasadas; o *Get messages* mostra o que está lá na hora.
- **Logs do fluxo:** `docker compose logs -f permission-service audit-service | grep "Audit message"`
  mostra cada mensagem publicada (`published`) e gravada (`registered`).
- **Demonstração com o consumidor parado:** `docker compose stop audit-service`, valide permissões, veja
  as mensagens esperando na fila e religue com `docker compose start audit-service`. A pasta
  `audit-service fora do ar` do Postman faz o roteiro com asserções.

## Rodar na máquina (profile `dev`)

Só a infraestrutura no Docker (os bancos e o RabbitMQ); as aplicações na IDE ou no terminal, cada
uma no seu:

```bash
docker compose up -d postgres audit-postgres rabbitmq
cd permission-service && ./mvnw spring-boot:run   # 8080, banco em localhost:5432
cd audit-service && ./mvnw spring-boot:run        # 8081, banco em localhost:5433
```

Nenhuma variável é necessária, e o Config Server não é usado: o profile `dev` já aponta tudo para
`localhost`. Com o banco publicado em outra porta, troque o endereço pela variável `DB_URL`, o mesmo
mecanismo que o Compose usa:

```bash
POSTGRES_HOST_PORT=5434 docker compose up -d postgres
cd permission-service && DB_URL=jdbc:postgresql://localhost:5434/permissions_saas ./mvnw spring-boot:run
```

Ao depurar, um breakpoint parado no `audit-service` estoura o timeout de 2s do cliente Feign. Para
depurar com calma, suba a aplicação principal com
`--spring.cloud.openfeign.client.config.audit-service.read-timeout=600000`.

## Debug remoto do container

O agente de debug (JDWP) **não** está dentro das imagens: o `Dockerfile` traz só o necessário para
rodar a aplicação. Quem liga o debug é o `docker-compose.yml`, pela variável `JAVA_TOOL_OPTIONS`, que a
JVM lê na partida. A aplicação principal escuta na porta `5005` e o `audit-service` na `5006`. Na IDE,
anexe (attach) um **Remote JVM Debug** em `localhost:5005` ou `localhost:5006`. O processo sobe com
`suspend=n`, ou seja, não espera o debugger conectar para iniciar.

## Live reload com `docker compose watch`

`docker compose watch` observa o `src/` e o `pom.xml` de cada aplicação, e o `./.env` no caso da
principal, e rebuilda só o container afetado:

```bash
docker compose up -d --build   # sobe a stack uma vez
docker compose watch           # em outro terminal, fica observando e rebuildando
```

## Build e testes

Em cada projeto (`permission-service/`, `audit-service/`, `config-server/`):

```bash
./mvnw clean package -DskipTests   # build
./mvnw test                        # testes de unidade
./mvnw test -Dtest=ClassName       # uma classe específica
./mvnw verify                      # inclui os testes de integração (*IT)
```

Os testes da aplicação principal rodam no profile `test`, com H2 em memória: não precisam de banco nem
do Config Server. Os outros dois projetos ainda não têm testes automatizados.
