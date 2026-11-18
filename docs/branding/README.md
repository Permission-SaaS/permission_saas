# Branding — identidade visual

A identidade visual do Permission SaaS, feita para servir também aos próximos projetos. Ela reúne as
cores, a tipografia, o espaçamento, as bordas, a elevação, o movimento, os ícones, as cores de dados e a
voz dos textos. Definida em 17/11/2026 a partir das cinco cores e das regras escolhidas pelo Jairo; o
contraste de cada combinação foi calculado, e não estimado.

| Arquivo | O que é |
|---|---|
| `README.md` | este guia |
| [`tokens.json`](tokens.json) | **a fonte da verdade**: todos os valores (cores, fontes, estilos de texto, espaçamento, raio, sombras, movimento), no formato W3C Design Tokens |
| [`tokens.css`](tokens.css) | as mesmas cores e sombras no formato do shadcn/ui com Tailwind CSS v4, pronto para o front |
| [`contrast.py`](contrast.py) | confere se o CSS bate com o JSON (cores e sombras), se espaçamentos e alturas de linha são múltiplos de 4, se o raio é o de 2 px e se cada par passa no WCAG AA; imprime as tabelas de contraste deste guia |
| [`figma/`](figma/) | os conjuntos para colar no plugin Tokens Studio do Figma, gerados do `tokens.json` pelo `figma/build.py` (ver [No Figma](#no-figma)) |

**Mudou um token? Mude o `tokens.json` e o `tokens.css` juntos e rode** (na raiz do repositório; cada
um sai com erro se algo quebrar):

```bash
python3 -I docs/branding/contrast.py        # contraste e CSS igual ao JSON
python3 -I docs/branding/figma/build.py     # regera os arquivos do Figma
```

---

## Princípios

1. **Técnico e confiável.** O produto valida acessos; a interface tem que passar segurança: preto,
   grafite e branco na maior parte, e o dourado só onde há ação ou destaque.
2. **Amigável.** A fonte arredondada e os textos em "você" tiram a frieza de um painel técnico.
3. **Minimalista.** Um raio só (2 px), poucas linhas, poucas cores por tela e um único botão primário. O
   que não ajuda a pessoa a decidir ou agir sai da tela.
4. **Legível primeiro.** Todo texto passa no WCAG AA nos dois temas, e o desenho começa pelo celular de
   360 px.

---

## Cores

### As cores da marca

| Cor | Papel | Onde está nas escalas |
|---|---|---|
| `#0d0d0e` | preto: texto no claro, fundo no escuro | `neutral-950` |
| `#2a2a2c` | grafite: superfícies no escuro, texto forte | `neutral-800` |
| `#e3b400` | dourado: a cor da marca, ação principal | `gold-500` |
| `#f6e6a6` | creme: destaque suave | `gold-100` |
| `#f8f8f8` | branco gelo: fundo no claro, texto no escuro | `neutral-50` |

> ⚠️ **A regra do dourado.** O `#e3b400` tem contraste de só **1,83:1** sobre o fundo claro. No tema
> claro ele **nunca** é texto, ícone ou borda: só fundo (de botão, de selo, de destaque), sempre com texto
> preto por cima (9,99:1). Para link e anel de foco no claro, use o `gold-800` (`#7a6200`, 5,53:1). No
> tema escuro, o próprio `#e3b400` pode ser texto e ícone (9,99:1 sobre o preto).

### Escalas primitivas

As escalas ficam no mesmo matiz das cores da marca (neutros levemente azulados, 240°, e dourado, 48°).
Não use as primitivas direto nas telas: use as **semânticas** (abaixo), que já mudam com o tema.

| Tom | `neutral` | `gold` |
|---|---|---|
| 50 | `#f8f8f8` ★ | `#fef9e7` |
| 100 | `#efeff0` | `#f6e6a6` ★ |
| 200 | `#e2e2e4` | `#f4da71` |
| 300 | `#cacace` | `#efcd45` |
| 400 | `#a0a0a6` | `#e9c11f` |
| 500 | `#8b8b92` | `#e3b400` ★ |
| 600 | `#77777e` | `#c29b00` |
| 700 | `#5c5c63` | `#997a00` |
| 800 | `#2a2a2c` ★ | `#7a6200` |
| 900 | `#1b1b1d` | `#5c4900` |
| 950 | `#0d0d0e` ★ | `#382d00` |

★ = cor da marca. Além delas: `white` (`#ffffff`) e quatro tons de cada cor de estado:

| Tom | `red` (perigo) | `green` (sucesso) | `orange` (aviso) | `blue` (informação) | `purple` (dados) |
|---|---|---|---|---|---|
| 50 | `#fef3f2` | `#ecfdf3` | `#fff6ed` | `#eff8ff` | `#f4f3ff` |
| 400 | `#f97066` | `#47cd89` | `#fb923c` | `#53b1fd` | `#b692f6` |
| 700 | `#b42318` | `#067647` | `#b54708` | `#175cd3` | `#6941c6` |
| 950 | `#3a1512` | `#0c2a1c` | `#3a1d07` | `#0b2140` | `#251a45` |

**Por que o aviso é laranja:** amarelo é a cor de aviso mais comum, mas aqui ele é a cor da marca. Um aviso
amarelo pareceria um botão. O laranja ainda é lido como "atenção" e não se confunde com o dourado.

### Cores semânticas

Os nomes seguem o shadcn/ui, para que os componentes usem as cores da marca sem ajuste. Cada nome vira
classe do Tailwind: `bg-primary`, `text-muted-foreground`, `border-input`, `text-method-get`...

| Nome | Tema claro | Tema escuro | Para quê |
|---|---|---|---|
| `background` | `#f8f8f8` | `#0d0d0e` | fundo da página |
| `foreground` | `#0d0d0e` | `#f8f8f8` | texto principal |
| `card` / `card-foreground` | `#ffffff` / `#0d0d0e` | `#1b1b1d` / `#f8f8f8` | cards e painéis |
| `popover` / `popover-foreground` | `#ffffff` / `#0d0d0e` | `#2a2a2c` / `#f8f8f8` | menus, popovers, modais |
| `primary` / `primary-foreground` | `#e3b400` / `#0d0d0e` | `#e3b400` / `#0d0d0e` | a ação principal da tela |
| `secondary` / `secondary-foreground` | `#f6e6a6` / `#0d0d0e` | `#382d00` / `#f6e6a6` | ação secundária, destaque suave |
| `muted` / `muted-foreground` | `#efeff0` / `#5c5c63` | `#2a2a2c` / `#a0a0a6` | áreas apagadas e texto secundário |
| `accent` / `accent-foreground` | `#fef9e7` / `#0d0d0e` | `#2a2a2c` / `#f8f8f8` | item com hover ou selecionado |
| `destructive` (+ `-foreground`, `-subtle`) | `#b42318` (+ `#ffffff`, `#fef3f2`) | `#f97066` (+ `#0d0d0e`, `#3a1512`) | excluir, erro |
| `success` (+ `-foreground`, `-subtle`) | `#067647` (+ `#ffffff`, `#ecfdf3`) | `#47cd89` (+ `#0d0d0e`, `#0c2a1c`) | sucesso, Ativo |
| `warning` (+ `-foreground`, `-subtle`) | `#b54708` (+ `#ffffff`, `#fff6ed`) | `#fb923c` (+ `#0d0d0e`, `#3a1d07`) | aviso |
| `info` (+ `-foreground`, `-subtle`) | `#175cd3` (+ `#ffffff`, `#eff8ff`) | `#53b1fd` (+ `#0d0d0e`, `#0b2140`) | informação |
| `border` | `#e2e2e4` | `#2a2a2c` | divisórias e contorno de cards (decorativo) |
| `input` | `#8b8b92` | `#77777e` | borda de campo de formulário (precisa de 3:1) |
| `ring` | `#7a6200` | `#e3b400` | anel de foco |
| `link` | `#7a6200` | `#e3b400` | link no meio do texto |

Para cada cor de estado: `-foreground` é o texto **sobre** a cor cheia (botão, toast), e `-subtle` é o
fundo suave de alerta e de selo, com o texto na própria cor (ex.: `text-success` sobre
`bg-success-subtle`).

### Contraste conferido

Gerado pelo `contrast.py`. Mínimo do WCAG 2.x: **4,5:1** para texto e **3:1** para componentes (borda de
campo, anel de foco). AAA de texto: 7:1. A borda decorativa (`border`) não entra, porque divisórias não
precisam de contraste.

#### Tema claro

| Texto ou elemento | Fundo | Contraste | Mínimo | AA | AAA | Onde aparece |
|---|---|---|---|---|---|---|
| `foreground` `#0d0d0e` | `background` `#f8f8f8` | 18.29:1 | 4.5:1 | ✓ | ✓ | texto principal |
| `card-foreground` `#0d0d0e` | `card` `#ffffff` | 19.43:1 | 4.5:1 | ✓ | ✓ | texto dentro de card |
| `popover-foreground` `#0d0d0e` | `popover` `#ffffff` | 19.43:1 | 4.5:1 | ✓ | ✓ | menu e popover |
| `muted-foreground` `#5c5c63` | `background` `#f8f8f8` | 6.25:1 | 4.5:1 | ✓ | — | texto secundário |
| `muted-foreground` `#5c5c63` | `card` `#ffffff` | 6.63:1 | 4.5:1 | ✓ | — | texto secundário em card |
| `muted-foreground` `#5c5c63` | `muted` `#efeff0` | 5.77:1 | 4.5:1 | ✓ | — | selo Inativo, área apagada |
| `primary-foreground` `#0d0d0e` | `primary` `#e3b400` | 9.99:1 | 4.5:1 | ✓ | ✓ | botão primário |
| `secondary-foreground` `#0d0d0e` | `secondary` `#f6e6a6` | 15.53:1 | 4.5:1 | ✓ | ✓ | botão secundário, destaque |
| `accent-foreground` `#0d0d0e` | `accent` `#fef9e7` | 18.43:1 | 4.5:1 | ✓ | ✓ | item com hover ou selecionado |
| `link` `#7a6200` | `background` `#f8f8f8` | 5.53:1 | 4.5:1 | ✓ | — | link |
| `link` `#7a6200` | `card` `#ffffff` | 5.87:1 | 4.5:1 | ✓ | — | link em card |
| `destructive-foreground` `#ffffff` | `destructive` `#b42318` | 6.57:1 | 4.5:1 | ✓ | — | botão de perigo |
| `destructive` `#b42318` | `background` `#f8f8f8` | 6.19:1 | 4.5:1 | ✓ | — | mensagem de erro |
| `destructive` `#b42318` | `card` `#ffffff` | 6.57:1 | 4.5:1 | ✓ | — | erro de campo em card |
| `destructive` `#b42318` | `destructive-subtle` `#fef3f2` | 6.05:1 | 4.5:1 | ✓ | — | alerta de erro |
| `success-foreground` `#ffffff` | `success` `#067647` | 5.69:1 | 4.5:1 | ✓ | — | botão ou toast de sucesso |
| `success` `#067647` | `card` `#ffffff` | 5.69:1 | 4.5:1 | ✓ | — | texto de sucesso em card |
| `success` `#067647` | `success-subtle` `#ecfdf3` | 5.40:1 | 4.5:1 | ✓ | — | selo Ativo, alerta de sucesso |
| `warning-foreground` `#ffffff` | `warning` `#b54708` | 5.43:1 | 4.5:1 | ✓ | — | toast de aviso |
| `warning` `#b54708` | `card` `#ffffff` | 5.43:1 | 4.5:1 | ✓ | — | texto de aviso em card |
| `warning` `#b54708` | `warning-subtle` `#fff6ed` | 5.08:1 | 4.5:1 | ✓ | — | alerta de aviso |
| `info-foreground` `#ffffff` | `info` `#175cd3` | 5.99:1 | 4.5:1 | ✓ | — | toast de informação |
| `info` `#175cd3` | `card` `#ffffff` | 5.99:1 | 4.5:1 | ✓ | — | texto informativo em card |
| `info` `#175cd3` | `info-subtle` `#eff8ff` | 5.57:1 | 4.5:1 | ✓ | — | alerta informativo |
| `method-get` `#175cd3` | `method-get-subtle` `#eff8ff` | 5.57:1 | 4.5:1 | ✓ | — | selo GET |
| `method-post` `#067647` | `method-post-subtle` `#ecfdf3` | 5.40:1 | 4.5:1 | ✓ | — | selo POST |
| `method-put` `#b54708` | `method-put-subtle` `#fff6ed` | 5.08:1 | 4.5:1 | ✓ | — | selo PUT |
| `method-patch` `#6941c6` | `method-patch-subtle` `#f4f3ff` | 6.02:1 | 4.5:1 | ✓ | — | selo PATCH |
| `method-delete` `#b42318` | `method-delete-subtle` `#fef3f2` | 6.05:1 | 4.5:1 | ✓ | — | selo DELETE |
| `method-get` `#175cd3` | `card` `#ffffff` | 5.99:1 | 4.5:1 | ✓ | — | método GET numa tabela |
| `method-patch` `#6941c6` | `card` `#ffffff` | 6.62:1 | 4.5:1 | ✓ | — | método PATCH numa tabela |
| `input` `#8b8b92` | `background` `#f8f8f8` | 3.19:1 | 3.0:1 | ✓ | — | borda de campo |
| `input` `#8b8b92` | `card` `#ffffff` | 3.38:1 | 3.0:1 | ✓ | — | borda de campo em card |
| `ring` `#7a6200` | `background` `#f8f8f8` | 5.53:1 | 3.0:1 | ✓ | — | anel de foco |
| `ring` `#7a6200` | `card` `#ffffff` | 5.87:1 | 3.0:1 | ✓ | — | anel de foco em card |
| `primary` `#e3b400` | `background` `#f8f8f8` | 1.83:1 | — | ❌ proibido | — | dourado como texto ou ícone |
| `primary` `#e3b400` | `card` `#ffffff` | 1.95:1 | — | ❌ proibido | — | dourado como texto ou ícone em card |

#### Tema escuro

| Texto ou elemento | Fundo | Contraste | Mínimo | AA | AAA | Onde aparece |
|---|---|---|---|---|---|---|
| `foreground` `#f8f8f8` | `background` `#0d0d0e` | 18.29:1 | 4.5:1 | ✓ | ✓ | texto principal |
| `card-foreground` `#f8f8f8` | `card` `#1b1b1d` | 16.19:1 | 4.5:1 | ✓ | ✓ | texto dentro de card |
| `popover-foreground` `#f8f8f8` | `popover` `#2a2a2c` | 13.49:1 | 4.5:1 | ✓ | ✓ | menu e popover |
| `muted-foreground` `#a0a0a6` | `background` `#0d0d0e` | 7.47:1 | 4.5:1 | ✓ | ✓ | texto secundário |
| `muted-foreground` `#a0a0a6` | `card` `#1b1b1d` | 6.61:1 | 4.5:1 | ✓ | — | texto secundário em card |
| `muted-foreground` `#a0a0a6` | `muted` `#2a2a2c` | 5.51:1 | 4.5:1 | ✓ | — | selo Inativo, área apagada |
| `primary-foreground` `#0d0d0e` | `primary` `#e3b400` | 9.99:1 | 4.5:1 | ✓ | ✓ | botão primário |
| `secondary-foreground` `#f6e6a6` | `secondary` `#382d00` | 10.88:1 | 4.5:1 | ✓ | ✓ | botão secundário, destaque |
| `accent-foreground` `#f8f8f8` | `accent` `#2a2a2c` | 13.49:1 | 4.5:1 | ✓ | ✓ | item com hover ou selecionado |
| `link` `#e3b400` | `background` `#0d0d0e` | 9.99:1 | 4.5:1 | ✓ | ✓ | link |
| `link` `#e3b400` | `card` `#1b1b1d` | 8.84:1 | 4.5:1 | ✓ | ✓ | link em card |
| `destructive-foreground` `#0d0d0e` | `destructive` `#f97066` | 6.97:1 | 4.5:1 | ✓ | — | botão de perigo |
| `destructive` `#f97066` | `background` `#0d0d0e` | 6.97:1 | 4.5:1 | ✓ | — | mensagem de erro |
| `destructive` `#f97066` | `card` `#1b1b1d` | 6.17:1 | 4.5:1 | ✓ | — | erro de campo em card |
| `destructive` `#f97066` | `destructive-subtle` `#3a1512` | 5.82:1 | 4.5:1 | ✓ | — | alerta de erro |
| `success-foreground` `#0d0d0e` | `success` `#47cd89` | 9.59:1 | 4.5:1 | ✓ | ✓ | botão ou toast de sucesso |
| `success` `#47cd89` | `card` `#1b1b1d` | 8.49:1 | 4.5:1 | ✓ | ✓ | texto de sucesso em card |
| `success` `#47cd89` | `success-subtle` `#0c2a1c` | 7.60:1 | 4.5:1 | ✓ | ✓ | selo Ativo, alerta de sucesso |
| `warning-foreground` `#0d0d0e` | `warning` `#fb923c` | 8.58:1 | 4.5:1 | ✓ | ✓ | toast de aviso |
| `warning` `#fb923c` | `card` `#1b1b1d` | 7.60:1 | 4.5:1 | ✓ | ✓ | texto de aviso em card |
| `warning` `#fb923c` | `warning-subtle` `#3a1d07` | 6.83:1 | 4.5:1 | ✓ | — | alerta de aviso |
| `info-foreground` `#0d0d0e` | `info` `#53b1fd` | 8.39:1 | 4.5:1 | ✓ | ✓ | toast de informação |
| `info` `#53b1fd` | `card` `#1b1b1d` | 7.43:1 | 4.5:1 | ✓ | ✓ | texto informativo em card |
| `info` `#53b1fd` | `info-subtle` `#0b2140` | 6.95:1 | 4.5:1 | ✓ | — | alerta informativo |
| `method-get` `#53b1fd` | `method-get-subtle` `#0b2140` | 6.95:1 | 4.5:1 | ✓ | — | selo GET |
| `method-post` `#47cd89` | `method-post-subtle` `#0c2a1c` | 7.60:1 | 4.5:1 | ✓ | ✓ | selo POST |
| `method-put` `#fb923c` | `method-put-subtle` `#3a1d07` | 6.83:1 | 4.5:1 | ✓ | — | selo PUT |
| `method-patch` `#b692f6` | `method-patch-subtle` `#251a45` | 6.42:1 | 4.5:1 | ✓ | — | selo PATCH |
| `method-delete` `#f97066` | `method-delete-subtle` `#3a1512` | 5.82:1 | 4.5:1 | ✓ | — | selo DELETE |
| `method-get` `#53b1fd` | `card` `#1b1b1d` | 7.43:1 | 4.5:1 | ✓ | ✓ | método GET numa tabela |
| `method-patch` `#b692f6` | `card` `#1b1b1d` | 6.90:1 | 4.5:1 | ✓ | — | método PATCH numa tabela |
| `input` `#77777e` | `background` `#0d0d0e` | 4.37:1 | 3.0:1 | ✓ | — | borda de campo |
| `input` `#77777e` | `card` `#1b1b1d` | 3.87:1 | 3.0:1 | ✓ | — | borda de campo em card |
| `ring` `#e3b400` | `background` `#0d0d0e` | 9.99:1 | 3.0:1 | ✓ | — | anel de foco |
| `ring` `#e3b400` | `card` `#1b1b1d` | 8.84:1 | 3.0:1 | ✓ | — | anel de foco em card |
| `primary` `#e3b400` | `background` `#0d0d0e` | 9.99:1 | 4.5:1 | ✓ | ✓ | dourado como texto ou ícone |
| `primary` `#e3b400` | `card` `#1b1b1d` | 8.84:1 | 4.5:1 | ✓ | ✓ | dourado como texto ou ícone em card |

**Combinações fora da tabela não estão conferidas.** Antes de usar uma nova (ex.: texto sobre o creme no
escuro), acrescente o par em `PAIRS`, no `contrast.py`, e rode a conferência.

---

## Tipografia

| Uso | Fonte | Por quê |
|---|---|---|
| Interface | **Nunito** | sem serifa, com as pontas arredondadas: amigável e muito legível em tela pequena |
| Código: rotas, ApiKey, JSON, métodos HTTP | **JetBrains Mono** | monoespaçada, com `0` e `O`, `1` e `l` bem diferentes, o que importa ao ler uma chave |

As duas são gratuitas, do Google Fonts, com licença OFL (uso comercial liberado). O Figma já tem as duas.
No front, entram pelos pacotes `@fontsource-variable/nunito` e `@fontsource-variable/jetbrains-mono`,
servidos pelo próprio site, sem chamada ao Google.

**Pesos:** 400 (texto), 600 (rótulos, botões, títulos de card), 700 (títulos), 800 (título de destaque).
Nada abaixo de 400: a Nunito fina perde legibilidade no celular.

### Escala

Só estes tamanhos existem (o `tokens.css` apaga os outros do Tailwind). Toda altura de linha é múltiplo
de 4.

| Classe | Tamanho / altura de linha |
|---|---|
| `text-xs` | 12 / 16 px |
| `text-sm` | 14 / 20 px |
| `text-base` | 16 / 24 px |
| `text-lg` | 18 / 28 px |
| `text-xl` | 20 / 28 px |
| `text-2xl` | 24 / 32 px |
| `text-3xl` | 28 / 36 px |
| `text-4xl` | 32 / 40 px |
| `text-5xl` | 40 / 48 px |

### Estilos de texto

Os nomes viram os estilos de texto do Figma. Mobile first: a coluna "Celular" é a base, e os títulos
crescem a partir do `md` (768 px).

| Estilo | Celular | A partir do `md` | Peso | Uso |
|---|---|---|---|---|
| Display | `text-3xl` | `text-5xl` | 800 | título de destaque (login, lista vazia) |
| Título 1 | `text-2xl` | `text-4xl` | 700 | título da tela |
| Título 2 | `text-xl` | `text-2xl` | 700 | seção da tela |
| Título 3 | `text-lg` | `text-xl` | 600 | título de card, de modal |
| Corpo | `text-base` | `text-base` | 400 | texto corrido, campos de formulário |
| Corpo pequeno | `text-sm` | `text-sm` | 400 | texto de apoio, células de tabela |
| Rótulo | `text-sm` | `text-sm` | 600 | rótulo de campo, botão, aba |
| Legenda | `text-xs` | `text-xs` | 400 | datas, contadores, ajuda do campo |
| Código | `text-sm`, mono | `text-sm`, mono | 400 | rota, ApiKey, JSON, selo de método |

O texto de campo de formulário fica em 16 px também no celular: abaixo disso, o Safari do iPhone dá zoom
na página quando o campo recebe o foco.

---

## Espaçamento

Tudo em **múltiplos de 4**. Coincide com o padrão do Tailwind (`p-1` = 4 px, `gap-2` = 8 px). **Não use
os fracionários do Tailwind** (`0.5`, `1.5`, `2.5`, `3.5`), que dão 2, 6, 10 e 14 px.

| px | Tailwind | Uso típico |
|---|---|---|
| 4 | `1` | ícone e texto colados, dentro de selo |
| 8 | `2` | entre ícone e texto num botão, entre rótulo e campo |
| 12 | `3` | preenchimento de selo e de campo pequeno |
| 16 | `4` | **margem lateral no celular**, preenchimento de card no celular, entre campos |
| 20 | `5` | preenchimento de botão na horizontal |
| 24 | `6` | preenchimento de card no desktop, entre cards |
| 32 | `8` | entre seções no celular |
| 40 | `10` | — |
| 48 | `12` | entre seções no desktop |
| 64 | `16` | respiro do topo da página no desktop |
| 80 | `20` | — |
| 96 | `24` | — |

**Alvo de toque:** botões, campos e itens de menu com pelo menos **44 px** de altura no celular (`h-11`).
A partir do `md`, 40 px (`h-10`) é aceitável. Um botão só com ícone também precisa de 44 × 44 px de área
clicável.

---

## Bordas

**Um raio só, de 2 px, em todo o projeto:** nem quadrado, nem arredondado demais. Um raio só é mais
minimalista e dá uma cara única ao sistema: o arredondado fica com as letras da Nunito, e as formas ficam
nítidas.

| Classe | Raio | Uso |
|---|---|---|
| `rounded-xs` | 2 px | **tudo**: botões, campos, selos, abas, cards, modais, toasts e o painel que sobe de baixo no celular |
| `rounded-full` | — | só avatar e pílula |

A escala de raios do Tailwind **fica intacta** (`rounded-sm`, `rounded-md`...): nada é apagado nem
redefinido, e ela continua lá se um dia for preciso. O projeto só não a usa. O `rounded-xs` já é o 2 px
padrão do Tailwind, sem configuração.

A linha de borda tem 1 px (`border`), e o anel de foco tem 2 px. Minimalismo vale também para as linhas:
prefira separar por espaço e por tom de fundo, e use a borda só onde ela ajuda a ler (campo de
formulário, card sobre fundo da mesma cor, divisória de tabela).

**shadcn/ui:** os componentes dele usam `rounded-md`, `rounded-lg` e `rounded-xl` no próprio código.
Como o raio do Tailwind não é redefinido, ao instalar cada componente troque essas classes por
`rounded-xs`.

---

## Elevação

| Nível | Tema claro | Tema escuro | Uso |
|---|---|---|---|
| 0 | `background`, sem sombra | `background` | a página |
| 1 | `card` + `shadow-sm` | `card` (`#1b1b1d`) | cards |
| 2 | `popover` + `shadow-md` | `popover` (`#2a2a2c`) | menus, popovers, toasts |
| 3 | `popover` + `shadow-lg`, com o fundo coberto por `#0d0d0e` a 60% | o mesmo | modais |

No escuro, sombra quase não aparece: quanto mais alto o nível, mais clara a superfície.

---

## Movimento

| Token | Duração | Uso |
|---|---|---|
| `--duration-fast` | 150 ms (`duration-150`) | hover, foco, troca de cor |
| `--duration-base` | 200 ms (`duration-200`) | entrar e sair: toast, menu, aba |
| `--duration-slow` | 300 ms (`duration-300`) | modal, painel de baixo |

Curva padrão: `ease-standard` (`cubic-bezier(0.2, 0, 0, 1)`): começa rápido e assenta devagar.
Quem pediu menos movimento no sistema operacional não vê animação de deslocamento: use as variantes
`motion-safe:` e `motion-reduce:` do Tailwind.

---

## Anel de foco

Todo elemento clicável mostra o foco quando a navegação é pelo teclado: um contorno de **2 px**, com **2
px de folga**, na cor `ring` (`#7a6200` no claro, `#e3b400` no escuro). No Tailwind:
`focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring`. Use a cor cheia: um
anel com transparência (ex.: `ring-ring/50`) perde o contraste de 3:1.

---

## Breakpoints (mobile first)

| Nome | Largura | O que é |
|---|---|---|
| base | **360 px** | a largura em que **toda tela é desenhada primeiro** (Galaxy S23, 360 × 780) |
| `md` | 768 px | tablet: a barra inferior vira cabeçalho, e os títulos crescem |
| `lg` | 1024 px | desktop pequeno: grades de 2 a 3 colunas |
| `xl` | 1280 px | desktop |
| frame | 1440 px | a largura do frame de desktop no Figma |

São os breakpoints padrão do Tailwind, sem configuração. **Regra:** em 360 px, nada transborda na
horizontal: nem tabela, nem rota comprida, nem ApiKey (quebre ou corte com reticências). O que cabe em
360 cabe em 390 e 430. No navegador, teste no modo de dispositivo com 360 × 780.

---

## Ícones

**Phosphor Icons** (`@phosphor-icons/react`, já no front).

| Situação | Peso | Tamanho |
|---|---|---|
| ícone na interface (botão, campo, aviso) | `regular` | 20 px (16 px dentro de texto pequeno e de selo) |
| item ativo da barra inferior e do cabeçalho | `fill` | 24 px |
| item inativo da barra | `regular` | 24 px |
| ilustração de estado vazio | `duotone` | 48 ou 64 px |

O ícone segue a cor do texto ao lado, e o dourado só vale no tema escuro. Ícone sozinho, sem texto, leva
um `aria-label`; ícone ao lado de texto leva `aria-hidden`.

---

## Cores de dados

### Métodos HTTP

Selo em `rounded-xs`, texto na fonte mono, em maiúsculas, `text-xs` e peso 600: o texto na cor do método
sobre o fundo `-subtle` dele.

| Método | Claro | Escuro | Classes |
|---|---|---|---|
| GET | `#175cd3` sobre `#eff8ff` | `#53b1fd` sobre `#0b2140` | `text-method-get bg-method-get-subtle` |
| POST | `#067647` sobre `#ecfdf3` | `#47cd89` sobre `#0c2a1c` | `text-method-post bg-method-post-subtle` |
| PUT | `#b54708` sobre `#fff6ed` | `#fb923c` sobre `#3a1d07` | `text-method-put bg-method-put-subtle` |
| PATCH | `#6941c6` sobre `#f4f3ff` | `#b692f6` sobre `#251a45` | `text-method-patch bg-method-patch-subtle` |
| DELETE | `#b42318` sobre `#fef3f2` | `#f97066` sobre `#3a1512` | `text-method-delete bg-method-delete-subtle` |

A cor nunca é a única pista: o nome do método está sempre escrito no selo.

### Status

| Selo | Cores | Ícone |
|---|---|---|
| Ativo | `text-success bg-success-subtle` | `CheckCircle` |
| Inativo | `text-muted-foreground bg-muted` | `MinusCircle` |
| Concessão (matriz cargo × rota) | `text-success` | `Check` |
| Sem concessão | `text-muted-foreground` | `Minus` |

---

## Voz e tom

O sistema fala com a pessoa como um colega técnico e gentil: direto, sem jargão e sem drama.

1. **"Você"**, nunca "o usuário".
2. **Frases curtas e na voz ativa.** "Informe o nome do projeto." e não "O nome do projeto deve ser
   informado."
3. **O erro diz o que houve e o que fazer.** "Não foi possível salvar o projeto. Tente de novo."
4. **Sem jargão na tela.** "Sua sessão expirou. Entre de novo." e não "401 Unauthorized"; "Não foi possível
   falar com o servidor." e não "Network error".
5. **Botões com verbo.** "Criar projeto", "Salvar", "Excluir", e não "OK" ou "Confirmar".
6. **Só a primeira letra em maiúscula** em títulos, botões e abas: "Novo projeto", e não "Novo Projeto".
7. **Sem exclamação e sem "Ops".** Sucesso é calmo: "Projeto criado."
8. **Uma palavra por ideia**, sempre a mesma (ver o glossário).

### Glossário

| Use | Não use |
|---|---|
| projeto, cargo, rota | role, route |
| conceder acesso, revogar acesso, concessão | grant, revoke |
| chave de API | token (para a ApiKey) |
| excluir | deletar, remover, apagar |
| salvar | gravar, persistir |
| entrar, sair, criar conta | login, logout, sign up (na interface) |
| trilha de auditoria | log |

### Do texto atual do front ao texto novo

O front da matéria de React tem bons exemplos e algumas inconsistências. Estas trocas entram quando cada
tela for refeita:

| Hoje | Com a voz da marca | Regra |
|---|---|---|
| "Ops!! Houve um erro ao criar o projeto..." | "Não foi possível criar o projeto." | 3, 7 |
| "Ocorreu um erro ao excluir o projeto. Tente novamente mais tarde." | "Não foi possível excluir o projeto. Tente de novo." | 3, 8 |
| "Deletando..." (no botão "Excluir") | "Excluindo..." | 8 |
| "Projeto editado com sucesso!" | "Projeto salvo." | 7 |
| "Novo Projeto" | "Novo projeto" | 6 |
| "Desculpe... Ocorreu um erro" | "Algo deu errado nesta página." | 3, 7 |
| "Informe o nome do projeto." | (fica) | 2 |
| "Não foi possível falar com o servidor. Tente de novo em instantes." | (fica) | 3, 4 |

---

## Nome, logo e favicon

**A definir**, numa sessão própria. O que falta decidir:

- **Nome:** se "Permission SaaS" fica como nome do produto ou se vira uma marca guarda-chuva para os
  próximos projetos.
- **Logo:** um símbolo e o nome escrito (*wordmark*), com as versões para fundo claro e escuro, o tamanho
  mínimo e a área de respiro em volta.
- **Favicon:** derivado do símbolo, em SVG e em PNG de 16, 32 e 180 px (o de 180 é o ícone de tela
  inicial do iPhone).

---

## Como usar

### No Figma

Pelo navegador e no plano gratuito do Figma, com o plugin **Tokens Studio for Figma** (gratuito). A
pasta [`figma/`](figma/) tem um arquivo por conjunto de tokens, gerado a partir do `tokens.json`:

| Arquivo | Vira no Figma |
|---|---|
| `primitive.json` | a coleção de variáveis `primitive` (as escalas de cor) |
| `light.json` | a coleção `light`: as cores semânticas do tema claro, que é o do mockup |
| `dark.json` | a coleção `dark` (opcional, ver o passo 9) |
| `base.json` | a coleção `base` (`espaco/4`, `espaco/8`... e `raio/padrao` = 2), os estilos de texto `texto/...` e os de efeito `sombra/...` |

No plano gratuito, **cada conjunto vira uma coleção com um modo só**: o Figma gratuito não deixa uma
coleção ter dois modos, e o Tokens Studio gratuito não exporta temas. Por isso o claro e o escuro são
coleções separadas, e não modos da mesma coleção.

1. **O arquivo.** Se for usar um kit do shadcn/ui da Figma Community, abra o kit e duplique-o para os
   seus rascunhos. Trabalhe dentro dessa cópia, porque os componentes do kit precisam estar no mesmo
   arquivo das telas.
2. **O plugin.** No menu de plugins, procure **Tokens Studio for Figma** e rode-o. O formato de tokens
   padrão dele (o *legacy*) é o dos arquivos da pasta: não mude essa configuração.
3. **Os conjuntos.** Crie quatro conjuntos (*token sets*) com estes nomes exatos: `primitive`, `light`,
   `dark` e `base`.
4. **O conteúdo.** Para cada conjunto: selecione-o, abra a visão JSON (o botão no alto, à direita, da
   lista de tokens), troque o `{}` pelo conteúdo inteiro do arquivo de mesmo nome e salve.
5. **Quais ficam ligados.** Deixe ligados `primitive`, `light` e `base`, e **desligue o `dark`**. O
   claro e o escuro têm os mesmos nomes (`background`, `primary`...), e com os dois ligados um apaga o
   outro.
6. **Exportar.** No menu de estilos e variáveis, na parte de baixo do plugin, escolha exportar para o
   Figma (no plano gratuito ele abre a exportação por conjuntos). Marque:
   - variáveis de **cor** e de **número**;
   - estilos de **tipografia** e de **efeito**;
   - **não** marque estilos de cor, porque as cores entram como variáveis.

   Confirme os conjuntos `primitive`, `light` e `base`. Os nomes do menu podem variar um pouco conforme
   a versão do plugin.
7. **Conferir.** Em *Local variables* aparecem as coleções `primitive`, `light` e `base`. Em *Text
   styles* aparecem `texto/display/celular`, `texto/corpo`... Em *Effect styles* aparecem
   `sombra/1-card`, `sombra/2-menu` e `sombra/3-modal`. Se o plugin acusar erro no peso da fonte, o
   gerador troca os números (`700`) pelos nomes (`Bold`).
8. **O kit.** Troque o raio dos componentes pela variável `raio/padrao` (2 px) e as cores pelas
   variáveis da coleção `light`. Se o kit já tiver variáveis com os nomes do shadcn/ui (`background`,
   `primary`...), também dá para só trocar os valores delas pelos da tabela "Cores semânticas".
9. **Tema escuro (opcional).** Desligue o `light`, ligue o `dark` e exporte só ele: vira a coleção
   `dark`.
10. **Desenhar.** Use os valores de `espaco` como *gap* e *padding* do Auto Layout e comece cada tela no
    frame de **360 px**.

### No código (bloco 2 da disciplina Full Stack)

1. Depois do `shadcn init` no `permission_saas_front`, troque o bloco de variáveis que ele gera no
   `index.css` pelo conteúdo do `tokens.css`.
2. Instale as fontes (`@fontsource-variable/nunito` e `@fontsource-variable/jetbrains-mono`) e importe as
   duas no `main.tsx`.
3. Em cada componente do shadcn/ui instalado, troque `rounded-md`, `rounded-lg` e `rounded-xl` por
   `rounded-xs`.
4. O tema escuro liga com a classe `dark` no `<html>`.
5. Use só as classes semânticas (`bg-primary`, `text-muted-foreground`) e nunca as primitivas
   (`bg-[#e3b400]`) nas telas.
