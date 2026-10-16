## Context

A Home pública (`/`) tem base sólida com tokens e componentes reutilizáveis já existentes em `voltix/voltix.py`:
- Tokens: `COLOR_NAVY`, `COLOR_NAVY_SOFT`, `COLOR_BLUE`, `COLOR_CYAN`, `COLOR_CYAN_DARK`, `COLOR_SURFACE`, `COLOR_CARD`, `COLOR_TEXT`, `COLOR_TEXT_MUTED`, `COLOR_BORDER`, semânticos; `RADIUS`, `CARD_SHADOW`, `FOCUS_STYLE`.
- Componentes: `site_header`, `site_footer`, `page_shell`, `surface_card`, `section_heading`, `feedback_text`, `status_badge`, `primary_button`, `secondary_button`, `empty_state`, `loading_text`, `status_panel`.
- Seções: `hero_section`, `benefits_strip`, `categories_section`, `products_section` em `home_page()`.
- Dados públicos: `State.public_categories`, `State.public_products`, `State.public_catalog_loading`, `State.public_catalog_message`, `State.load_public_catalog`.
- Links/rotas: `/`, `/catalogo`, `/cliente`, `/carrinho`, `/interno`; CTA "Explorar produtos" → `/catalogo`.

Inspeção via Chrome DevTools (página atual): sem overflow horizontal em desktop/mobile, estados presentes, CTA e navegação corretos. A análise de proporções indica espaço para tornar o Hero mais impactante, categorias mais expressivas e vitrine com hierarquia mais moderna, sem alterar comportamento.

### Análise das referências (Chrome DevTools)

**KaBuM! (`https://www.kabum.com.br/`) — estrutura comercial:**
- Header ~128px, fundo navy `rgb(0,77,142)`, 29 links, com **barra secundária de categorias** (Mundo Gamer, Hardware, PC Gamer, Computadores, Periféricos…). Faixa promocional fina no topo (~390×36).
- Hero em **carrossel** (~722×342) com painéis laterais; viewport de conteúdo full-bleed (~1521px).
- Atalhos de categorias como tiles com imagem; seções "Recomendados para você", "Mais vendidos…".
- Cards de produto ~230×366, imagem ~162px, **sem sombra/raio** (flat), com informação densa (cupom, preço, parcelamento).
- Tipografia: system sans, base 16px; títulos de seção 20px/600.

**Apple Store (`https://www.apple.com/br/store`) — acabamento premium:**
- Nav global fino (~44px), translúcido/overlay, minimalista, 229 links (mega-menu).
- Tipografia base 17px (SF Pro); **`h1` 80px/600**; títulos de seção 28px/600 — escala display generosa.
- Cards retrato ~400×500, **imagem dominante** (preenche o card), **raio 18px** (45 ocorrências), fundo claro; badge + título + subtítulo + preço ("A partir de…").
- Seções organizadas em **carrossel horizontal** (linhas com scroll, larguras 2760–4763px vs 1521px de viewport).
- Muito whitespace e hierarquia visual clara.

**Nenhum dos sites bloqueou a inspeção automatizada.** Não houve tentativa de contornar proteções.

**Comparação com a Home atual (local):** grids 1/3/4 colunas, título de hero modesto, **0 imagens** em uso (fallback de gradiente em hero/categorias/produtos), documento curto (~1715px). Referências sugerem: menos densidade horizontal, escala tipográfica maior, cantos mais arredondados, cards com imagem dominante e mais respiro — tudo alcançável apenas no frontend, exceto o que depende de imagens reais.

### Disponibilidade de dados (verificado em `voltix/voltix.py`)

- `PublicProductEntry` expõe `name`, `description`, `technical_specifications`, `category_name`, `brand_name`, **`image_url`** e `variations` (com `price`, `available_quantity`).
- A Home **já usa** `product.image_url` com fallback de gradiente (`products_section.tile`), mas no ambiente atual `image_url` está vazio → 0 imagens. Exibir a foto real só depende de haver imagem cadastrada no Xano (fora do escopo alterar dados).
- Banner de hero e imagens de categoria **não têm fonte de dados** → permanecem como gradientes (não inventar assets).
- Preço/disponibilidade **existem** nos dados, mas exibi-los na Home seria **informação nova** (não apenas apresentação) → requer aprovação explícita; por padrão, fora do escopo.

## Goals / Non-Goals

**Goals:**
- Transformação visual perceptível da Home (composição, hierarquia, tipografia, elevação) mantendo identidade azul/ciano.
- Hero com muito maior impacto visual, mantendo único CTA "Explorar produtos" e fallback existente.
- Categorias com cards mais expressivos e profissionais.
- Vitrine de produtos com hierarquia moderna (imagem dominante, conteúdo claro, área de ação bem definida).
- Navbar, benefícios, footer com acabamento consistente e responsivo.
- **Estrutura comercial (inspiração KaBuM!)**: barra secundária de categorias no topo, hierarquia de header mais próxima de e-commerce.
- **Acabamento premium (inspiração Apple Store)**: tipografia display de maior escala, mais respiro vertical, cantos mais arredondados e cards de imagem dominante.
- Garantir sem overflow horizontal em 375/768/1280/1536 px.

**Non-Goals:**
- Alterar rotas, `State`, eventos/handlers, chamadas Xano, autenticação/autorização, carrinho/checkout/pedidos/CRM, Domain Model.
- Adicionar dependências, assets ou novos componentes complexos.
- Alterar textos funcionais, mensagens de estado ou links existentes.
- Inventar informações comerciais, preços ou imagens.
- Modificar outras páginas/rotas além de `/`.

## Decisions

### 1) Reorganização estrutural do Hero (permitida)
Permite-se **reorganizar** a estrutura interna de `hero_section()` (layout, proporções, ordem visual dos blocos) usando apenas Reflex/Radix/Tailwind já disponíveis. Manter CTA único, fallback quando sem imagem, e todos os handlers intactos.

**Alternativa:** apenas ajustes incrementais. **Rejeitada** por não atingir transformação perceptível.

### 2) Cards de categorias mais expressivos
Reorganizar `categories_section()` para dar maior peso ao cabeçalho visual (gradiente existente), melhor espaçamento interno, hierarquia clara (nome + descrição opcional) e elevação mais perceptível no hover. **Não** alterar fonte de dados (`State.public_categories`), link `/catalogo` ou `empty_state`.

**Alternativa:** manter cards atuais. **Rejeitada**.

### 3) Vitrine com hierarquia moderna
Reorganizar `products_section()` tiles: área de imagem com maior destaque (proporção definida), conteúdo empilhado com ritmo claro (marca/categoria/nome), área "Ver no catálogo" bem definida. Preservar integralmente estados existentes, `State.load_public_catalog`, disabled conforme loading, e links `/catalogo`. **Não** alterar comportamento de detalhe/adicionar ao carrinho (não existe na Home).

**Alternativa:** ajustes incrementais. **Rejeitada**.

### 4) Navbar/Benefícios/Footer com acabamento consistente
Pequenas reorganizações visuais em `site_header()`, `benefits_strip()`, `site_footer()` (melhor separação, hierarquia, respiro responsivo), sem alterar rotas/links/textos.

### 5) Usar apenas tokens existentes
Todos refinamentos usam tokens já definidos. Elevação via `CARD_SHADOW` + hover ajustado com mesmo tom. Sem novos valores cromáticos.

### 6) Responsividade sem overflow horizontal
Rever grids/flex com breakpoints existentes (initial/sm/md/lg). Garantir `max_width` coerente, evitar larguras fixas problemáticas. Validar 375/768/1280/1536.

### 7) Estrutura comercial inspirada na KaBuM! (barra de categorias)
Adicionar uma **barra secundária de categorias** no topo (abaixo do header principal), alimentada por `State.public_categories` já existente, com cada item apontando para `/catalogo`. É estrutura de navegação nova, mas usa **dados e rotas existentes** (sem novas chamadas Xano, sem novas rotas, sem novos `State`). Em mobile, colapsa/rola horizontalmente.

**Alternativa:** manter header simples de uma linha. **Rejeitada** por não capturar a estrutura comercial de referência.

### 8) Acabamento premium inspirado na Apple Store
Maior escala tipográfica nos títulos (hero e títulos de seção), mais respiro vertical entre seções, cantos mais arredondados (valor **local** da Home, ex. ~16px, sem alterar o token global `RADIUS`), e cards de produto com **imagem dominante** (proporção retrato). Cards usam `image_url` real quando presente; fallback de gradiente quando ausente.

**Alternativa:** manter densidade/raio atuais. **Rejeitada** por não atingir percepção premium.

### 9) Imagens: apenas dados reais, sem assets inventados
Banner de hero e imagens de categoria **não têm fonte de dados** → permanecem gradientes. Somente imagens reais de produto (`image_url`) são exibidas. Nenhum asset/placeholder inventado. Upload de imagens de produto ocorre fora desta change (Xano/painel interno).

### 10) Preço/disponibilidade na Home: fora do escopo (requer aprovação)
Os dados possuem `price`/`available_quantity`, mas exibi-los na Home adiciona **informação comercial nova** (não é apenas apresentação). Fica **fora do escopo** desta change salvo aprovação explícita; se aprovado, será tratado como item separado para não misturar com a mudança estritamente visual.

## Análise de referências → mudanças propostas

| Área | KaBuM! (estrutura) | Apple Store (acabamento) | Proposta Voltix (frontend) | Depende de imagem? |
|---|---|---|---|---|
| Header | Barra de categorias + busca | Nav fino/overlay | Barra secundária de categorias (dados existentes) | Não |
| Hero | Carrossel + painéis | Escala display enorme | Headline maior + composição equilibrada; manter gradiente | Banner real: sim (indisponível) |
| Categorias | Tiles com imagem | Tiles grandes arredondados | Tiles maiores, cantos arredondados, gradiente existente | Tile real: sim (indisponível) |
| Produtos | Cards densos flat | Retrato imagem-dominante, raio 18px | Tiles retrato, imagem dominante, raio maior | Sim (`image_url` real) |
| Tipografia | Títulos 20px | `h1` 80px / seções 28px | Escalar títulos e respiro | Não |
| Superfícies | Flat | Cantos arredondados + whitespace | Raio local maior + elevação sutil | Não |

## Plano de implementação priorizado (curto)

1. **P1 — Tipografia, respiro e raio (premium, só visual)**: escalar títulos e aumentar espaçamento vertical; raio local maior nos cards da Home. Baixo risco, não depende de imagens.
2. **P2 — Hero Apple-style**: headline de maior escala e composição mais equilibrada, mantendo CTA único e gradiente.
3. **P3 — Tiles de produto retrato/imagem-dominante**: proporção retrato + raio maior, usando `image_url` real com fallback. Ganho pleno depende de imagens cadastradas.
4. **P4 — Categorias maiores/arredondadas** (estrutura KaBuM com fallback de gradiente).
5. **P5 — Barra secundária de categorias no header** (estrutura comercial; usa dados/rotas existentes).
6. **P6 (opcional, requer aprovação) — Preço/disponibilidade nos tiles**: informação nova; tratar separadamente.

Itens P1–P5 são **apenas frontend** e não dependem de imagens reais (rendem melhor com elas). P6 depende de aprovação de escopo.

## Risks / Trade-offs

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| Alterar handler/State acidentalmente | Baixa | Alto | Editar apenas apresentação/estrutura visual. Nunca `on_click`, eventos, `State.*`, rotas. |
| Quebra de layout em mobile com nova estrutura | Baixa | Médio | Testar empilhamento em 375px, manter `wrap`, grids responsivos, sem overflow horizontal. |
| Reduzir legibilidade com novos espaçamentos | Baixa | Médio | Manter line-height legível, contraste com tokens existentes, validar hierarquia. |
| Regressão em estados da vitrine | Baixa | Médio | Preservar `loading_text`, painel de erro com "Tentar novamente" → `State.load_public_catalog`, `empty_state`. Não alterar textos/handlers. |
| Impacto sutil insuficiente | Baixa | Baixo | Foco em proporções (Hero mais largo/impactante), elevação perceptível, melhor hierarquia — mudanças visuais concretas. |

## Migration Plan

1. **Tipografia, respiro e raio (premium)**: escalar títulos (hero/seções), aumentar espaçamento vertical, aplicar raio local maior nos cards da Home — sem alterar o token global `RADIUS`.
2. **Hero**: reorganizar `hero_section()` (headline de maior escala, proporções, spacing, bloco visual mais expressivo), preservar CTA único e fallback de gradiente.
3. **Benefícios**: refinar `benefits_strip()` (ícones destacados, alinhamento, separação).
4. **Categorias**: reestruturar cards em `categories_section()` (área visual mais forte, tiles maiores/arredondados, elevação, hierarquia). Preservar dados/estados e gradiente (sem imagens inventadas).
5. **Destaques**: reestruturar tiles em `products_section()` (retrato/imagem-dominante com `image_url` real + fallback, conteúdo claro, área ação). Preservar estados/handlers/links.
6. **Estrutura comercial**: adicionar barra secundária de categorias no header usando `State.public_categories` (links → `/catalogo`).
7. **Navbar/Footer/Page shell**: ajustes leves em `site_header()`, `site_footer()`, `page_shell()` se necessário para nova composição/respiração.
8. **Validação**: responsividade 375/768/1280/1536 (sem overflow X), `reflex compile --dry`, testes unitários existentes, inspeção DevTools, foco teclado preservado.
9. **Verificação comportamental**: confirmar CTA→`/catalogo`, links header/footer/barra de categorias, "Tentar novamente" funcional, sem alteração de dados/rotas.
