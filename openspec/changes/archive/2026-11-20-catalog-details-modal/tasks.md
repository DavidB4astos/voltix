## 1. Modal de detalhes do produto

- [x] 1.1 Converter `selected_product_details()` em `voltix/voltix.py` para `rx.dialog.root` / `rx.dialog.content` mantendo todos os elementos, classes e handlers
- [x] 1.2 Ajustar `assets/voltix-product-details.css` (se necessário) para exibição limpa e rolagem interna do modal em desktop (propriedades aplicadas diretamente em `rx.dialog.content`, preservando `voltix-product-details.css`)

## 2. Verificação e encerramento

- [x] 2.1 Adicionar ou ajustar teste focado em `tests/` verificando o modal (`rx.dialog` / `Fechar detalhes` / `product-detail-title`)
- [x] 2.2 Executar `python -m unittest discover -s tests -q`, `reflex compile` (restaurando `reflex.lock/*`), `git diff --check` e `openspec validate --all --strict`
- [x] 2.3 Registrar evidência em `evidence/verification.md`, arquivar com `openspec archive catalog-details-modal -y --skip-specs` e solicitar autorização antes de commit/push
