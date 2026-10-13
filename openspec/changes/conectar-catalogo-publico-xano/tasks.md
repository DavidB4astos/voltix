## 1. Configuração de ambiente

- [x] 1.1 Adicionar ao `.env` local as quatro chaves públicas (`XANO_PUBLIC_CATEGORIES_URL`, `XANO_PUBLIC_PRODUCTS_URL`, `XANO_PUBLIC_PRODUCT_DETAILS_URL`, `XANO_PUBLIC_PRODUCT_IMAGE_URL`) com a base `https://x8ki-letl-twmt.n7.xano.io/api:cVn4Vybh`, verificando que as chaves já existem em `.env.example` e que `.env` permanece ignorado pelo Git
- [x] 1.2 Verificar que `.env` não aparece em `git status` (não versionado) e que nenhum valor sensível é gravado em arquivo versionado

## 2. Cliente do catálogo público

- [x] 2.1 Adicionar o parâmetro opcional `path_suffix` a `_public_catalog_request` em `voltix/voltix.py`, mantendo o comportamento atual quando não informado
- [x] 2.2 Usar `path_suffix="/image"` em `_public_product_image` para solicitar `/products/{product_id}/image`, verificando o caminho montado
- [x] 2.3 Confirmar que categorias (`/categories`), produtos com filtro (`/products?category_id=`) e detalhes (`/products/{product_id}`) permanecem inalterados

## 3. Testes

- [x] 3.1 Alinhar as assertivas de `tests/test_public_catalog.py` que esperam `$db.categoria.status`/`$db.marca.status` para `$category_record.status`/`$brand_record.status`, sem remover as demais validações read-only
- [x] 3.2 Executar `python -m unittest tests.test_public_catalog -v` e confirmar que todos os testes passam
- [x] 3.3 Executar a suíte de testes completa (`python -m unittest discover -s tests`) e confirmar ausência de regressões

## 4. Verificação da mudança

- [x] 4.1 Validar a Change com OpenSpec (`openspec validate conectar-catalogo-publico-xano --strict`) e confirmar que está consistente
