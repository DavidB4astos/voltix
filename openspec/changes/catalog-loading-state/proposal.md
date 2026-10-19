## Why

Em uma primeira visita (sessão nova) à Home ou a `/catalogo`, o Reflex renderiza com os defaults de estado (`public_products = []`, `public_catalog_loading = False`) antes de o handler `load_public_catalog` concluir: como handlers coroutine do Reflex 0.9.12 emitem delta somente ao final, o cliente nunca observa `loading = True` e a condição do empty state é satisfeita durante toda a espera do Xano. O visitante vê "Nenhum produto disponível para exibição." de forma incorreta por vários segundos (1 request de categorias + 1 de produtos + N requests de imagem + eventuais retries de 429) até os dados chegarem.

## What Changes

- Novo var de estado `public_catalog_loaded: bool = False`, setado como `True` no `finally` do handler de carregamento do catálogo público, indicando que a primeira carga (sucesso ou falha) da sessão foi concluída.
- Home (`Destaques da loja`) e `/catalogo`: tratar "primeira carga ainda não concluída" como estado de carregamento, distinguindo os três estados: carregando, catálogo vazio (carga concluída sem produtos) e produtos disponíveis.
- Condição do empty state passa a exigir que a primeira carga tenha sido concluída, impedindo o empty state prematuro.
- Comportamento de erro (mensagem + "Tentar novamente"), reuso de cache (TTL), retry de 429, filtro por categoria e contratos com o Xano permanecem inalterados.

## Capabilities

### New Capabilities

_(nenhuma)_

### Modified Capabilities

- `public-catalog`: novo requisito sobre a apresentação distinta dos três estados iniciais do catálogo (carregando / vazio / com produtos) na primeira carga da sessão.
- `public-home`: requisito do product showcase esclarecido para exigir que o estado de carregamento da primeira carga não seja apresentado como lista vazia.

## Impact

- Código: `voltix/voltix.py` apenas — var de estado (~1971), handler `load_public_catalog` (~2246-2268), condições de render da Home (~6406-6435) e de `/catalogo` (~6761-6799).
- Testes: `tests/test_public_catalog.py` (casos mínimos para os três estados usando o harness `_FakePublicState` existente).
- Fora de escopo: página de detalhes (`public_product_loading`/`public_product_message`), filtros por categoria além do estado inicial, retry/429, cache, contratos Xano, novas melhorias visuais.
- Compatibilidade: somente recursos de estado/condição já suportados pelo Reflex 0.9.12 (`rx.cond`, operadores `&`/`|`); nenhum upgrade de dependência.
- Sem mudança de backend Xano, sem mudança de rota, sem quebra de contrato existente.
