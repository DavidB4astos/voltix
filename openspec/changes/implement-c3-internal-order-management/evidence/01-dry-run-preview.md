# 01 — C3: dry-run e verificação local (09/11/2026)

## Escopo do preview

Comando (somente preview, sem escrita):

```
xano workspace push -d xano --dry-run \
  -i "api/internal_orders/orders_GET.xs" \
  -i "api/internal_orders/order_id_GET.xs" \
  -i "api/internal_orders/order_id_status_POST.xs"
```

Saída:

```
Include: api/internal_orders/orders_GET.xs, api/internal_orders/order_id_GET.xs, api/internal_orders/order_id_status_POST.xs
Matched: 3 of 104 files

=== Push Preview: workspace 147981 ===
  instance: x8ki-letl-twmt.n7.xano.io  |  workspace: David's Workspace  |  cli: v1.2.0

  API Endpoints        +3 created

--- Changes ---
  CREATE           query              orders/{order_id} GET
  CREATE           query              orders/{order_id}/status POST
  CREATE           query              orders GET
```

Nenhum aviso de referência não resolvida. Nenhuma alteração fora do escopo (o grupo
`Voltix Internal Orders`, a função de cancelamento e o endpoint de cancelamento da C2
não aparecem no preview).

## Validação de sintaxe (language server oficial da Xano)

Pacote `@xano/xanoscript-language-server@12.27.0`, o mesmo usado na C2:

```
OK xano/api/internal_orders/orders_GET.xs
OK xano/api/internal_orders/order_id_GET.xs
OK xano/api/internal_orders/order_id_status_POST.xs
```

O parser rejeitou o filtro `|count` na condição da busca textual
(`Unknown filter function 'count'`). A condição passou a usar
`$db.pedido.cliente_id in $customer_ids` diretamente: com a lista vazia o termo é falso,
então o critério cai para o código do Pedido, sem precisar de contagem.

## Verificação local

- `openspec validate implement-c3-internal-order-management --strict` → válido.
- `python -m unittest discover -s tests -q` → 188 testes, OK (exit 0).
- `git diff --cached --check` → exit 0 (apenas warnings CRLF informativos).
- Commit local: `20c195f feat: implement C3 internal order management endpoints`.

## Estado

Nada foi publicado. A publicação depende do gate explícito do usuário (tarefa 4.2).
