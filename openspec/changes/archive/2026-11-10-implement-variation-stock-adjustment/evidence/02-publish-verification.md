# 02 — Publicação do ajuste de estoque (10/11/2026)

## Dry-run restrito

```text
xano workspace push -d xano --dry-run \
  -i "api/product_management/variation/variation_id_stock_adjustments_POST.xs"
```

Resultado:

```text
Matched: 1 of 115 files
API Endpoints        +1 created
CREATE           query              variations/{variation_id}/stock-adjustments POST
```

Nenhum schema, tabela, outro endpoint ou variável de ambiente apareceu no plano.

## Publicação (autorizada pelo usuário)

Primeira tentativa falhou na importação com erro de sintaxe em `-$input.delta`. A
expressão foi trocada por `0 - $input.delta`; o dry-run foi repetido com o mesmo
preview de uma única query nova.

```text
xano workspace push -d xano --force \
  -i "api/product_management/variation/variation_id_stock_adjustments_POST.xs"
```

Resultado:

```text
Matched: 1 of 115 files
Synced 1 GUIDs to local files
Pushed 1 documents to workspace 147981 from xano in 2.7s
```

O CLI emitiu "Unresolved References" para `user` e `variacao_produto`, o mesmo
comportamento heurístico de push parcial já observado nas changes anteriores.

GUID sincronizado: `NiRGIMH9OHa57klOkcqHNkk0tOc`.

## Verificação por pull independente

```text
xano workspace pull -d <temporary directory>
Pulled 116 documents
```

Arquivo remoto equivalente:
`api/product_management/variations/variation_id/stock_adjustments_POST.xs`.

Conferências:

- `auth = "user"` e precondições de `ADMINISTRADOR` ativo antes do `db.get` de negócio.
- `db.get variacao_produto` e resposta com allowlist preservados.
- `db.increment variacao_produto` com guarda
  `quantidade_disponivel >= $required_quantity`, `value = $input.delta` e
  `return = {type: "count"}` preservados.
- `0 - $input.delta` preservado após a normalização do push.
- Delta zero, `notfound` e estoque insuficiente preservados.
- GUID remoto igual ao local.

## Verificação remota somente leitura

```text
POST https://x8ki-letl-twmt.n7.xano.io/api:umWTO5yo/variations/1/stock-adjustments
sem sessão
```

Resultado: **401** `ERROR_CODE_UNAUTHORIZED`, antes de qualquer leitura ou escrita de
negócio.

Nenhuma escrita real em estoque foi executada. Não houve chamada autenticada positiva.
