# e2e-playwright Specification

## Purpose
Definir os testes de ponta a ponta (Playwright) que validam o login do cliente e a navegação pelas telas de compra contra o app Reflex + Xano rodando localmente, garantindo que a verificação E2E use apenas leituras, credenciais de teste em variáveis de ambiente e não realize compras ou pagamentos reais.

## Requirements

### Requirement: E2E validation of login and navigation over purchase surfaces

The project SHALL provide an end-to-end Playwright test that validates login as a customer and navigation across the purchase surfaces against the running Reflex app and Xano integration, exercising only read operations, using existing test infrastructure and test data.

#### Scenario: Login and navigation run against local app with existing test data
- WHEN the E2E test runs with the local app at http://localhost:3000 and Xano configured
- THEN it performs customer login (real authentication) and navigates catalog, cart, checkout and orders screens
- AND the screens trigger only read operations in Xano (GET requests)
- AND it never adds items, confirms orders or simulates payments, and it never creates new customers
- AND credentials come from environment variables (E2E_TEST_EMAIL / E2E_TEST_PASSWORD), never hard-coded in versioned files
