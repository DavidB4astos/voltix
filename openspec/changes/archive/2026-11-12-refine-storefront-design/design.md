# Design — refinamento da storefront

## Context

A storefront já usa uma identidade própria (navy/azul/ciano, superfícies claras)
com CSS escopado por área em `assets/*.css` e cabeçalho público composto em
`site_header()` com dois ramos: um desktop (≥1024 px, barra navy enxuta) e um legado
(abaixo de 1024 px, empilhado e volumoso). O catálogo renderiza cards com o Icecat
credit-line denso; a Home oferece uma barra de categorias horizontal sem indicação
visual de rolagem. A auditoria em 375/768/1280 px (12/11/2026) confirmou os pontos:
navegação mobile domina a primeira dobra, categoria recortada, grade de 1 coluna em
768 px e créditos dominando o card. Os dados, rotas e regras de negócio não mudam.

## Goals / Non-Goals

**Goals:**

- Navegação pública abaixo de 1024 px compacta: identidade, Início, Produtos,
  conta e carrinho sempre alcançáveis, com rótulos curtos e ícones; mesma lista de
  destinos e mesmas permissões de acesso.
- Barra de categorias da Home com rolagem horizontal suave e affordance visível,
  sem recortar rótulos.
- Catálogo em duas colunas entre 768 e 1023 px (três colunas a partir de 1280 px),
  com altura de mídia estável e sem overflow.
- Créditos do Icecat mantidos (obrigatórios) porém compactos.
- Verificação visual em 375, 768 e 1280 px das páginas públicas principais.

**Non-Goals:**

- Workspace interno (segunda change), backend, Xano, permissões, dados, rotas.
- Novas imagens de produto ou re-upload de mídia; hero/banner permanecem como estão
  (inclusive a arte editorial gerada por IA, já creditada).
- Mudança de marca, tipografia base ou paleta; busca por item/preço continua sem
  alteração de comportamento.
- Runtime screen audit (permanece adiado por decisão do usuário).

## Decisions

- **Mobile como cabeçalho próprio, não reaproveitamento do legado.** O ramo legado
  foi mantido "para larguras compactas" e nunca refinado; o desktop já prova o
  padrão (barra navy, ícones + rótulos curtos). A decisão é criar
  `assets/voltix-navigation.css` um tratamento `@media (max-width: 1023px)` com barra
  de altura fixa (~56–64 px), identidade à esquerda, navegação central (Início,
  Produtos) e ações à direita (Minha conta, Carrinho), usando as mesmas `site_header`
  links e o mesmo `aria_label`/ativo; alternativo: manter o legado com CSS mais
  apertado, rejeitado por não resolver hierarquia nem densidade. O legado pode ser
  removido do fluxo público após a verificação.
- **Categoria com affordance, não com paginação.** A `.vx-home-category-bar` já é um
  trilho com `overflow-x: auto`; a decisão é adicionar `scroll-snap`, scrollbar
  discreta e fade nas bordas (pseudo-elemento com gradiente da superfície) indicando
  conteúdo além da dobra; alternativo: limitar número de categorias ou trocar por
  select, rejeitado porque muda a ordem/alcance do conteúdo.
- **Grade por faixa de largura, via CSS, não via rx.match.** Os cards já usam
  grid/flex no CSS; a decisão é expor as faixas em `voltix-catalog-cards.css`
  (1 coluna <768 px, 2 colunas 768–1023 px, 3 colunas ≥1280 px) e fixar
  `aspect-ratio` da mídia para altura estável; alternativo: `rx.cond` por breakpoint,
  rejeitado porque duplicaria a árvore de componentes e o estado.
- **Créditos compactos, nunca removidos.** Reduzir para uma linha com tamanho
  menor, manter autor, link "Fonte", licença e aviso completos e acessíveis por
  teclado; alternativo: ocultar atrás de disclosure/tooltip, rejeitado por violar a
  licença Icecat e o contrato da demo.
- **Sem mudança de preços nos cards.** Preço permanece restrito às variações no
  detalhe (comportamento atual correto para catálogo multi-variação).
- **Verificação visual como critério de aceite**, com capturas nos três breakpoints,
  para não repetir o histórico de "compile verde, visual nunca conferido".

## Risks / Trade-offs

- [Risco] Substituir o cabeçalho legado pode quebrar `aria-current`, o
  `site_header` compartilhado ou testes estruturais → Mitigação: manter os mesmos
  destinos/ícones, adicionar testes que verificam presença de `vx-nav__mobile`,
  destinos e classes; preservar `site_header`/`site_core` para páginas internas.
- [Risco] Categoria com scroll-snap + fade pode confundir usuários que esperam ver
  tudo → Mitigação: a fade só aparece enquanto houver conteúdo fora da dobra e o
  trilho permanece totalmente navegável por toque/teclado.
- [Risco] Duas colunas em 768 px podem deixar cards apertados com imagens
  verticais → Mitigação: altura de mídia fixa por `aspect-ratio` e `object-fit:
  contain` já existentes; verificar nas imagens reais dos 23 produtos.
- [Risco] Créditos menores podem reduzir contraste → Mitigação: manter ≥ contraste
  AA para texto de tamanho pequeno e validar em 375 px.
- [Risco] Testes existentes de estrutura do cabeçalho público falharem →
  Mitigação: atualizar expectativas junto com a implementação e preservar a suíte.

## Migration Plan

1. Ajustar o ramo de navegação pública abaixo de 1024 px (componente + CSS).
2. Refinar a `.vx-home-category-bar` (scroll-snap + fade + scrollbar) e o
   `voltix-navigation.css`.
3. Reajustar faixas de colunas e `aspect-ratio` em `voltix-catalog-cards.css`.
4. Compactar `compact_credit` no cards do catálogo.
5. Executar suíte, `reflex compile`, servidor local e capturas em 375/768/1280 px de
   `/`, `/catalogo`, `/cliente`, `/carrinho`, `/checkout`, `/pedidos`.
6. Restaurar `reflex.lock/*` se alterado; commit/push somente com autorização.

## Open Questions

Nenhuma: escopo, restrições (sem novas imagens de produto, identidade mantida,
IA só para arte não-produto) e validação visual foram aprovados pelo usuário em
12/11/2026.
