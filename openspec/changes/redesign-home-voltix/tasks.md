## 1. Revisão e preparação
- [x] 1.1 Ler `voltix/voltix.py` focando em `home_page()` (`hero_section`, `benefits_strip`, `categories_section`, `products_section`), `site_header()`, `site_footer()`, `page_shell()` e tokens existentes.
- [x] 1.2 Confirmar escopo estritamente visual; não tocar `State`, eventos/handlers, rotas, chamadas Xano, auth/autorização.
- [x] 1.3 Revisar proposta/design atualizados e alinhar com transformação perceptível desejada.

## 2. Hero transformado (perceptível)
- [x] 2.1 Reorganizar estruturalmente `hero_section()` para maior impacto: melhorar proporções entre texto e bloco visual (grid responsivo), aumentar respiro e hierarquia.
- [x] 2.2 Elevar presença do bloco visual (gradiente existente ou imagem) mantendo alturas consistentes (`min_height="280px"`, `max_height="380px"`), `object_fit`, radius, sombra. Preservar fallback quando sem imagem.
- [x] 2.3 Refinar headline/subtítulo (escala/tracking/line-height) sem alterar textos. Manter **único** CTA primário "Explorar produtos" → `/catalogo`, com estilos/hover/focus existentes.
- [x] 2.4 Validar empilhamento mobile e sem overflow horizontal.

## 3. Benefícios com acabamento mais coeso
- [x] 3.1 Reorganizar `benefits_strip()` para dar maior presença aos ícones, melhor alinhamento ícone+texto e separação entre itens.
- [x] 3.2 Manter textos/ícones existentes e uso de `surface_card`. Grid responsivo 1/2/3 cols sem overflow.
- [x] 3.3 Aplicar elevação sutil consistente usando tokens existentes.

## 4. Categorias com cards mais expressivos
- [x] 4.1 Reestruturar `categories_section()` cards: área visual mais forte (manter gradiente existente), melhor espaçamento interno, hierarquia clara (nome + descrição opcional).
- [x] 4.2 Elevação mais perceptível no hover mantendo tokens. Garantir `height="100%"` e alinhamento consistente.
- [x] 4.3 Preservar `empty_state` quando sem categorias, dados via `State.public_categories`, link `/catalogo` inalterado.
- [x] 4.4 Validar grid 1/2/3/4 cols responsivo sem desalinhamento.

## 5. Vitrine de destaques com hierarquia moderna
- [x] 5.1 Reestruturar `products_section()` tiles: área de imagem dominante (180px, `object_fit="cover"`), conteúdo organizado (marca/categoria/nome) com melhor ritmo, área "Ver no catálogo" bem definida.
- [x] 5.2 Preservar link `/catalogo` em cada tile. **Não** alterar comportamento de detalhe/adicionar ao carrinho.
- [x] 5.3 Preservar integralmente estados: `loading_text`, painel de erro com "Tentar novamente" → `State.load_public_catalog` (disabled conforme `State.public_catalog_loading`), `empty_state`. Não alterar textos/handlers.
- [x] 5.4 Aplicar elevação mais perceptível mantendo tokens. Grid 1/2/3 cols responsivo, sem overflow horizontal.

## 6. Navbar, Footer e Page Shell (acabamento)
- [x] 6.1 Aprimorar `site_header()` visualmente (hierarquia, distinção links comerciais vs `/interno`, responsividade mobile) sem alterar rotas/links/textos. Preservar separador interno, `logo_href`, `wrap="wrap"`.
- [x] 6.2 Aprimorar `site_footer()` (respiro, separação visual) preservando textos "Projeto acadêmico" e "Preços e pagamentos simulados".
- [x] 6.3 Ajustar `page_shell()` **apenas** se necessário para suportar nova composição (apresentação-only). Não alterar lógica.

## 7. Validação e verificação
- [x] 7.1 Testar responsividade 375, 768, 1280, 1536 px — **sem overflow horizontal**.
- [x] 7.2 Inspecionar via Chrome DevTools: sem erros console, sem falhas network, CTA/links corretos, estados visíveis.
- [x] 7.3 Verificar foco teclado (`FOCUS_STYLE`) preservado.
- [x] 7.4 `reflex compile --dry` sem erros.
- [x] 7.5 `python -m unittest discover -s tests -p "test_*.py"` (todos existentes passando).
- [x] 7.6 Revisar manualmente: Hero, benefícios, categorias, destaques, header, footer — confirmar transformação perceptível e **apenas visual**.
- [x] 7.7 `openspec validate redesign-home-voltix` válido.
- [x] 7.8 Conferir: nenhum dado/handler/rota/Xano alterado.

## 8. Refinamentos com referências (KaBuM! / Apple Store)

> Escopo estritamente visual/frontend. Não implementar sem aprovação. Não alterar Xano, `State`, handlers, rotas ou funcionalidades.

- [x] 8.1 Escalar tipografia (headline do hero e títulos de seção) e aumentar o respiro vertical entre seções (inspiração Apple).
- [x] 8.2 Aplicar raio de canto local maior e elevação sutil nos cards da Home, sem alterar o token global `RADIUS`.
- [x] 8.3 Hero: headline de maior escala e composição mais equilibrada (inspiração Apple), mantendo CTA único "Explorar produtos" → `/catalogo` e fallback de gradiente.
- [x] 8.4 Destaques: tiles em proporção retrato com imagem dominante (`product.image_url` real) e fallback de gradiente quando ausente.
- [x] 8.5 Categorias: tiles maiores/arredondados (estrutura comercial inspirada na KaBuM!), preservando dados e gradiente existentes.
- [x] 8.6 Header: barra secundária de categorias alimentada por `State.public_categories` (links → `/catalogo`), sem novas rotas/chamadas.
- [x] 8.7 Validar 375/768/1280/1536 sem overflow horizontal; `reflex compile --dry`; testes unitários; inspeção DevTools; foco teclado preservado.

### P6 — Preço (verificado, não exibido)

- Avaliado: a fonte de dados da Home (`State.public_products`, carregada por `load_public_catalog` → `_fetch_public_products` → `_public_catalog_products`) constroi `PublicProductEntry` com **`variations=[]`**; `_public_product_entry` não lê preço. Preços existem apenas **por variação** via endpoint de **detalhes** (`load_public_product_details`), e um produto pode ter múltiplas variações com preços distintos → **ambiguidade**.
- Conclusão: **sem preço não ambíguo disponível na Home**. Exibi-lo exigiria novas chamadas/`State` (fora do escopo, proibido). **Preço não exibido.** Limitação informada ao usuário.

## 9. Refinamento visual final (altura e densidade)

> Escopo estritamente visual. Dados QA, handlers, rotas e Xano inalterados.

- [x] 9.1 Hero: reduzir altura excessiva — `spacing 6→4`, `min-height 320px→220px`, visual `max-height 440px→300px`, `grid spacing 8→5`, padding do shell `1.5rem/3rem → 1.25rem/2rem`. Textos, CTA e fallback preservados (área pronta para banner futuro, sem imagem fictícia).
- [x] 9.2 Categorias: menos espaço vazio — cabeçalho `150px→120px`, card `padding 1.25→1rem`, `padding_top 0.9→0.5rem`, nome `1.2→1.1rem` e descrição `0.9→0.85rem` com truncamento (`nowrap` + `ellipsis` + `overflow hidden`) para nomes longos; dados intactos.
- [x] 9.3 Produtos: equilibrar imagem/informação — imagem `340px→300px`, card `padding 1.25→1rem`, divisor `margin_top 0.75→0.5rem`. Sem preços exibidos.
- [x] 9.4 Validar 375/768/1280/1536 sem overflow horizontal; `reflex compile --dry` sem erros.

## 10. Largura do contêiner da Home (`size="4"`)

- [x] 10.1 `page_shell()`: parâmetro opcional `size: str = "3"` repassado a `rx.container`. Padrão `"3"` mantém as demais páginas idênticas (`rt-r-size-3` → `--container-3: 880px`).
- [x] 10.2 `home_page()`: `size="4"` junto a `max_width="72rem"` — exclusivo da Home (`rt-r-size-4` → `--container-4: 1136px`, conteúdo efetivo **1120px**).
- [x] 10.3 `reflex compile --dry` sem erros. Servidor não reiniciado (hot reload).
- [x] 10.4 Validação DevTools Home — 375/768/1280/1536: sem overflow horizontal; conteúdo 1120px no desktop; hero 3 linhas e 431px; cards de categorias 4×268px e de produtos 3×363px com alturas iguais por linha.
- [x] 10.5 Regressão de largura: `/catalogo` e `/interno` permanecem em `size="3"` / 880px; nenhum outro componente ou página alterado. Xano, `State`, handlers e Changes vizinhas intocados.
- Nota: na altura da §10, `site_header()`, `site_footer()` e `category_bar()` ainda eram alinhados à esquerda (desalinhamento pré-existente de 64px). Corrigido na §11.

## 11. Alinhamento horizontal do chrome da Home

- [x] 11.1 `site_header()` e `site_footer()`: novo parâmetro opcional `wide: bool = False`. Quando `True`: `size="4"`, `margin_x="auto"` (contêiner centralizado como o conteúdo) e `padding_x="1rem"`. Padrão `False` mantém `size="3"`, `padding_x="2rem"` e sem margem — demais páginas byte a byte idênticas.
- [x] 11.2 `category_bar()` (aninhado em `home_page`, exclusivo da Home): `size="4"`, `margin_x="auto"`, `padding_x="1rem"`.
- [x] 11.3 `home_page()`: `site_header(..., wide=True)`; `page_shell(..., size="4")` repassa `site_footer(wide=size != "3")`.
- [x] 11.4 `reflex compile --dry` sem erros; `openspec validate` válido; hot reload (servidor não reiniciado).
- [x] 11.5 Validação DevTools Home (1536/1280/768/375): header, barra de categorias, conteúdo e rodapé com aresta esquerda e largura idênticas — desktop 1536: 200–1320 (1120px); 1280: 72–1192 (1120px); 768: 16 (721px); 375: 16 (343px). `overflow-x` falso em todos; barra de categorias continua com scroll horizontal (795 > 343) no mobile; console sem erros.
- [x] 11.6 Regressão: `/catalogo` e `/interno` inalterados (cabeçalho/rodapé `size="3"`, `padding 32px`, 880px em 136; conteúdo 880/864). Xano, `State`, handlers, rotas e Changes vizinhas intocados.
