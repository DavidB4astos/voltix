# 07 — Evidências: correção do erro HTTP 429 no catálogo público

> Anexo de verificação da AP2. Registra, com dados reais coletados, o comportamento do catálogo público **antes** e **depois** da mudança `resiliencia-catalogo-publico`.
> Distingue explicitamente **testes automatizados** (`tests/`) de **verificações visuais/funcionais** (navegador + log do backend).

## 1. Contexto e causa

- Sintoma: a Home (`/`) e o Catálogo (`/catalogo`) exibem "Não foi possível carregar o catálogo. Tente novamente." de forma intermitente.
- Causa confirmada: o plano gratuito do Xano limita a **10 requisições por 20 segundos**; ao exceder, o Xano responde **HTTP 429** com o cabeçalho `Retry-After: 20`.
- Fatores que agravam: cada carregamento faz 1 GET de categorias + 1 GET de produtos + 1 GET de imagem por produto; o mesmo `on_load` (`State.load_public_catalog`) é usado em `/` e `/catalogo`; em modo dev os efeitos são executados duas vezes; "Ver detalhes" adiciona mais requisições.

## 2. Ambiente dos testes

| Item | Valor |
|------|-------|
| Sistema | Windows 10 (win32) |
| Python | 3.14.7 (`.venv`) |
| Reflex | 0.9.12 |
| Backend/dados | Xano (plano gratuito), instância `x8ki-letl-twmt.n7.xano.io` |
| Base do catálogo público | `https://x8ki-letl-twmt.n7.xano.io/api:cVn4Vybh` |
| Endpoints (somente-leitura) | `GET /categories`, `GET /products`, `GET /products/{id}/image` |
| Ferramenta do baseline | script somente-leitura de rajada (fora do repositório), sem alterar código de produção |

## 3. Casos de teste

| # | Caso | Tipo | Resultado esperado |
|---|------|------|--------------------|
| CT-01 | Rajada de 15 GETs seguidos em `/categories` | Automatizado (script) | 200 até o limite; depois 429 com `Retry-After` |
| CT-02 | 6 rounds de carga do catálogo (categorias+produtos+imagem) sem pausa | Automatizado (script) | No baseline, 429; após a correção, sem 429 (cache) |
| CT-03 | Navegação repetida Home↔Catálogo dentro do TTL | Automatizado (`unittest`) | Reutiliza dados, sem novas requisições ao Xano |
| CT-04 | Expiração do TTL | Automatizado (`unittest`) | Dispara nova consulta ao Xano |
| CT-05 | Duas cargas simultâneas | Automatizado (`unittest`) | Um único conjunto de requisições |
| CT-06 | HTTP 429 transitório com `Retry-After` | Automatizado (`unittest`) | Repete e conclui com sucesso, sem falha ao visitante |
| CT-07 | HTTP 429 persistente | Automatizado (`unittest`) | Informa falha e permite nova tentativa |
| CT-08 | Log de falha sem dados sensíveis | Automatizado (`unittest`) | Log com endpoint lógico e status, sem credenciais/URL/path |
| CV-01 | Navegar repetidamente entre Home e Catálogo no navegador | Verificação visual | Mensagem de erro não reaparece; catálogo carrega |
| CV-02 | Verificação de compilação (`reflex compile --dry`) | Verificação técnica | Compila sem erros |

## 4. Baseline (antes da correção)

Capturado em `2026-10-14T14:04:12Z`. Dados reais do script de rajada.

### CT-01 — Rajada de 15 GETs em `/categories`

| Seq | Status | Retry-After | Tempo (ms) |
|-----|--------|-------------|------------|
| 1–10 | 200 | — | 1262.7, 473.9, 730.9, 472.8, 459.2, 464.9, 915.9, 476.9, 504.3, 463.5 |
| 11 | 429 | 20 | 468.4 |
| 12 | 429 | 20 | 454.5 |
| 13 | 429 | 20 | 469.0 |
| 14 | 429 | 20 | 461.5 |
| 15 | 429 | 20 | 467.6 |

**Resultado observado:** exatamente 10 requisições aceitas (200) e, a partir da 11ª, todas `429` com `Retry-After: 20` — confirma o limite de **10/20 s**.

### CT-02 — 6 rounds de carga do catálogo sem pausa

| Round | categories | products | product_image |
|-------|-----------|----------|---------------|
| 1 | 429 | 429 | 429 |
| 2 | 429 | 429 | 429 |
| 3 | 429 | 429 | 429 |
| 4 | 429 | 429 | 429 |
| 5 | 429 | 429 | 429 |
| 6 | 429 | 429 | 429 |

**Resultado observado:** após o limite ser atingido, **todas** as 18 requisições de navegação retornaram `429`, reproduzindo a falha exibida ao visitante.

### Resumo do baseline

- 10 requisições aceitas → limite atingido → demais `429` com `Retry-After: 20`.
- Navegação repetida não se recupera dentro da janela de 20 s.
- O backend não registrava a causa; a interface mostrava apenas a mensagem genérica.

## 5. Pós-correção

### 5.1 Testes automatizados (`tests/test_public_catalog.py`, com mocks)

`python -m unittest discover -s tests` → **83 testes, todos OK** (0 falhas). Mapeamento dos casos:

| Caso | Teste | Resultado |
|------|-------|-----------|
| CT-03 | `test_repeated_navigation_within_ttl_reuses_cached_data` | ok — 2ª navegação não refaz requisições (3 chamadas para 2 carregamentos) |
| CT-04 | `test_catalog_cache_expires_and_refetches` | ok — após expirar o TTL, refaz a consulta (6 chamadas para 2 carregamentos) |
| CT-05 | `test_concurrent_loads_issue_a_single_set_of_requests` | ok — 2 cargas concorrentes somam 3 requisições |
| CT-05b | `test_reuse_respects_selected_category` | ok — troca de categoria usa chave de cache separada |
| CT-06 | `test_rate_limit_retry_succeeds_after_transient_429` / `test_rate_limit_wait_seconds_defaults_and_caps` | ok — repete e conclui; espera respeita `Retry-After` e teto |
| CT-07 | `test_persistent_429_is_observable_and_does_not_simulate_success` | ok — 429 persistente permanece observável, sem sucesso simulado |
| CT-08 | `test_catalog_failure_is_logged_without_sensitive_data` | ok — log com endpoint lógico e status, sem token/URL/host/caminho privado |

### 5.2 Verificações funcionais (código real do app contra o Xano)

Capturado em `2026-10-14T14:13:42Z`, exercitando `voltix.voltix` (sem mocks de rede):

| Verificação | Resultado observado |
|-------------|---------------------|
| CT-02 reexecutado — 6 navegações repetidas Home↔Catálogo | **3 requisições de rede no total** (todas `200`), 1 produto carregado, **mensagem de erro vazia** |
| Single-flight — 2 sessões simultâneas | **3 requisições no total** para as duas sessões (mesmo resultado) |
| CT-09 — HTTP 429 real com `Retry-After: 20` | tentativa com respostas `[429, 200]`, tempo do cliente **≈ 20,9 s** (respeita o `Retry-After: 20`), **concluiu com sucesso** (2 categorias), **sem log de falha** |

Interpretação: no baseline, 6 navegações geravam 18 requisições e todas caíam em `429`; após a correção, as mesmas 6 navegações geram 3 requisições (cache) e nenhum erro. Em rajada que ainda estoura o limite, o retry respeita o `Retry-After` e conclui sem exibir falha ao visitante.

### 5.3 Verificações visuais / técnicas

| Caso | Tipo | Resultado |
|------|------|-----------|
| CV-02 — `reflex compile --dry` | técnica | **ok** — "App compiled successfully in 1.136 seconds" |
| CV-01 — navegação repetida Home↔Catálogo no navegador | visual | **ok** — confirmado pelo usuário em 14/10/2026: catálogo carrega corretamente, sem o erro de carregamento |

> A verificação visual (CV-01) foi realizada pelo próprio usuário no navegador e por ele confirmada; esta sessão não executou testes visuais adicionais.

## 6. Conclusão

- Baseline: limite de **10/20 s** confirmado; navegação repetida retornava `429` em 100% das requisições após o limite.
- Pós-correção (automatizado + funcional): cache e single-flight reduzem as requisições; o retry com `Retry-After` mantém o catálogo funcional sem exibir falha; falhas persistentes seguem observáveis e logadas com segurança.
- Verificação visual (CV-01): confirmada pelo próprio usuário em 14/10/2026 — o catálogo carrega corretamente e o erro de carregamento não reaparece.

