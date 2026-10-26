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

## 7. Correção do fan-out de imagens (2026-10-22)

### 7.1 Causa

A carga do catálogo fazia uma requisição HTTP de imagem por produto (`public_catalog.product_image`) via `asyncio.gather`. Com 20 produtos, a carga fria emitia ~22 requisições e excedia o limite de 10/20 s do Xano Free. O log `reflex_v3000_err.log` registrou 18 respostas `429` nesse endpoint, incluindo 4 novas após ~1h16 sem tráfego.

### 7.2 Implementação no working tree

- `xano/api/public_catalog/products_GET.xs`: `imagem_principal` incluída na projeção interna dos dois ramos; URL assinada com TTL 3600 no `foreach`; campo `image_url` na resposta; caminho privado omitido.
- `voltix/voltix.py`: `_public_catalog_products` lê e valida `image_url`; `_fetch_public_products` usa a URL da listagem e não chama mais `_public_product_image` por produto; `resolve_demo_image_named` e o endpoint dedicado do detalhe permanecem.
- `tests/test_public_catalog.py`: mocks e contagens atualizados de 3 para 2 requisições por carga; teste de regressão com múltiplos produtos confirma `await_count == 2` e nenhuma chamada por produto.

### 7.3 Verificação automatizada desta passagem

| Verificação | Resultado |
|---|---|
| `python -m unittest discover -s tests` | **139 testes OK** |
| `python -m unittest discover -s tests -p "test_public_catalog.py"` | **23 testes OK** |
| `python -m py_compile voltix/voltix.py` | **OK** |
| `reflex compile` | **OK** — app compilado em 6,392 s |
| `git diff --check` | **OK** (sem erros; apenas avisos de CRLF) |
| Hashes de `reflex.lock/*` antes/depois do compile | **inalterados** |

Contrato esperado após a publicação: a carga fria emite no máximo **2 requisições** (categorias + produtos), independentemente da quantidade de produtos, sem requisições de imagem por produto. O detalhe continua usando o endpoint dedicado.

### 7.4 Pendente (bloqueado pela publicação manual no Xano)

- Publicar `products_GET.xs` no Xano e validar o contrato com uma chamada somente-leitura.
- Abrir `/catalogo` e a Home em sessão limpa, confirmar imagens, ausência de `429` e registrar a contagem real de requisições.
- O smoke e a medição real **não foram executados** nesta passagem; a tarefa 7.6 e o archive da Home permanecem bloqueados até essa publicação.

### 8. Verificação pós-publicação (2026-10-23)

#### 8.1 Contrato do endpoint publicado

Chamada única e somente-leitura a `GET /products`, sem repetição:

| Verificação | Resultado |
|---|---|
| HTTP | **200** |
| Tempo | **0,869 s** |
| Produtos | **23** (`ATIVO=23`) |
| Campo `image_url` presente | **23/23** |
| `image_url` HTTPS | **0** |
| `image_url` nulo/vazio | **23** |
| Campo `imagem_principal` exposto | **0** |

O endpoint publicado inclui `image_url` e não expõe `imagem_principal` nem caminhos privados. Como todos os produtos estão sem imagem no Xano, o ramo HTTPS assinado não pôde ser exercitado; a resposta atual é integralmente `null`.

#### 8.2 Smoke de `/catalogo` — inválido por servidor desatualizado

O servidor `localhost:3000` foi reutilizado sem reinício (PID **15944**, iniciado em 21/10/2026 17:41, comando `reflex run --env prod --single-port --frontend-port 3000`). O reload de `/catalogo` renderizou **23 produtos**, **3 imagens locais** (`/demo/vtx-demo-003.jpg`, `004.jpg`, `015.jpg`) e **20 placeholders**, mas exibiu **"Connection Error:"**.

O log `reflex_v3000_err.log` foi atualizado durante o reload e passou de 18 para **46 linhas**, com **28 novas falhas** de `public_catalog.product_image` (**12×429**, **16×`None`**). Isso prova que o processo em execução ainda usa o build anterior e continua o fan-out de imagens; portanto, o smoke **não valida** a correção e **não foi repetido**, conforme a regra de não insistir sob HTTP 429.

#### 8.3 Estado das tarefas

- **7.2:** concluída — publicação e contrato validados.
- **5.3:** **PASSOU** em 2026-10-23; `/carrinho`, `/cliente` e `/interno` permanecem aprovados na tentativa anterior.
- **7.6:** **PASSOU** em 2026-10-23 (passagem única); `/catalogo` e Home verificados.
- **6.7:** **pronto para encerramento; archive não executado** — aguarda aprovação explícita.

#### 8.4 Verificação final de `/catalogo` e Home (2026-10-23 10:18–10:22)

Passagem única, reutilizando o servidor existente (`localhost:3000`, PID **31912**), sem reinício, build ou teste adicional.

**`/catalogo` — PASSOU.**

- 23 cards de produto renderizados.
- 3 imagens locais (`/demo/vtx-demo-003.jpg`, `004.jpg`, `015.jpg`) com `complete=true` e `naturalWidth > 0`.
- **0 imagens quebradas.**
- 20 cards com `image_url` nulo foram apresentados sem `<img>` e sem ícone quebrado; a área de imagem é omitida (`div` de 0 px), sem placeholder visual dedicado.
- Evidência: `C:\Users\venda\AppData\Local\Temp\opencode\voltix-final-catalogo-20261023.png`.

**Home (`/`) — PASSOU.**

- Hero "Tecnologia premium para elevar o seu setup." presente.
- Bloco de categorias e seção "Categorias" presentes.
- Seção editorial "Tecnologia em contexto" presente.
- Vitrine "Destaques da loja" com 3 produtos e 5 imagens locais no total do snapshot.
- Evidência: `C:\Users\venda\AppData\Local\Temp\opencode\voltix-final-home-20261023.png`.
- A avaliação DOM detalhada da Home expirou na ferramenta, mas o snapshot de acessibilidade confirmou as seções e as imagens.

**Xano / 429 — PASSOU.**

- `reflex.err.log` do servidor novo: **0 linhas**, sem novo HTTP 429.
- `reflex_v3000_err.log` antigo: inalterado (46 linhas, mtime 09:58:31), pertencente ao build anterior.
- A contagem de rede em runtime não foi medida (SSR; o browser não emitiu XHR/fetch); a cobertura de 2 requisições permanece no teste de regressão 7.4.

Nenhum código, dependência, imagem ou lockfile foi alterado; nenhum commit, push Git ou archive OpenSpec foi executado.
