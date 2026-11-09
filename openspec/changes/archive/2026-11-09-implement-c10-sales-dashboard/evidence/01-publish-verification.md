# 01 — C10: publicação e verificação (09/11/2026)

## Dry-run (restrito)

```
xano workspace push -d xano --dry-run \
  -i "api/internal_orders/reports_sales_GET.xs" \
  -i "api/internal_orders/api_group.xs"
```

Resultado:

```
Include: api/internal_orders/reports_sales_GET.xs, api/internal_orders/api_group.xs
Matched: 2 of 105 files

API Groups           ~1 updated
API Endpoints        +1 created

UPDATE           api_group          Voltix Internal Orders
CREATE           query              reports/sales GET
```

Nenhum schema, tabela ou outro endpoint incluído.

## Publicação (autorizada pelo usuário)

Comando (mesmo conjunto do dry-run, com `--force`):

```
xano workspace push -d xano --force \
  -i "api/internal_orders/reports_sales_GET.xs" \
  -i "api/internal_orders/api_group.xs"
```

Resultado: `Matched: 2 of 105 files` · `Synced 1 GUIDs to local files` ·
`Pushed 2 documents to workspace 147981 from xano in 2.1s`.

O CLI emitiu "Unresolved References" para `user` e `pedido` — o mesmo comportamento
heurístico de push parcial já observado na C1–C3. O pull independente confirmou que as
referências `db.get user` e `db.query pedido` foram preservadas, sem placeholders.

GUID sincronizado:

| Documento | GUID |
|---|---|
| `query reports/sales GET` | `Heqy-LV7kOfaJOsQmSnqu2KOrgk` |

## Pull independente

Snapshot remoto (`api/voltix_internal_orders/reports/sales_GET.xs`) confere com o local:

- `auth = "user"` e precondição de `FUNCIONARIO`/`ADMINISTRADOR` ativo.
- `from`/`to` opcionais validados por regex `YYYY-MM-DD`; padrão em UTC.
- Período padrão de 30 dias inclusivos; limite de 366 dias inclusivos
  (`fim_dia_ms - inicio_ms <= 31536000000`).
- `db.query pedido` filtrando `data_pedido` entre início e fim e status em
  `PAGAMENTO_CONFIRMADO`, `EM_PREPARACAO`, `ENVIADO`, `ENTREGUE`.
- `output` restrito a `id`, `data_pedido`, `status`, `valor_total`.
- Cálculo de faturamento, quantidade, ticket médio e série diária em XanoScript, com
  `round:2` na resposta e `serie_diaria` ascendente.
- Nenhum `db.get CLIENTE` e nenhum dado pessoal na resposta.

Diferenças apenas de serialização canônica (fences e alinhamento de campos). Sem
alteração de comportamento.

Nota: o pull renderiza a descrição do grupo uma vez como comentário, resultando em duas
linhas de comentário idênticas em `voltix_internal_orders.xs`. É um artefato de
serialização; o texto publicado é o novo ("Internal order consultation, cancellation and
sales reporting.") e não há alteração funcional.

## Verificação de borda (somente leitura, sem sessão)

| Rota | Resultado |
|---|---|
| `GET /api:voltix-internal-orders/reports/sales` | HTTP 401 |
| `GET /api:voltix-internal-orders/orders` (controle) | HTTP 401 |

A rota existe na borda e exige autenticação antes de qualquer agregação. Nenhum Pedido
foi lido de forma autenticada nem alterado.

Nota: uma primeira sondagem usou por engano a base do endpoint público de Pedidos
(`/api:voltix-customer/...`) e retornou 404. Refeita na base do grupo interno
(`/api:voltix-internal-orders/...`), retornou 401.

## Limites

- Não houve ciclo autenticado nem dados sintéticos de venda: verificação somente leitura,
  conforme decisão do usuário em 09/11/2026.
- Não havia credencial de FUNCIONARIO nem de ADMINISTRADOR no ambiente para exercitar
  autorização positiva/negativa por papel nem a agregação real.
- O parse de datas usa formato explícito `Y-m-d` em UTC; datas impossíveis como
  `2026-02-31` podem ser normalizadas pelo parser, risco aceito no design.

## Verificação local

- Language server oficial (`validate.mjs`) → `OK` nos dois arquivos.
- `openspec validate implement-c10-sales-dashboard --strict` → válido.
- `python -m unittest discover -s tests -q` → 188 testes, OK.
- `git diff --check` → limpo.
