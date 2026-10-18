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
- [x] 5.2 Validar com ADMINISTRADOR ativo listagem, criação de Produto com variação, edição, upload de imagem opcional, status de Produto/variações e persistência após reload; confirmar SKU único e rejeição de referências inativas novas. **Concluída com ressalva explícita de ambiente:** todos os critérios executáveis foram validados ao vivo (ver "Estado de validação do ambiente" e o anexo `evidencias-5.2-5.3.md`); o upload de imagem opcional não é validável na instância Xano Free (HTTP 403) e permanece apenas como limitação conhecida de ambiente, **não declarado validado**.
- [x] 5.3 Validar autorização backend negativa para FUNCIONARIO, sessão ausente/inválida e usuário inativo, e validar entradas inválidas de SKU, preço, quantidade e produto sem variação; confirmar ausência de persistência parcial
- [x] 5.4 Auditar escopo final para confirmar ausência de catálogo público, pesquisa, carrinho, pedidos, pagamentos, CRM, estoque/movimentações ou galeria; confirmar que nenhuma credencial ou token foi versionado

## Estado de validação do ambiente

- Publicação desbloqueada: o bloqueio anterior (`allow_push: false`) deixou de impedir a publicação; os endpoints desta Change foram publicados no workspace Xano e os guids retornados foram sincronizados nos 5 arquivos de endpoint versionados. As estruturas de dados e os destinos configurados já existem no ambiente.
- Correção F1 publicada (2026-10-18): os endpoints versionados `products/{product_id} PATCH` (guid `YJOD1IemBD5iLEfVD1EIPRpi5Vc`) e `variations/{variation_id} PATCH` (guid `MQCNgUmw-9fx-AScrC5HGOTBO2Y`) tiveram removido o filtro `min:1` dos ids opcionais (`categoria_id?`/`marca_id?`/`produto_id?`), com pré-condições passando a tratar id ausente/não positivo como "não informado"; a validação de referência (db.get + precondition de referência ATIVA) e a autorização ADMINISTRADOR+ATIVO foram preservadas. `workspace push --dry-run` confirmou alteração apenas desses 2 endpoints; push escopado concluído; `workspace pull` confirmou o conteúdo no servidor com referências `db.*` íntegras.
- 5.2 validado nos critérios executáveis ao vivo (ADMINISTRADOR ativo): listagem, criação de Produto com variação, edição, persistência após reload, SKU único (`400 "A variation with this SKU already exists."`), rejeição de referência inativa nova (`400 "An active category is required."`), alternância de status de Produto e variação (`PATCH /products/{id}` e `PATCH /variations/{id}` apenas com `{"status":...}` → 200) e demais negações de referência (`400`) e autorização (`401`). Pendência de ambiente: o upload de imagem opcional não é validável na instância Xano Free → HTTP 403 (`ERROR_CODE_ACCESS_DENIED`, "Not supported. Please upgrade your Xano instance."); não é falha de implementação e não é marcado como validado.
- 5.3 validado ao vivo: sessão ausente (`401 "Unauthorized - Authentication Required"`) e token inválido (`401 "Invalid token."`); FUNCIONARIO ativo (`403 "Administrator access is required."`) e usuário INATIVO (`403 "Internal access is not available."` via `auth/me`, isolando o status); entradas inválidas de SKU/preço/quantidade (`400 "Each variation requires a unique SKU, positive price, and non-negative quantity."`), produto sem variação (`[]` → `400 "At least one product variation is required."`, parâmetro ausente → `400 "Missing param: variacoes"`); ausência de persistência parcial confirmada.
- Estado dos dados preservado: produto temporário id=5 e variação temporária id=5 inativados; categoria 2 restaurada para ATIVO; produtos 1-4 e variações 1-4 inalterados. Nenhum token/senha versionado (tokens apenas em memória, limpos ao final).
- As validações automatizadas locais de implementação são evidência técnica, mas não substituem as verificações ponta a ponta exigidas por essas tarefas.
- Limitação conhecida (fora de escopo implementar nesta Change): o upload de imagem principal depende do recurso de armazenamento/upload da instância Xano, indisponível no plano Free (HTTP 403, `ERROR_CODE_ACCESS_DENIED`, "Not supported. Please upgrade your Xano instance."). Enquanto o ambiente permanecer Free, esse critério permanece não validado e não é declarado funcional. A solução futura dependerá de plano pago ou de armazenamento externo gratuito compatível, decisão a ser avaliada em mudança própria. As demais funcionalidades de Produto e variação — inclusive a imagem principal opcional ausente — permanecem válidas sem depender do upload.
