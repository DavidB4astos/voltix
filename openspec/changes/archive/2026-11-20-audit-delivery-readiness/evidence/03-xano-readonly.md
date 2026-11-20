# Evidência 03 — Xano somente leitura

Data: 20/11/2026  
Modo: Somente leitura (`xano workspace pull` sem `--env` e sem `--records`, em diretório temporário isolado fora do repositório)

## 1. Execução do pull

- **Comando:** `xano workspace pull -d <scratch>/xano-pull` (sem `--env`, sem `--records`, sem `push`, `POST`, `PATCH` ou `DELETE`).
- **Resultado:** `Pulled 126 documents` (`exit 0`), sem erros e sem HTTP 429.

## 2. Comparação local (`xano/`) vs remoto (`scratch/xano-pull/`)

- **Contagem:** `125` arquivos locais vs `126` arquivos remotos.
- **Diferença de contagem (+1 remoto):** `table/tmp_rollback_test.xs` — pendência conhecida e documentada; não removida nem alterada nesta auditoria.
- **Diferenças de organização/nomenclatura (local vs remoto):**
  - Local usa `api_group.xs` e diretórios `customer/`, `internal_crm/`, `internal_customers/`, `internal_orders/`, `internal_password_recovery/`, `internal_users/`, `brand/`, `category/`, `product/`, `variation/`.
  - Remoto usa `<group>.xs` e diretórios `voltix_customer/`, `voltix_internal_crm/`, `voltix_internal_customers/`, `voltix_internal_orders/`, `voltix_internal_password_recovery/`, `voltix_internal_users/`, `brands/`, `categories/`, `products/`, `variations/`, além de `integration/integration/health_GET.xs`.
- **Diferenças de conteúdo nos 33 arquivos com mesmo caminho relativo:**
  - Inspeção amostral em `api/public_catalog/products_GET.xs`, `function/voltix_orders/cancel_order.xs`, `api/authentication/auth/login_POST.xs` e `api/authentication/auth/internal_access_GET.xs` mostra apenas formatação do serializador do Xano (aspas no nome da query, espaços em linhas em branco, arrays inline vs multilinha).
- **Pendências conhecidas preservadas (não alteradas):** joins de carrinho/checkout, defaults de schema, upload com 403, `tmp_rollback_test` e prova isolada bloqueada por E6.
