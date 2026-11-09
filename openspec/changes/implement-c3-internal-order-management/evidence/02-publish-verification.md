# 02 — C3: publicação e verificação (09/11/2026)

## Publicação (autorizada pelo usuário)

Comando (mesmo conjunto do dry-run, sem `--dry-run`):

```
xano workspace push -d xano \
  -i "api/internal_orders/orders_GET.xs" \
  -i "api/internal_orders/order_id_GET.xs" \
  -i "api/internal_orders/order_id_status_POST.xs" \
  --force
```

Resultado: `Matched: 3 of 104 files` · `Synced 3 GUIDs to local files` ·
`Pushed 3 documents to workspace 147981 from xano in 2.3s`.

O CLI emitiu "Unresolved References" para `user`, `pedido`, `CLIENTE`, `item_pedido`,
`variacao_produto` e `pagamento` — o mesmo comportamento heurístico de push parcial já
observado na C1 e na C2. O import resolveu: o pull independente traz os documentos
completos e as rotas respondem na borda.

GUIDs sincronizados:

| Documento | GUID |
|---|---|
| `query orders GET` | `tUE2qV0smb9WtKkQOylnyL_PSVQ` |
| `query orders/{order_id} GET` | `bKoog0ceqOFnT6b-t-KNoIRNDYA` |
| `query orders/{order_id}/status POST` | `fI2zXn8RiO-j_mVymCxgccA6FiM` |

## Pull independente

Snapshots remotos conferem com o local:

- `api/voltix_internal_orders/orders_GET.xs` — `auth = "user"`, precondição de
  FUNCIONARIO/ADMINISTRADOR ativo, validação de `q` (até 100), `status`, `page` e
  `per_page` (1–50), busca por código do Pedido ou `cliente_id in $customer_ids` e
  paginação com totais.
- `api/voltix_internal_orders/orders/order_id_GET.xs` — Cliente (nome + e-mail
  mascarado), endereço de entrega, itens com SKU/nome da variação e Pagamento; sem CPF,
  telefone, senha ou token.
- `api/voltix_internal_orders/orders/order_id/status_POST.xs` — `auth = "user"`,
  precondição de ADMINISTRADOR ativo, enum de alvo restrito a
  `EM_PREPARACAO`/`ENVIADO`/`ENTREGUE`, sequência por status atual dentro de
  `db.transaction`, `db.edit` gravando apenas `status`/`updated_at` e resposta
  `{pedido_id, codigo, status_anterior, status_atual, alterado}`.

Diferença apenas de serialização canônica (ex.: `q?=""` volta como `q?`, campos de
resposta alinhados). Sem alteração de comportamento. O padrão de `q` opcional é o mesmo
do endpoint C4 já em produção (`internal_customers/customers_GET.xs`).

## Verificação de borda (somente leitura, sem sessão)

| Rota | Resultado |
|---|---|
| `GET /api:voltix-internal-orders/orders` | HTTP 401 `ERROR_CODE_UNAUTHORIZED` |
| `GET /api:voltix-internal-orders/orders/1` | HTTP 401 `ERROR_CODE_UNAUTHORIZED` |
| `POST /api:voltix-internal-orders/orders/1/status` (corpo `{"status":"EM_PREPARACAO"}`) | HTTP 401 `ERROR_CODE_UNAUTHORIZED` |

As três rotas existem na borda e exigem autenticação antes de qualquer leitura/escrita.
Nenhum Pedido foi alterado.

Nota: uma primeira tentativa de `POST` via `curl` no PowerShell enviou JSON inválido por
escape de aspas e recebeu HTTP 500 `Error parsing JSON` ainda na validação de entrada.
Reenviado com corpo em arquivo, o mesmo pedido retornou 401 e nada foi escrito.

## Limites

- Não houve ciclo de compra/transição real: verificação somente leitura, conforme
  decisão do usuário em 09/11/2026.
- Não havia credencial de FUNCIONARIO nem de ADMINISTRADOR no ambiente para testar
  autorização positiva/negativa por papel. Fica para um ciclo sintético, se autorizado
  em outra change.

## Verificação local

- `openspec validate implement-c3-internal-order-management --strict` → válido.
- `python -m unittest discover -s tests -q` → 188 testes, OK.
