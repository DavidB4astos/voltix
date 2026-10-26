## 1. Backend - XanoScript

- [x] 1.1 Adicionar input opcional `q` (text?) ao `xano/api/public_catalog/products_GET.xs`. Verificar que o endpoint continua aceitando apenas leitura anônima.
- [x] 1.2 Aplicar filtro por nome case-insensitive com correspondência parcial em `produto.nome` quando `q` não estiver vazio/whitespace, combinando com `category_id` (AND) quando ambos fornecidos. Verificar que ambos os ramos (com e sem `category_id`) foram atualizados.
- [x] 1.3 Garantir que o formato de resposta permanece idêntico e que apenas produtos `ATIVO` são considerados. Verificar que `imagem_principal` não é exposta e `image_url` continua sendo assinado quando existir.

## 2. Frontend - Reflex

- [x] 2.1 Adicionar campo de busca no catálogo público vinculado ao `State`. Verificar que a UI permite digitar termo e acionar busca.
- [x] 2.2 Atualizar `_fetch_public_products` para enviar `q` (trimado) quando presente. Verificar que parâmetros são passados corretamente.
- [x] 2.3 Incluir `q` na chave de cache/reutilização quando aplicável para respeitar "Reuse respects the selected category" e evitar reutilizar resultados de busca diferentes. Verificar comportamento.
- [x] 2.4 Integrar com estados existentes (loading/empty/loaded/error). Verificar que busca sem resultados exibe estado vazio.

## 3. Testes

- [x] 3.1 Ampliar `tests/test_public_catalog.py` com casos: filtro por nome, case-insensitive, combinado com categoria, sem resultados, termo vazio ignorado. Verificar que testes passam.

## 4. Documentação e validação

- [x] 4.1 Atualizar `docs/roadmap-changes.md` para refletir `pesquisa-catalogo` como change ativa/proposta. Verificar alteração registrada.
- [x] 4.2 Executar `cmd /c "openspec validate pesquisa-catalogo --strict"`. Verificar saída sem erros.
- [x] 4.3 Revisar artefatos (proposal/design/specs/tasks) quanto à aderência ao escopo (apenas nome, sem SKU/descrição). Verificar conformidade. (Verificado: escopo restrito a nome via `q`, sem SKU/descrição, sem expansão; cache/429/estados preservados.)
