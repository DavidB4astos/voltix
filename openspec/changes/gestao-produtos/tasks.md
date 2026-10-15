## 1. Estruturas de Produto e VariacaoProduto no Xano

- [x] 1.1 Criar schemas Xano separados para Produto e VariacaoProduto com relações a Categoria, Marca e Produto, status e auditoria conforme o Domain Model; validar estruturas, relações e valores permitidos
- [x] 1.2 Configurar SKU obrigatório e globalmente único e validar preço positivo e quantidade não negativa; verificar unicidade incluindo variações inativas

## 2. Operações e autorização no backend

- [x] 2.1 Criar operações protegidas para listar produtos com categorias, marcas e variações e para criar produto com uma ou mais variações iniciais; validar referências ativas, atomicidade e ausência de produto incompleto em falhas
- [x] 2.2 Criar operações protegidas para editar e alterar status de Produto; verificar preservação de status durante edição, retenção das relações existentes com Categoria/Marca inativa e preservação de produtos com histórico comercial
- [x] 2.3 Criar operações protegidas para adicionar, editar e alterar status de VariacaoProduto usando o atributo nome ou descrição; verificar SKU, preço, quantidade não negativa, ao menos uma variação por produto e preservação de variações com histórico comercial
- [x] 2.4 Implementar upload opcional e associação de imagem principal no armazenamento nativo do Xano; verificar upload, atualização e falha sem substituir referência persistida
- [x] 2.5 Validar em cada operação sessão válida, usuário ATIVO e perfil ADMINISTRADOR antes de ler ou alterar dados; testar rejeição para FUNCIONARIO, sessão ausente/inválida e usuário inativo

## 3. Integração server-side no State Reflex

- [x] 3.1 Configurar destinos Xano por ambiente e implementar chamadas HTTP server-side para Produto, VariacaoProduto e imagem pelo State; verificar erro explícito para configuração ausente e ausência de credenciais ou destinos privados no código versionado
- [x] 3.2 Implementar no State listagem, criação inicial do agregado, edição, status e manutenção de variações com `_auth_token` somente no backend; testar sucesso, validação, autorização, falhas HTTP/rede e respostas inválidas sem sucesso simulado

## 4. Interface administrativa de Produtos

- [x] 4.1 Adicionar gestão de Produto à área interna, visível somente para ADMINISTRADOR, com seleção de Categoria/Marca ativas e exibição do status de associações já existentes; verificar que FUNCIONARIO não recebe controles
- [x] 4.2 Conectar formulários de Produto, variações e imagem opcional aos eventos do State; verificar campos, status, loading, mensagens, confirmação após reload e ausência de ação de exclusão definitiva

## 5. Verificação ponta a ponta e de escopo

- [x] 5.1 Executar testes automatizados, `python -m py_compile voltix/voltix.py`, `reflex compile`, validação dos XanoScript alterados e `git diff --check`; resolver somente falhas desta Change
- [ ] 5.2 Validar com ADMINISTRADOR ativo listagem, criação de Produto com variação, edição, upload de imagem opcional, status de Produto/variações e persistência após reload; confirmar SKU único e rejeição de referências inativas novas
- [ ] 5.3 Validar autorização backend negativa para FUNCIONARIO, sessão ausente/inválida e usuário inativo, e validar entradas inválidas de SKU, preço, quantidade e produto sem variação; confirmar ausência de persistência parcial
- [x] 5.4 Auditar escopo final para confirmar ausência de catálogo público, pesquisa, carrinho, pedidos, pagamentos, CRM, estoque/movimentações ou galeria; confirmar que nenhuma credencial ou token foi versionado

## Estado de validação do ambiente

- Publicação desbloqueada: o bloqueio anterior (`allow_push: false`) deixou de impedir a publicação; os endpoints desta Change foram publicados no workspace Xano e os guids retornados foram sincronizados nos 5 arquivos de endpoint versionados. As estruturas de dados e os destinos configurados já existem no ambiente.
- 5.2 parcialmente validado. Evidência fornecida (execução no painel pelo usuário): listagem administrativa com Categoria/Marca/variações, criação de Produto com variação inicial e edição de Produto com persistência após recarregar a página. Verificação ao vivo desta sessão (sem sessão válida) confirmou que `GET products` e `GET variations` rejeitam acesso não autenticado (HTTP 401). Ainda não validados: upload de imagem opcional, unicidade de SKU e rejeição de referência inativa nova — exigem sessão de ADMINISTRADOR ativo, indisponível no repositório.
- 5.3 parcialmente validado. Verificação ao vivo (Xano `live`, grupos `umWTO5yo`/`voltix-catalog-management`): requisições com sessão ausente e com token inválido são rejeitadas em `GET products`, `GET variations`, `GET categories`, `GET brands` (HTTP 401) e em `POST products`, `POST variations`, `PATCH products/{id}`, `PATCH variations/{id}` (HTTP 401 quando a entrada é válida; HTTP 400 de validação de entrada, antes de executar a stack, quando inválida). Nenhuma mutação foi persistida. Ainda não validados: rejeição para perfil FUNCIONARIO, usuário inativo e entradas inválidas de SKU, preço, quantidade e produto sem variação — exigem tokens de ADMINISTRADOR, FUNCIONARIO e usuário inativo, indisponíveis no repositório (`auth/login` só aceita UsuarioInterno pré-existente).
- Alteração de status validada ao vivo com registros temporários TMP-VALIDB: `PATCH variations/{id}` (HTTP 200, variação ID 4 → INATIVO) e `PATCH products/{id}` (HTTP 200, produto ID 4 → INATIVO); `GET` final confirmou ambos INATIVOS. Categoria e marca do produto foram preservadas, nenhum outro registro foi alterado e o produto TMP-VALID anterior não foi modificado. Um `HTTP 400` inicial (`ERROR_CODE_INPUT_ERROR`, `categoria_id` < 1) foi diagnosticado e resolvido enviando `categoria_id`/`marca_id` atuais no payload, sem alterar as associações.
- As validações automatizadas locais de implementação são evidência técnica, mas não substituem as verificações ponta a ponta exigidas por essas tarefas.
