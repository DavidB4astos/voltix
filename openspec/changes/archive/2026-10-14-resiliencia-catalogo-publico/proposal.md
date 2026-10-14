## Why

O catálogo público falha de forma intermitente com a mensagem "Não foi possível carregar o catálogo. Tente novamente.". A causa foi confirmada em investigação: o plano gratuito do Xano limita a **10 requisições por 20 segundos** (`HTTP 429`, `Retry-After: 20`). Cada carregamento do catálogo emite 1 requisição de categorias + 1 de produtos + 1 de imagem por produto, e o mesmo `load_public_catalog` está em `on_load` tanto da Home (`/`) quanto do Catálogo (`/catalogo`); somado à dupla execução de efeitos do modo dev, navegar entre as páginas em menos de 20 segundos estoura o limite e o `429` é tratado como falha genérica silenciosa. É necessária uma correção mínima de resiliência, mantendo o plano gratuito e os contratos do Xano. Esta é a **prioridade da entrega da AP2 (19/10/2026)** e deve vir acompanhada de **testes sistemáticos com evidências**.

## What Changes

- Reaproveitar dados do catálogo público (categorias e produtos, incluindo imagem resolvida) por um **curto TTL em memória** no backend, para que a navegação entre Home e Catálogo não emita novas requisições ao Xano dentro do período.
- Impedir **carregamentos simultâneos duplicados** (single-flight): enquanto um carregamento está em andamento, novas solicitações reutilizam o resultado em progresso em vez de disparar novas requisições.
- Tratar **HTTP 429** respeitando `Retry-After`, com número limitado de tentativas e backoff; se persistir, apresentar a falha (sem dados simulados) e permitir nova tentativa.
- **Registrar as falhas no backend** para diagnóstico, sem expor credenciais, tokens, URLs completas ou caminhos privados.
- Planejar e executar **testes sistemáticos com evidências** para a AP2: casos de teste antes da correção, testes automatizados e funcionais após a correção, navegação repetida e verificação do comportamento sob HTTP 429, registrando resultados e eventuais erros encontrados em um documento de evidências.
- **Preservar** os contratos atuais com o Xano, o plano gratuito, as rotas, a interface visual e as demais funcionalidades.

Ficam fora desta Change: alterações nos XanoScripts ou nos contratos de endpoints, migração/upgrade do plano Xano, novas rotas, autenticação, regras de negócio, carrinho, checkout, pedidos, pagamentos, CRM, e qualquer mudança de layout ou de escopo funcional.

## Capabilities

### New Capabilities

- Nenhuma.

### Modified Capabilities

- `public-catalog`: o carregamento público passa a reutilizar dados por curto TTL, a evitar cargas simultâneas duplicadas, a tratar limite de taxa (HTTP 429) com `Retry-After` e tentativas limitadas, e a registrar falhas de forma observável sem expor dados sensíveis — sem alterar os contratos das requisições ao Xano.

## Impact

- `voltix/voltix.py`: camada de requisição (`_request_xano_json` / `_server_side_xano_request`) ganha tratamento de 429 com `Retry-After` e log; `load_public_catalog` / `_fetch_public_products` passam a usar cache de curto TTL e single-flight, mantendo a mensagem de falha e o botão "Tentar novamente" existentes.
- `tests/test_public_catalog.py`: novos testes para navegação repetida, cache, expiração, requisições simultâneas e HTTP 429, no estilo atual (unittest/AsyncMock/patch de `_server_side_xano_request` e `urllib.request.urlopen`).
- `docs/ap2/`: novo documento de evidências da correção (casos antes/depois, resultados e erros), como insumo da entrega da AP2.
- Sem novas dependências; sem alteração de rotas, sessão, autorização, State de negócio, UI, dados ou XanoScript.
