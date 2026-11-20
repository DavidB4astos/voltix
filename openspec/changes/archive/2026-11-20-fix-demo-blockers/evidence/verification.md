# Verificação — fix-demo-blockers (20/11/2026)

## Ambiente

- Interpretador: `.venv-novo-pc\Scripts\python.exe`.
- Servidores locais de produção: `http://localhost:3091/` (cache antigo) e
  `http://localhost:3092/` (instância limpa, usada para as verificações finais).
- Navegador em 1280x800 e 375x812, DPR 1. Navegação somente leitura até a autorização de gravação
  de D1; depois, sessão de ADMINISTRADOR na 3092 para inativação via interface.
- Xano: workspace `147981`, instância `x8ki-letl-twmt.n7.xano.io`.

## Artefatos e código

- `openspec validate fix-demo-blockers --strict`: **válido**.
- `openspec validate --all --strict`: **29 itens válidos, 0 falhas** antes do arquivamento (28 specs
  + a change); **28 itens válidos, 0 falhas** após o arquivamento. Apenas avisos informativos de
  requisitos longos, já presentes antes da change.
- Suíte: **445 testes OK** (435 anteriores + 10 novos em `tests/test_demo_blockers.py`).
- `reflex compile --dry`: **sucesso**.
- Teste existente `tests/test_storefront_design.py` atualizado: o cabeçalho mobile não usa mais
  rolagem horizontal; a home mantém a rolagem horizontal das categorias.

## D2 — preço nos cards

- Endpoint `xano/api/public_catalog/products_GET.xs` publicado com autorização explícita.
  Dry-run: `UPDATE query products GET` (1 documento). Push: `Pushed 1 documents to workspace 147981`.
- Chamada somente leitura ao endpoint público: **23 produtos**, todos com `preco_minimo`.
- Conferência contra o detalhe: produtos 39, 26, 27, 34 e 29 têm `preco_minimo` igual ao menor
  preço das variações `ATIVO` (119.9, 399.9, 199.9, 249.9, 299.9).
- No navegador (3092, cache limpo): **22 cards** exibem `a partir de R$ 119,90`,
  `a partir de R$ 399,90`, etc. O único sem preço é `TMP-VALIDB-20261015142856-A`, sem variação
  ativa — comportamento correto, sem inventar valor.
- Após D1, o recarregamento final mostrou **20 cards, todos com preço** (`Catálogo · 20 produtos`).
- Parser validado diretamente com o payload publicado: `min_price == "119.90"`.

## D3 — selo do runtime

- `rxconfig.py` com `show_built_with_reflex=False`.
- No DOM/HTML das páginas verificadas: nenhuma ocorrência de `Built with Reflex`.
- Rodapé público legível (texto integral em 1280 px).

## D4 — placeholder padronizado

- 8 dos 23 cards exibem o mesmo bloco `.vx-image-placeholder`, com `border-style: dashed`, fundo
  neutro e texto integral `Imagem não disponível`; após D1, 5 dos 20 cards restantes.
- Mesmo texto/classe no detalhe. Nenhuma foto de outro produto e nenhum crédito inventado.
- Limitação registrada: oito fotos continuam pendentes de fonte/direitos; decisão do usuário
  congelou novas imagens de produto.

## D5 — cabeçalho mobile

- Em 375 px: pílulas `Catálogo público`, `Área do Cliente`, `Carrinho`, `Acesso interno`.
- `Acesso interno`: `left=112`, `right=219`, `top=105`, `bottom=143` em viewport de 375 px
  (inteiramente visível, em segunda linha); `overflow` horizontal do documento = 0.

## D6 — valor monetário na tabela de Pedidos

- Com sessão de ADMINISTRADOR na 3092, tabela com 2 pedidos: `R$ 119,90` e `R$ 2999,90`.
- `R$ 2999,90`: `Range.getClientRects().length === 1`, `white-space: nowrap`, `scrollWidth ===
  clientWidth === 86`; `overflow` horizontal do documento = 0.

## D1 — limpeza dos produtos de teste

- Autorização explícita de gravação obtida antes da inativação. Os três produtos foram localizados
  na listagem administrativa e inativados pela interface, sem exclusão:
  `TMP-VALIDB-20261015142856-A`, `Notebook Voltix Teste Hp`, `mouse`.
- Após cada ação, o badge mudou de `Ativo` para `Inativo` e a ação de `Inativar produto` para
  `Reativar produto` (confirmado no DOM da 3092).
- Recarregamento do catálogo público na 3092: `Catálogo · 20 produtos`, **20 cards com
  `a partir de R$`**, nenhum dos três nomes presente no DOM. Os 20 produtos restantes foram
  preservados.

## Inspeção final 1280 / 768 / 375 px

- `reflex compile`: sucesso; `reflex.lock/*` restaurado; `git diff --check` sem erros de whitespace.
- Catálogo público nas três larguras: 20 cards, todos com preço, 5 placeholders, `overflow` do
  documento = 0 e nenhuma ocorrência de `Built with Reflex` no HTML; rodapé legível.
- Em 375 px, `Acesso interno` permanece em `left=112, right=219, top=105, bottom=143`.
- Pedidos em 375 px: `R$ 119,90` e `R$ 2999,90` continuam em uma linha; a tabela usa
  `.rt-ScrollAreaViewport` com `overflow-x: scroll` (`scrollWidth=649`, `clientWidth=281`), sem
  overflow no documento.

## Limitação de runtime

- Uma varredura de detalhes de 23 produtos foi interrompida pelo limite do plano Free
  (10 requests/20 s, HTTP 429). A conferência de menor preço foi concluída em 5 produtos e pelo
  parser, sem necessidade de mais chamadas.
