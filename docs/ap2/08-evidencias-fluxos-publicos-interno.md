# 08 — Evidências: verificação ao vivo dos fluxos públicos e do acesso interno

> Anexo de verificação da AP2. Registra, com dados reais coletados, a verificação **ao vivo** dos fluxos hoje demonstráveis do Voltix: Home (`/`), Catálogo público (`/catalogo`), Acesso interno (`/interno`) e Integração Reflex↔Xano.
> Distingue explicitamente **testes automatizados** (`tests/`) de **verificação funcional** (código real do app exercitado contra o Xano publicado, sem mocks de rede).

## 1. Contexto e objetivo

- Complementa o `07-evidencias-catalogo-429.md` (que trata a resiliência a `HTTP 429`).
- Objetivo: registrar quais fluxos do sistema efetivamente **respondem contra o backend publicado** e quais **não estão configurados**, para embasar a entrega e a demonstração da AP2.
- Escopo desta verificação: apenas leitura anônima/autenticada nos endpoints; **nenhum dado foi criado, alterado ou removido** no Xano.

## 2. Ambiente dos testes

| Item | Valor |
|------|-------|
| Sistema | Windows 10 (win32) |
| Python | 3.14.7 (`.venv`) |
| Reflex | 0.9.12 |
| Backend/dados | Xano, instância `x8ki-letl-twmt.n7.xano.io` |
| Ferramenta | script somente-leitura (fora do repositório), sem alterar código de produção |
| Execução | `python` do `.venv` importando `voltix.voltix` e chamando os handlers reais |
| Timestamp | `2026-10-14T14:58:58Z` |

## 3. Cobertura de configuração do Xano (`.env`)

O aplicativo depende de 21 variáveis de ambiente de endpoint, agrupadas por área. No ambiente local, apenas **8 estão preenchidas**:

| Grupo | Variáveis | Preenchidas |
|-------|-----------|-------------|
| Integração | `XANO_HEALTH_URL` | 1 de 1 |
| Acesso interno | `XANO_LOGIN_URL`, `XANO_ME_URL`, `XANO_INTERNAL_ACCESS_URL` | 3 de 3 |
| Catálogo público | `XANO_PUBLIC_CATEGORIES_URL`, `XANO_PUBLIC_PRODUCTS_URL`, `XANO_PUBLIC_PRODUCT_DETAILS_URL`, `XANO_PUBLIC_PRODUCT_IMAGE_URL` | 4 de 4 |
| Gestão de catálogo | `XANO_CATEGORIES_URL`, `XANO_BRANDS_URL` | **0 de 2** |
| Gestão de produtos | `XANO_PRODUCTS_URL`, `XANO_VARIATIONS_URL` | **0 de 2** |
| Cliente / Endereços | `XANO_CUSTOMER_URL`, `XANO_CUSTOMER_LOGIN_URL`, `XANO_CUSTOMER_ME_URL`, `XANO_CUSTOMER_ADDRESSES_URL` | **0 de 4** |
| Carrinho | `XANO_CART_URL` | **0 de 1** |
| Checkout / Pedidos | `XANO_CHECKOUT_REVIEW_URL`, `XANO_CHECKOUT_CONFIRM_URL`, `XANO_ORDERS_URL`, `XANO_PAYMENT_SIMULATION_URL` | **0 de 4** |

**Consequência:** os fluxos de **gestão (categorias/marcas e produtos), cliente/endereços, carrinho, checkout, pedidos e pagamento** têm implementação e testes automatizados, porém **não possuem endpoints configurados** e, portanto, **não são executáveis ao vivo** neste ambiente. Isso decorre do bloqueio externo de publicação do Xano (`allow_push: false`) já registrado nos `tasks.md` das changes `gestao-produtos`, `cadastro-cliente-enderecos` e `checkout-pedidos`.

## 4. Casos de verificação

| # | Caso | Tipo | Resultado esperado |
|---|------|------|--------------------|
| LV-01 | Carga do catálogo (handler real de Home `/` e Catálogo `/catalogo`) | Funcional (rede real) | Categorias e produtos carregados, sem mensagem de erro |
| LV-02 | Reutilização de cache (2ª carga imediata) | Funcional (rede real) | Sem nova requisição; resultado igual |
| LV-03 | Detalhe do primeiro produto | Funcional (rede real) | Produto com variações carregado |
| LV-04 | Health da integração Reflex↔Xano | Funcional (rede real) | `status = ok` |
| LV-05 | Login interno com credenciais inválidas | Funcional (rede real) | Rejeição (`HTTP 403`) |
| LV-06 | Identidade (`/me`) com token inválido | Funcional (rede real) | Rejeição (`HTTP 401`) |
| LV-07 | Regra de acesso interno com token inválido | Funcional (rede real) | Rejeição (`HTTP 401`) |

## 5. Resultados observados

| # | Verificação | Resultado observado |
|---|-------------|---------------------|
| LV-01 | Catálogo (Home/Catálogo) | **2 categorias**, **1 produto**, **mensagem de erro vazia**, tempo **1,44 s** |
| LV-02 | 2ª carga (cache) | **0,0 s**, mesmos dados, sem erro — cache reutilizado |
| LV-03 | Detalhe do produto `1` | **carregado com sucesso**, **1 variação**, sem mensagem de erro |
| LV-04 | Health | `{"status": "ok", "service": "voltix-xano", "integration": "available"}` |
| LV-05 | Login interno (inválido) | `HTTP 403` — endpoint ativo, rejeita credenciais inválidas |
| LV-06 | `/me` (token inválido) | `HTTP 401` — endpoint ativo, exige autenticação |
| LV-07 | Acesso interno (token inválido) | `HTTP 401` — endpoint ativo, exige autenticação |

Interpretação: os fluxos **Home** e **Catálogo público** carregam dados reais do backend publicado, com cache funcionando (segunda carga sem tráfego). A **Integração** está `ok`. Os endpoints de **Acesso interno** estão publicados e **aplicam autenticação** corretamente (rejeitam credenciais/token inválidos).

## 6. Limitações e pendências

- **Não executado:** login de ADMINISTRADOR válido e renderização do `/interno` no navegador. Requer **credenciais reais** de administrador e sessão de navegador; não há, no repositório, usuário/senha de teste (nada foi inventado).
- **Não demonstrável ao vivo:** gestão de produtos/categorias, cliente/endereços, carrinho, checkout, pedidos e pagamento — endpoints ausentes no `.env` (§3).
- **Verificação de interface:** esta sessão não executou testes de navegador (cliques/renderização); os fluxos foram exercitados pelo código real do app contra o backend, não por automação de UI.

## 7. Conclusão

- **Demonstrável ao vivo hoje:** Home `/`, Catálogo público `/catalogo`, Acesso interno `/interno` (rejeição segura) e Integração Reflex↔Xano.
- **Validado no código real, mas sem endpoint publicado:** demais fluxos (EP-05 a EP-10), cobertos apenas por testes automatizados.
- Nenhuma alteração foi feita em código, dados ou configurações do Xano; a evidência é de somente leitura.
