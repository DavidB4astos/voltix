## ADDED Requirements

### Requirement: Public catalog exposes the minimum active variation price
A listagem pública de produtos SHALL incluir, para cada produto `ATIVO`, o campo `preco_minimo` com o menor `preco` entre suas variações `ATIVO`, sem exigir autenticação e sem alterar os demais campos da resposta. Quando o produto não tiver variação `ATIVA`, o campo SHALL ser nulo ou vazio e o cliente SHALL omitir o preço do card, sem inventar valor, promoção ou disponibilidade. Quando presente, o card do catálogo SHALL exibir `a partir de R$ <valor>` no formato monetário consolidado (`R$ <inteiro>,<fração>` com exatamente duas casas), alinhado à imagem, à descrição e à ação `Ver detalhes`. O painel de detalhes, os preços das variações e as regras de carrinho SHALL permanecer inalterados.

#### Scenario: Product has active variations
- **WHEN** a listagem pública retorna um produto com uma ou mais variações `ATIVO` de preços diferentes
- **THEN** `preco_minimo` contém o menor preço entre essas variações e o card exibe `a partir de R$ <valor>`

#### Scenario: Product has no active variation
- **WHEN** a listagem pública retorna um produto sem variação `ATIVA`
- **THEN** `preco_minimo` é nulo ou vazio e o card não exibe nem inventa preço

#### Scenario: Price follows the consolidated money format
- **WHEN** `preco_minimo` é `119.9`
- **THEN** o card exibe `a partir de R$ 119,90`, sem aspas, escapes ou recálculo do valor do backend

#### Scenario: Detail and cart behavior stay unchanged
- **WHEN** o visitante abre os detalhes a partir de um card que exibe preço
- **THEN** os preços das variações e a ação de adicionar ao carrinho mantêm exatamente o comportamento anterior
