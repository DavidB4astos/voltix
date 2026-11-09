# 02 — C2: publicação e verificação (09/11/2026)

## Publicação (autorizada pelo usuário)

Comando (mesmo conjunto do dry-run, sem `--dry-run`):

```
xano workspace push -d xano \
  -i "function/voltix_orders/cancel_order.xs" \
  -i "api/customer/order_id_cancel_POST.xs" \
  -i "api/internal_orders/*.xs" \
  --force
```

Resultado: `Matched: 4 of 101 files` · `Pushed 4 documents to workspace 147981 from xano in 2.0s`.

O CLI emitiu "Unresolved References" para `CLIENTE`, `pedido`, `user`, `item_pedido`
e `pagamento` — o mesmo comportamento heurístico de push parcial observado na C1.
O import resolveu: o pull independente mostra os documentos completos (abaixo) e as
rotas respondem na borda.

GUIDs sincronizados para os arquivos locais:

| Documento | GUID |
|---|---|
| `function "Voltix Orders/cancel_order"` | `HKe2JA4ZIdhoAfBE1Oz0zsjiSTs` |
| `api_group "Voltix Internal Orders"` | `oWAMOJGZJbLdEILuMVsUWTApsWU` |
| `query orders/{order_id}/cancel` (Customer) | `KaXivnEAM4aoFgmhzlaUJ54J1ZQ` |
| `query orders/{order_id}/cancel` (Internal Orders) | `gbhLdzuqbGXFbqmtSEZPOuefczw` |

## Pull independente

Snapshots remotos conferem com o local:

- `function/voltix_orders/cancel_order.xs` — transação com `db.get pedido`, janela por
  `kind`, `db.query item_pedido` + `foreach` + `db.increment variacao_produto`
  (`where`, `return = {type: "count"}`), `db.edit pedido`, `db.query pagamento`,
  `db.edit pagamento`, resposta `{pedido_id, codigo, pedido_status, efeito}`.
- `api/voltix_customer/orders/order_id/cancel_POST.xs` — `auth = "CLIENTE"`, checagem de
  `CLIENTE` ATIVO e de dono (`owned_order.cliente_id == $auth.id`), `kind = "cliente"`.
- `api/voltix_internal_orders/orders/order_id/cancel_POST.xs` — `auth = "user"`,
  precondição `role == "ADMINISTRADOR"` e `status == "ATIVO"`, `kind = "admin"`.
- `api/voltix_internal_orders/voltix_internal_orders.xs` — grupo `voltix-internal-orders`.

Diferença apenas de serialização canônica (ex.: `error_type = "standard"` omitido por ser
o padrão; `db.increment variacao_produto` sem aspas). Sem alteração de comportamento.

## Verificação de borda (somente leitura, sem sessão)

| Rota | Resultado |
|---|---|
| `POST /api:voltix-customer/orders/1/cancel` | HTTP 401 `ERROR_CODE_UNAUTHORIZED` |
| `POST /api:voltix-internal-orders/orders/1/cancel` | HTTP 401 `ERROR_CODE_UNAUTHORIZED` |

As duas rotas existem na borda (inclusive o grupo novo) e exigem autenticação antes de
qualquer leitura/escrita. Nenhum Pedido, ItemPedido, Pagamento ou estoque foi alterado.

## Limites

- Não houve ciclo de compra/cancelamento real: verificação somente leitura, conforme
  decisão do usuário em 09/11/2026 (gate de publicação).
- Não havia credencial de Cliente nem de ADMIN disponível no ambiente para testar
  autorização positiva/negativa por papel. Fica para o ciclo sintético, se autorizado
  em outra change.
- Risco concorrente de devolução dupla registrado no `design.md` (limite do XanoScript:
  `db.edit` não aceita `where`).

## Verificação local

- `openspec validate implement-c2-order-cancellation --strict` → válido.
- `python -m unittest discover -s tests -q` → 188 testes, OK.
