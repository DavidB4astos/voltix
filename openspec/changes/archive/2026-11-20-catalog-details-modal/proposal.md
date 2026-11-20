## Why

Atualmente, em `/catalogo`, `selected_product_details()` é renderizado como um bloco estático acima da grade de produtos (`rx.grid`). Quando o visitante rola a página e clica em `Ver detalhes` em um produto mais abaixo, o painel abre lá em cima da tela, fora da área visível.

## What Changes

- Substituir o posicionamento estático no topo de `selected_product_details()` por um modal centralizado (`rx.dialog.root` / `rx.dialog.content`) controlado por `State.public_selected_product != None`.
- Preservar integralmente:
  - Ação `Ver detalhes` (`State.load_public_product_details(product.id)`) e `Fechar detalhes` (`State.close_public_product_details`), além de fechamento por `Esc` ou clique fora (`on_open_change`).
  - Todos os elementos e regras do detalhe (imagem / `"Imagem não disponível"`, marca, categoria, descrição, variações, SKU, preço, estoque, `"Adicionar ao carrinho"`, feedback do carrinho e especificações técnicas).
- Ajustar `assets/voltix-product-details.css` se necessário para rolagem interna confortável dentro do modal (`max-height`, `overflow-y: auto`) sem afetar a grade do catálogo.
- **Fora do escopo:** alterações em Xano, endpoints, `State` de negócio, regras de carrinho ou specs consolidadas.

## Capabilities

### New Capabilities

- Nenhuma.

### Modified Capabilities

- Nenhuma (`skip_specs: true` em `.openspec.yaml`).

## Impact

- **Worktree:** `.worktrees/catalog-details-modal` (branch `catalog-details-modal`).
- **Arquivos:** `voltix/voltix.py`, `assets/voltix-product-details.css` (se necessário) e teste focado em `tests/`.
- **Gates:** `python -m unittest discover -s tests -q`, `reflex compile` (com restauração de `reflex.lock/*`), `git diff --check` e `openspec validate --all --strict`.
