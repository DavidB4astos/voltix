## Context

A Home pública é composta por `home_page()` em `voltix/voltix.py`, com seções internas `hero_section()`, `benefits_strip()`, `categories_section()`, `products_section()` e `category_bar()`, montadas por `page_shell()` com `site_header()` e `site_footer()`. Os dados vêm de `State.public_categories`, `State.public_products`, `State.public_catalog_loading`, `State.public_catalog_loaded` e `State.public_catalog_message`, carregados por `State.load_public_catalog`.

Restrições confirmadas no código:

- `PublicProductEntry` expõe `name`, `description`, `technical_specifications`, `category_name`, `brand_name`, `image_url` e `variations`; na listagem pública `variations` é **vazio**, portanto **não há preço disponível** na Home.
- `CatalogEntry` expõe apenas `id`, `name`, `description` e `status` — **não há imagem de categoria**.
- As imagens demo aprovadas são resolvidas por nome/SKU em `voltix/demo_images.py`; somente 3 dos 20 SKUs têm arquivo local (`vtx-demo-003.jpg`, `vtx-demo-004.jpg`, `vtx-demo-015.jpg`).
- As três fotos do kit são idênticas (mesmo hash) às já existentes em `assets/demo/`; não é necessário adicionar ativos.
- `rx.App` aceita `stylesheets` (Reflex 0.9.12 instalado; `requirements.txt` declara 0.9.11).
- Os componentes do kit não foram compilados nem executados; usam `list[dict]`, indexação de dicionário em `rx.foreach` e fatiamento de lista (`products[:3]`), padrões que não se aplicam diretamente a `Var` de State. São referência de composição, não código de produção.
- `_fetch_public_products` chama `_public_product_image` para cada produto via `asyncio.gather`; com 20 produtos, a carga fria emite ~22 requisições e excede o limite do Xano Free (10/20 s), resultando em HTTP 429 e bloqueando a verificação de `/catalogo`.

## Goals / Non-Goals

**Goals:**

- Entregar a composição A+B (Studio Premium + Galeria de Produto) na Home, com hero editorial escuro, vitrine curta, bloco editorial, benefícios em faixa e categorias refinadas.
- Reaproveitar ao máximo o kit (estrutura, CSS, tipografia, espaçamento), preservando a identidade Voltix aprovada e o chrome compartilhado.
- Manter a mudança restrita à Home, sem novas dependências e sem alterar dados, rotas ou comportamento.
- Eliminar o fan-out de imagens da listagem pública para permitir a verificação de `/catalogo`, absorvendo a correção mínima de backend necessária.

**Non-Goals:**

- Reescrever `site_header()`, `site_footer()` ou `page_shell()`; o kit não substitui o chrome compartilhado.
- Exibir preço, estoque, desconto ou avaliação na Home.
- Criar imagens de categoria ou baixar novas fotos de terceiros.
- Implementar visualmente catálogo, detalhe, carrinho, checkout, conta ou administração.
- Otimizar/recomprimir as imagens existentes (fica para change posterior).
- Otimizar o N+1 interno de categoria/marca em `products_GET.xs`; a correção absorvida limita-se ao fan-out de imagens.
- Alterar `requirements.txt`, a versão do Reflex, dependências ou lockfiles.
- Exibir créditos no catálogo (registrado como pendência separada).

## Decisions

### 1) Portar a composição do kit para as seções existentes, sem importar o pacote do kit

Os módulos `componentes/*.py` não são compatíveis como estão (tipagem `list[dict]`, `products[:3]`, `rx.heading`/`rx.link` sem validação em 0.9.12, dependência de `class_name` do kit e duplicação de header/footer). A decisão é **portar a composição visual** para dentro de `home_page()` e suas funções internas, mantendo a estrutura de arquivo único do projeto.

**Alternativa considerada:** criar `voltix/home_components.py` importando os arquivos do kit. Rejeitada: duplicaria o chrome, exigiria adaptar contratos de dados e fragmentaria o padrão atual sem ganho de tempo.

### 2) Reaproveitar `site_header`, `site_footer` e `page_shell`

O header e o footer do kit são maquetes isoladas e não conhecem as rotas, o menu de categorias, o badge "Loja" nem o rodapé institucional existentes. A Home continua usando os componentes compartilhados; o refinamento visual fica restrito às seções internas.

**Alternativa considerada:** adotar o header/footer do kit. Rejeitada: alteraria todas as páginas (violação direta do escopo).

### 3) CSS próprio em `assets/voltix-home.css`, escopado por `.vx-home`

O CSS do kit é portado para `assets/voltix-home.css`, registrado em `rx.App(stylesheets=["/voltix-home.css"])`, com duas correções obrigatórias:

- todas as regras ficam sob `.vx-home` (variáveis `--vx-*` declaradas em `.vx-home`, não em `:root`);
- remover seletores globais `a:focus-visible, button:focus-visible`; foco fica em `.vx-home a:focus-visible`, `.vx-home button:focus-visible` e controles com classe própria.

**Alternativa considerada:** estilos inline via props Reflex. Rejeitada: repetição, perda de media queries e dificuldade de manter `prefers-reduced-motion`.

### 4) Mapear a paleta do kit nos tokens aprovados do Voltix

O kit propõe `#2457D6`/`#111827`, que conflitam com a identidade consolidada em `visual-interface`. O mapeamento é semântico, preservando os tokens existentes:

| Papel no kit | Token Voltix |
|---|---|
| ink / ink-soft (hero e rodapé) | `COLOR_NAVY` (`#071525`) / `COLOR_NAVY_SOFT` (`#0F2A46`) |
| paper | `COLOR_SURFACE` (`#F5F7FB`) |
| surface | `COLOR_CARD` (`#FFFFFF`) |
| text / muted | `COLOR_TEXT` (`#243B53`) / `COLOR_TEXT_MUTED` (`#486581`) |
| blue / blue-hover | `COLOR_BLUE` (`#0866D9`) / `COLOR_CYAN_DARK` |
| acento | `COLOR_CYAN` (`#00B8D9`) |
| line | `COLOR_BORDER` (`#D9E2EC`) |
| focus | `FOCUS_STYLE` existente |
| raio de card | `RADIUS` (`12px`) com raio local maior apenas no hero/editorial, como já ocorre na Home |

Tipografia permanece `Inter` (fonte do app), não `system-ui` do kit.

**Alternativa considerada:** adotar os HEX do kit. Rejeitada: criaria uma segunda identidade e conflitaria com `visual-interface`.

### 5) Vitrine curada por correspondência verificável, sem fallback posicional

`rx.foreach` não permite fatiar a lista de State de forma confiável, e não existe SKU em `PublicProductEntry`. A seleção é feita por uma `@rx.var` somente-leitura em `State` (`home_showcase_products`) que:

1. inclui apenas produtos cujo `image_url` resolvido é um ativo local aprovado (`/demo/...`) — a resolução já parte da identidade do próprio produto (SKU/nome exato) em `_fetch_public_products`/`resolve_demo_image_named`;
2. mantém a ordem atual do catálogo e limita a 4 itens;
3. retorna lista vazia quando nenhum produto tem correspondência verificável — a seção é omitida, sem selecionar por posição, sem preencher slots e sem reutilizar imagem de outro produto.

Não há chamada adicional ao Xano nem alteração de elegibilidade; a variável apenas lê `public_products`. A correspondência é considerada verificável porque a imagem é resolvida a partir do próprio produto, nunca atribuída por índice.

**Alternativa considerada:** usar os 4 primeiros produtos quando nenhum tem imagem. Rejeitada: associaria imagem incorreta ou repetida e viola a decisão de não usar fallback posicional.

**Alternativa considerada:** filtrar dentro do template com `rx.cond` por `image_url.startswith("/demo/")`. Rejeitada: não limita a quantidade e não permite omitir a seção de forma limpa.

### 6) Sem preço na Home

A listagem pública não retorna preço (`variations=[]`). Os cards exibem marca, categoria, nome, imagem e o link "Ver no catálogo" para `/catalogo`, como já ocorre hoje. Nenhum valor é inventado ou buscado em endpoint adicional.

**Alternativa considerada:** passar a retornar preço no endpoint público. Rejeitada nesta change: alteração de API/Xano fora do escopo e com impacto de contrato.

### 7) Bloco editorial usando fotografia aprovada já existente

O kit usa duas fotos do Unsplash (externas, com marcas e pessoas a revisar). A change usa a fotografia local já aprovada `vtx-demo-015.jpg` (CC0, macro de processador) como imagem editorial, com crédito obrigatório e texto que descreve exatamente o que a imagem mostra ("o detalhe que compõe o setup"), sem apresentá-la como produto específico nem inventar contexto.

**Alternativa considerada:** baixar as fotos do Unsplash. Rejeitada: adiciona ativos de terceiros, exige revisão de marcas/pessoas e não é necessária para a AP2.

### 8) Proveniência e créditos de imagem na Home, a partir do manifesto existente

A Home distingue duas origens de imagem:

- **Fotografia de terceiros com licença:** `assets/demo/manifest.json` registra autor, licença e URLs. `voltix/demo_images.py` expõe `demo_image_credit()` por nome de arquivo, lida do manifesto (fonte única). Autor, licença e fonte são visíveis sem interação; se o crédito não puder ser resolvido, a imagem não é exibida.
- **Imagem própria ou gerada, sem autoria fotográfica de terceiros:** a proveniência é declarada em `assets/demo/manifest.json` na lista `editorial_images` (origem, finalidade, natureza e nota de uso) e apresentada como legenda visível na seção. Nenhum autor, licença ou fonte é inventado.

Essa distinção foi adotada na opção B do encerramento controlado (2026-10-22): o hero mantém a imagem editorial gerada por IA fornecida pelo responsável do projeto e a especificação passa a exigir proveniência adequada, não uma licença inexistente.

**Alternativa considerada:** hard-code dos créditos no template. Rejeitada: duplicaria a fonte de verdade e divergiria do manifesto.

**Alternativa considerada:** tratar a imagem gerada como fotografia licenciada e inventar autor/licença. Rejeitada: informação falsa.

### 9) Placeholder neutro, sem gradiente

O fallback de imagem em card deixa de usar gradiente e passa a usar superfície neutra com ícone, alinhado à direção premium. Nenhuma imagem é simulada.

### 10) Movimento apenas por CSS

Transições de 140–220 ms em `transform` e `opacity`, hover somente em `@media (hover: hover)` e bloco `prefers-reduced-motion` desativando movimento. Sem JS, sem dependência nova, sem autoplay ou parallax.

### 11) Hero sem eyebrow

O kit abre a primeira dobra com um rótulo "TECNOLOGIA COM INTENÇÃO". Esse padrão de eyebrow/kicker é removido: a hierarquia começa no H1, alinhada à referência Apple Store e à regra de interface aprovada. Nenhum pill, kicker ou overline é renderizado acima do título.

**Alternativa considerada:** manter o rótulo como diferencial de marca. Rejeitada: adiciona ruído, enfraquece a hierarquia e contraria a direção visual aprovada.

### 12) Mídia do hero restrita a ativos locais aprovados

O hero usa um ativo local aprovado como painel visual: uma fotografia licenciada de `assets/demo/` ou uma imagem própria/gerada fornecida pelo responsável do projeto e declarada em `assets/demo/manifest.json` (`editorial_images`). A escolha é feita na implementação avaliando recorte e legibilidade; se o ativo não funcionar bem na composição (recorte que distorça ou prejudique o texto), o hero usa um painel gráfico próprio construído com os tokens Voltix (superfícies navy, linhas e acento cyan), sem imagem. URLs externas e imagens de terceiros sem licença são proibidas. A imagem gerada usada no hero é ilustrativa, não representa SKUs específicos e exibe legenda de proveniência.

**Alternativa considerada:** hotlink das imagens do Unsplash usadas no kit. Rejeitada: dependência externa, licenciamento e risco de o recurso desaparecer.

**Alternativa considerada:** substituir a imagem gerada por painel gráfico (opção A do encerramento). Rejeitada nesta decisão: preserva menos a direção editorial aprovada; a opção B mantém a imagem com proveniência explícita.

### 13) Categorias como cards tipográficos

O kit baseia os cards de categoria em imagens que não existem nos dados (`CatalogEntry` só tem `id`, `name`, `description`, `status`) e as fotos do kit não correspondem a categorias. A change usa cards tipográficos premium (nome, descrição opcional, indicador de seta e destino existente), sem criar imagem fictícia, sem placeholder de foto e sem alterar a fonte de dados.

**Alternativa considerada:** usar as fotos demo como imagem de categoria. Rejeitada: associaria fotos de produtos a categorias, criando informação falsa.

### 14) Correção absorvida: imagem do produto na própria listagem pública

A listagem pública passa a ser a fonte da referência de imagem. `products_GET.xs` inclui `imagem_principal` na projeção interna dos dois ramos (com e sem filtro de categoria), assina a URL no `foreach` com TTL de 3600 s e retorna `image_url` no objeto de cada produto. O caminho privado continua omitido da resposta. `_public_catalog_products` valida `image_url` (HTTPS ou vazio/nulo) e `_fetch_public_products` usa esse campo, mantendo `resolve_demo_image_named` como substituição por ativo local e removendo o `asyncio.gather` de `_public_product_image`. O endpoint dedicado e o fluxo de detalhe permanecem inalterados.

**Por que:** a carga fria deixa de emitir N requisições de imagem e passa a emitir no máximo duas (categorias + produtos), independentemente da quantidade de produtos. A alteração é aditiva, não expõe o caminho privado e preserva a preferência por imagens locais aprovadas.

**Alternativas consideradas:**

- **Endpoint em lote (`/products/images?ids=...`)**: exigiria novo endpoint, tratamento de lista de IDs e um segundo round-trip; rejeitado por complexidade desnecessária para o catálogo atual.
- **Retornar apenas `has_image` e carregar imagens sob demanda**: o catálogo continuaria fazendo N requisições para exibir todos os cards; rejeitado porque não elimina a causa do 429.
- **Incluir `imagem_principal` bruta na resposta**: rejeitado por expor o caminho privado.
- **Remover `resolve_demo_image_named` da listagem**: rejeitado porque quebraria a preferência por ativos locais aprovados.

**Ordem de implantação:** publicar o Xano primeiro e depois o frontend. Se o frontend novo rodar contra o endpoint antigo, `image_url` estará ausente e será tratado como vazio; o catálogo carrega com placeholders até a publicação, sem falhar.

## Risks / Trade-offs

- **Vazamento de CSS para outras telas** → todas as regras sob `.vx-home`, revisão manual do arquivo e smoke visual em `/catalogo`, `/carrinho`, `/cliente` e `/interno`.
- **Variável derivada altera a superfície de `State`** → somente leitura, sem eventos nem mutações; testada pela suíte existente e por inspeção de comportamento.
- **Vitrine pode ficar vazia** → decisão explícita: sem correspondência verificável, a seção é omitida; não há seleção por posição nem preenchimento com produto sem imagem. Conteúdo (mais fotos aprovadas) resolve a médio prazo.
- **Correspondência por imagem resolvida do próprio produto** → a imagem só entra se vier da resolução por SKU/nome exato do produto; nenhum card usa imagem de outro item.
- **Imagens de 300–380 KB podem piorar LCP** → usar `loading="lazy"` fora do hero, dimensões reservadas e registrar otimização de imagens como pendência posterior.
- **Divergência Reflex 0.9.11 (requirements) vs 0.9.12 (ambiente)** → validar com a versão instalada e registrar a divergência; `requirements.txt`, Reflex e lockfiles não são alterados nesta change.
- **Créditos aumentam densidade visual do card** → texto pequeno e discreto, com `rel="noopener"` e sem competir com o nome do produto; crédito sempre visível, nunca só no hover.
- **Foto do hero pode não render bem no recorte** → avaliar na implementação; se não funcionar, usar painel gráfico próprio, sem imagem externa.
- **Kit não executado** → nenhum arquivo do kit é importado; a validação é feita no app real.
- **Assinar N URLs dentro de `products_GET` pode aumentar a latência** → medir a resposta com o catálogo real; se ficar próxima do limite de execução do Xano, reavaliar um endpoint em lote em change posterior.
- **Backend novo ainda não publicado** → o parser trata ausência de `image_url` como vazio; o catálogo carrega com placeholders até a publicação. Publicar o Xano primeiro.
- **Vazamento do caminho privado** → a resposta é montada campo a campo; manter a rejeição de `imagem_principal` no parser e verificar o contrato por teste.

## Migration Plan

1. Adicionar `assets/voltix-home.css` e registrá-lo em `rx.App` (sem alterar o tema Radix).
2. Ajustar `home_page()` e seções internas; adicionar a variável derivada e o helper de crédito.
3. Corrigir a listagem pública: atualizar `products_GET.xs`, publicar o endpoint, ajustar o parser/fetch no Reflex e remover o fan-out de imagens; manter o endpoint dedicado para o detalhe.
4. Validar `python -m py_compile`, suíte existente, `reflex compile` e inspeção visual em 360/390/768/1024/1440 px; executar o smoke de `/catalogo` e medir as requisições.
5. Rollback: remover o stylesheet do `rx.App`, reverter as seções da Home, a variável derivada e a correção do catálogo; o endpoint dedicado de imagem permanece. Nenhum dado ou rota é migrado.

## Implementation Record (2026-10-22)

Encerramento controlado, somente documentação, conformidade e sincronização de especificação. Nenhum commit, push ou archive foi executado.

**Emenda de escopo (2026-10-22):** a change absorveu a correção mínima do fan-out de imagens do catálogo público, originalmente planejada em `fix-catalog-image-n1`. A correção é necessária para desbloquear a verificação 5.3 e é registrada no delta `specs/public-catalog/spec.md`; os artefatos originais foram movidos para `docs/superseded-changes/2026-10-22-fix-catalog-image-n1/` como referência histórica. A implementação da correção ainda não foi executada nem publicada no Xano.

**Arquivos efetivamente tocados pela implementação (working tree):**

- `voltix/voltix.py` — seções da Home, `home_showcase_products`, `credit_line`, `rx.App(stylesheets=["/voltix-home.css"])`.
- `voltix/demo_images.py` — `demo_image_credit()` e leitura do manifesto.
- `assets/voltix-home.css` — camada visual escopada em `.vx-home`.
- `assets/demo/manifest.json` — nova lista `editorial_images` para `vtx-editorial-setup.jpg`.
- `assets/demo/vtx-editorial-setup.jpg` — imagem editorial fornecida pelo responsável do projeto (hero).
- `.gitignore` — ignora `docs/voltix-frontend-kit.zip`.

**Divergências de escopo registradas (não revertidas por decisão do responsável):**

1. `reflex.lock/bun.lock` e `reflex.lock/package.json` aparecem modificados no `git diff` (provavelmente artefato de `reflex compile`, com Reflex 0.9.12 instalado versus 0.9.11 em `requirements.txt`). Não foram revertidos; a divergência de versão permanece como pendência separada.
2. A tarefa 5.4 original previa que os arquivos tocados se limitassem a `voltix/voltix.py`, `voltix/demo_images.py`, `assets/voltix-home.css` e `.gitignore`. O conjunto real é maior (manifesto, imagem editorial e lockfiles). O critério original não foi atendido e a tarefa foi reaberta com esta justificativa.

**Verificações desta passagem:** `python -m py_compile voltix/voltix.py` e `git diff --check` (ver `tasks.md`). Inspeção visual multi-viewport (5.2), smoke de regressão (5.3), `reflex compile` e suíte completa não foram reexecutados nesta passagem controlada e permanecem **NÃO VERIFICADOS** neste encerramento.

### Waiver decision (2026-10-22)

O responsável do projeto autorizou (opção B) a dispensa temporária das verificações 5.2 e 5.3, mantendo-as **NÃO VERIFICADAS** e pendentes para a etapa posterior de testes, e aceitou o desvio documentado da 5.4. Arquivos fora do escopo (`reflex.lock/*`, `assets/demo/manifest.json`, `assets/demo/vtx-editorial-setup.jpg` e demais) permanecem preservados e devem ser excluídos de qualquer commit da Change.

A dispensa é uma decisão de encerramento, **não** uma aprovação de teste. `AGENTS.md` §6 e `openspec/config.yaml` exigem verificação efetiva para considerar a mudança concluída e arquivá-la; não há cláusula de exceção. O OpenSpec aceita arquivar com tarefas incompletas mediante confirmação, mas essa permissividade da ferramenta não sobrepõe a regra do projeto. **O archive permanece impedido** até que 5.2/5.3 sejam executadas ou a regra seja formalmente alterada com aprovação.

## Open Questions

- Recompressão e variantes responsivas das imagens (P1, após a AP2).
- Exibição de créditos também no catálogo (lacuna pré-existente; pendência separada, fora desta change).
- Divergência `requirements.txt` (0.9.11) vs ambiente (0.9.12): corrigir em change própria, fora deste escopo.
- Ampliar o conjunto de fotografias aprovadas para que a vitrine tenha mais de três correspondências verificáveis.
