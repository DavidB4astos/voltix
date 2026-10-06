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

- 5.2 e 5.3 permanecem pendentes: o E2E real não foi executado porque o workspace Xano v1 está com `allow_push: false`, bloqueando externamente a publicação dos endpoints desta Change. Nenhum resultado de E2E é declarado.
- As validações automatizadas locais de implementação são evidência técnica, mas não substituem as verificações ponta a ponta exigidas por essas tarefas.
