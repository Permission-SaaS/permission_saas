# 📋 Planejamento — Desenvolvimento de aplicações interativas com React

**Aluno:** Jairo Williams Guedes Lopes Neto
**Disciplina:** Desenvolvimento de aplicações interativas com React
**Prazo:** 09/11/2026 23:59 (relatório técnico em PDF no Moodle)
**Disponibilidade:** ~2h/dia
**Base:** Permission SaaS como ficou depois da disciplina de microsserviços (tag `arq-etapa-4`) e da
separação em repositórios (ADR-015). O front-end vai no `permission_saas_front`, que até aqui só tinha
README.

> ⚠️ Este arquivo é o plano **desta** disciplina. Os planos das disciplinas anteriores são evidência
> já submetida e **não devem ser alterados**.

---

## Contexto

O Permission SaaS chega nesta disciplina com o back-end pronto: o `permission-service`, um monolito
modular, mais o `audit-service` e o `config-server`. Ainda não tem nenhuma tela. A disciplina pede um
CRUD em React que consuma uma API, com navegação, gerenciamento de estado e tratamento de erros (ver
`README.md` e `ETAPA1..3.md` desta pasta).

O front-end vira o **painel do cliente do SaaS**: a pessoa se cadastra, entra e gerencia os próprios
projetos. Papéis e rotas ficam de fora nesta disciplina. Com isso, entram no escopo dois itens que o
`CLAUDE.md` listava como trabalho futuro: o **código do front-end** e a **autenticação JWT**.

### O enunciado e a rubrica não pedem as mesmas coisas

| A rubrica cobra | O enunciado (features) | Como fica |
|---|---|---|
| Create React App (item 2) | — | Vite no lugar do CRA, porque o CRA foi descontinuado em 14/02/2025 (ADR-016) |
| Redux: actions, reducers, store, `useSelector`, `useDispatch` (itens 9, 10, 12) | só fala em Context API | os dois: Redux para a sessão e Context para as notificações |
| Componentes funcionais **e de classe** (item 6) | — | um `ErrorBoundary`, que no React 19 ainda só existe como classe |
| Teste em navegadores diferentes (item 1) | — | Chrome, Firefox e Edge no fechamento, com prints no relatório |
| "Uma API externa" (itens 13–16) | uma "API real" de terceiros (OpenWeather, GitHub) | **a própria API do `permission-service`**: o professor liberou em 07/10/2026, e o relatório cita a liberação |

---

## Decisões

1. **Stack:** React (19.3 em 07/10/2026), TypeScript, Vite e Tailwind CSS (ADR-016). As outras
   dependências entram quando um bloco precisar delas, não antes.
2. **Funcional antes de bonito.** O Tailwind serve para deixar a tela organizada, sem investir em
   design agora.
3. **Escopo:** cadastro e login básicos, só para entrar no sistema, e o CRUD de projetos com nome,
   descrição e `maxRoles`. Papéis e rotas ficam como extensão, se sobrar tempo.
4. **CRUD antes do JWT.** O JWT não vale ponto na rubrica do React, e o CRUD concentra a maior parte
   dela. A data de corte do JWT é **28/10**: se não estiver pronto, o login vira uma simulação no front,
   e o Redux e a rota privada continuam iguais.
5. **Modo de trabalho:** o Jairo quer **reaprender React até conseguir desenvolver sozinho**.
   - Ele escreve o código, inclusive o JWT no back-end, por inteiro, com orientação.
   - A IA ensina, revisa e escreve a documentação.
   - Trechos pontuais de código vêm da IA só quando ele travar, como a política 🟡 permite.

### Decisões técnicas (recomendadas; cada uma é confirmada no bloco em que aparece)

| Tema | Recomendação | Motivo |
|---|---|---|
| Chamada à API | **proxy do Vite**: o front chama `/api/...`, e o Vite repassa para `localhost:8080` sem o prefixo | Dispensa CORS no back-end. Sem o prefixo `/api`, a rota de tela `/projects` colidiria com o endpoint `/projects` ao recarregar a página |
| HTTP | **`fetch`** com um wrapper próprio (`httpClient`) | O timeout com `Promise.race` e o `AbortController` aparecem naturalmente; o Axios esconderia os dois |
| Estado | React Query para os dados da API, Redux Toolkit para a sessão, Context para as notificações | Cada um resolve um problema diferente, o que é o texto do item 12 da rubrica |
| Componente de classe | `ErrorBoundary` | No React 19, ainda só existe como classe |
| Error boundary | **Escrito à mão** (decidido em 16/10), no `shared/components`, em vez da lib `react-error-boundary` | Com a lib, a classe ficaria no `node_modules`, e o item 6 da rubrica pede componente de classe no meu código; escrever também ensina o que a lib faz por dentro. Em produção, a lib seria a escolha (`resetKeys`, `onReset`, `showBoundary` para erros assíncronos); a troca fica possível depois da entrega e entra nas considerações finais do relatório |
| Estilos | Tailwind v4, com o plugin `@tailwindcss/vite` | O item 11 cita Styled Components, MUI e CSS Modules como exemplos; o Tailwind é equivalente |
| Linter | **ESLint** (decidido em 08/10), no lugar do Oxlint, que é o padrão do template | É o que a maioria dos projetos usa. Vem com o plugin de hooks do time do React, que já liga `rules-of-hooks` e `exhaustive-deps` |
| Formatador | **Prettier** (decidido em 10/10), com as regras padrão escritas no `.prettierrc` e o plugin oficial do Tailwind, que ordena as classes | O formato fica definido no projeto, e não no editor de cada um. O `npm run format:check` confere |
| Roteamento | **React Router 8 no modo declarativo** (decidido em 14/10): `<BrowserRouter>`, `<Routes>` e `<Route>` | O modo data traria *loaders* e *actions*, que repetem o papel do React Query, e captura sozinho os erros de render das rotas, que nunca chegariam ao `ErrorBoundary`. Se um dia precisar, o React Router tem um guia oficial de migração para o modo data |
| Idioma | **Interface em português, código em inglês** (decidido em 14/10) | Os prints vão para o relatório, e o relatório e a documentação estão em português. Nomes, arquivos, URLs e commits seguem em inglês, como no back-end |
| `clientId` antes do JWT | `VITE_DEV_CLIENT_ID` no `.env.local`, removida no bloco 5 | O `POST /projects` exige `clientId`, e ainda não haverá sessão |

---

## Como vamos trabalhar

1. **Questionário diagnóstico, antes de qualquer código.** São umas 15 perguntas curtas, respondidas
   com as próprias palavras, sem pesquisar, e "não sei" vale como resposta. Os temas são JS moderno,
   React, TypeScript e o problema que cada biblioteca resolve. O resultado define a profundidade de
   cada bloco.
2. **Cada passo segue o mesmo ciclo:**
   1. explicação do conceito com um exemplo pequeno, fora do projeto;
   2. o Jairo implementa;
   3. revisão ("veja se está correto"), apontando o problema concreto e o porquê;
   4. duas ou três perguntas de fixação.
3. **Cada uso de IA é registrado** na seção [Uso de IA](#uso-de-ia), que alimenta o item 9 do
   relatório (Créditos).

---

## Estrutura de pastas

Modular, com um módulo por módulo do sistema, espelhando o back-end:

```
permission_saas_front/
├── index.html · package.json · vite.config.ts · tsconfig*.json
├── .env.example              # variáveis VITE_* documentadas, sem segredo
└── src/
    ├── main.tsx              # ponto de entrada: monta o App dentro dos providers
    ├── index.css             # @import "tailwindcss"
    ├── app/                  # liga as peças; o único lugar que conhece todos os módulos
    │   ├── App.tsx · router.tsx · providers.tsx · store.ts (bloco 5)
    │   └── layout/           # a casca da tela: cabeçalho, menu e o <Outlet/>
    ├── modules/              # um por módulo do sistema
    │   ├── identity/         # cadastro, login e sessão   ↔ módulo identity do permission-service
    │   │   ├── api/          # chamadas HTTP do módulo
    │   │   ├── components/   # RegisterForm, LoginForm
    │   │   ├── pages/        # RegisterPage, LoginPage
    │   │   ├── store/        # authSlice do Redux (bloco 5)
    │   │   ├── types.ts      # tipos dos DTOs da API
    │   │   └── index.ts      # o que o módulo expõe aos outros
    │   └── project/          # CRUD de projetos           ↔ módulo project
    │       └── api/ · components/ · hooks/ · pages/ · types.ts · index.ts
    └── shared/               # genérico, sem regra de negócio
        ├── api/              # httpClient: fetch, prefixo /api, timeout, erros
        ├── components/       # Button, Input, Table, ErrorBoundary
        ├── context/          # NotificationContext
        └── hooks/            # useForm, useDebounce
```

**Regras:**

- **As importações vão num sentido só:** `app` → `modules` → `shared`.
  - O `shared` nunca importa de `modules`.
  - Um módulo só importa outro pelo `index.ts` dele, a mesma ideia das fronteiras do Spring Modulith no
    back-end.
- **Pasta só existe quando tem arquivo**, até porque o git não guarda pasta vazia. A árvore fica
  documentada no `docs/ARCHITECTURE.md` do front, junto com as convenções de código.
- **Um componente nasce dentro do módulo** e só vai para o `shared` quando um segundo módulo precisar
  dele.
- **O token chega ao `httpClient` pelo `app`** (bloco 5), para o `shared` não depender do `identity`.

---

## Cronograma

| Bloco | Datas | O que se faz | Itens da rubrica |
|---|---|---|---|
| 0. Diagnóstico e estrutura | 08–09/10 | questionário; `npm create vite@latest` (template `react-ts`) no `permission_saas_front`; tour pelos arquivos gerados; Tailwind; `.gitignore` (`node_modules`, `dist`); README com como rodar e a estrutura | 2, 4, 11 |
| 1. Base | 10–13/10 | `httpClient` (prefixo `/api`, conversão do `ErrorResponse` da API, timeout com `Promise.race`, `signal`); proxy do Vite; layout; React Router com as rotas ainda vazias; `NotificationContext`; `ErrorBoundary` | 3, 6, 14 |
| 2. Cadastro | 14–16/10 | `RegisterPage`; formulário controlado com o hook `useForm`; validação; `POST /clients/register`; tratamento do 409 (e-mail em uso) e do 400; mensagem de sucesso ou erro na tela | 5, 7, 13, 14 |
| 3. CRUD de projetos | 17–23/10 | React Query (consultas e mutações, cache invalidado depois de cada mudança); telas de lista, detalhe e formulário (criar e editar usam o mesmo formulário); componentes reutilizáveis com props; busca por nome com debounce e `AbortController`; confirmação de exclusão com template literal; o front valida o que der antes de chamar a API (formulário, e `id` da URL fora do formato UUID vira "projeto não encontrado") | 5, 7, 8, 13, 15, 16 |
| 4. JWT no back-end | 24–28/10 | `POST /auth/login` no `identity`: confere a senha em bcrypt e gera o token (o `jjwt` já está no `pom.xml`, sem uso); filtro do token Bearer; `/projects/**` passa a exigir login, enquanto `/validate-permission`, `/clients/register` e o Swagger (Basic) continuam como estão; cada cliente só vê os próprios projetos; UUID inválido no caminho passa a dar 400 (hoje cai no tratamento genérico do `GlobalExceptionHandler` e vira 500); Postman com o passo de login; `API.md` e ADR-017 | nenhum (sustenta a rota privada) |
| 5. Login, Redux e rota privada | 29–31/10 | `store` e `authSlice` (actions e reducers); `useSelector` e `useDispatch`; `LoginForm` **não controlado**; `PrivateRoute`; logout; token no `httpClient`; remoção do `VITE_DEV_CLIENT_ID` | 9, 10, 12 |
| 6. Fechamento | 01–03/11 | teste no Chrome, no Firefox e no Edge; revisão dos comentários; screenshots; relatório com os 9 itens e o registro de uso de IA, citando a liberação do professor e o ADR-016 | 1, 3 |
| Folga | 04–08/11 | atrasos; entrega até 09/11 | — |

### Ordem de corte, se atrasar

1. **JWT no back-end** (data de corte: 28/10). O login vira uma simulação no front, e o Redux e a rota
   privada ficam iguais.
2. **Componente de terceiros**, pedido no enunciado, mas fora da rubrica.
3. **Timeout com `Promise.race`.**

### Itens do enunciado que a rubrica não pontua

Ficam no plano porque estão nas features: `useEffect` (debounce da busca), hook personalizado
(`useForm`), Context API (`NotificationContext`), formulário não controlado (login), rotas privadas,
`AbortController`, `Promise.race` e um componente de terceiros (a escolher no bloco 3).

---

## Situação (atualizado em 22/10/2026)

- [x] Enunciado separado em `README.md` e `ETAPA1..3.md`
- [x] Stack decidida e registrada (ADR-016)
- [x] Professor liberou a própria API como "API externa" (07/10)
- [x] Plano aprovado
- [x] Questionário diagnóstico (07/10). Resultado:
  - **Firme:** destructuring e spread, generics (pela analogia com Java), React Router, a ideia da `key`,
    e a de que o state muda pelo setter.
  - **Reforçar no bloco em que aparece:** o que dispara um render e o que é o `useEffect` (inclusive a
    função de limpeza), imutabilidade e referência, formulário controlado × não controlado, hooks
    personalizados e as regras dos hooks, props × state, JSX (compilação × execução) e tipo de função
    em TypeScript.
  - **Do zero:** Redux e React Query, com explicação completa antes de codar (blocos 3 e 5).
  - **Ajuste:** o bloco 1 começa com o modelo mental de render, usando o contador do próprio template
    do Vite.
- [x] **Bloco 0:**
  - [x] Projeto criado com o Vite (08/10): `create-vite` 9.2.1, template `react-ts`, ESLint; build e lint
    passando; README com como rodar
  - [x] Tailwind v4.3 com o plugin `@tailwindcss/vite` (10/10)
  - [x] Prettier com o plugin do Tailwind e `.vscode/extensions.json` (10/10)
  - [x] Limpeza do template: a página de demonstração deu lugar a uma página provisória (10/10)
  - [x] Estrutura de pastas: nasceu com o router (14/10). A árvore e as convenções de código ficam no
    `docs/ARCHITECTURE.md` do front (15/10), que cresce junto com o código
- [ ] **Bloco 1** ← em andamento. Ordem decidida em 12/10: primeiro o que aparece na tela; o `httpClient`,
  que não tem tela e só é usado no bloco 2, fica por último
  - [x] Modelo mental de render, com experimentos descartáveis no contador do `App.tsx` (12–14/10): o que
    dispara um render, o state como foto do render, a fila de updates (valor × função), `StrictMode`,
    imutabilidade e referência (`Object.is`)
  - [x] React Router e layout (14–15/10): modo declarativo, `AppLayout` com `Outlet`, rotas do CRUD com
    páginas provisórias e o 404
  - [x] `ErrorBoundary` (16–19/10): componente de classe no `shared`, em volta da área de páginas (recriado a
    cada rota pela `key`) e do app inteiro, com requisitos e experimentos de previsão. No caminho: alias `@/` e
    as convenções novas no `docs/ARCHITECTURE.md` do front
  - [x] `NotificationContext` (20–22/10): contexto, provider e hook no `shared`, com o valor estável
    (`useCallback` + `useMemo`) e um componente por aviso com o próprio timer; o provider entra pelo
    `app/providers.tsx`, dentro do `ErrorBoundary` de fora e fora do `BrowserRouter`. Requisitos e
    experimentos de previsão; as convenções do Context no `docs/ARCHITECTURE.md` do front
  - [ ] Proxy do Vite e `httpClient` ← próximo passo

---

## Uso de IA

Política 🟡: a IA pode ser usada para tirar dúvidas, sugerir organização, gerar trechos pontuais de
código, depurar, refatorar, revisar estilos, preparar dados de teste, apoiar formulários e chamadas à
API e sugerir abordagens de estado, Hooks, Context API, operações assíncronas e navegação. Todo uso é
citado no relatório.

Ferramenta: **Claude Code**, da Anthropic.

| Data | Parte | Como a IA foi usada |
|---|---|---|
| 07/10/2026 | Enunciado e plano | Formatou o enunciado em Markdown e o separou por etapa; confrontou o enunciado com a rubrica; ajudou a montar este plano e a estrutura de pastas. As decisões de escopo, stack e ordem foram minhas |
| 07/10/2026 | Diagnóstico | Questionário de conceitos (JS, React, TypeScript, bibliotecas) e correção comentada das minhas respostas |
| 08/10/2026 | Bloco 0 | Explicou o comando de criação do projeto e a diferença entre Oxlint e ESLint; a escolha do ESLint foi minha |
| 08/10/2026 | Bloco 0 | Explicou os arquivos gerados pelo template. A meu pedido, juntou as regras do `.gitignore`, escreveu o README com como rodar e fez os commits. O projeto foi criado por mim |
| 10/10/2026 | Bloco 0 | Explicou a abordagem *utility-first* do Tailwind e revisou a instalação, que fiz seguindo o guia oficial |
| 10/10/2026 | Bloco 0 | Propôs a configuração do Prettier, que instalei e configurei; revisou a limpeza do template e apontou o import do `App.css` apagado. A meu pedido, criou o `.vscode/extensions.json`, ajustou o `.gitignore` e o README e fez os commits |
| 12–14/10/2026 | Bloco 1 | Explicou o modelo de render (o que dispara um render, o state como foto, a fila de updates, `StrictMode`, imutabilidade) com um exemplo fora do projeto, propôs os experimentos e revisou minhas previsões e respostas. Sugeriu a ordem do bloco 1, que aceitei. Escrevi os experimentos e os descartei |
| 14–15/10/2026 | Bloco 1 | Explicou o React Router (os três modos, rotas aninhadas, layout com `Outlet`, `useParams`, `Navigate` e `NavLink`) com um exemplo fora do projeto e revisou as rotas e o layout que escrevi; ao responder uma pergunta de fixação, apontou que a API devolve 500 para um UUID inválido. O modo declarativo e o português na interface foram escolhas minhas. A meu pedido, criou o `docs/ARCHITECTURE.md` do front com a estrutura de pastas e as convenções de código e atualizou o README |
| 16–17/10/2026 | Bloco 1 | Explicou error boundaries e componentes de classe com um exemplo fora do projeto; como tech lead, avaliou a lib `react-error-boundary` contra escrever o componente, e a decisão de escrever foi minha; a meu pedido, passou os requisitos do `ErrorBoundary` sem código e revisou minhas respostas e previsões. Também a meu pedido, configurou o alias `@/` (`tsconfig.app.json` e `vite.config.ts`), trocou os imports que atravessam pastas e registrou a convenção, que aprovei |
| 19/10/2026 | Bloco 1 | Revisou o `ErrorBoundary` que escrevi, item por item do checklist, e explicou os erros que encontrei no caminho: o `this` perdido em método passado como callback, a mutação do state na classe e o erro de handler que o boundary não captura. Pesquisou na documentação do React qual padrão de handler em classe é o recomendado; a escolha foi minha. A meu pedido, criou o checklist do passo, organizou as pendências e registrou as convenções que aprovei (prefixo `on`, barrel do `shared`, `??`, modificadores explícitos, dado fixo fora do componente, tipos e pastas de componente). Também ajudou a acessar o servidor de dev pela rede da empresa, com o navegador integrado do VS Code |
| 20–22/10/2026 | Bloco 1 | Explicou a Context API com analogias e exemplos fora do projeto: as três peças, por que os `children` do provider não renderizam de novo, o custo do prop drilling, `useCallback` e `useMemo`, e o `crypto.randomUUID`. Revisou o contexto, o provider, o hook e o toast que escrevi, e apontou a causa do loop infinito (o `notify` chamado no corpo do componente) e a do timer que reiniciava (um timer só, no provider, em vez de um por aviso). A meu pedido, fez o visual do toast (cores e ícones por tipo, animação de entrada e o container que não bloqueia cliques), estreitou o tipo do `role`, corrigiu um import e um acento, removeu os botões de teste e registrou as convenções que aprovei (comandos sem `handle`, o padrão do Context, arquivo sem JSX em `.ts`). A lógica (o state, os comandos, o timer por aviso e a guarda do hook) foi minha. Também revisou minhas previsões dos experimentos |

---

## Verificação

**A cada bloco:**

```bash
# infraestrutura e API (na raiz do guarda-chuva; o PostgreSQL do host ocupa a 5432)
POSTGRES_HOST_PORT=5434 docker compose up -d postgres audit-postgres rabbitmq
# permission-service no profile dev (pela IDE ou ./mvnw spring-boot:run no permission_saas_api)

# front (no permission_saas_front)
npm run dev      # fluxo no navegador
npm run build    # roda o tsc -b: erro de tipo quebra o build
npm run lint     # ESLint
```

- **Bloco 4:** `./mvnw test` no `permission_saas_api` e a coleção do Postman pelo newman, já com o
  passo de login.
- **Bloco 6:** os 16 itens da rubrica conferidos um a um contra o código e os prints.
