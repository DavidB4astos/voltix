# Evidência 04 — Segurança e autorização

Data: 20/11/2026  
Escopo: Conferência estática de contratos XanoScript publicados (`scratch/xano-pull/`), código Reflex (`voltix/`) e higiene de segredos/repositório.

## 1. Autorização no backend (XanoScript)

- **Autenticação interna (`authentication/auth/*`):**
  - `internal_access_GET` e `me_GET` exigem `auth = "user"`, perfil `FUNCIONARIO` ou `ADMINISTRADOR` e `status == "ATIVO"`.
- **Catálogo e produtos (`catalog_management/*`, `product_management/*`):**
  - Todos os endpoints administrativos exigem `auth` + `ADMINISTRADOR` + `ATIVO`.
- **Área do cliente (`voltix_customer/*`):**
  - Exceto `login_POST`, todos os endpoints (`me_GET`, `addresses*`, `cart*`, `checkout*`, `orders*`) exigem autenticação de cliente e `status == "ATIVO"`.
- **Clientes internos e pedidos (`voltix_internal_customers/*`, `voltix_internal_orders/*`):**
  - Leituras (`customers_GET`, `customer_id_GET`, `customer_id/orders_GET`, `orders_GET`, `order_id_GET`, `reports/sales_GET`) exigem `FUNCIONARIO` ou `ADMINISTRADOR` + `ATIVO`.
  - Mutações sensíveis (`customers/customer_id_PATCH`, `orders/order_id/cancel_POST`, `orders/order_id/status_POST`) exigem exclusivamente `ADMINISTRADOR` + `ATIVO`.
- **CRM (`voltix_internal_crm/*`) e usuários internos (`voltix_internal_users/*`):**
  - CRM acessível a `FUNCIONARIO` e `ADMINISTRADOR` ativos; listagem/gestão de usuários restrita a `ADMINISTRADOR` ativo (preservando edição do próprio perfil/senha).
- **Observação pós-entrega:** os endpoints legados `db_xano_bastos/status_cliente/*` permanecem com `auth=False` no workspace remoto; não são consumidos pelo frontend Voltix, mas ficam registrados como item de higiene **pós-entrega**.

## 2. Proteção de dados sensíveis e segredos

- `.gitignore` bloqueia `.env` e `.env.*` (mantendo apenas `.env.example` versionado).
- Nenhum arquivo `.env`, token, hash, senha, CPF sem máscara, e-mail ou telefone de cliente foi exposto nas evidências ou nos arquivos versionados desta change.
