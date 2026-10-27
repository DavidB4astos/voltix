## Context

Ver `proposal.md` para a motivação. O estado atual relevante:

- `xano/api/public_catalog/products_GET.xs` retorna todos os produtos `ATIVO` (ou os de uma categoria) em uma única requisição, mas a projeção não inclui `imagem_principal` e a resposta não inclui referência de imagem. Dentro do `foreach`, o endpoint já faz `db.get` de categoria e marca por produto.
- `xano/api/public_catalog/product/product_id_image_GET.xs` resolve a imagem de um produto por vez, com `db.get` e `storage.sign_private_url` (TTL 3600 s).
- `voltix/voltix/voltix.py` (`_fetch_public_products`) chama `_public_product_image(product.id)` para todos os produtos via `asyncio.gather`; em seguida, `resolve_demo_image_named` substitui a URL por ativo local quando aplicável.
- O limite do Xano Free é 10 requisições HTTP por 20 s. Com 20 produtos, uma carga fria emite ~22 requisições; o retry de 429 amplifica a rajada e o cache só é gravado quando a carga inteira conclui com sucesso.
- O fluxo de detalhe (`load_public_product_details`) já usa `_public_product_image` uma vez por clique; não faz parte do fan-out da listagem.

## Goals / Non-Goals

**Goals:**

- Reduzir a carga fria do catálogo a duas requisições HTTP (categorias + produtos), independentemente da quantidade de produtos.
- Manter a imagem principal disponível na listagem sem expor o caminho privado.
- Preservar o comportamento de imagens locais demo e o endpoint dedicado para o detalhe.
- Manter o contrato aditivo e a degradação segura se o backend novo ainda não estiver publicado.

**Non-Goals:**

- Alterar layout, componentes visuais, textos, rotas ou estados da Home/catálogo.
- Alterar o TTL do cache, adicionar paginação ou mudar a ordenação de produtos.
- Otimizar o N+1 interno de categoria/marca em `products_GET.xs`.
- Baixar/completar imagens demo, recomprimir imagens ou alterar o manifesto.
- Alterar o fluxo de detalhe, autenticação, autorização, carrinho, checkout ou administração.
- Alterar o plano do Xano, dependências, versão do Reflex ou lockfiles.

## Decisions

### 1) Incluir `image_url` assinada na resposta de `products_GET.xs`

A listagem passa a ser a fonte da referência de imagem. A projeção interna de `produto` inclui `imagem_principal` nos dois ramos (com e sem filtro de categoria); no `foreach` já existente, o endpoint assina a URL quando o caminho existe e adiciona `image_url` ao objeto retornado. A resposta continua sendo uma lista de objetos com os campos atuais; o caminho privado não é incluído.

**Por que:** elimina N requisições HTTP com uma única chamada que já itera todos os produtos. Não exige novo endpoint, novo parâmetro de entrada nem alteração do contrato de detalhe. A assinatura de N URLs ocorre dentro da mesma requisição, que é o que conta para o limite do plano.

**Alternativas consideradas:**

- **Endpoint em lote (`/products/images?ids=...`)**: exigiria novo endpoint, tratamento de lista de IDs e um segundo round-trip; rejeitado por complexidade desnecessária para o tamanho atual do catálogo.
- **Retornar apenas `has_image` e carregar imagens sob demanda**: o catálogo continuaria fazendo N requisições para exibir todos os cards; rejeitado porque não elimina a causa do 429.
- **Incluir `imagem_principal` bruta na resposta**: rejeitado por expor o caminho privado e violar a spec de segurança.

### 2) Manter o endpoint dedicado de imagem para o detalhe

`products/{id}/image` permanece como está e continua sendo usado por `load_public_product_details` (uma requisição por clique). A mudança remove apenas o fan-out da listagem.

**Por que:** limita o escopo e preserva o comportamento do detalhe, que já funciona e não participa da carga fria do catálogo.

**Alternativa considerada:** mover a imagem para o endpoint de detalhe e remover o endpoint dedicado. Rejeitada: alteraria o contrato de detalhe e ampliaria a mudança sem necessidade para o 429.

### 3) O frontend consome a imagem da listagem e mantém a resolução local demo

`_public_catalog_products` passa a ler `image_url` (string HTTPS ou ausente/nula), mantendo a rejeição de `imagem_principal`. `_fetch_public_products` deixa de chamar `_public_product_image` para cada produto; usa a URL da listagem e aplica `resolve_demo_image_named` por cima. Assim, ativos locais aprovados continuam tendo prioridade, e os demais usam a URL assinada da listagem ou o placeholder.

**Por que:** a URL já vem pronta na resposta; a resolução local é uma substituição de apresentação, não uma nova chamada de rede.

**Alternativa considerada:** remover `resolve_demo_image_named` do fluxo de listagem. Rejeitada: quebraria a preferência por ativos locais aprovados e a spec de imagens demo.

### 4) Contrato aditivo e ordem de implantação

O novo campo é aditivo e o endpoint antigo continua disponível. A ordem recomendada é publicar o Xano primeiro e depois o frontend. Se o frontend novo rodar contra o endpoint antigo, `image_url` estará ausente e será tratado como vazio; o catálogo ainda carrega com duas requisições, exibindo placeholders até o backend ser publicado.

**Por que:** evita indisponibilidade durante a janela de implantação e permite rollback independente.

**Alternativa considerada:** exigir o campo e falhar quando ausente. Rejeitada: criaria uma falha desnecessária durante a implantação e não melhoraria a segurança.

### 5) Não alterar cache, paginação ou o N+1 de categoria/marca

O TTL de 30 s e o single-flight permanecem. O `products_GET.xs` continua fazendo `db.get` de categoria/marca por produto; isso não gera requisições HTTP adicionais e não é a causa do 429.

**Por que:** a mudança mínima que resolve o limite é a eliminação do fan-out de imagens; outras otimizações podem ser feitas em changes próprias.

## Risks / Trade-offs

- **Assinar N URLs dentro de uma requisição pode aumentar a latência do `products_GET`** → medir o tempo da resposta com o catálogo real; se ficar próximo do limite de execução do Xano, reavaliar um endpoint em lote em change posterior.
- **Resposta maior por incluir URLs assinadas** → o impacto é de poucos KB para 20 produtos; aceitável para o catálogo atual.
- **URL assinada expira em 3600 s** → o cache do catálogo é de 30 s; uma nova carga renova a URL. Abas abertas por mais de 1 h já carregaram as imagens no navegador; recarregar a página busca uma nova listagem.
- **Vazamento do caminho privado** → a resposta é montada campo a campo e não inclui `imagem_principal`; adicionar teste/verificação do contrato e manter a rejeição no parser do frontend.
- **Backend novo não publicado** → o parser trata ausência de `image_url` como vazio; o catálogo carrega, mas sem imagens Xano até a publicação. Publicar o Xano primeiro.
- **Regressão nas contagens de requisições dos testes** → atualizar os mocks e adicionar um teste explícito de duas requisições por carga fria.
- **O N+1 de categoria/marca permanece** → registrado como dívida separada; não afeta o limite HTTP nem o escopo desta change.

## Migration Plan

1. Atualizar `products_GET.xs`: incluir `imagem_principal` na projeção interna dos dois ramos, assinar a URL no `foreach` e adicionar `image_url` ao objeto de resposta; confirmar que o caminho privado não aparece no JSON.
2. Publicar o endpoint no Xano e verificar o contrato com uma chamada somente-leitura: todos os produtos `ATIVO`, `image_url` presente ou nulo, nenhum `imagem_principal`, uma única requisição.
3. Atualizar `_public_catalog_products` e `_fetch_public_products` no Reflex; remover o `asyncio.gather` de imagens da listagem, mantendo `_public_product_image` para o detalhe.
4. Atualizar `tests/test_public_catalog.py` (payloads, side effects e contagens de 3 para 2) e adicionar o teste de carga com duas requisições e sem chamadas de imagem por produto.
5. Executar `python -m unittest discover -s tests`, `python -m py_compile voltix/voltix.py` e `reflex compile`.
6. Fazer o smoke de `/catalogo` e da Home, medir as requisições no log e registrar a evidência em `docs/ap2/07-evidencias-catalogo-429.md`.
7. Rollback: reverter `products_GET.xs` e o parser/fetch do frontend; o endpoint dedicado de imagem permanece, restaurando o comportamento anterior. Nenhum dado é migrado.

## Open Questions

Nenhuma pendente para iniciar a implementação.
