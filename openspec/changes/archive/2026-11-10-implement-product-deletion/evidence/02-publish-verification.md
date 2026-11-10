# Publicação e verificação remota — exclusão de Produto

Data: 10/11/2026

## Dry-run

Comando restrito a
`api/product_management/product/product_id_DELETE.xs`:

- 1 de 116 arquivos incluído.
- Preview: apenas `CREATE query products/{product_id} DELETE`.
- Nenhuma alteração de tabela, dado ou outro endpoint.

## Publicação

Publicação restrita ao mesmo arquivo, com autorização explícita do usuário:

- Documento publicado no workspace 147981.
- GUID atribuído: `llIS7uIUZNJLK43ouTICR_QU5zU`.
- Avisos de referências não resolvidas são heurísticos do push parcial; as
  tabelas `user`, `produto`, `variacao_produto`, `item_pedido` e
  `item_carrinho` já existem no workspace.

## Pull independente

O pull independente gravou
`api/product_management/products/product_id_DELETE.xs` e confirmou:

- `auth = "user"` e guarda de `ADMINISTRADOR` ativo antes de `db.get produto`.
- `notfound` para produto ausente.
- `db.transaction` com consulta de variações.
- Consultas em `item_pedido` e `item_carrinho` por `variacao_produto_id`.
- `badrequest` com mensagem de histórico comercial e inativação.
- `db.del variacao_produto` por `produto_id` e `db.del produto` por `id`.
- Resposta `{id, deleted: true}` e GUID preservado.

As diferenças em relação ao arquivo local são apenas de formatação de
whitespace e da representação do objeto de resposta.

## Verificação remota somente leitura

- `DELETE products/{product_id}` sem sessão respondeu **HTTP 401**.
- Nenhuma exclusão real foi executada.
- Nenhuma escrita em Produto, Variação, Pedido, Carrinho ou Pagamento foi
  realizada durante a verificação.
