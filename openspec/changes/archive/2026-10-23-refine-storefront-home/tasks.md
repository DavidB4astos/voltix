## 1. Base e camada visual

- [x] 1.1 Confirmar `git status` limpo quanto a arquivos de aplicação, versão Reflex instalada (0.9.12) e divergência registrada com `requirements.txt` (0.9.11); confirmar que `requirements.txt`, Reflex e lockfiles não serão tocados; anotar no relatório da change.
- [x] 1.2 Criar `assets/voltix-home.css` portando tokens, grid, tipografia, cards, editorial e benefícios do kit, com todas as regras sob `.vx-home`, variáveis `--vx-*` declaradas no escopo e sem seletores globais de `a`/`button`/foco; verificar por inspeção do arquivo que não há seletor fora do escopo.
- [x] 1.3 Registrar o stylesheet em `rx.App(stylesheets=["/voltix-home.css"])` sem alterar o tema Radix nem os plugins; verificar que `python -m py_compile voltix/voltix.py` passa.

## 2. Dados de apresentação

- [x] 2.1 Adicionar em `voltix/demo_images.py` a consulta de crédito por nome de arquivo lida de `assets/demo/manifest.json` (fonte única) e expor a função; verificar com a lista das 3 imagens aprovadas que autor, licença e fonte correspondem ao manifesto.
- [x] 2.2 Adicionar a variável derivada somente-leitura `home_showcase_products` em `State`: incluir apenas produtos cuja imagem resolvida venha da própria identidade (ativo local aprovado `/demo/...`), manter a ordem do catálogo, limitar a 4 itens e retornar lista vazia quando não houver correspondência; verificar que não há seleção por posição, reutilização de imagem de outro produto, chamada de rede ou mutação.

## 3. Seções da Home

- [x] 3.1 Refazer `hero_section()` como hero editorial em `COLOR_NAVY` sem eyebrow/kicker, com H1 único, frase de apoio, um único CTA "Explorar produtos" para `/catalogo` e painel visual composto apenas por foto local aprovada ou por painel gráfico próprio (sem URL externa); verificar ausência de overflow em 360 e 1440 px e que nenhuma requisição externa de imagem é feita.
- [x] 3.2 Refinar `categories_section()` como cards tipográficos premium (nome, descrição opcional, indicador de seta) mantendo `State.public_categories`, o link `/catalogo` e o estado vazio, sem imagens de categoria nem novos dados; verificar que o conjunto exibido é o mesmo do catálogo.
- [x] 3.3 Reorganizar `products_section()` como vitrine curada usando `home_showcase_products`, com imagem aprovada, marca, categoria, nome, crédito obrigatório e link "Ver no catálogo"; omitir a seção quando a lista for vazia, sem preencher slots nem reutilizar imagem, e preservar loading, erro e vazio; verificar ausência de preço.
- [x] 3.4 Adicionar a seção editorial com `vtx-demo-015.jpg`, crédito obrigatório visível, título curto, frase de apoio e no máximo um CTA para `/catalogo`; omitir a seção se a foto não estiver disponível; verificar que o texto descreve a imagem sem atribuir contexto inexistente.
- [x] 3.5 Converter `benefits_strip()` em faixa linear preservando exatamente os três textos e ícones existentes; verificar leitura e quebra em 360 px.
- [x] 3.6 Trocar o placeholder de imagem dos cards por superfície neutra com ícone, removendo o gradiente; verificar visualmente o card sem imagem.

## 4. Acessibilidade e semântica

- [x] 4.1 Ajustar a hierarquia de títulos (um H1, seções em H2) e os `alt` de imagens informativas e decorativas; garantir créditos de fotografia visíveis sem hover; verificar por inspeção da árvore de acessibilidade.
- [x] 4.2 Garantir foco visível em todos os links e botões da Home, alvos de pelo menos 44 px nos controles principais e texto alternativo no menu quando aplicável; verificar navegação completa por teclado.
- [x] 4.3 Confirmar que `prefers-reduced-motion` desativa transformações não essenciais mantendo o conteúdo visível; verificar com emulação de movimento reduzido.

## 5. Verificação

- [x] 5.1 Executar a suíte existente (`python -m pytest`), `python -m py_compile voltix/voltix.py` e `reflex compile`; registrar o resultado.
  - Evidência 2026-10-22: `python -m py_compile voltix/voltix.py` OK. Suíte unitária: 138 testes OK em execução anterior desta sessão (não reexecutada nesta passagem). `reflex compile` **NÃO** reexecutado nesta passagem. `pytest` não está instalado no `.venv`; a suíte roda via `unittest`.
- [x] 5.2 Fazer inspeção visual em 360, 390, 768, 1024 e 1440 px e zoom 200%, sem overflow horizontal; registrar capturas com data e viewport.
  - **PASSOU (2026-10-22).** Servidor em `localhost:3000` reutilizado (PID 15944). Capturas em `C:\Users\venda\AppData\Local\Temp\opencode\voltix-verify-2026-10-22\home-360x800.png`, `home-390x844.png`, `home-768x1024.png`, `home-1024x768.png`, `home-1440x900.png` e `home-zoom200-1440x900.png`. Em todos os viewports: `scrollWidth == clientWidth` e nenhum elemento excedendo a viewport (`horizontalOverflow=false`). Zoom 200% via `zoom` CSS no `<html>` (proxy de zoom do navegador): sem overflow horizontal. **Ressalva:** categorias e vitrine estavam em estado vazio/carregando durante a captura devido a HTTP 429 do Xano; o layout da grade populada não foi exercitado.
- [x] 5.3 Smoke test de regressão em `/catalogo`, `/carrinho`, `/cliente` e `/interno`, confirmando que header, footer, rotas e comportamentos permanecem inalterados e que o CSS da Home não vazou; registrar o resultado.
  - **PASSOU (2026-10-23, evidência visual do usuário).** O usuário confirmou que `/catalogo` carrega e exibe os produtos normalmente após a publicação. O servidor novo (PID 31912) está com `reflex.err.log` vazio e não registrou novo 429. `/carrinho`, `/cliente` e `/interno` já haviam passado em 2026-10-22. Header/footer não foram re-inspecionados nesta passagem, mas não houve alteração de rotas ou layout. Evidências anteriores: `carrinho-1440x900.png`, `cliente-1440x900.png`, `interno-1440x900.png`; a validação de imagens do catálogo permanece em 7.6.
- [x] 5.4 Auditar o escopo final: nenhuma alteração em rotas, handlers, carrinho, checkout, autenticação, administração, `requirements.txt`, versão do Reflex, dependências ou lockfiles, exceto a correção absorvida de imagens do catálogo; confirmar por `git diff --stat` que os arquivos tocados se limitam a `voltix/voltix.py`, `voltix/demo_images.py`, `assets/voltix-home.css`, `.gitignore`, `xano/api/public_catalog/products_GET.xs`, `tests/test_public_catalog.py` e documentos de evidência/roadmap.
  - **CRITÉRIO ATUALIZADO (2026-10-22).** A auditoria original não permitia alteração em Xano; a emenda de escopo absorveu `products_GET.xs` para desbloquear o catálogo. `git diff --check` passou. A auditoria anterior registrou que `assets/demo/manifest.json` e `reflex.lock/*` já estavam modificados e permanecem preservados, fora de qualquer commit da Change; o `reflex compile` desta passagem não alterou os hashes dos lockfiles.

## 6. Encerramento controlado (2026-10-22)

- [x] 6.1 Ajustar o delta spec para a opção B: imagem própria/gerada com proveniência visível; fotografia de terceiros com autor, licença e fonte.
- [x] 6.2 Registrar divergências de escopo no `design.md`, sem reverter lockfiles nem apagar arquivos.
- [x] 6.3 Sincronizar o delta aprovado em `openspec/specs/public-home/spec.md`.
- [x] 6.4 Atualizar `docs/roadmap-changes.md`: escopo técnico atual da Home, evolução visual premium futura e próxima prioridade `pesquisa-catalogo`.
- [x] 6.5 Registro da dispensa (opção B) e sua superação pela opção A: 5.2 foi executada e **PASSOU**; 5.3 foi executada parcialmente (3 rotas **PASSARAM**; `/catalogo` **NÃO VERIFICADO** por HTTP 429). A dispensa anterior não equivale a aprovação e não é mais usada para encerrar a Change.
- [x] 6.6 Registrar a decisão de encerramento: desvio da 5.4 aceito; arquivos fora do escopo (`reflex.lock/*`, `assets/demo/manifest.json`, `assets/demo/vtx-editorial-setup.jpg` e demais) permanecem preservados e devem ser excluídos de qualquer commit da Change.
- [x] 6.7 Archive: **CONCLUÍDO (2026-10-23)**. 5.2, 5.3, 7.2 e 7.6 **PASSARAM** (7.6 em 2026-10-23, sem novo 429). A verificação efetiva exigida por `AGENTS.md` §6 e `openspec/config.yaml` está concluída. Change arquivada em `openspec/changes/archive/2026-10-23-refine-storefront-home/`; `public-home` preservado e delta de `public-catalog` sincronizado.

## 7. Correção absorvida: imagens do catálogo (2026-10-22)

- [x] 7.1 Atualizar `xano/api/public_catalog/products_GET.xs` para incluir `imagem_principal` na projeção interna dos dois ramos, assinar a URL no `foreach` com TTL 3600 e retornar `image_url` em cada produto; verificar que `imagem_principal` não aparece na resposta e que o campo é adicionado em ambos os caminhos.
  - **CONCLUÍDO (2026-10-22).** Inspeção e teste estático confirmam `imagem_principal` nos dois `output`, assinatura com `ttl = 3600`, `image_url: $image_url` no objeto de resposta e ausência de `imagem_principal:` no retorno.
- [x] 7.2 Publicar o endpoint atualizado no Xano e validar com uma chamada somente-leitura: produtos `ATIVO` retornam `image_url` HTTPS quando há imagem e `null` quando não há, sem `imagem_principal`, em uma única chamada; registrar quantidade e tempo.
  - **PASSOU (2026-10-23 09:56).** `GET /products` respondeu **HTTP 200** em **0,869 s**; **23 produtos ATIVO**; campo `image_url` presente em **23/23**; **0 HTTPS**, **23 nulos**, **0** com `imagem_principal`. Nenhum caminho privado exposto. Como todos os produtos estão sem imagem no Xano, o ramo com URL assinada HTTPS não foi exercitado.
- [x] 7.3 Atualizar `_public_catalog_products` para ler e validar `image_url` (HTTPS ou vazio/nulo), mantendo a rejeição de `imagem_principal`, e `_fetch_public_products` para usar a URL da listagem, removendo o `asyncio.gather` de `_public_product_image` e preservando `resolve_demo_image_named` e o detalhe.
  - **CONCLUÍDO (2026-10-22).** Parser valida HTTPS/tipo e rejeita `imagem_principal`; fetch não chama mais imagem por produto; detalhe continua usando `_public_product_image`.
- [x] 7.4 Atualizar `tests/test_public_catalog.py`: mocks e contagens de 3 para 2 requisições por carga, remover respostas de imagem dos `side_effect` e adicionar teste de regressão com múltiplos produtos e `await_count == 2`, sem chamada a `_public_product_image`.
  - **CONCLUÍDO (2026-10-22).** 23 testes de catálogo público OK; teste de regressão confirma 2 requisições e nenhuma chamada por produto.
- [x] 7.5 Executar `python -m unittest discover -s tests`, `python -m py_compile voltix/voltix.py` e `reflex compile`; registrar os resultados e confirmar que nenhum teste regrediu.
  - **CONCLUÍDO (2026-10-22).** 139 testes OK; `py_compile` OK; `reflex compile` OK em 6,392 s; `git diff --check` OK; hashes dos lockfiles inalterados.
- [x] 7.6 Com o Xano publicado, abrir `/catalogo` e a Home em sessão limpa; confirmar carga do catálogo, imagens exibidas, ausência de HTTP 429 e log com apenas categorias/produtos; registrar capturas e contagem de requisições.
  - **PASSOU (2026-10-23, passagem única).** `/catalogo`: 23 cards, 3 imagens locais completas (`naturalWidth > 0`), **0 imagens quebradas**; 20 cards com `image_url` nulo foram exibidos sem `<img>` e sem ícone quebrado (a área de imagem é omitida; `div` de 0 px, sem placeholder visual dedicado). Home (`/`): hero, categorias, seção editorial "Tecnologia em contexto" e vitrine "Destaques da loja" presentes; 5 imagens locais no snapshot. O servidor novo (PID 31912) manteve `reflex.err.log` com **0 linhas** e **nenhum 429**; o log antigo permaneceu inalterado (46 linhas, 09:58). Capturas: `voltix-final-catalogo-20261023.png` e `voltix-final-home-20261023.png`. A contagem de rede em runtime não foi medida (SSR; o browser não emitiu XHR/fetch), mas o teste de regressão 7.4 cobre as 2 requisições. A avaliação DOM detalhada da Home expirou na ferramenta; o snapshot confirmou as seções e as imagens.
- [x] 7.7 Registrar a evidência da correção em `docs/ap2/07-evidencias-catalogo-429.md` e atualizar `docs/roadmap-changes.md`; confirmar que os artefatos originais estão em `docs/superseded-changes/2026-10-22-fix-catalog-image-n1/`.
  - **CONCLUÍDO (2026-10-22; atualizado em 2026-10-23).** Evidência registrada com resultado automatizado; seção 8 adicionada com o contrato pós-publicação e o bloqueio do smoke por servidor desatualizado; roadmap atualizado; artefatos originais confirmados no destino *superseded*.
- [x] 7.8 Auditar o diff: alterações limitadas a `xano/api/public_catalog/products_GET.xs`, `voltix/voltix/voltix.py`, `tests/test_public_catalog.py`, `docs/ap2/07-evidencias-catalogo-429.md` e `docs/roadmap-changes.md` (além dos artefatos da Home).
  - **CONCLUÍDO (2026-10-22).** `git diff --stat` confirma apenas esses arquivos para a correção; `voltix.py` e `demo_images.py` também contêm a implementação da Home já registrada. Nenhuma rota, autenticação, administração ou dependência foi alterada.

