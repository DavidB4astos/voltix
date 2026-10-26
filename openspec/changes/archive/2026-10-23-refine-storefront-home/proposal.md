## Why

A Home pública (`/`) já tem hero, benefícios, categorias e vitrine, mas ainda não sustenta a percepção de e-commerce de tecnologia premium esperada na AP2: a hierarquia é genérica, a vitrine se comporta como lista extensa e não há bloco editorial que dê contexto de uso aos produtos. O kit `docs/voltix-frontend-kit.zip` entrega direção visual A+B (Studio Premium + Galeria de Produto) e componentes de referência que podem ser aproveitados sem reescrever a aplicação.

A verificação da Home também expôs um bloqueio no catálogo público: cada carga emite uma requisição de imagem por produto, excedendo o limite do Xano Free e retornando HTTP 429. Como a Home depende desse mesmo fluxo e a correção é pequena e diretamente necessária para concluir a verificação, ela é absorvida nesta change.

## What Changes

- **Hero editorial premium**: reorganizar a primeira dobra em superfície escura (navy), sem eyebrow, com título de forte hierarquia, texto de apoio, um único CTA "Explorar produtos" para `/catalogo` e mídia composta apenas por ativo local aprovado; se a fotografia não funcionar bem na composição, usar painel gráfico próprio construído com os tokens do projeto. Nenhuma imagem externa é permitida.
- **Vitrine curada**: substituir a grade extensa por uma seleção curta de no máximo 4 produtos, formada **somente** por correspondências verificáveis entre o produto e uma imagem aprovada em assets locais. Não há seleção por posição nem fallback para produtos sem correspondência; se houver menos elegíveis, menos cards são renderizados. Exibir marca, categoria, nome e imagem real, **sem preço** e com crédito obrigatório.
- **Bloco editorial**: adicionar uma seção de contexto ("Tecnologia em contexto") com fotografia aprovada de assets locais, crédito, título curto, uma frase de apoio e no máximo um CTA para `/catalogo`.
- **Benefícios**: converter a faixa de três cards idênticos em uma faixa linear, preservando textos e ícones existentes.
- **Categorias**: substituir os cards atuais por cards tipográficos premium, mantendo `State.public_categories` e o destino `/catalogo`; nenhuma imagem fictícia é criada.
- **Créditos de fotografia**: toda fotografia exibida na Home cuja licença exija atribuição SHALL apresentar autor, licença e link da fonte. A ausência de créditos no catálogo fica registrada como pendência separada, fora desta change.
- **Camada visual isolada**: adicionar CSS próprio da Home com prefixo `vx-`, carregado pelo app, integralmente escopado à Home para não alterar administração, catálogo, carrinho, checkout ou conta.
- **Correção absorvida de imagens do catálogo**: incluir `image_url` assinada na listagem pública (`products_GET.xs`), consumir esse campo no frontend e remover a requisição de imagem por produto; o endpoint dedicado permanece para o detalhe. A carga fria passa a emitir no máximo duas requisições (categorias + produtos), independentemente da quantidade de produtos, sem expor o caminho privado.
- **Acessibilidade e responsividade**: um único H1, ordem semântica de títulos, foco visível, alvos de toque de 44 px, `alt` descritivo, `prefers-reduced-motion` e ausência de overflow horizontal em 360–1440 px.

**Fora do escopo:** checkout, autenticação, administração, banco de dados, outras alterações de Xano/XanoScript ou APIs além da correção de imagens descrita, rotas, preços, estoque exibido, novas dependências, imagens externas ou de terceiros, alteração de header/footer compartilhados, reescrita de `voltix.py` além das seções da Home e do fluxo de imagens do catálogo, implementação visual de catálogo/detalhe/carrinho, e qualquer alteração em `requirements.txt`, versão do Reflex, dependências ou lockfiles.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `public-home`: hero editorial (superfície escura, sem eyebrow e CTA único), vitrine curada por correspondência verificável e sem preço, bloco editorial com foto aprovada, cards de categoria tipográficos, créditos obrigatórios de fotografia, e requisito de isolamento visual/acessibilidade da Home.
- `public-catalog`: a listagem pública entrega a referência de imagem de cada produto na própria resposta, com URL assinada temporária; o cliente não emite uma requisição de imagem por produto e o endpoint dedicado permanece para o detalhe.

## Impact

- **Código**: `voltix/voltix.py` (`home_page()` e suas seções internas, `_public_catalog_products`, `_fetch_public_products`), uma variável derivada de apresentação em `State`, e `rx.App` para registrar o novo stylesheet.
- **Backend**: `xano/api/public_catalog/products_GET.xs` passa a incluir `imagem_principal` na projeção interna, assinar a URL por produto e retornar `image_url`; o caminho privado permanece omitido. O endpoint dedicado `product/{product_id}/image_GET.xs` e o fluxo de detalhe não mudam.
- **Assets**: novo `assets/voltix-home.css`; reutiliza as 3 fotografias já aprovadas em `assets/demo/` (nenhuma imagem nova).
- **Dados/negócio**: a única alteração de backend é a entrega de imagem na listagem pública. Nenhuma alteração em elegibilidade de produtos, carrinho, checkout ou autorização. Nenhum preço passa a ser exibido.
- **Dependências**: nenhuma nova; Reflex/Radix/Tailwind já configurados.
- **Testes**: `tests/test_public_catalog.py` atualizado para duas requisições por carga fria, com teste de regressão contra o fan-out de imagens; suíte existente deve permanecer verde; validação por `py_compile`, `reflex compile` e inspeção visual em múltiplas larguras.
