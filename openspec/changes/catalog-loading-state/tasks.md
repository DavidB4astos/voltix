## 1. Estado de carregamento

- [x] 1.1 Adicionar `public_catalog_loaded: bool = False` em `voltix/voltix.py` ao lado de `public_catalog_loading` e verificar que a suíte existente continua verde (`python -m unittest tests.test_public_catalog`)
- [x] 1.2 Setar `self.public_catalog_loaded = True` no bloco `finally` de `load_public_catalog` e verificar com teste unitário que após sucesso o valor é `True` e `public_products` foi preenchido
- [x] 1.3 Verificar com teste unitário que após falha do carregamento `public_catalog_loaded` é `True` e `public_catalog_message` está preenchido (não fica preso em "não concluído")

## 2. Render da Home e do catálogo

- [x] 2.1 Em `Destaques da loja` (Home), exibir `loading_text` enquanto `public_catalog_loading | public_catalog_loaded == False` e condicionar o empty state a `public_catalog_loaded == True`, verificando por inspeção do código que os ramos de erro e de grade permanecem inalterados
- [x] 2.2 Em `/catalogo`, aplicar as mesmas condições: loading durante a primeira carga e empty state somente com carga concluída, preservando a cascata de mensagem de erro e grade de produtos
- [x] 2.3 Confirmar por leitura que nenhuma condição da página de detalhes (`public_product_loading`/`public_product_message`) foi alterada

## 3. Verificação

- [x] 3.1 Adicionar em `tests/test_public_catalog.py` o teste de estado inicial: nova instância inicia com `public_catalog_loaded = False` e rodar `python -m unittest tests.test_public_catalog`
- [x] 3.2 Rodar a suíte completa (`python -m unittest discover tests`) e confirmar todos os testes verdes
- [x] 3.3 Verificar em navegador com sessão nova: ao abrir `/` e depois `/catalogo` em aba anônima, o estado de carregamento aparece antes dos produtos e "Nenhum produto disponível" não aparece durante a primeira carga; com catálogo sem produtos ativos, o empty state aparece somente após a carga concluir (verificação manual registrada em tasks ao concluir)
- [x] 3.4 Validar a change (`openspec validate catalog-loading-state --strict`) e conferir que `git status` contém apenas os arquivos da change, de `voltix/voltix.py` e de `tests/test_public_catalog.py`
