### **Uso de IAs: Sinal Amarelo 🟡**

Neste trabalho, os alunos têm permissão para usar ferramentas baseadas em IA nas seguintes tarefas: **esclarecimento de conceitos, sugestões de arquitetura e organização do código, geração ou complementação de trechos pontuais de código, identificação e correção de erros, refatoração, criação e revisão de componentes React, elaboração de dados para testes, integração entre frontend e backend, diagnóstico de problemas relacionados ao consumo de APIs REST, elaboração de testes e documentação, configuração do ambiente, Docker e processos de deploy**. Todas as fontes, incluindo ferramentas de IA, devem ser devidamente citadas. O uso de IA de forma inconsistente com os parâmetros acima será considerado má conduta acadêmica e estará sujeito à aplicação do código disciplinar. Observe que os resultados da IA podem ser tendenciosos e imprecisos. É responsabilidade do aluno garantir que as informações usadas da IA sejam precisas. Aprender como usar ferramentas baseadas em IA de maneira cuidadosa e estratégica contribui para o desenvolvimento das habilidades, refinamento de seu trabalho e prepara o aluno para sua futura carreira.

---

Este projeto foi pensado para você aprender, na prática, como construir uma aplicação full stack, integrando Back-end (Spring Boot) e Front-end (React). O objetivo é que você compreenda a comunicação entre as camadas e adote boas práticas de desenvolvimento em cada etapa do processo.

Para facilitar o seu aprendizado, uma API já será fornecida. Ela servirá como ponto de partida para o backend, facilitando a integração com o frontend. Assim, você poderá focar na troca de dados, na construção das funcionalidades e na aplicação das melhores práticas que vai aprender ao longo da disciplina.

**API Carros:** https://github.com/leoinfnet/trabalho_final_react_noite

Durante o projeto, você terá a chance de:

- **Entender a comunicação entre camadas:** descubra como conectar o frontend ao backend de forma eficiente, utilizando APIs RESTful.
- **Aplicar boas práticas de integração:** aprenda a lidar com segurança, autenticação, controle de erros e organização do código.
- **Desenvolver uma aplicação completa:** passe por todas as etapas, desde a configuração do ambiente até a implantação do sistema.
- **Construir funcionalidades avançadas:** trabalhe com operações CRUD, segurança JWT e deploy com Docker.

---

### **Etapas**

O desenvolvimento do projeto será dividido em cinco etapas principais obrigatórias e uma opcional, com foco na integração e aprimoramento do sistema em cada fase. Essas etapas serão dedicadas ao desenvolvimento contínuo, incluindo a implementação de funcionalidades, segurança, e melhorias de código. Ao final do projeto, você terá uma aplicação web full-stack completamente funcional, integrada e segura.

| Etapa | Título | Principais tópicos |
|---|---|---|
| [Etapa 0](ETAPA0.md) | Integração do Frontend e Backend (preparação) | ambiente Spring Boot + React, backend com serviço RESTful básico, frontend inicial consumindo esse serviço, mockup da interface |
| [Etapa 1](ETAPA1.md) | Integração do Frontend e Backend | chamadas às APIs RESTful, consumo correto dos dados, validação de dados e tratamento de erros nas requisições |
| [Etapa 2](ETAPA2.md) | Criando e Consultando Dados com CRUD | Create e Read no backend, integrados ao frontend |
| [Etapa 3](ETAPA3.md) | Atualizando e Excluindo Dados com CRUD | Update e Delete no backend, integrados ao frontend, testes e validação das operações |
| [Etapa 4](ETAPA4.md) | Segurança da Aplicação | comunicação segura, autenticação e autorização, validação da segurança |
| [Etapa 5](ETAPA5.md) | Melhorias e Segurança Avançada | refatoração, APIs REST seguras, logout seguro, CRUD com autenticação JWT |
| [Etapa 6](ETAPA6.md) | Implantação, Containers e Deploy do Frontend (**opcional**) | Docker, deploy do backend (AWS, se API própria), deploy do frontend (ex.: Netlify) |

---

### **Instruções para Entrega do Projeto**

Para a entrega do projeto, você precisará seguir os passos abaixo, garantindo que todos os requisitos e funcionalidades solicitadas nas etapas sejam implementadas corretamente. A entrega será avaliada com base no cumprimento das etapas de desenvolvimento, bem como na qualidade e na organização do código.

1. **Submissão do Código Fonte:**

   O código completo do projeto, incluindo backend e frontend, precisará ser enviado por meio de um repositório GitHub (ou outra plataforma de versionamento acordada). Certifique-se de que:

   - O código esteja bem estruturado, com pastas e arquivos organizados de maneira clara.
   - O código esteja comentado adequadamente, especialmente para trechos mais complexos.
   - O repositório esteja público ou acessível para a avaliação.

2. **Documentação do Projeto:**

   Junto com o código fonte, você precisa fornecer um arquivo de documentação explicando as seguintes informações:

   - **Visão geral do projeto:** Explique o objetivo do seu projeto, as tecnologias utilizadas e os principais desafios enfrentados.
   - **Passos para rodar a aplicação localmente:** Inclua instruções detalhadas de como rodar tanto o backend quanto o frontend em um ambiente de desenvolvimento local, incluindo as dependências necessárias, configuração de variáveis de ambiente (se houver) e como executar a aplicação.
   - **Instruções de deploy:** Caso tenha realizado o deploy do frontend e/ou backend, forneça as instruções necessárias para acessar a aplicação online (se aplicável) e qualquer outra informações relevante para a execução em produção.
   - **Testes:** Se possível, descreva os testes realizados para garantir a qualidade da aplicação, especialmente os testes automatizados, e explique como executá-los.

3. **Demonstrativo de Funcionamento:**

   Caso o deploy da aplicação tenha sido realizado em uma plataforma como Netlify ou AWS, forneça os links para que a aplicação possa ser acessada e testada. Caso o projeto não tenha sido implantado, garanta que a aplicação esteja funcional localmente e forneça os detalhes para que o avaliador possa testar o funcionamento sem dificuldades.

4. **Entrega de Arquivos Adicionais (se houver):**

   Se você tiver utilizado Docker ou outras tecnologias de conteinerização, inclua os arquivos de configuração necessários (como Dockerfile, docker-compose.yml, etc.) e explique como executar o ambiente containerizado localmente.

5. **Formato de entrega:**

   - O trabalho final deve ser entregue em formato PDF contendo: Link para o GITHUB ou outro versionador de código (Não será aceito em outro formato, como zip, por exemplo).
   - No arquivo PDF você deve deixar claro onde em cada parte do código está implementada a funcionalidade solicitada. Exemplo:
     - Funcionalidade de Login: link para o código no repositório onde está a funcionalidade (Pode ser GIST).
   - No PDF deve conter prints de todas as funcionalidades do código rodando.
   - Certifique-se de que todos os arquivos essenciais estejam presentes e acessíveis para o avaliador.
   - Caso utilize outras plataformas ou recursos externos (como AWS, Netlify, Docker, etc.), forneça os links de acesso junto com a documentação.

**O projeto que não seguir as regras acima não obterá conceito para aprovação.**

Assim que terminar, salve o seu arquivo PDF e poste no Moodle. Utilize o seu nome para nomear o arquivo, identificando também a disciplina no seguinte formato: “nomedoaluno_nomedadisciplina_pd.PDF”.

---

### **Status da entrega**

| | |
|---|---|
| Abertura para envios | segunda, 14 dez 2026, 07:00 |
| Número da tentativa | Esta é a tentativa 1 (2 tentativas permitidas). |
| Status da entrega | Nenhuma tentativa |
| Status da avaliação | Não avaliado |
| Data de entrega | segunda, 14 dez 2026, 23:59 |
| Tempo restante | 28 dias 3 horas |

---

### **Rubrica**

Template de Rubrica para ser utilizado com a extensão Rubricator

1. **Configurar e operar um ambiente de desenvolvimento Spring**

   O aluno configurou o ambiente de desenvolvimento Spring Boot e React de forma eficiente, garantindo integração contínua e fluidez no desenvolvimento?

   - Não demonstrou o item de rubrica
   - Demonstrou o item de rubrica

2. **Configurar e operar um ambiente de desenvolvimento Spring**

   O aluno utilizou o serviço RESTful fornecido com precisão, implementando validações robustas para garantir consistência e segurança nas operações?

   - Não demonstrou o item de rubrica
   - Demonstrou o item de rubrica

3. **Configurar e operar um ambiente de desenvolvimento Spring**

   O aluno desenvolveu um frontend inicial funcional e responsivo, consumindo corretamente os dados do serviço RESTful e apresentando-os de maneira clara e intuitiva?

   - Não demonstrou o item de rubrica
   - Demonstrou o item de rubrica

4. **Configurar e operar um ambiente de desenvolvimento Spring**

   O aluno elaborou um mockup detalhado e alinhado às melhores práticas de design de interface, servindo como base sólida para as etapas subsequentes do projeto?

   - Não demonstrou o item de rubrica
   - Demonstrou o item de rubrica

5. **Implementar funcionalidades CRUD**

   O aluno implementou as funcionalidades de criação e consulta no backend com excelência, utilizando práticas avançadas de programação e validação de dados?

   - Não demonstrou o item de rubrica
   - Demonstrou o item de rubrica

6. **Implementar funcionalidades CRUD**

   O aluno integrou a criação e consulta do backend ao frontend de maneira fluida, assegurando a sincronia dos dados e a correta manipulação no frontend?

   - Não demonstrou o item de rubrica
   - Demonstrou o item de rubrica

7. **Implementar funcionalidades CRUD**

   O aluno implementou as funcionalidades de atualização e exclusão no backend com testes abrangentes, garantindo a consistência e robustez das operações?

   - Não demonstrou o item de rubrica
   - Demonstrou o item de rubrica

8. **Implementar funcionalidades CRUD**

   O aluno integrou as funcionalidades de atualização e exclusão do backend ao frontend, assegurando uma experiência de usuário intuitiva e funcional?

   - Não demonstrou o item de rubrica
   - Demonstrou o item de rubrica

9. **Aprimorar a interface para exportação de dados**

   O aluno implementou autenticação avançada utilizando JWT, protegendo de forma exemplar a funcionalidade de exportação de dados?

   - Não demonstrou o item de rubrica
   - Demonstrou o item de rubrica

10. **Aprimorar a interface para exportação de dados**

    O aluno garantiu a comunicação segura entre cliente e servidor na funcionalidade de exportação de dados, utilizando protocolos de segurança e criptografia adequados?

    - Não demonstrou o item de rubrica
    - Demonstrou o item de rubrica

11. **Aprimorar a interface para exportação de dados**

    O aluno validou a segurança da funcionalidade de exportação, realizando testes detalhados para prevenir vulnerabilidades?

    - Não demonstrou o item de rubrica
    - Demonstrou o item de rubrica

12. **Aprimorar a interface para exportação de dados**

    O aluno integrou a autenticação JWT na exportação de dados, garantindo proteção total contra acessos não autorizados?

    - Não demonstrou o item de rubrica
    - Demonstrou o item de rubrica

13. **Garantir a qualidade, segurança e disponibilidade da aplicação**

    O aluno realizou refatorações no código, eliminando duplicações e implementando padrões de design, resultando em uma aplicação eficiente e escalável?

    - Não demonstrou o item de rubrica
    - Demonstrou o item de rubrica

14. **Garantir a qualidade, segurança e disponibilidade da aplicação**

    O aluno desenvolveu APIs REST com mecanismos avançados de segurança, protegendo todas as trocas de informações da aplicação?

    - Não demonstrou o item de rubrica
    - Demonstrou o item de rubrica

15. **Garantir a qualidade, segurança e disponibilidade da aplicação**

    O aluno implementou a funcionalidade de logout seguro com alto nível de confiabilidade, protegendo dados sensíveis dos usuários?

    - Não demonstrou o item de rubrica
    - Demonstrou o item de rubrica

16. **Garantir a qualidade, segurança e disponibilidade da aplicação**

    O aluno validou de forma abrangente a segurança e a disponibilidade das operações CRUD, garantindo consistência e resiliência do sistema?

    - Não demonstrou o item de rubrica
    - Demonstrou o item de rubrica
