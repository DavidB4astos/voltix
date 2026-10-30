## Context
Produto mantém informações e associações; SKU, preço e quantidade pertencem à variação. Administrador é o único perfil autorizado. Imagem opcional e limitação histórica de upload continuam vigentes.
## Decisions
- Manter funções locais product_form e variation_form e guard administrativo, com todos os eventos existentes.
- Formulários com labels persistentes, seção de identificação, associações e variação inicial na criação; imagem opcional na edição com feedback existente. Não adicionar obrigatoriedade ou mudar validadores.
- Layout desktop com formulário e lista separados; variação selecionada aparece junto ao editor. Não criar seleção que faça nova requisição.
- Lista preserva descrição, especificações, associações inativas, status e presença de imagem. Variações em tabela semântica; ações existentes nomeadas e desabilitadas durante loading.
- CSS vx-products escopado. Scroll da tabela quando necessário, sem overflow da página. Sem thumbnails inventadas, indicadores de vendas ou estoque calculado.
## Verification
Suite existente e compilação completa. Comparar AST de State antes/depois. Conferir criação, edição, adicionar/editar variação, loading/erro e conteúdo com fixtures isoladas, incluindo associação inativa e ausência de imagem. Não executar mutações no Xano. Registrar limites, validar strict, consolidar spec e arquivar somente após verificação.
