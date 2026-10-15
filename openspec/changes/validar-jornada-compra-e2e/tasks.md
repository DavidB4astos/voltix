## 1. Vinculação de arquivos e2e

- [x] 1.1 Incluir e2e/package.json, e2e/package-lock.json e e2e/playwright.config.js nos artefatos da change (rastreados via Git staging da change).
- [x] 1.2 Verificar compatibilidade com config existente (workers=1, baseURL, timeout).

## 2. Teste de navegação e login E2E

- [x] 2.1 Criar e2e/tests/journey-shopping.spec.js cobrindo: login cliente → catálogo → carrinho → checkout → pedidos, apenas com leituras no Xano (GETs); sem adicionar item, confirmar pedido ou simular pagamento.
- [x] 2.2 Reutilizar credenciais de teste definidas em .env (E2E_TEST_EMAIL / E2E_TEST_PASSWORD); não criar novos clientes e não versionar credenciais.
- [x] 2.3 Garantir sem compras/pagamentos reais; sem alterações em backend/Xano.

## 3. Validação

- [x] 3.1 Validar sintaxe do teste Playwright (`npx playwright test --list` + execução do teste).
- [x] 3.2 `openspec validate validar-jornada-compra-e2e --strict`.
