## 1. Backend (Xano)

- [ ] 1.1 Atualizar `xano/api/public_catalog/products_GET.xs` para incluir `imagem_principal` na projeção interna dos dois ramos (com e sem filtro de categoria), assinar a URL no `foreach` com TTL 3600 e retornar `image_url` no objeto de cada produto; verificar por inspeção do arquivo que `imagem_principal` não aparece na resposta e que o campo é adicionado em ambos os caminhos.
- [ ] 1.2 Publicar o endpoint atualizado no Xano e validar com uma chamada somente-leitura: todos os produtos `ATIVO` retornam `image_url` (URL HTTPS) quando há imagem e `null` quando não há, nenhum retorno contém `imagem_principal`, e a chamada é única; registrar a contagem de produtos e o tempo da resposta.

## 2. Frontend (Reflex)

- [ ] 2.1 Atualizar `_public_catalog_products` em `voltix/voltix/voltix.py` para ler e validar `image_url` (HTTPS ou vazio/nulo) e continuar rejeitando `imagem_principal`; verificar com os testes unitários de parsing, incluindo URL inválida e tipo inválido.
- [ ] 2.2 Atualizar `_fetch_public_products` para remover o `asyncio.gather` de `_public_product_image` e usar a URL da listagem, mantendo `resolve_demo_image_named` como substituição por ativo local; verificar que o fluxo de listagem não chama `_public_product_image` e que o detalhe continua chamando o endpoint dedicado.

## 3. Testes

- [ ] 3.1 Atualizar os mocks e as contagens de `tests/test_public_catalog.py` de 3 para 2 requisições por carga (categorias + produtos), removendo as respostas de imagem dos `side_effect`; verificar que a suíte de catálogo público passa.
- [ ] 3.2 Adicionar teste de regressão que carrega múltiplos produtos com `image_url` na listagem e confirma `await_count == 2`, uso das URLs retornadas e nenhuma chamada a `_public_product_image`; verificar que o teste falha se o fan-out for reintroduzido.

## 4. Verificação e evidência

- [ ] 4.1 Executar `python -m unittest discover -s tests`, `python -m py_compile voltix/voltix.py` e `reflex compile`; registrar os resultados e confirmar que nenhum teste existente regrediu.
- [ ] 4.2 Com o Xano publicado, abrir `/catalogo` e a Home em uma sessão limpa; confirmar que o catálogo carrega, que as imagens são exibidas, que não há HTTP 429 e que o log mostra apenas as requisições de categorias e produtos; registrar as capturas e a contagem de requisições.
- [ ] 4.3 Registrar a evidência da correção em `docs/ap2/07-evidencias-catalogo-429.md` (nova medição de requisições e resultado do smoke) e atualizar `docs/roadmap-changes.md`; verificar que a documentação descreve a eliminação do fan-out sem contradizer as specs.
- [ ] 4.4 Confirmar que a verificação de `/catalogo` desta change fornece a evidência necessária para retomar a tarefa 5.3 da change `refine-storefront-home`, sem alterar o status ou arquivar aquela change nesta etapa.

## 5. Auditoria de escopo

- [ ] 5.1 Executar `git diff --stat` e confirmar que as alterações se limitam a `xano/api/public_catalog/products_GET.xs`, `voltix/voltix/voltix.py`, `tests/test_public_catalog.py` e aos documentos de evidência/roadmap; verificar que `requirements.txt`, versão do Reflex, lockfiles, Home, outras rotas, autenticação e administração não foram alterados.
- [ ] 5.2 Revisar o contrato final de `products_GET.xs` contra a spec `public-catalog`: imagem assinada na listagem, caminho privado ausente, endpoint dedicado preservado para o detalhe e nenhuma requisição de imagem por produto; verificar por inspeção e por teste.
