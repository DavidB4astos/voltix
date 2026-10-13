# Tasks

## 1. Base da Home e relocação da rota interna

- [x] 1.1 Registrar `index()` (acesso interno) em `/interno` e criar `home_page()` registrada em `/`, verificando via inspeção do source que `route="/interno"` e `route="/"` estão corretamente associados no `app.add_page`.
- [x] 1.2 Atualizar o link "Acesso interno" para `/interno` nos cabeçalhos das páginas públicas e conferir que todos os links do cabeçalho continuam apontando para rotas existentes.

## 2. Componentes da Home

- [x] 2.1 Atualizar tokens de cor da identidade para navy `#071525` e azul `#0866D9` (mantendo ciano, branco e fundo `#F5F7FB`) e verificar que `reflex compile --dry` compila sem erros.
- [x] 2.2 Criar componente de herói premium (título à esquerda, imagem de eletrônicos à direita com fallback gradiente, botão "Explorar produtos" → `/catalogo`) e verificar visualmente o render em `/`.
- [x] 2.3 Criar a faixa horizontal de benefícios e os cards de categorias (nome + bloco visual), reutilizando as categorias públicas do State; conferir que somente categorias ativas públicas aparecem.
- [x] 2.4 Criar a vitrine de produtos em grid responsivo (1/2/3 colunas) usando os produtos públicos do Xano e estados de loading/vazio/erro existentes; garantir ausência de overflow em 375 px.

## 3. Navegação e rodapé

- [x] 3.1 Modular o cabeçalho da Home (barra superior navy com logo, menu horizontal, conta e carrinho) sobre `site_header`, mantendo os mesmos destinos e o estado ativo da rota `/`.
- [x] 3.2 Exibir o rodapé institucional na Home via `page_shell`/`site_footer` e conferir que desktop e mobile mantêm o conteúdo legível.

## 4. Verificação e regressão

- [x] 4.1 Executar `python -m unittest discover -s tests -p "test_*.py"` e corrigir somente asserts de rota/link afetados pela relocação do acesso interno, sem alterar comportamento.
- [x] 4.2 Executar `reflex compile --dry` e `openspec validate home-publica-voltix`, confirmando que a Home compila e a Change permanece válida.

## 5. Refinamento visual da Home (validação visual em dev)

- [x] 5.1 Refinar o cabeçalho: altura e paddings consistentes, hover/estado ativo das pills mais trabalhados, ícones em "Minha conta" e "Carrinho" e comportamento responsivo (menu compacto no mobile), mantendo navy/azul/ciano e os mesmos destinos de rota.
- [x] 5.2 Refinar o herói: ajustar altura, hierarquia tipográfica (eyebrow, título, subtítulo), botão "Explorar produtos" como CTA de destaque; manter fallback gradiente (sem imagem estática) e usar imagem real de produto público quando disponível.
- [x] 5.3 Transformar os benefícios em faixa compacta horizontal com ícones (`rx.icon`) em vez de três cards grandes, responsiva em 1/3/5 colunas.
- [x] 5.4 Refinar os cards de categorias e de produtos (bloco visual, hover, espaçamento, alinhamento), preservando `State.public_categories`/`State.public_products` e sem criar dados fictícios; melhorar o estado vazio/loading.
- [x] 5.5 Ajustar ritmo de espaçamento vertical, largura de conteúdo e responsividade (desktop/tablet/celular) garantindo ausência de overflow a partir de 375 px.
- [x] 5.6 Reexecutar `python -m unittest discover -s tests -p "test_*.py"`, `reflex compile --dry` e `openspec validate home-publica-voltix`, confirmando que as rotas `/`, `/interno` e `/catalogo` permanecem íntegras.

## 6. Refinamento de cabeçalho e Home (capturas atuais)

- [x] 6.1 Refinar `site_header`: espaçamento horizontal consistente entre itens, ícone e texto dentro do mesmo link, padding interno uniforme das pills, estados normal/hover/ativo/foco mais claros, contraste do badge de área e navegação agrupada e responsiva em 375/768/1280; separar visualmente o acesso interno da navegação comercial; manter fundo navy/azul/ciano, logotipo clicável e os destinos de rota atuais.
- [x] 6.2 Refinar o hero da Home (`/`): proporções e equilíbrio entre texto e painel, hierarquia tipográfica títulos/subtítulo e CTA "Explorar produtos" com maior destaque; manter o fallback visual atual (sem inventar imagens) e usar imagem real de produto quando disponível.
- [x] 6.3 Ajustar o ritmo de espaçamento entre as seções da Home e a apresentação dos estados vazios de categorias/produtos, sem criar dados fictícios; preservar os grids responsivos.
- [x] 6.4 Reexecutar `python -m unittest discover -s tests -p "test_*.py"`, `reflex compile --dry` e `openspec validate home-publica-voltix`.

## 7. Correções pós-validação visual

- [x] 7.1 Aumentar o espaçamento horizontal entre os links do cabeçalho e o padding interno das pills, mantendo separação consistente entre ícone e texto.
- [x] 7.2 Redistribuir o painel do hero (padding interno, divisor e altura reduzida) para diminuir a sensação de espaço vazio, sem inventar imagens.
- [x] 7.3 Substituir o erro solto de "Destaques da loja" pelo `status_panel` compartilhado (largura máxima e botão proporcional).
- [x] 7.4 Reexecutar `python -m unittest discover -s tests -p "test_*.py"`, `reflex compile --dry` e `openspec validate home-publica-voltix`.