## Why

A Home pública (`/`) tem base sólida, mas ainda não transmite a presença visual esperada de um e-commerce de tecnologia premium. A composição atual é organizada, porém pouco marcante: o Hero não cria impacto suficiente, as categorias competem visualmente entre si, e a vitrine de destaques carece da hierarquia clara típica de lojas modernas.

O objetivo é **transformar visualmente** a Home para transmitir mais solidez e profissionalismo, elevando significativamente a percepção de qualidade, sem alterar dados, comportamento, rotas, handlers ou integrações com Xano.

## Referências visuais (inspiração, não cópia)

A composição deve combinar duas referências, preservando a identidade azul/ciano do Voltix:

- **KaBuM! (`kabum.com.br`)** — referência de **estrutura comercial**: barra promocional/institucional no topo, header azul com busca em destaque, **barra secundária de categorias**, banner principal em carrossel com painéis laterais, atalhos de categorias, e vitrines de produtos em linhas horizontais com cards densos.
- **Apple Store (`apple.com/br/store`)** — referência de **acabamento premium**: tipografia display de grande escala, muito respiro (whitespace), cantos arredondados generosos (~18px), cards de imagem dominantes (proporção retrato ~4:5), seções em carrossel horizontal e cromo de navegação minimalista.

Inspeção via Chrome DevTools confirmou: KaBuM header ~128px (navy `rgb(0,77,142)`, 29 links + barra de categorias), hero carrossel ~722×342, cards de produto ~230×366 (imagem ~162px, sem sombra); Apple tipografia base 17px, `h1` de 80px/600, títulos de seção 28px/600, cards ~400×500 com raio 18px e imagem preenchendo o card. Nenhum dos dois impediu a inspeção automatizada.

**Nada de código, imagens, logos ou identidade visual será copiado.** A inspiração é estrutural e de acabamento, adaptada aos tokens e ao conteúdo existentes do Voltix.

## What Changes

- **Hero (transformação perceptível)**: reposicionar headline, subtítulo, bloco visual e CTA para criar uma composição muito mais marcante. Reorganizar o layout com proporções mais equilibradas (texto com maior respiro à esquerda, painel visual mais expressivo à direita), mantendo **único** CTA primário "Explorar produtos" e o fallback existente quando não houver imagem. O bloco visual passa a ter maior peso e presença sem mascarar o conteúdo.
- **Navbar**: dar acabamento mais profissional (maior hierarquia, distinção mais clara entre links comerciais e "Acesso interno"), com melhor comportamento responsivo mobile. Rotas e links permanecem inalterados.
- **Tipografia**: escalar títulos de forma mais expressiva, com melhor tracking e line-height, para criar hierarquia visual mais forte (inspiração Apple: escala display generosa, títulos de seção maiores), sem alterar textos funcionais existentes.
- **Categorias (cards visualmente mais expressivos)**: reorganizar estruturalmente os cards para darem mais destaque. Cada card terá área visual mais forte (cabeçalho/área de identidade com gradiente existente), melhor separação entre elementos, hierarquia mais clara (nome + descrição opcional) e elevação mais perceptível no hover. Utiliza apenas dados existentes (`State.public_categories`), preserva `empty_state` e link `/catalogo`.
- **Destaques (vitrine com hierarquia moderna)**: reorganizar estruturalmente os tiles para aproximar-se da composição de e-commerce moderno. A área de imagem passa a ter maior destaque (proporção mais definida, inspiração Apple de card retrato com imagem dominante e cantos arredondados), com conteúdo organizado de forma mais vertical e clara (marca, categoria, nome e área de ação bem definida). Usa `product.image_url` quando disponível e o fallback de gradiente existente quando não houver imagem real. Preservar integralmente estados (loading/erro/vazio), `State.load_public_catalog` e links para `/catalogo`.
- **Barra de categorias (estrutura comercial)**: adicionar uma barra secundária de navegação por categorias no topo (inspiração KaBuM), alimentada por `State.public_categories` já existentes, apontando para `/catalogo`. Sem novas rotas, sem novas chamadas de dados.
- **Cantos e superfícies premium**: adotar raio de canto mais generoso e elevação sutil nos cards da Home (inspiração Apple), usando tokens/valores locais da Home (sem alterar o token global `RADIUS` usado por outras páginas).
- **Benefícios**: acabamento mais coeso e destacado (ícones com maior presença, alinhamento refinado, superfície com melhor separação visual), sem alterar textos ou ícones existentes.
- **Cards/superfícies**: elevação e definição mais perceptíveis (sombra/hover mais definidos), utilizando **apenas** tokens existentes (`surface_card`, `RADIUS`, `CARD_SHADOW`, `COLOR_*`, `FOCUS_STYLE`). Sem novos valores cromáticos ou dependências.
- **Footer**: maior respiro e separação visual, preservando integralmente os textos institucionais.

**Fora do escopo:** alteração de rotas, Xano/APIs, `State`, eventos, handlers, autenticação, autorização, carrinho, checkout, pedidos, CRM, Domain Model, criação de componentes complexos, adição de dependências. **Não** inventar informações comerciais, preços, promoções, banners ou imagens. **Não** copiar código, imagens, logos ou identidade visual das referências. Não exibir preços/disponibilidade nos tiles sem aprovação explícita (é informação nova, não apenas apresentação). Imagens de banner/categoria não estão disponíveis e permanecem como gradientes; apenas imagens reais de produtos (`image_url`) podem ser exibidas.

## Capabilities

### New Capabilities
- `redesign-home-voltix`: transformação visual perceptível da Home pública (`/`), responsiva desktop e mobile, **sem mudança comportamental**.

### Modified Capabilities
Nenhuma. Mudança estritamente visual.

## Impact

- **Arquivos afetados (somente apresentação)**: `voltix/voltix.py` — principalmente `home_page()` (`hero_section`, `benefits_strip`, `categories_section`, `products_section`). Eventuais ajustes em `site_header()`, `site_footer()` e `page_shell()` apenas quando necessário para suportar a nova composição estrutural, sempre sem alterar comportamento.
- **Sem impacto em dados/negócio**: nenhuma alteração em chamadas Xano, `State` (fields/events), permissões, rotas ou textos funcionais.
- **Sem novas dependências**: utiliza apenas Reflex/Radix/Tailwind já configurados.
- **Testes**: não requer novos testes. Testes unitários existentes devem continuar passando. `reflex compile --dry` deve ser válido.
- **Alcance**: exclusivamente Home pública (`/`).
