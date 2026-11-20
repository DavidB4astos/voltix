## ADDED Requirements

### Requirement: Catalog cards present price and an honest standardized placeholder
Os cards do catálogo SHALL manter a área de mídia estável e SHALL apresentar o preço mínimo real, quando disponível, entre a descrição e a ação `Ver detalhes`, no formato `a partir de R$ <valor>`. Quando a URL de imagem estiver vazia, o card e o detalhe SHALL usar o mesmo placeholder padronizado, com indicação explícita e legível por texto `Imagem não disponível`, sem atribuir outra fotografia ao produto, sem inventar crédito e sem remover os demais dados. A ausência de imagem SHALL continuar sendo tratada como conteúdo pendente, não como falha de carregamento.

#### Scenario: Card aligns image, price and action
- **WHEN** um produto com imagem e preço mínimo real aparece no catálogo
- **THEN** o card apresenta mídia, nome, descrição, `a partir de R$ <valor>` e a ação existente em uma hierarquia consistente, sem overflow

#### Scenario: Missing image has one standardized treatment
- **WHEN** a URL de imagem do produto está vazia no card ou no detalhe
- **THEN** ambos exibem o mesmo bloco visual com o texto `Imagem não disponível`, mantendo os dados e a ação do produto

#### Scenario: Placeholder never substitutes a photograph
- **WHEN** o placeholder é exibido
- **THEN** nenhuma imagem de outro modelo, nenhum preço invented e nenhum crédito de foto são atribuídos ao produto

### Requirement: Internal monetary cells stay on one line
As células monetárias das tabelas internas SHALL exibir o valor em uma única linha, com `white-space: nowrap`, alinhamento consistente e a mesma representação monetária usada no restante da aplicação. A coluna SHALL acomodar valores altos como `R$ 2999,90` sem quebrar no meio do número; se a soma das colunas exceder a largura disponível, a tabela SHALL continuar rolável horizontalmente dentro do seu contêiner, sem alterar o valor recebido do backend.

#### Scenario: High total in the internal orders table
- **WHEN** a tabela de Pedidos internos exibe um total como `R$ 2999,90`
- **THEN** o valor aparece em uma única linha e permanece legível, sem modificar o valor ou a ação da linha

## MODIFIED Requirements

### Requirement: Shared navigation and page endings are responsive
Customer-facing pages SHALL use a consistent header/navigation treatment and a consistent footer presentation. At mobile widths (below 1024 px), navigation SHALL present a compact header that keeps the Voltix identity, the primary routes and the cart/account actions visible with short labels and icons, without wrapping into multiple large rows; category shortcuts offered alongside the home header SHALL scroll horizontally with a visible affordance instead of clipping labels. Navigation links SHALL lead only to existing routes and preserve their existing access behavior. Abaixo de 1024 px, o destino `Acesso interno` SHALL permanecer dentro da viewport, sem depender de gesto de rolagem na fileira de pílulas. Nenhum selo fixo do runtime SHALL sobrepor o rodapé público ou ações no canto inferior das páginas; quando a configuração do runtime estiver disponível, ela SHALL ser usada para desativar esse selo.

#### Scenario: Customer navigates using desktop or mobile header
- **WHEN** a customer uses navigation at desktop or mobile width
- **THEN** existing route links remain identifiable and usable without changing access requirements

#### Scenario: Mobile header remains compact and fully visible
- **WHEN** the storefront header renders below 1024 px
- **THEN** the primary routes (Início, Produtos), the account/cart destinations and `Acesso interno` remain accessible within the viewport, in a compact wrapped header that does not dominate the first viewport, and no route label is clipped

#### Scenario: Home category shortcuts show that more items exist
- **WHEN** the home page offers horizontal scrolling category shortcuts on a small screen
- **THEN** the row scrolls smoothly and a visible cue (for example a fade, edge hint or scrollbar) indicates that more categories are available off-screen

#### Scenario: Internal access is reachable without horizontal scrolling
- **WHEN** o cabeçalho compacto é exibido em 375 px
- **THEN** a pílula `Acesso interno` aparece integralmente dentro da viewport, ainda que em uma segunda linha

#### Scenario: Runtime badge does not cover the footer
- **WHEN** um visitante chega ao fim de qualquer página pública ou abre o painel de Pedidos
- **THEN** o texto do rodapé e as ações do canto inferior permanecem integralmente legíveis
