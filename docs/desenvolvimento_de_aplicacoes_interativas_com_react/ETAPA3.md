Etapa 3: **Integração com APIs externas e navegação em uma aplicação**

*Feature III do enunciado.*

Nesta feature, abordaremos a integração com APIs externas e a implementação de navegação entre diferentes páginas da aplicação, utilizando componentes de terceiros e técnicas para garantir uma experiência do usuário suave. As principais atividades a serem realizadas incluem:

1. **Integração com APIs externas e manipulação de dados**

   - Utilizar Fetch API ou Axios para realizar requisições GET e POST, permitindo operações de criar, ler, atualizar e deletar dados na API.
   - Gerenciar possíveis erros nas requisições com tratamento de erros, como exibir alertas em caso de falha, assegurando que o usuário seja informado de problemas nas operações.
   - Integrar uma API real (ex.: OpenWeather para uma aplicação escolar ou GitHub para uma academia) e exibir os dados de forma dinâmica, utilizando React Query para gerenciar o cache e permitir atualizações automáticas, melhorando a eficiência na manipulação de dados.

2. **Navegação entre diferentes páginas e uso de componentes de terceiros**

   - Configurar rotas básicas para a navegação entre diferentes páginas da aplicação (ex.: página de lista, página de detalhes, página de edição) utilizando React Router, garantindo que o usuário possa navegar facilmente pelas diferentes funcionalidades.
   - Implementar rotas privadas para proteger determinadas áreas da aplicação, como o acesso ao painel administrativo, garantindo que somente usuários autorizados possam acessar informações sensíveis.
   - Utilizar componentes de terceiros (ex.: AG Grid para exibição de dados em tabelas ou Material UI para estilização da interface) para aprimorar a estética e a funcionalidade da aplicação.
   - Tratar race conditions com `Promise.race` e utilizar `AbortController` para cancelar requisições ao lidar com dados dinâmicos, assegurando que a aplicação permaneça responsiva e livre de conflitos em operações assíncronas.

Essa abordagem permitirá a construção de uma aplicação CRUD interativa, que não apenas manipula dados de forma eficiente, mas também oferece uma experiência de usuário fluida através de navegação intuitiva e uso de componentes de alta qualidade.
