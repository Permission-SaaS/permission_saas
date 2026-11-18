# 📋 Planejamento — Desenvolvimento Full Stack com React e Spring Boot

**Aluno:** Jairo Williams Guedes Lopes Neto
**Disciplina:** Desenvolvimento Full Stack com React e Spring Boot [26E4_3]
**Prazo:** 14/12/2026 23:59 (PDF no Moodle; os envios só abrem nesse dia, às 07:00; 2 tentativas)
**Situação:** 🟡 em andamento — plano aprovado em 16/11/2026 e reordenado no mesmo dia (deploy para o fim)
**Disponibilidade:** ~2h/dia, variável
**Base:** Permission SaaS como ficou depois da disciplina de React (tag `react-entrega`): o
`permission-service`, o `audit-service`, o `config-server` e o `permission_saas_front` com o CRUD de
projetos e o login simulado.

> ⚠️ Este arquivo é o plano **desta** disciplina. Os planos das disciplinas anteriores são evidência
> já submetida e **não devem ser alterados**.

---

## Contexto

A disciplina pede uma aplicação full stack com Spring Boot e React: integração entre as camadas, CRUD,
autenticação JWT com logout seguro e, opcionalmente, deploy com Docker (ver `README.md` e
`ETAPA0..6.md` desta pasta). O enunciado fornece uma API pronta (a "API Carros"), mas a Etapa 6 permite
uma API própria. **Este projeto usa a própria API (`permission-service`) e o próprio front
(`permission_saas_front`)**, que já existem.

O que esta disciplina acrescenta ao sistema:

- **Autenticação de verdade:** o login simulado da disciplina de React vira login com JWT, com refresh
  token e logout revogado no servidor. A tela de cadastro, cortada em 28/10, volta.
- **Autorização por dono:** hoje o `GET /projects` lista os projetos de todos os clientes, e o
  `POST /projects` recebe o `clientId` no corpo. Com o JWT, o cliente vem do token e só vê os próprios
  projetos.
- **Exportação e importação** do projeto completo em JSON. A exportação já estava listada como
  trabalho futuro do sistema.
- **Testes, CI e refatoração:** testes de API e de integração no back-end, GitHub Actions em cada
  repositório e uma refatoração guiada por auditoria de código.
- **Deploy (Etapa 6, opcional):** fica para o fim, e só entra se sobrar folga. A próxima disciplina é
  só de deploy, então ele provavelmente vai para ela. O que adianta o deploy e também conta nesta
  rubrica (Docker do front, CI, HTTPS local) entra antes (ver [Decisões](#decisões)).

### Onde o sistema está hoje

- **API:** o `spring-boot-starter-security` e o `jjwt` já estão no `pom.xml`, mas a `SecurityConfig`
  libera tudo (`anyRequest().permitAll()`). Hoje o login só protege o Swagger, com Basic Auth. O
  `PasswordEncoder` BCrypt já existe.
- **`Client`:** já tem `passwordHash`, `loginAttempts`, `blocked`, `blockExpiresAt` e `lastLoginAt`, ou
  seja, está pronto para o login e para o bloqueio por tentativas. O `POST /clients/register` já existe.
- **Import:** o de rotas por CSV com Spring Batch já existe. Não existe nenhum export.
- **Testes na API:** são 7 arquivos, e os do CRUD de projetos estão entre eles. O H2 está no pom.
  Nenhum repositório tem CI.
- **Front:** o `httpClient` próprio, o `useForm` próprio, o login simulado (sessão no `localStorage`), o
  `PrivateRoute` e o `VITE_DEV_CLIENT_ID` para criar projetos. Os comentários adicionados para a rubrica
  de React **ficam**, porque este enunciado pede "código comentado adequadamente".
- **Docker:** o Compose sobe api, audit, config, RabbitMQ e os dois PostgreSQL, publicando todas as
  portas no host, inclusive as de debug (5005 e 5006). O front ainda não tem Dockerfile.

### O enunciado e a rubrica não pedem as mesmas coisas

| A rubrica cobra | O enunciado (etapas) | Como fica |
|---|---|---|
| Exportação de dados protegida por JWT (itens 9–12) | nenhuma etapa fala em exportação | export e import do projeto completo em JSON (bloco 5) |
| Mockup "detalhado" (item 4) | a Etapa 0 pede um mockup | 30 telas (celular em 360 px e desktop), com estados e navegação clicável, feitas pela IA com a liberação do professor (bloco 0) |
| "Integração contínua" (item 1) | — | GitHub Actions em cada repositório (bloco 1) |
| "Serviço RESTful fornecido" (item 2) | a Etapa 6 permite uma API própria | a própria API; o relatório explica a escolha |
| Testes "abrangentes" do update e do delete (item 7) e da segurança (itens 11 e 16) | a Etapa 3 pede testar e validar | unidade, MockMvc e Testcontainers (blocos 2, 3 e 5) |
| "Protocolos de segurança e criptografia" (item 10) | a Etapa 4 pede comunicação segura | HTTPS com Caddy no Compose local, BCrypt nas senhas, JWT assinado (bloco 3) |
| — | Etapa 6 opcional (Docker + deploy) | só se sobrar folga; senão, vai para a próxima disciplina |

---

## Decisões

Tomadas pelo Jairo em 16/11/2026, num jogo de perguntas com a IA.

1. **API e front próprios**, e não a API Carros.
2. **Sessão:** access token curto (~15 min) na memória do front + refresh token em cookie
   `HttpOnly; Secure; SameSite=Strict`, salvo com hash no banco, com rotação a cada uso e detecção de
   reuso. O logout revoga o refresh no servidor e apaga o cookie.
3. **Login e cadastro:** o `Client` entra com e-mail e senha, e a tela de cadastro volta. Cada cliente
   só vê e altera os próprios projetos, e o `VITE_DEV_CLIENT_ID` sai.
4. **Exportação e importação do projeto completo em JSON** (cargos, rotas e concessões), conferindo o
   dono pelo token. No front, o detalhe do projeto passa a mostrar os cargos e as rotas **só para
   leitura**, para mostrar o resultado do import.
5. **Testes do back-end:** unidade nos casos de uso, MockMvc com Spring Security e integração com
   Testcontainers (PostgreSQL).
6. **Bibliotecas do front:** Axios no lugar do `httpClient`, React Hook Form + Zod no lugar do `useForm`
   e shadcn/ui. Sem Vitest.
7. **Mockup** com as telas novas e as atuais, no visual do branding. Decidido em 16/11 no Figma, desenhado pelo Jairo; **em 17/11 o professor liberou o uso de IA para o mockup**, e o Jairo pediu que a IA o fizesse. Ficou num canvas de design do Claude (sem instalar nada, com navegação clicável e comentários); o Jairo revisa e pede os ajustes. O ambiente do Figma (`docs/branding/figma/`) continua pronto, se um dia o mockup for para lá.
8. **Ordem: seguir as etapas do enunciado** (revisto em 16/11; a primeira escolha era o deploy cedo). O
   deploy é opcional e fica para o fim, só se sobrar folga, porque a próxima disciplina é só de deploy.
9. **Adiantar o deploy sem fazer o deploy:** entra antes o que prepara o deploy e também conta nesta
   rubrica:
   - o **Dockerfile do front** no Compose local (o enunciado pede os arquivos de Docker que forem
     usados);
   - o **CI com GitHub Actions**, com testes e build a cada push (item 1);
   - o **HTTPS local com o Caddy** na frente da API, com cabeçalhos de segurança (item 10);
   - as **portas só de desenvolvimento** (debug, bancos, RabbitMQ, audit) separadas das que um servidor
     publicaria.
10. **Deploy, quando acontecer:** a intenção registrada em 16/11 é a stack inteira num EC2 da AWS, com
    domínio próprio e Caddy, e o front no Netlify, com deploy automático pelo Actions. Ela é
    **confirmada quando o deploy começar**, porque o enunciado da próxima disciplina pode pedir outra
    plataforma.
11. **Refatoração com auditoria primeiro:** a IA revisa a API e o front e entrega os achados com motivo e
    esforço, e o Jairo escolhe o que entra.
12. **Modo de trabalho:** o mesmo da disciplina de React (ver [Como vamos trabalhar](#como-vamos-trabalhar)).

**O cookie do refresh token sem deploy:** em desenvolvimento, o proxy do Vite deixa o front e a API na
mesma origem, então o cookie `SameSite=Strict` viaja sem CORS. O `Secure` não atrapalha, porque o
navegador trata `localhost` como contexto seguro. No deploy, um domínio próprio (front em `app.<domínio>`
e API em `api.<domínio>`) mantém os dois *same-site*, e o cookie continua funcionando.

### Decisões técnicas (recomendadas; cada uma é confirmada no bloco em que aparece)

| Tema | Recomendação | Motivo |
|---|---|---|
| Validação do JWT | `spring-boot-starter-oauth2-resource-server` (`NimbusJwtDecoder`, HS256), com o segredo vindo de variável sem default (ADR-012); o jjwt sai do pom | É o caminho padrão do Spring Security, e o filtro escrito à mão repetiria o que ele já faz |
| Esquemas de autenticação | O JWT protege o painel (`/projects/**`, `/auth/**`, `/clients/me`); o `POST /validate-permission` continua com `ApiKey` | O painel é usado por pessoas; o `validate-permission` é chamado de sistema para sistema. Vira o ADR-017 |
| Projeto de outro cliente | Responde **404**, não 403 | Não revela que o id existe |
| Endpoints novos | `POST /auth/login`, `POST /auth/refresh`, `POST /auth/logout`, `GET /auth/me`, `GET /projects/{id}/export`, `POST /projects/import` | **Breaking change:** o `clientId` sai do corpo do `POST /projects` e passa a vir do token |
| Segurança extra (itens 10 e 14) | Bloqueio por tentativas (com os campos que o `Client` já tem); CORS por lista de origens; HTTPS e cabeçalhos de segurança (HSTS e afins) no Caddy; limite de tamanho no import | Cada item é uma camada a mais, testável e fácil de mostrar no relatório |
| HTTPS local | Caddy no Compose, com o certificado da autoridade local dele (`tls internal`) | Mostra a comunicação criptografada sem domínio nem servidor, e o mesmo Caddy vira o do deploy, trocando só o certificado |
| Front em Docker | Dockerfile multi-stage (build com Node, servido pelo nginx) no Compose local | Adianta o deploy e entra nos arquivos de Docker que o enunciado pede |
| Branding | O shadcn/ui do bloco 2 parte do `tokens.css` de [`docs/branding/`](../branding/README.md) (cores dos dois temas, Nunito, escala de texto, raio único de 2 px); o tema claro é o padrão, e o escuro entra se sobrar tempo | O branding é global, para este e os próximos projetos, e já tem o contraste AA conferido por script |
| Logout entre abas | `BroadcastChannel`, se sobrar tempo | Estava nos trabalhos futuros do relatório de React |
| ADRs | ADR-017 (autenticação JWT e os dois esquemas); o do deploy só quando o deploy for feito, no `docs/ARCHITECTURE.md` do umbrella | O log de ADRs é único para o sistema |
| Tag de entrega | `fullstack-entrega`, anotada, no umbrella | Segue o padrão do `react-entrega` e não colide com `etapa-*` e `arq-etapa-*` |


### Ajustes que o mockup pede no código

Decididos na revisão do mockup. Entram quando a tela correspondente for refeita (bloco 2 para o CRUD,
bloco 4 para login e cadastro).

| Ajuste | Decidido em | Onde |
|---|---|---|
| **Excluir em dois passos**, no celular e no desktop: (1) o aviso do que é excluído e de que não dá para desfazer; (2) digitar o nome do projeto. O botão de excluir só fica ativo quando o nome bate exatamente, com maiúsculas e minúsculas | 17/11 | `ProjectDetail` (hoje é um passo só, o modal com o nome) |
| **O erro do nome só aparece quando o texto digitado deixa de bater com o começo do nome.** "Loja vir" não acusa nada, e "Loja V" acusa. Hoje o erro aparece a cada letra que ainda não completa o nome | 17/11 | `ProjectDetail`: hoje `hasError = confirmProjectName !== "" && !isProjectNameConfirmed`; passa a ser `confirmProjectName !== "" && !project.name.startsWith(confirmProjectName)`. O botão continua dependendo do nome exato (`isProjectNameConfirmed`) |
| **O cabeçalho atual quebra em 360 px:** o nome do usuário e o "Sair" saem da tela, e a busca não ocupa a largura (print `entrega/prints/04-front-projetos-celular.png`). Resolve com a barra inferior e o cabeçalho fino do mockup | 17/11 | `AppLayout` e a lista de projetos |
| **Textos na voz da marca:** "Ops!!" sai, "Deletando..." vira "Excluindo...", "Novo Projeto" vira "Novo projeto"... A tabela completa está no branding, em "Voz e tom" | 17/11 | as telas que forem refeitas |

---

## Como vamos trabalhar

1. **Diagnóstico curto** antes do bloco 1 (Docker, CI) e antes do bloco 3 (Spring Security, JWT, cookies,
   CORS e HTTPS): umas 8 perguntas cada, respondidas com as próprias palavras, e "não sei" vale como
   resposta. O resultado define a profundidade de cada bloco.
2. **Cada passo segue o mesmo ciclo:**
   1. explicação do conceito, primeiro em termos simples e com um exemplo pequeno, fora do projeto;
   2. o Jairo implementa;
   3. revisão, apontando o problema concreto e o porquê;
   4. duas ou três perguntas de fixação.
3. **Quem faz o quê:**
   - **Jairo:** a revisão do mockup (feito pela IA, com a liberação do professor); o que adianta o deploy (o Dockerfile do front, o CI, o Caddy e a separação das
     portas), porque o deploy é o assunto da próxima disciplina; o fluxo de autenticação no back (login,
     refresh com rotação, logout, regra de dono); no front, o que é novo (o interceptor de refresh do
     Axios, o primeiro formulário com React Hook Form + Zod, o primeiro componente do shadcn/ui, o
     download e o upload de arquivo); os testes de segurança.
   - **IA:** o plano e a documentação, a auditoria de código e o que o Jairo já sabe fazer: a troca do
     `httpClient` pelo Axios, a migração dos formulários seguintes, migrations, propriedades, CORS, DTOs e
     mappers, a base do Testcontainers e os testes do CRUD que seguem o padrão já existente. Cada trecho
     vem explicado.
   - **Credenciais:** as do GitHub (e as da AWS e do domínio, se o deploy acontecer) ficam só com o
     Jairo. A IA nunca as vê nem as usa.
4. **Cada uso de IA é registrado** na seção [Uso de IA](#uso-de-ia), que alimenta a citação de fontes do
   PDF.

---

## Cronograma

Os blocos seguem as etapas do enunciado. As Etapas 1 a 3 (integração e CRUD) já existem desde a
disciplina de React, então o bloco 2 as melhora em vez de construí-las.

| Bloco | Etapa | Datas | O que se faz | Rubrica |
|---|---|---|---|---|
| 0. Ambiente e mockup | 0 | 17–20/11 | branding; mockup com todas as telas e estados (feito pela IA, revisado pelo Jairo); conferir o ambiente local | 1, 4 |
| 1. Docker do front e CI | 0 | 21–24/11 | diagnóstico; Dockerfile do front no Compose; portas só de desenvolvimento separadas; GitHub Actions (testes e build de api, audit, config e front). **Em paralelo:** a IA faz a auditoria de código, e no fim do bloco o Jairo escolhe os achados | 1, 3, 13 |
| 2. Integração e CRUD | 1–3 | 25–29/11 | Axios no lugar do `httpClient`; formulários com React Hook Form + Zod; cargos e rotas para leitura no detalhe; revisão das validações; base do Testcontainers e testes do CRUD (criar, consultar, atualizar e excluir) | 2, 3, 5–8 |
| 3. Segurança | 4 | 30/11–04/12 | diagnóstico; migration do refresh token; login, refresh, logout e `/auth/me`; regra de dono nos projetos; bloqueio por tentativas; CORS; HTTPS local com o Caddy; testes de segurança; ADR-017 | 14, 16 |
| 4. JWT no front e logout seguro | 5 | 05–07/12 | interceptor de refresh do Axios; login e cadastro de verdade com shadcn/ui; logout chamando a API; o token fora do `localStorage`; sai o `VITE_DEV_CLIENT_ID`; o CRUD funcionando com o JWT | 6, 8, 15 |
| 5. Exportar, importar e refatorar | 5 | 08–11/12 | export e import do projeto em JSON, com dono, validação e limite de tamanho; testes de segurança da exportação; botões no front; os achados da auditoria escolhidos no bloco 1 | 9–13 |
| 6. Fechamento | 7 | 12–13/12 | prints; `ENTREGA.md` (visão geral, como rodar localmente, Docker, testes, link do código de cada funcionalidade); o PDF `jaironeto_desenvolvimentofullstackcomreactespringboot_pd.pdf`; a seção "Uso de IA" do README; a tag `fullstack-entrega` | todas |
| Envio | — | 14/12, depois das 07:00 | o Jairo posta o PDF no Moodle | — |
| Deploy | 6 (opcional) | só com folga | a stack no ar (decisão 10). Sem folga, vai para a próxima disciplina, e o relatório explica que o deploy foi adiantado (Docker, CI, Caddy) mas não feito | — |

### Ordem de corte, se atrasar

O JWT, o logout seguro, o export protegido e os testes de segurança **não são cortados**.

1. **O deploy** (já está fora do caminho principal).
2. **A reforma visual das telas atuais.** O shadcn/ui entra só nas telas novas (login, cadastro,
   exportar e importar).
3. **O logout entre abas.**
4. **Os achados de menor impacto da auditoria.** Ficam só os de segurança e os de maior impacto.

---

## Situação

- [x] Enunciado separado em `README.md` e `ETAPA0..6.md` (16/11)
- [x] Escopo e decisões definidos num jogo de perguntas (16/11)
- [x] Plano aprovado e reordenado para seguir as etapas, com o deploy no fim (16/11)
- [x] Branding em `docs/branding/` (17/11)
- [x] Professor liberou a IA para o mockup (17/11)
- [x] **Bloco 0** (17/11):
  - [x] mockup no [canvas](https://claude.ai/artifact/5CUHCznKRK51vLerPZfoVq): 26 telas no celular e 9 no desktop, com a exclusão em dois passos; revisado e aprovado pelo Jairo
  - [x] as 35 telas em PNG em `entrega/mockup/` (celular em 2x, desktop em 1x)
  - [x] ambiente conferido, com 4 prints em `entrega/prints/`: a API respondendo (`/actuator/health`), a lista de projetos no front, a mesma chamada pelo proxy do Vite (`/api/projects`) e o front atual em 360 px. Os prints usaram um PostgreSQL temporário com dados de demonstração, apagado depois; o banco local do Jairo não foi tocado
  - [ ] compartilhar o canvas com o professor (só leitura) e guardar o link para o PDF
- [ ] **Bloco 1:** diagnóstico; Dockerfile do front; portas de desenvolvimento separadas; CI; auditoria
      de código (IA) e escolha dos achados
- [ ] **Bloco 2:** Axios; React Hook Form + Zod; cargos e rotas no detalhe; validações; testes do CRUD
- [ ] **Bloco 3:** diagnóstico; JWT no back-end; regra de dono; HTTPS local; testes de segurança; ADR-017
- [ ] **Bloco 4:** JWT no front; login e cadastro; logout seguro
- [ ] **Bloco 5:** exportar e importar; refatoração
- [ ] **Bloco 6:** `ENTREGA.md`, prints, PDF, tag `fullstack-entrega`
- [ ] PDF postado no Moodle (14/12, a partir das 07:00)
- [ ] Deploy (opcional, só com folga)

---

## Uso de IA

Política 🟡: a IA pode ser usada para esclarecer conceitos, sugerir arquitetura e organização do código,
gerar ou complementar trechos pontuais de código, identificar e corrigir erros, refatorar, criar e
revisar componentes React, preparar dados de teste, integrar o front e o back, diagnosticar problemas no
consumo de APIs REST, escrever testes e documentação e configurar o ambiente, o Docker e o deploy. Todo
uso é citado no PDF.

Ferramenta: **Claude Code**, da Anthropic.

| Data | Parte | Como a IA foi usada |
|---|---|---|
| 16/11/2026 | Enunciado e plano | Formatou o enunciado em Markdown e o separou por etapa; confrontou o enunciado com a rubrica e apontou a exportação de dados, que só a rubrica cobra; leu o código para levantar o que já existe. Conduziu um jogo de perguntas com as opções de cada decisão (sessão JWT, login, exportação, deploy, CI/CD, testes, bibliotecas, mockup, HTTPS, refatoração, ordem e cortes) e montou este plano a partir das minhas respostas. Depois, a meu pedido, reordenou o plano para seguir as etapas, com o deploy no fim, e separou o que adianta o deploy. As escolhas foram minhas |
| 17/11/2026 | Bloco 0 | Explicou o que é um mockup (wireframe, mockup e protótipo) e as boas práticas de design de interface que a rubrica cobra, com a analogia da planta de uma casa; conduziu um jogo de perguntas sobre as telas (fidelidade, navegação, card, detalhe, importar e exportar, sessão expirada, cadastro, lista vazia, conta) e criou um checklist do bloco com as decisões. A escolha do mobile first e as demais decisões foram minhas |
| 17/11/2026 | Bloco 0 (branding) | A partir das cinco cores e das regras que escolhi (sem serifa e arredondada, espaçamentos em múltiplos de 4 e, depois de eu revisar, um raio único de 2 px, mantendo a escala do Tailwind), gerou o branding em `docs/branding/`: as escalas de cor, as cores semânticas dos dois temas, a escala tipográfica, o espaçamento, as bordas, a elevação, o movimento, os ícones, as cores dos métodos HTTP e a voz e tom; escreveu o `contrast.py`, que calcula o contraste WCAG de cada par e confere os tokens. Apontou que o dourado não pode ser texto no tema claro (1,83:1) e que o aviso não podia ser amarelo. Preparou o ambiente do Figma: os arquivos para o plugin Tokens Studio (gerados do `tokens.json` por um script) e o passo a passo para o plano gratuito, pelo navegador. O tema claro como padrão, a Nunito, o laranja no aviso e a largura de 360 px foram escolhas minhas; as telas do mockup são desenhadas por mim |
| 17/11/2026 | Bloco 0 (mockup) | Com a liberação do professor para usar IA no mockup, e a meu pedido, desenhou o mockup num canvas de design do Claude: 30 telas, 24 no celular (360 px) e 6 no desktop (1440 px), com os estados de carregando, vazio, erro e sucesso, e links entre as telas para navegar. Partiu das decisões de tela que tomei no jogo de perguntas e do branding. Propôs como a matriz de concessões fica no celular (um cargo por vez). A revisão das telas é minha |
| 17/11/2026 | Bloco 0 (fechamento) | A meu pedido, gerou as 35 telas do mockup em PNG num Chrome sem janela e tirou os 4 prints do ambiente com um script que sobe o front, faz o login de demonstração e captura as telas. Para os prints, rodou a API contra um PostgreSQL temporário com dados de demonstração e apagou tudo depois. Apontou que o cabeçalho do front atual quebra em 360 px; o ajuste ficou para o bloco 2 |

---

## Verificação

**A cada bloco:**

```bash
# infraestrutura e API (na raiz do guarda-chuva; o PostgreSQL do host ocupa a 5432)
POSTGRES_HOST_PORT=5434 docker compose up -d postgres audit-postgres rabbitmq
# permission-service no profile dev (pela IDE ou ./mvnw spring-boot:run no permission_saas_api)
./mvnw verify    # no permission_saas_api; a partir do bloco 2, com Testcontainers (Docker rodando)

# front (no permission_saas_front)
npm run dev      # fluxo no navegador
npm run check    # build (tsc), lint e formatação
```

- **Bloco 1:** `docker compose up -d --build` sobe o front junto com o resto, e ele lista os projetos da
  API; um push em cada repositório roda o workflow, e um teste quebrado deixa o CI vermelho.
- **Bloco 2:** o CRUD completo no navegador continua igual depois da troca para Axios e React Hook Form;
  os testes do CRUD passam no CI.
- **Blocos 3 a 5:** sem token, a API responde 401; o projeto de outro cliente responde 404; um token
  adulterado ou expirado responde 401; um refresh reusado revoga a família inteira; depois do logout, o
  refresh é recusado; uma requisição CORS de outra origem é bloqueada; `curl -I https://localhost/...`
  pelo Caddy mostra o HSTS; o fluxo completo no navegador (cadastro → login → CRUD → exportar → importar
  → logout).
- **Bloco 6:** os 16 itens da rubrica conferidos um a um contra o código, os links e os prints.
