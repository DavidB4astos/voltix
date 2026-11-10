## Why

O painel de produtos permite criar, editar e inativar produtos, mas não permite remover um
cadastro feito por engano. Itens de teste, duplicidades e produtos criados antes de qualquer
vínculo comercial permanecem para sempre na listagem, porque a única saída é a inativação.
A exclusão de Produto é o próximo item aprovado da fila de produto (item 10), limitada a
produtos sem uso comercial para não quebrar histórico de Pedido nem carrinhos de Cliente.

## What Changes

- Criar o endpoint Xano `DELETE products/{product_id}` no grupo já publicado
  `Product Management`, com `auth = "user"` e autorização exclusiva de `ADMINISTRADOR`
  ativo, verificada antes de ler qualquer registro de negócio.
- Responder `404` quando o produto não existir.
- Bloquear a exclusão com `400` quando qualquer `ItemPedido` ou `ItemCarrinho` referenciar
  uma variação do produto, orientando a usar a inativação. Não existe `409` no conjunto
  fechado de `error_type` do XanoScript.
- Sem referências comerciais, excluir todas as variações do produto e o próprio produto em
  uma única transação. O produto não é inativado; ele é removido definitivamente.
- Não remover arquivo de imagem armazenado, não alterar Pedido, Pagamento, Carrinho,
  Categoria ou Marca e não excluir registros de outros produtos.
- Adicionar ao painel de produtos a ação "Excluir produto", visível apenas para
  `ADMINISTRADOR`, com confirmação explícita em dois passos e mensagens observáveis para
  sucesso, bloqueio por histórico, autorização, produto inexistente e falha de rede.
- Reutilizar `XANO_PRODUCTS_URL_ENV` com o método `DELETE`, sem criar variável de ambiente.

## Capabilities

### New Capabilities

Nenhuma capability nova.

### Modified Capabilities

- `product-management`: acrescenta a exclusão definitiva de produto sem uso comercial e a
  ação correspondente no painel, preservando a regra existente de que produto ou variação
  com histórico comercial é mantido e inativado.

## Impact

- Xano: novo arquivo `xano/api/product_management/product/product_id_DELETE.xs`; publicação
  restrita ao endpoint, pendente de autorização explícita.
- Código: `voltix/voltix.py` (Estado, handlers e cartões de produto). Nenhuma variável de
  ambiente nova.
- Testes: contrato, handler, mensagens e checagens do XanoScript em
  `tests/test_product_management.py`.
- Specs: delta em `product-management`.
- Docs: `docs/roadmap-changes.md` e `docs/AI_AGENT_HANDOFF.md` após a verificação.
- Fora do escopo: exclusão de produto com histórico comercial, exclusão de Categoria ou
  Marca, limpeza de itens de carrinho, remoção de arquivo de imagem, exclusão em massa,
  restauração/desfazer, alteração de checkout, pedidos ou pagamentos e qualquer alteração
  de schema Xano.
