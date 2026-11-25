# Auditoria de código

A auditoria que guia a refatoração da disciplina (decisão 11 do [plano](PLAN.md)). A IA revisa a API
(`permission_saas_api`) e o front (`permission_saas_front`) e entrega cada achado com o motivo e o
esforço; o Jairo escolhe o que entra e quando.

- **1ª passada, bugs (18/11):** feita com o `/code-review` do Claude Code sobre os dois repositórios. Os
  achados mais graves foram conferidos no código antes de entrar aqui.
- **2ª passada, desenho do código:** pendente. Olha o que o `/code-review` não cobre: duplicação, nomes,
  código morto da disciplina de React e cobertura de testes.

**Escolha do Jairo (18/11):** entram todos. Os que se ligam à disciplina vão para o bloco em que aquele
código já vai ser mexido; os outros ficam numa fila e são corrigidos quando sobrar tempo, já que o
cronograma está três dias adiantado. Quem faz cada um é decidido quando o item entrar; o que for novo
para o Jairo fica com ele.

Esforço: **P** até 30 min · **M** de 1 a 2 h · **G** meio dia ou mais.

## Nos blocos da disciplina

### Bloco 2: CRUD, testes do CRUD e fundação do front

| # | Achado | Por que importa | Onde | Esforço | Feito |
|---|---|---|---|---|---|
| A01 | O handler genérico (`@ExceptionHandler(Exception.class)`) pega as exceções de erro do cliente do próprio Spring MVC e responde 500, com stack trace no log | UUID inválido no path, método não suportado, URL inexistente, tipo de conteúdo errado no import do CSV (o `API.md` promete 400) e violação de constraint viram 500. Os testes com MockMvc do bloco esbarram nisso | api: `shared/api/GlobalExceptionHandler` (estender `ResponseEntityExceptionHandler` ou tratar essas exceções antes do genérico) | M | [ ] |
| A02 | O Flyway roda com `validate-on-migrate: false` | Uma migration já aplicada pode ser editada sem aviso: o banco local fica com a versão antiga, e o do CI e do Testcontainers com a nova. **Antes de mudar, ver se foi desligado de propósito na divisão em repositórios** (há também `ignore-migration-patterns`) | api: `application.yml` | P | [ ] |
| A03 | O `<form>` do projeto não tem `noValidate`, contra a regra do `docs/ARCHITECTURE.md` do front | O balão nativo do navegador (para `1.5` ou `e` no limite de cargos) aparece antes e impede a nossa mensagem em português. A reescrita com React Hook Form precisa manter o `noValidate` | front: `ProjectForm.tsx` | P | [ ] |
| A04 | O `NotificationProvider` usa `crypto.randomUUID()`, que só existe em HTTPS ou em `localhost` | Pelo IP da rede (o front do Docker aberto no celular), toda notificação lança erro, e a mutação aparece como falha mesmo quando o servidor salvou. Some quando o Sonner substituir o provider; **até lá, no bloco 1, testar pelo `localhost`**. Ao corrigir, tirar o aviso do `docs/RUNNING.md` | front: `NotificationProvider.tsx` | P | [ ] |
| A18 | O Axios não tem timeout por padrão, e o `httpClient` atual desiste em 5 s (achado na revisão da parte A do bloco 1, 25/11) | Sem o `timeout` na instância do Axios, uma API lenta deixa a tela carregando sem fim. Com a API parada, o nginx já responde 504 em 5 s, mas uma API que aceita a conexão e demora não é coberta por ele | front: a instância do Axios que substitui o `httpClient` | P | [ ] |

### Bloco 3: JWT no back-end e regra de dono

| # | Achado | Por que importa | Onde | Esforço | Feito |
|---|---|---|---|---|---|
| A05 | Criar projeto não confere se o `clientId` existe | Um UUID qualquer (ou o `VITE_DEV_CLIENT_ID` depois de zerar o banco) cria um projeto de um cliente que não existe. Com a regra de dono, o `clientId` passa a vir do token, e o caso some; o teste de segurança deve cobrir isso | api: `CreateProjectUseCase` | P | [ ] |
| A06 | O e-mail do cliente diferencia maiúsculas de minúsculas | `Maria@x.com` e `maria@x.com` viram duas contas, o que pesa no login por e-mail. Normalizar na entrada e garantir a unicidade sem diferenciar maiúsculas (migration) | api: `RegisterClientUseCase`, tabela de clientes | M | [ ] |
| A07 | `RegisterClientRequest.rawPassword` não tem `@NotBlank` | Uma senha vazia chega ao caso de uso | api: `RegisterClientRequest` | P | [ ] |
| A08 | A `ApiKey` não é conferida contra o dono do projeto (limitação já registrada no `DOMAIN.md` da API) | Na validação de permissão, uma chave de um cliente consulta o projeto de outro. É a mesma regra de dono do bloco, no outro esquema de autenticação | api: validação de permissão | M | [ ] |

### Bloco 4: JWT no front e logout seguro

| # | Achado | Por que importa | Onde | Esforço | Feito |
|---|---|---|---|---|---|
| A09 | O logout não limpa o cache do React Query | Com os projetos por dono, quem entra em seguida na mesma aba vê por um instante os projetos de quem saiu. `queryClient.clear()` no logout | front: `AppLayout.tsx` (o logout vai para o Zustand) | P | [ ] |

### Bloco 5: exportar, importar e refatorar

| # | Achado | Por que importa | Onde | Esforço | Feito |
|---|---|---|---|---|---|
| A10 | A normalização do path (barra no começo, sem barra no fim) só existe no import do CSV | `/orders/` cadastrado pela API e `orders` vindo do CSV viram duas rotas, e a concessão de uma não vale para a outra. O import em JSON também cria rotas, então a regra vai para o domínio (`Route` e `Project.addRoute`) e para a validação | api: `RouteImportProcessor`, domínio de rotas | M | [ ] |
| A11 | O import do CSV não confere o tamanho dos campos (nome ≤ 80, path e descrição ≤ 255) | Um nome longo derruba o lote inteiro no commit: o passo falha, e as linhas seguintes nem são lidas. O import em JSON precisa da mesma validação | api: `RouteImportProcessor` | P | [ ] |
| A12 | O projeto não tem trava otimista (`@Version`) | Dois "adicionar cargo" ao mesmo tempo passam pela regra do limite e gravam cargos além do máximo; nada no banco impede | api: `ProjectJpaEntity` (migration + `@Version`, conflito vira 409) | M | [ ] |

## Fila para os dias de folga

Fora do tema da disciplina (cobrança, integração com o audit-service, desempenho). Entram quando sobrar
tempo; o que não entrar vai para os trabalhos futuros do relatório.

| # | Achado | Por que importa | Onde | Esforço | Feito |
|---|---|---|---|---|---|
| A13 | Cadastrar um plano com nome repetido dá 500 | O `PlanRepository.findByName` existe e nunca é usado; deveria ser um 409 de domínio. O nome também não tem `@Size` | api: `RegisterPlanUseCase` | P | [ ] |
| A14 | Pagamento recusado: o `throw` dentro do `@Transactional` desfaz o registro da assinatura recusada | O código quer guardar a tentativa recusada, mas o rollback apaga. Hoje não aparece porque o simulador sempre aprova | api: `SubscribeToPlanUseCase` | P | [ ] |
| A15 | Qualquer erro do Feign, inclusive 4xx e falha de leitura da resposta, vira "audit-service fora do ar" (503) | Se o contrato copiado (ADR-008) divergir, a resposta aponta uma queda que não existe | api: `AuditTrailClientAdapter` | P | [ ] |
| A16 | A rota com parâmetro (`orders/{id}`, o próprio exemplo do `API.md`) nunca bate com o path real (`/orders/42`) | A comparação é por texto literal; a concessão só vale se quem chama mandar `/orders/{id}`. Pede casamento por padrão | api: `CheckRouteAccessUseCase` | G | [ ] |
| A17 | Cada `/validate-permission` carrega o projeto inteiro (cargos, rotas e concessões), além do bcrypt contra cada chave ativa (limitação do `DOMAIN.md`) | Com 50 cargos, são cerca de 53 SELECTs por validação, no caminho mais usado do produto. Uma consulta direta e uma busca da chave em O(1) resolvem | api: `CheckRouteAccessUseCase`, busca da `ApiKey` | G | [ ] |
