## Context

Reutiliza e2e/ já instalado (Playwright + config) e credenciais de teste fornecidas por .env (E2E_TEST_EMAIL / E2E_TEST_PASSWORD). Não há credenciais admin internas; o fluxo é de cliente público. O teste valida leitura das telas, não a compra em si.

## Goals

- Vincular e2e/package.json, package-lock.json, playwright.config.js à change.
- Criar journey-shopping.spec.js cobrindo: /cliente (login real), /catalogo, /carrinho, /checkout e /pedidos — apenas navegação e leituras no Xano.
- Não adicionar item, confirmar pedido nem simular pagamento (nenhuma compra real).
- Isolar execução (workers=1), sem parallel, reutilizar config existente.

## Decisions

- Reusar config existente (baseURL http://localhost:3000, headless, 1 worker, sem webServer), com carregamento do .env do repositório.
- Credenciais somente via variáveis de ambiente; nunca hardcoded em arquivos versionados.
- Seletores estáveis (textos/roles) presentes no app.
- Não arquivar screenshots nesse teste (mantém padrão only-on-failure).
- Não incluir axe-core (não instalado).
- Não repetir smoke/visual-check existentes.

## Risks / Trade-offs

- Dependência do app rodando localmente (pré-condição documentada no teste; skip se credenciais ausentes).
- Cobertura limitada a navegação/leituras: a compra completa (POST de adição, confirmação e pagamento) fica para mudança futura com dados efêmeros autorizados.
