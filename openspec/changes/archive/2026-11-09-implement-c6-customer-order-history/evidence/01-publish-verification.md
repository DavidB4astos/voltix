# 01 — C6: publicação e verificação (09/11/2026)

## Dry-run (restrito)

```
xano workspace push -d xano --dry-run \
  -i "api/internal_customers/customer_id_orders_GET.xs"
```

Resultado:

```
Include: api/internal_customers/customer_id_orders_GET.xs
Matched: 1 of 106 files

API Endpoints        +1 created

CREATE           query              customers/{customer_id}/orders GET
```

Nenhum schema, grupo ou endpoint existente incluído.

## Publicação (autorizada pelo usuário)

Comando (mesmo conjunto do dry-run, com `--force`):

```
xano workspace push -d xano --force \
  -i "api/internal_customers/customer_id_orders_GET.xs"
```

Resultado: `Matched: 1 of 106 files` · `Synced 1 GUIDs to local files` ·
`Pushed 1 documents to workspace 147981 from xano in 2.5s`.

O CLI emitiu "Unresolved References" para `user`, `CLIENTE`, `pedido`, `item_pedido` e
`variacao_produto` — o mesmo comportamento heurístico de push parcial já observado na
C1–C3 e C10. O pull independente confirmou que as referências foram preservadas.

GUID sincronizado:

| Documento | GUID |
|---|---|
| `query customers/{customer_id}/orders GET` | `QMKTnSUPm-1AD2LrR-GxyKhKCPA` |

## Pull independente

Snapshot remoto (`api/voltix_internal_customers/customers/customer_id/orders_GET.xs`)
confere com o local:

- `auth = "user"` e precondição de `FUNCIONARIO`/`ADMINISTRADOR` ativo.
- `customer_id` com `filters=min:1`; `db.get CLIENTE` restrito a `id` e `notfound` quando
  o Cliente não existe.
- Filtros `status` (TODOS ou seis estados), `from`/`to` (`YYYY-MM-DD`, UTC, inclusivos) e
  paginação `page`/`per_page` (1–50); `from > to` é rejeitado.
- `db.query pedido` com `where` por Cliente, status e período, ordenação
  `data_pedido desc, id desc`, `paging` com totais e `output` restrito ao resumo.
- `db.query item_pedido` por `pedido_id in $order_ids` e `db.query variacao_produto` por
  `id in $variation_ids`, sem N+1.
- Itens inline com SKU, nome, quantidade, preço unitário e subtotal; Pedido sem item
  retorna `itens: []`.
- Resposta com `cliente_id`, `items`, `page`, `per_page`, `total_items` e
  `total_pages`; nenhum dado pessoal do Cliente.
- Nenhum `db.edit`, `db.add`, `db.patch` ou `db.delete`.

Diferenças apenas de serialização canônica (fences e alinhamento de campos). Sem
alteração de comportamento.

## Verificação de borda (somente leitura, sem sessão)

| Rota | Resultado |
|---|---|
| `GET /api:voltix-internal-customers/customers/1/orders` | HTTP 401 |
| `GET /api:voltix-internal-customers/customers/1` (controle) | HTTP 401 |

A rota existe na borda e exige autenticação antes de qualquer leitura. Nenhum Pedido foi
lido de forma autenticada nem alterado.

## Limites

- Não houve consulta autenticada nem dados sintéticos: verificação somente leitura,
  conforme decisão do usuário em 09/11/2026.
- Não havia credencial de FUNCIONARIO nem de ADMINISTRADOR no ambiente para exercitar
  autorização positiva/negativa, paginação real ou o agrupamento de itens.
- Se uma variação referenciada por ItemPedido não existir mais, o item retorna `sku` e
  `nome_ou_descricao` nulos, sem interromper a resposta; o subtotal persistido é mantido.
- Datas impossíveis como `2026-02-31` podem ser normalizadas pelo parser, risco aceito no
  design.

## Verificação local

- Language server oficial (`validate.mjs`) → `OK`.
- `openspec validate implement-c6-customer-order-history --strict` → válido.
- `python -m unittest discover -s tests -q` → 188 testes, OK.
- `git diff --check` → limpo.
- `reflex.lock` alterado pelo compile local foi restaurado e não entrou no commit.
