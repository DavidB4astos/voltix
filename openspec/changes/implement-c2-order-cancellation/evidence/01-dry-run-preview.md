# 01 — C2: dry-run e verificação local (09/11/2026)

## Escopo do preview

Comando (somente preview, sem escrita):

```
xano workspace push -d xano --dry-run \
  -i "function/voltix_orders/cancel_order.xs" \
  -i "api/customer/order_id_cancel_POST.xs" \
  -i "api/internal_orders/*.xs"
```

Saída:

```
Include: function/voltix_orders/cancel_order.xs, api/customer/order_id_cancel_POST.xs, api/internal_orders/*.xs
Matched: 4 of 101 files

=== Push Preview: workspace 147981 ===
  instance: x8ki-letl-twmt.n7.xano.io  |  workspace: David's Workspace  |  cli: v1.2.0

  Functions            +1 created
  API Groups           +1 created
  API Endpoints        +2 created

--- Changes ---
  CREATE           api_group          Voltix Internal Orders
  CREATE           function           Voltix Orders/cancel_order
  CREATE           query              orders/{order_id}/cancel POST
  CREATE           query              orders/{order_id}/cancel POST
```

Nenhum aviso de referência não resolvida. Nenhuma alteração fora do escopo
(nem tabelas, nem endpoints existentes).

## Validação de sintaxe (language server oficial da Xano)

Pacote `@xano/xanoscript-language-server@12.27.0` (parser Chevrotain usado pelo
VS Code/Cursor). Os quatro arquivos passaram sem erros:

```
OK xano/function/voltix_orders/cancel_order.xs
OK xano/api/customer/order_id_cancel_POST.xs
OK xano/api/internal_orders/order_id_cancel_POST.xs
OK xano/api/internal_orders/api_group.xs
```

O validador foi conferido com casos negativos: `db.edit` com `where` e atributo
inexistente falham, confirmando que `db.edit` aceita apenas
`field_name`/`field_value`/`data`. Isso motivou a correção do desenho: a
idempotência é feita pela leitura de estado **dentro** da transação, e
`db.increment` (que aceita `where` + `return = {type: "count"}`) é usado só para
devolver estoque.

## Verificação local

- `openspec validate implement-c2-order-cancellation --strict` → válido.
- `python -m unittest discover -s tests -q` → 188 testes, OK (exit 0).
- `git diff --cached --check` → sem problemas (apenas warnings CRLF informativos).
- Commit local: `968481c feat: implement C2 order cancellation with stock return`.

## Estado

Nada foi publicado. A publicação depende do gate explícito do usuário (tarefa 4.2).
