# Verificação local — exclusão de Produto

Data: 10/11/2026

## Escopo verificado

- `DELETE products/{product_id}` com `auth = "user"` e autorização de
  `ADMINISTRADOR` ativo antes de ler o produto.
- `404` para produto inexistente.
- Verificação de referências em `item_pedido` e `item_carrinho` por
  `variacao_produto_id`, dentro de `db.transaction`.
- `400` (`badrequest`) quando houver histórico comercial, com orientação de
  inativação; não existe `409` no conjunto fechado de `error_type`.
- Sem referências, `db.del variacao_produto` por `produto_id` e `db.del produto`
  por `id` na mesma transação.
- Resposta limitada a `{id, deleted: true}`.
- Painel de produtos com "Excluir produto" e confirmação em dois passos,
  visível apenas para `ADMINISTRADOR`.
- Limpeza do formulário de edição, da variação e do ajuste de estoque quando o
  produto excluído estava selecionado.
- Mensagens para `400` de histórico, `404`, `401`, `403` e rede.

## Resultados

| Verificação | Resultado |
|---|---|
| Testes focados `tests.test_product_management` | 32 aprovados |
| Suíte completa | 362 aprovados |
| `openspec validate implement-product-deletion --strict` | válido |
| `openspec validate --all --strict` | 27 itens aprovados (26 specs + change) |
| `reflex compile` | sucesso |
| `git diff --check` | limpo |
| `reflex.lock/*` | restaurado; nenhuma migração de dependências |

Nenhuma exclusão real foi executada e nenhum dado de Cliente, Pedido ou
Carrinho foi alterado.
