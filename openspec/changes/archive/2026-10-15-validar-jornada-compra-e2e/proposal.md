## Why

Validar via Playwright o login como cliente e a navegação pelas superfícies de compra do Voltix (catálogo, carrinho, checkout, pedidos) contra o app Reflex + Xano em ambiente real, distinguindo navegação/leituras de operações de compra. Vincular os arquivos e2e existentes (package.json, package-lock.json, playwright.config.js) à change e reutilizar a infraestrutura já instalada.

## What Changes

- Vincular e2e/package.json, e2e/package-lock.json e e2e/playwright.config.js à change (para controle por OpenSpec).
- Adicionar teste Playwright e2e/tests/journey-shopping.spec.js cobrindo login e navegação pelas telas de compra, com apenas leituras (GETs) no Xano; sem adicionar item, confirmar pedido ou simular pagamento.
- Ler credenciais de teste via variáveis de ambiente (.env, não versionado); remover credenciais já existentes em arquivos versionados.
- Documentar no delta apenas aspectos de validação E2E.

## Impact

- Áreas: e2e/, openspec/changes/validar-jornada-compra-e2e/
- Não afeta frontend Python (exceto referências), backend Xano, testes unitários, schema de BD.
- Seguro: credenciais em .env (git-ignored); nenhuma mutação de compra realizada pelo teste.
