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

O front-end vira o **painel do cliente do SaaS**: a pessoa entra e gerencia os próprios projetos.
Papéis e rotas ficam de fora nesta disciplina. Com isso, entra no escopo um item que o `CLAUDE.md`
listava como trabalho futuro: o **código do front-end**. A **autenticação JWT** também entrava, mas
saiu em 28/10, na data de corte, junto com a tela de cadastro (ver [Cronograma](#cronograma)).

### O enunciado e a rubrica não pedem as mesmas coisas

| A rubrica cobra                                                                 | O enunciado (features)                            | Como fica                                                                                                    |
| ------------------------------------------------------------------------------- | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| Create React App (item 2)                                                       | —                                                 | Vite no lugar do CRA, porque o CRA foi descontinuado em 14/02/2025 (ADR-016)                                 |
| Redux: actions, reducers, store, `useSelector`, `useDispatch` (itens 9, 10, 12) | só fala em Context API                            | os dois: Redux para a sessão e Context para as notificações                                                  |
| Componentes funcionais **e de classe** (item 6)                                 | —                                                 | um `ErrorBoundary`, que no React 19 ainda só existe como classe                                              |
| Teste em navegadores diferentes (item 1)                                        | —                                                 | Chrome, Firefox e Edge no fechamento, com prints no relatório                                                |
| "Uma API externa" (itens 13–16)                                                 | uma "API real" de terceiros (OpenWeather, GitHub) | **a própria API do `permission-service`**: o professor liberou em 07/10/2026, e o relatório cita a liberação |

---

## Decisões

1. **Stack:** React (19.3 em 07/10/2026), TypeScript, Vite e Tailwind CSS (ADR-016). As outras
   dependências entram quando um bloco precisar delas, não antes.
2. **Funcional antes de bonito.** O Tailwind serve para deixar a tela organizada, sem investir em
   design agora.
3. **Escopo:** login básico, só para entrar no sistema, e o CRUD de projetos com nome, descrição e
   `maxRoles`. Papéis e rotas ficam como extensão, se sobrar tempo. O cadastro saiu em 28/10.
4. **CRUD antes do JWT.** O JWT não vale ponto na rubrica do React, e o CRUD concentra a maior parte
   dela. A data de corte do JWT é **28/10**: se não estiver pronto, o login vira uma simulação no front,
   e o Redux e a rota privada continuam iguais. **Aplicada em 28/10:** o JWT não tinha começado.
5. **Modo de trabalho:** o Jairo quer **reaprender React até conseguir desenvolver sozinho**.
   - Ele escreve o código, com orientação.
   - A IA ensina, revisa e escreve a documentação.
   - Trechos pontuais de código vêm da IA quando ele travar, como a política 🟡 permite.
   - **Desde 28/10**, para caber no prazo, a IA também escreve a parte estrutural: os tipos dos DTOs, as
     funções de chamada da API e a configuração do React Query e do store, explicando cada trecho. Os
     componentes, os hooks, os formulários e a lógica que a rubrica pontua continuam com ele.

### Decisões técnicas (recomendadas; cada uma é confirmada no bloco em que aparece)

| Tema                 | Recomendação                                                                                                                           | Motivo                                                                                                                                                                                                                                                                                                                                                     |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Chamada à API        | **proxy do Vite**: o front chama `/api/...`, e o Vite repassa para `localhost:8080` sem o prefixo                                      | Dispensa CORS no back-end. Sem o prefixo `/api`, a rota de tela `/projects` colidiria com o endpoint `/projects` ao recarregar a página                                                                                                                                                                                                                    |
| HTTP                 | **`fetch`** com um wrapper próprio (`httpClient`), confirmado em 22/10                                                                 | O timeout com `Promise.race` e o `AbortController` aparecem naturalmente; o Axios esconderia os dois. O objetivo é aprender o que o Axios faz por dentro; a troca fica possível depois da entrega                                                                                                                                                          |
| Estado               | React Query para os dados da API, Redux Toolkit para a sessão, Context para as notificações                                            | Cada um resolve um problema diferente, o que é o texto do item 12 da rubrica                                                                                                                                                                                                                                                                               |
| Componente de classe | `ErrorBoundary`                                                                                                                        | No React 19, ainda só existe como classe                                                                                                                                                                                                                                                                                                                   |
| Error boundary       | **Escrito à mão** (decidido em 16/10), no `shared/components`, em vez da lib `react-error-boundary`                                    | Com a lib, a classe ficaria no `node_modules`, e o item 6 da rubrica pede componente de classe no meu código; escrever também ensina o que a lib faz por dentro. Em produção, a lib seria a escolha (`resetKeys`, `onReset`, `showBoundary` para erros assíncronos); a troca fica possível depois da entrega e entra nas considerações finais do relatório |
| Estilos              | Tailwind v4, com o plugin `@tailwindcss/vite`                                                                                          | O item 11 cita Styled Components, MUI e CSS Modules como exemplos; o Tailwind é equivalente                                                                                                                                                                                                                                                                |
| Linter               | **ESLint** (decidido em 08/10), no lugar do Oxlint, que é o padrão do template                                                         | É o que a maioria dos projetos usa. Vem com o plugin de hooks do time do React, que já liga `rules-of-hooks` e `exhaustive-deps`                                                                                                                                                                                                                           |
| Formatador           | **Prettier** (decidido em 10/10), com as regras padrão escritas no `.prettierrc` e o plugin oficial do Tailwind, que ordena as classes | O formato fica definido no projeto, e não no editor de cada um. O `npm run format:check` confere                                                                                                                                                                                                                                                           |
| Roteamento           | **React Router 8 no modo declarativo** (decidido em 14/10): `<BrowserRouter>`, `<Routes>` e `<Route>`                                  | O modo data traria _loaders_ e _actions_, que repetem o papel do React Query, e captura sozinho os erros de render das rotas, que nunca chegariam ao `ErrorBoundary`. Se um dia precisar, o React Router tem um guia oficial de migração para o modo data                                                                                                  |
| Idioma               | **Interface em português, código em inglês** (decidido em 14/10)                                                                       | Os prints vão para o relatório, e o relatório e a documentação estão em português. Nomes, arquivos, URLs e commits seguem em inglês, como no back-end                                                                                                                                                                                                      |
| `clientId` sem JWT   | `VITE_DEV_CLIENT_ID` no `.env.local`                                                                                                   | O `POST /projects` exige `clientId`. Sairia no bloco 5, mas, com o JWT cortado (28/10), o login simulado não tem um `clientId` de verdade, e a variável fica                                                                                                                                                                                               |

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
    │   ├── identity/         # login e sessão   ↔ módulo identity do permission-service
    │   │   ├── components/   # LoginForm
    │   │   ├── pages/        # LoginPage
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
- **Se o JWT voltar** (saiu em 28/10), o token chega ao `httpClient` pelo `app`, para o `shared` não
  depender do `identity`.

---

## Cronograma

| Bloco                          | Datas                            | O que se faz                                                                                                                                                                                                                                                                                                                                                                                                                  | Itens da rubrica                     |
| ------------------------------ | -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 0. Diagnóstico e estrutura     | 08–09/10                         | questionário; `npm create vite@latest` (template `react-ts`) no `permission_saas_front`; tour pelos arquivos gerados; Tailwind; `.gitignore` (`node_modules`, `dist`); README com como rodar e a estrutura                                                                                                                                                                                                                    | 2, 4, 11                             |
| 1. Base                        | 10/10–01/11 (previsto: 10–13/10) | `httpClient` (prefixo `/api`, conversão do `ErrorResponse` da API, timeout com `Promise.race`, `signal`); proxy do Vite; layout; React Router com as rotas ainda vazias; `NotificationContext`; `ErrorBoundary`                                                                                                                                                                                                               | 3, 6, 14                             |
| 2. Cadastro                    | **saiu em 28/10**                | Nem o enunciado nem a rubrica pedem cadastro, e o formulário de projeto (bloco 3) já cobre o formulário controlado, o `useForm`, a validação e o erro 400. Vira trabalho futuro no relatório                                                                                                                                                                                                                                  | 5, 7, 13, 14 (cobertos pelo bloco 3) |
| 3. CRUD de projetos            | 30/10–04/11                      | React Query (consultas e mutações, cache invalidado depois de cada mudança); telas de lista, detalhe e formulário (criar e editar usam o mesmo formulário); componentes reutilizáveis com props; busca por nome com debounce e `AbortController`; confirmação de exclusão com template literal; o front valida o que der antes de chamar a API (formulário, e `id` da URL fora do formato UUID vira "projeto não encontrado") | 5, 7, 8, 13, 15, 16                  |
| 4. JWT no back-end             | **saiu em 28/10**                | Cortado na data de corte, sem ter começado. O UUID inválido no caminho continua dando 500 na API; o front já o trata como "projeto não encontrado" (bloco 3)                                                                                                                                                                                                                                                                  | nenhum                               |
| 5. Login, Redux e rota privada | 05–06/11                         | `store` e `authSlice` (actions e reducers); `useSelector` e `useDispatch`; `LoginForm` **não controlado**, com o login simulado no front; `PrivateRoute`; logout                                                                                                                                                                                                                                                              | 9, 10, 12                            |
| 6. Fechamento                  | 07–09/11                         | teste no Chrome, no Firefox e no Edge; revisão dos comentários; screenshots; relatório com os 9 itens e o registro de uso de IA, citando a liberação do professor e o ADR-016                                                                                                                                                                                                                                                 | 1, 3                                 |
| Folga                          | —                                | consumida pelo atraso do bloco 1                                                                                                                                                                                                                                                                                                                                                                                              | —                                    |

**Replanejado em 28/10.** O bloco 1 tinha 4 dias no plano e levou 18. Faltavam uns 23 dias de trabalho
para 13 de calendário, já contando a folga. Saíram o JWT, pela regra de corte, e a tela de cadastro; os
checklists passam a ter 2 ou 3 experimentos por passo; e a IA passa a escrever a parte estrutural
(decisão 5). Mesmo assim, o cronograma fica sem margem.

### Ordem de corte, se atrasar

1. ~~**JWT no back-end** (data de corte: 28/10). O login vira uma simulação no front, e o Redux e a rota
   privada ficam iguais.~~ Aplicado em 28/10.
2. **Componente de terceiros**, pedido no enunciado, mas fora da rubrica.
3. **Timeout com `Promise.race`.**

### Itens do enunciado que a rubrica não pontua

Ficam no plano porque estão nas features: `useEffect` (debounce da busca), hook personalizado
(`useForm`), Context API (`NotificationContext`), formulário não controlado (login), rotas privadas,
`AbortController`, `Promise.race` e um componente de terceiros (a escolher no bloco 3).

---

## Situação (atualizado em 03/11/2026)

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
- [x] **Bloco 1** (10/10–01/11). Ordem decidida em 12/10: primeiro o que aparece na tela; o `httpClient`,
      que não tem tela, ficou por último
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
  - [x] Proxy do Vite e `httpClient` (22/10–01/11): o proxy repassa `/api` para a API sem o prefixo, e o
        `httpClient` no `shared` faz o JSON, o timeout com `Promise.race` que também aborta, o `signal` de
        quem chama (`AbortSignal.any`) e converte toda falha num `HttpError` com `kind` e `status`.
        Requisitos, perguntas e experimentos de previsão (CORS sem o proxy, F5 com o proxy, erros da API,
        timeout e cancelamento); as convenções de chamada à API no `docs/ARCHITECTURE.md` do front
- [ ] **Bloco 2:** saiu em 28/10 (ver [Cronograma](#cronograma))
- [ ] **Bloco 4:** saiu em 28/10, na data de corte do JWT
- [ ] **Bloco 3** ← em andamento (01/11–)
  - [x] Lista de projetos com o React Query (01/11): a parte estrutural (tipos, chamadas, chaves de
        cache e o `QueryClient`) e a página com carregando, erro, vazio e a lista; experimentos do cache
        ao trocar de página, da busca ao voltar o foco e da API parada. No caminho: o organizador de
        imports no Prettier e o `npm run check`
  - [x] Busca com debounce (02–03/11): o hook `useDebounce` no `shared`, a busca por nome e o filtro de
        status na chave da query, com o `signal` cancelando a busca velha pelo `AbortSignal.any`; o
        `ProjectList` e o `ProjectCard` por props, em cima de um `Card` no `shared`, e a data formatada
        com o `Intl`. Requisitos, perguntas e experimentos de previsão (com o debounce, sem a limpeza do
        effect e sem o hook no 3G lento); as convenções de filtros e de debounce e a de peça visual no
        `docs/ARCHITECTURE.md` do front
  - [ ] Detalhe do projeto ← próximo passo
  - [ ] Formulário de criar e editar, com o `useForm`, e os avisos de sucesso e erro
  - [ ] Exclusão com confirmação

---

## Uso de IA

Política 🟡: a IA pode ser usada para tirar dúvidas, sugerir organização, gerar trechos pontuais de
código, depurar, refatorar, revisar estilos, preparar dados de teste, apoiar formulários e chamadas à
API e sugerir abordagens de estado, Hooks, Context API, operações assíncronas e navegação. Todo uso é
citado no relatório.

Ferramenta: **Claude Code**, da Anthropic.

| Data             | Parte             | Como a IA foi usada                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| ---------------- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 07/10/2026       | Enunciado e plano | Formatou o enunciado em Markdown e o separou por etapa; confrontou o enunciado com a rubrica; ajudou a montar este plano e a estrutura de pastas. As decisões de escopo, stack e ordem foram minhas                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| 07/10/2026       | Diagnóstico       | Questionário de conceitos (JS, React, TypeScript, bibliotecas) e correção comentada das minhas respostas                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| 08/10/2026       | Bloco 0           | Explicou o comando de criação do projeto e a diferença entre Oxlint e ESLint; a escolha do ESLint foi minha                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 08/10/2026       | Bloco 0           | Explicou os arquivos gerados pelo template. A meu pedido, juntou as regras do `.gitignore`, escreveu o README com como rodar e fez os commits. O projeto foi criado por mim                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 10/10/2026       | Bloco 0           | Explicou a abordagem _utility-first_ do Tailwind e revisou a instalação, que fiz seguindo o guia oficial                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| 10/10/2026       | Bloco 0           | Propôs a configuração do Prettier, que instalei e configurei; revisou a limpeza do template e apontou o import do `App.css` apagado. A meu pedido, criou o `.vscode/extensions.json`, ajustou o `.gitignore` e o README e fez os commits                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| 12–14/10/2026    | Bloco 1           | Explicou o modelo de render (o que dispara um render, o state como foto, a fila de updates, `StrictMode`, imutabilidade) com um exemplo fora do projeto, propôs os experimentos e revisou minhas previsões e respostas. Sugeriu a ordem do bloco 1, que aceitei. Escrevi os experimentos e os descartei                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| 14–15/10/2026    | Bloco 1           | Explicou o React Router (os três modos, rotas aninhadas, layout com `Outlet`, `useParams`, `Navigate` e `NavLink`) com um exemplo fora do projeto e revisou as rotas e o layout que escrevi; ao responder uma pergunta de fixação, apontou que a API devolve 500 para um UUID inválido. O modo declarativo e o português na interface foram escolhas minhas. A meu pedido, criou o `docs/ARCHITECTURE.md` do front com a estrutura de pastas e as convenções de código e atualizou o README                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 16–17/10/2026    | Bloco 1           | Explicou error boundaries e componentes de classe com um exemplo fora do projeto; como tech lead, avaliou a lib `react-error-boundary` contra escrever o componente, e a decisão de escrever foi minha; a meu pedido, passou os requisitos do `ErrorBoundary` sem código e revisou minhas respostas e previsões. Também a meu pedido, configurou o alias `@/` (`tsconfig.app.json` e `vite.config.ts`), trocou os imports que atravessam pastas e registrou a convenção, que aprovei                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| 19/10/2026       | Bloco 1           | Revisou o `ErrorBoundary` que escrevi, item por item do checklist, e explicou os erros que encontrei no caminho: o `this` perdido em método passado como callback, a mutação do state na classe e o erro de handler que o boundary não captura. Pesquisou na documentação do React qual padrão de handler em classe é o recomendado; a escolha foi minha. A meu pedido, criou o checklist do passo, organizou as pendências e registrou as convenções que aprovei (prefixo `on`, barrel do `shared`, `??`, modificadores explícitos, dado fixo fora do componente, tipos e pastas de componente). Também ajudou a acessar o servidor de dev pela rede da empresa, com o navegador integrado do VS Code                                                                                                                                                                                                                                     |
| 20–22/10/2026    | Bloco 1           | Explicou a Context API com analogias e exemplos fora do projeto: as três peças, por que os `children` do provider não renderizam de novo, o custo do prop drilling, `useCallback` e `useMemo`, e o `crypto.randomUUID`. Revisou o contexto, o provider, o hook e o toast que escrevi, e apontou a causa do loop infinito (o `notify` chamado no corpo do componente) e a do timer que reiniciava (um timer só, no provider, em vez de um por aviso). A meu pedido, fez o visual do toast (cores e ícones por tipo, animação de entrada e o container que não bloqueia cliques), estreitou o tipo do `role`, corrigiu um import e um acento, removeu os botões de teste e registrou as convenções que aprovei (comandos sem `handle`, o padrão do Context, arquivo sem JSX em `.ts`). A lógica (o state, os comandos, o timer por aviso e a guarda do hook) foi minha. Também revisou minhas previsões dos experimentos                     |
| 22–28/10/2026    | Bloco 1           | Explicou o proxy do Vite, a origem e o CORS, e o que o `fetch` faz e não faz (erro HTTP × falha de rede, corpo lido uma vez, timeout, `AbortController`) com analogias, e comparou o `fetch` com o Axios; a escolha do `fetch` foi minha. A meu pedido, passou os requisitos do `httpClient` sem código e revisou minhas respostas e previsões. Diagnosticou por que a API não subia (o banco do container estava na 5434 e a API procurava na 5432) e por que o `/api/ping` não abria no navegador do VS Code (o cabeçalho `X-Frame-Options` do Spring Security), testando os endereços com `curl`; o proxy foi escrito por mim. Avaliou o cronograma em 22/10 e em 28/10 e propôs cortes: em 22/10 mantive o plano; em 28/10 aceitei o corte do JWT (a regra do plano), o do cadastro, menos experimentos por passo e a IA escrevendo a parte estrutural                                                                                 |
| 28/10–01/11/2026 | Bloco 1           | Na divisão combinada em 28/10, escreveu a classe `HttpError` (o tipo do erro e os campos) e os tipos `ErrorResponse` e `RequestOptions`. Explicou o `AbortSignal.any` e a Promise do relógio no `Promise.race` com exemplos fora do projeto, quando travei, e revisou o `httpClient` que escrevi (barra dupla no caminho, Promise que abortava ao ser criada, `throw` num listener, 204 e corpo de erro sem JSON, cancelamento classificado pelo nome do erro). A meu pedido, escreveu a leitura da mensagem de erro com mensagem genérica quando o corpo não é o `ErrorResponse`. Também a meu pedido, montou a página temporária com os botões dos experimentos. Revisou os resultados dos experimentos e, a meu pedido, fechou o passo: removeu a página temporária, conferiu build, lint e formatação e registrou as convenções que aprovei. O `request`, o `Promise.race`, a junção dos sinais e a classificação dos erros foram meus |
| 01/11/2026       | Bloco 3           | Na divisão combinada em 28/10, escreveu a parte estrutural do CRUD: os tipos dos DTOs de projeto, as funções de chamada da API (`projectApi.ts`), as chaves de cache (`projectKeys.ts`) e o `QueryClient` com o `QueryClientProvider`. Explicou o React Query com analogias e um exemplo fora do projeto e passou os requisitos da lista sem código. A meu pedido, configurou o plugin que organiza os imports no Prettier e o script `check` (build, lint e formatação num comando só); revisou os experimentos da lista e, a meu pedido, conferiu as requisições num Chrome sem tela, pelo protocolo de depuração, e escreveu a mensagem de erro da lista escolhida pelo `kind`. A lista e as instalações foram minhas                                                                                                                                                                                                                   |
| 02–03/11/2026    | Bloco 3           | Explicou o debounce com uma analogia e um exemplo fora do projeto e passou os requisitos sem código. Revisou o hook e a página (o objeto novo na dependência do effect, que renderizava sem parar; o `false` no `onlyActive`, que trazia só os inativos; o `??` no lugar do `&&`) e explicou o eixo do flex e as margens automáticas. Sugeriu o select de status no lugar do checkbox e o `Intl.DateTimeFormat`, com o trecho de `formatDateTime`. A meu pedido, escreveu o componente `Card` do `shared` e as partes dele e as classes do Tailwind da lista, do card e da página, levando a grade para fora do `map` do `ProjectList`, e tirou uma anotação de tipo que sobrava no hook. Revisou os experimentos e as perguntas e criou o checklist do passo. O hook, a página, a lista, o `ProjectCard` e o select foram meus                                                                                                            |

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

- **Bloco 6:** os 16 itens da rubrica conferidos um a um contra o código e os prints.
