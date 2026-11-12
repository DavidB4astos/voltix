## Why

A auditoria visual executada em 12/11/2026 nas larguras 375, 768 e 1280 px mostrou que a
loja pública funciona, mas está longe do seu potencial:

- em larguras abaixo de 1024 px, a navegação pública vira um cabeçalho "legado" de
  várias linhas com botões grandes, ocupando cerca de um terço da primeira dobra;
- a Home recorta a barra de categorias (ex.: "Compone...") sem indicação de rolagem;
- no catálogo em 768 px os cards caem para uma coluna gigante com a imagem ocupando a
  tela inteira;
- os créditos de licença do Icecat nos cards, embora obrigatórios, dominam a área do
  card e pesam na leitura da oferta.

Desktop (1280 px) e tablet (768 px) já rendem bem; o trabalho é refinar a experiência
responsiva da storefront sem tocar em negócio, dados ou rotas.

## What Changes

- Redesenhar a navegação pública abaixo de 1024 px: barra compacta, identidade à
  esquerda, rótulos curtas com ícones, sem empacotamento em múltiplas linhas, mantendo
  todos os destinos existentes e seu comportamento de acesso.
- Dar à barra de categorias da Home um tratamento de rolagem horizontal com indicação
  visível de que há mais itens (sem recortar rótulos).
- Ajustar o catálogo para duas colunas entre 768 e 1023 px (mantendo três colunas a
  partir de 1280 px) e estabilizar a altura da área de mídia dos cards.
- Compactar a linha de créditos/licença do Icecat nos cards (tipografia e quebra
  reduzidas, licença e link à fonte preservados).
- Verificar visualmente `/`, `/catalogo`, `/cliente`, `/carrinho`, `/checkout` e
  `/pedidos` em 375, 768 e 1280 px.

Sem **BREAKING** changes: rotas, State, handlers, dados, regras de negócio e acesso
não mudam.

## Capabilities

### New Capabilities

<!-- Nenhuma capability nova; o comportamento observável é coberto pela capability existente. -->

### Modified Capabilities

- `visual-interface`: navegação pública abaixo de 1024 px passa a exigir cabeçalho
  compacto com os mesmos destinos e hierarquia clara; categorias da Home ganham
  affordance de rolagem horizontal; o catálogo passa a exibir duas colunas entre 768 e
  1023 px; créditos do Icecat nos cards devem ser compactos preservando a licença.

## Impact

- Frontend: `voltix/voltix.py` (site_header/estrutura pública, cards do catálogo,
  eventuais ajustes de componente), `assets/voltix-navigation.css`,
  `assets/voltix-home.css`, `assets/voltix-catalog-cards.css`,
  `assets/voltix-catalog-search.css`, novos ou ajustados estilos de navbar compacta.
- Testes: novos testes de contrato/estrutura (cabeçalho compacto, grade de cards,
  créditos); suíte existente preservada.
- Verificação: dry-run inexistente (sem Xano), `reflex compile`,
  `openspec validate --all --strict` e inspeção visual em 375/768/1280 px.
- Fora do escopo: workspace interno (segunda change), backend, Xano, regras de negócio,
  novas imagens de produto, alterações de dados, preço nos cards (preço vive nas
  variações) e o runtime screen audit já adiado em
  `docs/deferred-changes/2026-11-10-runtime-screen-audit/`.
