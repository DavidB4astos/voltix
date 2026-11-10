# Handoff para agente de IA — Voltix

> Atualizado em 10/11/2026. Este documento resume o trabalho já realizado,
> o estado verificável do repositório e as regras para continuar o projeto com
> segurança. Não contém senhas, tokens, URLs privadas de credenciais ou dados
> pessoais de clientes.

## 1. Projeto e arquitetura

Voltix é um e-commerce acadêmico de tecnologia integrado a recursos internos
de CRM. A arquitetura aprovada é fixa:

- **Frontend:** Reflex/Python.
- **Backend e dados:** Xano/XanoScript.
- **Versionamento:** Git e GitHub.
- **Método de mudança:** OpenSpec.

Três perfis existem no produto:

- **Cliente:** catálogo, conta, carrinho, checkout e pedidos próprios.
- **Funcionário:** dashboard de vendas, dashboard de CRM, consulta interna de
  clientes, atendimentos e pedidos.
- **Administrador:** dashboard de vendas, dashboard de CRM, consulta de
  clientes, atendimentos e pedidos, além de gestão de produtos, categorias,
  marcas e importação.

Leia obrigatoriamente antes de qualquer alteração:

1. `AGENTS.md`
2. `docs/project-overview.md`
3. `docs/domain-model.md`
4. `docs/roadmap-changes.md`
5. `openspec/config.yaml`

As decisões em documentação não devem ser alteradas por suposição. Frontend,
backend e persistência devem permanecer separados. Autenticação e autorização
precisam ser garantidas pelo Xano, não só pela interface.

## 2. Regra de trabalho obrigatória

Trabalhe em **uma change por vez**:

1. Inspecione documentação, specs consolidadas e changes arquivadas.
2. Defina escopo e peça aprovação antes de criar ou alterar uma change.
3. Crie `proposal.md`, `design.md`, `tasks.md` e, se necessário, deltas em
   `specs/<capability>/spec.md`.
4. Valide com `openspec validate <change-id> --strict`.
5. Implemente apenas as tarefas aprovadas.
6. Execute verificações proporcionais ao escopo e registre evidências sem
   expor dados pessoais.
7. Atualize tarefas, faça a revisão final, arquive a change e valide todas as
   specs.
8. Faça um commit focado e confirme `git status --short --branch`.

Não arquive uma change somente porque o código compila. Arquivamento exige
escopo concluído, evidências e limitações documentadas. Não misture mudança
visual, alteração de negócio e publicação Xano na mesma change sem justificativa
explícita.

## 3. Segurança, privacidade e Xano

Nunca imprima, copie para documentos ou versione:

- `.env`, credenciais Xano, tokens, chaves de API ou conteúdo de snapshots que
  os contenham;
- dados reais de clientes, CPF sem máscara, senhas, hashes, e-mails ou pedidos;
- capturas de tela contendo registros reais.

O perfil Xano local se chama `voltix`; o workspace padrão usado pelo projeto é
o ambiente real. Portanto:

- faça **dry-run** antes de qualquer publicação;
- mostre claramente ao usuário quais documentos e rotas serão publicados;
- publique somente um pacote mínimo criado para a change, nunca o workspace
  inteiro;
- não use flags perigosas como `--force`, `--sync`, `--delete`, `--records`,
  `--env`, `--truncate` ou `--no-transaction`;
- após publicar, faça um pull independente e compare somente as queries
  pretendidas;
- não altere registros reais para provar testes.

O plano Xano atual é gratuito. Não existe ambiente isolado aprovado e o
sandbox automático do Xano não foi considerado disponível no plano atual.
Qualquer teste que escreva dados (compra, checkout, estoque, cancelamento,
importação real) exige ambiente isolado, autorizado e sem dados reais.

## 4. Estado do Git e do OpenSpec

Na conferência de 10/11/2026, a cobertura de `internal-access` e
`reflex-xano-integration` foi adicionada, o dashboard de CRM foi entregue como
capability própria, a edição administrativa de Cliente foi implementada e
publicada e o ajuste de estoque por variação foi implementado e publicado.
`openspec validate --all --strict` aprovou 26 specs consolidadas e a
suíte `python -m unittest discover -s tests -q` aprovou 356 testes. Esses
resultados são um registro datado, não substituem uma nova verificação após
mudanças.

Antes de prosseguir, confira o estado real com:

```powershell
git status --short --branch
git log --oneline -8
openspec list
```

Não faça `push` automaticamente. Peça confirmação ao usuário ou siga uma
autorização explícita já dada. A identidade Git aprovada para este repositório
é `David Bastos <david.bastos@live.com>`.

### Auditoria interna desktop — concluída e arquivada

`openspec/changes/archive/2026-11-03-audit-internal-desktop-flow/`

As tarefas foram concluídas e a change foi arquivada em `eb83ac2`. A revisão
incluiu a navegação de Administrador e Funcionário, limites de teclado e
restrição de seções no código. Não foram testadas rotas administrativas
diretas, autorização remota independente no Xano ou mutações; nenhuma captura
PNG nova do perfil Funcionário foi produzida, conforme decisão do usuário.

As evidências e limitações estão registradas em `evidence/` e
`evidence/final-review.md`. Não reabrir a auditoria para repetir essas tarefas
sem novo escopo aprovado.

Também estão concluídas e arquivadas as changes `2026-11-03-fix-internal-login-heading-hierarchy`,
`2026-11-03-format-internal-product-prices` e
`2026-11-03-associate-internal-login-labels`. Consulte `openspec list` e o
Git para obter o estado atual, em vez de presumir que ainda há change ativa.

## 5. Trabalho implementado e verificado

### Loja pública e desktop

A Home pública foi refinada em changes arquivadas para uma aparência premium:

- identidade navy/cyan preservada;
- hero editorial sem eyebrow/kicker, com mídia local e proveniência;
- benefícios em faixa editorial;
- categorias em apresentação tipográfica;
- vitrine de produtos com estados de carregamento, vazio e erro distintos;
- seção editorial e créditos de imagem;
- cabeçalho desktop refinado com Início, Produtos, Minha conta, Carrinho e
  Acesso interno.

As páginas desktop de catálogo, detalhes de produto, conta, carrinho, checkout,
pedidos e rodapé também receberam refinamentos arquivados. O foco aprovado foi
desktop: o layout compacto/mobile não deve ser apresentado como revisão móvel
concluída.

`localhost:3000` e `127.0.0.1:3000` mostraram aparência diferente em certa
ocasião, mas a investigação confirmou que a causa era a **largura do viewport**:
o cabeçalho compacto aparece em largura menor. Não eram duas versões do app.

### Área interna desktop

As seguintes changes foram concluídas e arquivadas:

- `refine-internal-workspace`: shell interno, sidebar e navegação por papel.
- `refine-internal-customers-desktop`: consulta somente leitura, filtros,
  máscara e detalhe de cliente.
- `refine-internal-products-desktop`: gestão de produtos e variações.
- `refine-internal-catalog-desktop`: categorias e marcas.
- `refine-internal-import-desktop`: apresentação da importação em massa.
- `implement-customer-history-panel`: histórico de Pedidos na ficha do Cliente.
- `implement-attendance-panel`: seção de Atendimentos do CRM interno.
- `implement-order-panel`: seção de Pedidos do painel interno.
- `implement-sales-dashboard-panel`: seção Dashboard do painel interno (C10).
- `add-internal-access-integration-tests`: cobertura de acesso interno e saúde da integração (C8).
- `implement-crm-dashboard`: seção CRM consolidada no painel interno.
- `implement-internal-customer-edit`: edição administrativa e status de Cliente (C9).

O controle de seção interno deve continuar restrito no `State`:

- Funcionário: `dashboard`, `crm`, `clientes`, `atendimentos`, `pedidos`.
- Administrador: `dashboard`, `crm`, `clientes`, `atendimentos`, `pedidos`,
  `produtos`, `catalogo`, `importacao`.

Os refinamentos de Importação, Categorias e Marcas preservaram State, handlers,
parsers, limites e Xano. Foram testados com dados fictícios/isolados; importação
real não foi executada.

### Xano — reconciliações já publicadas e verificadas

Foram publicadas mudanças pequenas e específicas, todas com dry-run, pull
posterior e sem modificar registros reais:

1. `harden-published-legacy-customers`
   - proteção de quatro rotas legadas de cliente;
   - leitura própria e ativa; PATCH com whitelist; DELETE autorizado mas negado;
   - cadastro POST preservado.
2. `reconcile-xano-group-identifiers`
   - alinhamento local dos identificadores de grupos Product Management e
     Public Catalog; sem alteração de URLs ou metadados remotos.
3. `reconcile-admin-product-reads`
   - GETs administrativos de produtos e variações com guarda de Administrador,
     allowlists e ordenação.
4. `reconcile-public-catalog-ordering`
   - ordenação de categorias e variações no catálogo público.
5. `reconcile-cart-checkout-ordering`
   - ordenação determinística de itens de carrinho/checkout.

**Não declarar que todo o Xano está sincronizado.** Permanecem pendências de
joins de carrinho/checkout, defaults de schema, comportamento de upload e uma
tabela remota temporária que não deve ser excluída por suposição. Consulte:

- `docs/auditorias/xano-sync-2026-10-30.md`
- `docs/deferred-changes/2026-10-30-cart-join-runtime-tests/README.md`

### Estoque e checkout

A C1 (baixa/reserva atômica de estoque no checkout) foi **IMPLEMENTADA e PUBLICADA em 05/11/2026** no XanoFree (change `implement-c1-atomic-decrement`, commits `854fa8b`, `af2e959`). O checkout revalida e baixa estoque atomicamente por item dentro da mesma transação que cria Pedido/ItemPedido/Pagamento; em falta → HTTP 200 `confirmado=false`, nada persiste, Carrinho intacto. Pull confere; rota responde à validação esperada; 188 testes e `openspec validate` verdes. A spec consolidada `checkout-orders` traz o delta; a transação e guarda seguem exatamente o modelo aprovado na prova de 04/11 (dados sintéticos, E6 exceção). Verificação remota = somente leitura (decisão do usuário em 05/11). Artefatos de prova foram excluídos em 05/11; nenhum consumo de estoque real ou pedido foi escrito.

### Cancelamento de pedidos

A C2 (cancelamento de pedido) foi **IMPLEMENTADA e PUBLICADA em 09/11/2026** no
XanoFree (change `implement-c2-order-cancellation`, commit `968481c` + evidências).
A função `Voltix Orders/cancel_order` devolve o estoque item a item dentro de uma
transação, marca Pedido e Pagamento como `CANCELADO` e é idempotente quando chamada
de novo. `POST /api:voltix-customer/orders/{order_id}/cancel` (auth CLIENTE, só o
próprio Pedido em `AGUARDANDO_PAGAMENTO`) e
`POST /api:voltix-internal-orders/orders/{order_id}/cancel` (auth `user`, exige
ADMINISTRADOR ATIVO, aceita `AGUARDANDO_PAGAMENTO` e `PAGAMENTO_CONFIRMADO`).
Verificação remota somente leitura (pull + 401 nas duas rotas); nenhum Pedido,
Pagamento ou estoque real foi alterado. Limite conhecido: `db.edit` no XanoScript
não aceita `where`, então o risco de devolução dupla em cancelamentos
*simultâneos* do mesmo Pedido permanece documentado no design.

### Gestão de pedidos

A C3 (gestão interna de pedidos) foi **IMPLEMENTADA e PUBLICADA em 09/11/2026** no
XanoFree (change `implement-c3-internal-order-management`, commits `20c195f` e
`a60b54f` + evidências). Três endpoints no grupo `Voltix Internal Orders`:
`GET /api:voltix-internal-orders/orders` (lista paginada, filtros `q`/`status`,
`per_page` 1–50), `GET .../orders/{order_id}` (detalhe com Cliente, e-mail
mascarado, itens, endereço e Pagamento) para FUNCIONARIO ou ADMINISTRADOR
`ATIVO`; e `POST .../orders/{order_id}/status` só para ADMINISTRADOR `ATIVO`.
A transição é estrita, um passo por chamada:
`PAGAMENTO_CONFIRMADO → EM_PREPARACAO → ENVIADO → ENTREGUE`; alvo igual ao atual
é sucesso `alterado=false` sem gravar; `CANCELADO` não é alvo aceito. `db.edit`
grava apenas `status`/`updated_at`. Verificação remota somente leitura (pull +
401 nas três rotas). A tela correspondente foi entregue em `implement-order-panel`.

### Relatório de vendas

A C10 (dashboard de vendas, backend) foi **IMPLEMENTADA e PUBLICADA em
09/11/2026** no XanoFree (change `implement-c10-sales-dashboard` + evidência).
`GET /api:voltix-internal-orders/reports/sales` é somente leitura, exige
FUNCIONARIO ou ADMINISTRADOR `ATIVO` e responde `faturamento`, `pedidos`,
`ticket_medio`, `periodo`, `status_incluidos` e `serie_diaria`. Faturamento e
quantidade somam apenas Pedidos em `PAGAMENTO_CONFIRMADO`, `EM_PREPARACAO`,
`ENVIADO` ou `ENTREGUE`; `AGUARDANDO_PAGAMENTO` e `CANCELADO` ficam fora.
Período padrão de 30 dias inclusivos em UTC, com `from`/`to` opcionais em
`YYYY-MM-DD` e limite de 366 dias. A agregação é feita em XanoScript sobre uma
`db.query pedido` restrita a `id`, `data_pedido`, `status` e `valor_total`.
Verificação remota somente leitura (pull + 401); sem dados sintéticos.

A **tela do Dashboard (C10)** foi entregue em 09/11/2026 pela change
`implement-sales-dashboard-panel`, sem backend novo. **Dashboard** é a primeira
opção da navegação interna, disponível a FUNCIONARIO e ADMINISTRADOR ativos.
Exibe cartões de faturamento, Pedidos e ticket médio, o período aplicado, os
status incluídos e a série diária em ordem crescente, com filtros opcionais
`from`/`to` (`YYYY-MM-DD`, UTC, no máximo 366 dias inclusivos) e estados de
carregamento, vazio, erro e sessão não autorizada. O contrato
`voltix/internal_sales.py` valida chaves exatas, período, status, série e
coerência de totais, quantizando valores monetários em duas casas; a URL vem de
`XANO_INTERNAL_SALES_URL`, usada server-side com token interno. `401`/`403`
encerram a sessão; `400` informa período inválido e mantém a sessão; respostas
malformadas não renderizam. 290 testes, `openspec validate --all --strict`
(25 itens), `git diff --check` e `reflex compile` verdes, com `reflex.lock`
restaurado.

### Cobertura de acesso interno e integração (C8)

A change `add-internal-access-integration-tests`, concluída em 10/11/2026, cobriu as
duas capabilities que não tinham nenhum teste dedicado, sem alterar produção ou Xano.
`tests/test_internal_access.py` verifica login, `submit_login`, `validate_session`,
`enter_internal_area`, logout, troca de identidade e separação Cliente × UsuarioInterno,
além das guardas de perfil/status nos XanoScripts. `tests/test_integration_health.py`
verifica o contrato exato de saúde, configuração ausente, HTTP, rede, payload inválido,
nova tentativa e ausência de autenticação/dados de domínio na requisição. 32 testes
novos, 322 na suíte completa, `openspec validate --all --strict` (26 itens) e
`git diff --check` verdes, com `reflex.lock` restaurado. Evidência:
[01](../openspec/changes/archive/2026-11-10-add-internal-access-integration-tests/evidence/01-local-verification.md).

### Histórico do Cliente

A C6 (histórico de Pedidos por Cliente) foi **IMPLEMENTADA e PUBLICADA em
09/11/2026** no XanoFree (change `implement-c6-customer-order-history` +
evidência). `GET /api:voltix-internal-customers/customers/{customer_id}/orders`
é somente leitura, exige FUNCIONARIO ou ADMINISTRADOR `ATIVO`, valida que o
Cliente existe (`notfound`) e responde `cliente_id`, `items`, `page`,
`per_page`, `total_items` e `total_pages`. Cada Pedido traz `id`, `codigo`,
`data_pedido`, `status`, `subtotal`, `valor_frete`, `valor_total` e `itens` com
`variacao_id`, `sku`, `nome_ou_descricao`, `quantidade`, `preco_unitario` e
`subtotal`. Filtros opcionais `status` (seis estados), `from`/`to`
(`YYYY-MM-DD`, UTC, inclusivos) e paginação 20/50; ordenação
`data_pedido desc, id desc`. As consultas de itens e variações são agrupadas por
página (`in`), sem N+1. Nenhum dado pessoal do Cliente na resposta. Verificação
remota somente leitura (pull + 401); sem dados sintéticos.

A **tela do histórico** foi entregue em 09/11/2026 pela change
`implement-customer-history-panel`, sem backend novo. A ficha do Cliente no painel
interno agora carrega automaticamente o histórico em uma seção de largura total abaixo
da lista/detalhe, com filtros de status (`TODOS` por padrão) e período (`from`/`to` em
UTC, inclusivos), paginação de 20, Pedidos com resumo e itens sempre expandidos, e
estados distintos de carregamento/vazio/erro. Fechar/trocar o Cliente, atualizar a
lista ou logout limpa o histórico; 401/403 encerram a sessão; respostas obsoletas são
descartadas por geração. O contrato de `voltix/internal_customers.py` valida chaves
exatas, status, datas, valores e totais antes de levar os dados ao navegador. A URL vem
de `XANO_INTERNAL_CUSTOMER_ORDERS_URL` (placeholder `{customer_id}`), sempre server-side
com token interno. 205 testes, `openspec validate --all --strict` (21 itens) e
`reflex compile` verdes.

### Atendimentos (C7)

A C7 (atendimentos de CRM, backend) foi **IMPLEMENTADA e PUBLICADA em
09/11/2026** no XanoFree (change `implement-c7-attendance-management` +
evidências). A tabela `atendimento` guarda `cliente_id`, `usuario_interno_id`,
`pedido_id` opcional, `assunto`, `descricao`, `status`, `data_atendimento`,
`created_at` e `updated_at`. O grupo `Voltix Internal CRM` expõe cinco endpoints
em `/api:voltix-internal-crm/atendimentos`: `POST`, `GET` (lista com filtros
`cliente_id`/`status` e paginação 20/50), `GET /{attendance_id}`,
`PATCH /{attendance_id}` e `POST /{attendance_id}/status`. Todos exigem
FUNCIONARIO ou ADMINISTRADOR `ATIVO`; a criação usa o próprio interno como
responsável e valida Pedido do mesmo Cliente. `ABERTO`/`EM_ATENDIMENTO` são
editáveis; `FINALIZADO`/`CANCELADO` são imutáveis. A transição
`ABERTO → EM_ATENDIMENTO` é permitida a qualquer interno; finalizar/cancelar
exige o responsável ou um ADMINISTRADOR; repetir o status é no-op idempotente.
A primeira verificação de borda encontrou HTTP 400 por `filters=min:1` em campos
opcionais; a correção foi publicada e as rotas passaram a responder 401 sem
sessão. Pull independente confirma FKs, preconditions, enum e índices. E5:
plano Free e 0 429 confirmados; o Xano não exibiu o consumo de registros, que
fica como limitação monitorada.

A **tela de atendimentos** foi entregue em 09/11/2026 pela change
`implement-attendance-panel`, sem backend novo. A seção **Atendimentos** está
disponível a FUNCIONARIO e ADMINISTRADOR ativos, com listagem por
`cliente_id`/`status` e paginação de 20, criação usando o interno autenticado
como responsável, detalhe com vínculos somente leitura, edição apenas em
`ABERTO`/`EM_ATENDIMENTO` e controles de status limitados por responsável/papel.
O contrato `voltix/internal_attendances.py` valida chaves exatas, status, datas e
totais antes do navegador; `XANO_INTERNAL_ATTENDANCES_URL`,
`XANO_INTERNAL_ATTENDANCE_DETAILS_URL` e `XANO_INTERNAL_ATTENDANCE_STATUS_URL`
vêm do ambiente e são usadas server-side. `401` encerra a sessão; `403` em
leitura/criação/edição também, enquanto `403` de transição é negação de operação
e mantém a sessão. 235 testes, `openspec validate --all --strict` (23 itens),
`git diff --check` e `reflex compile` verdes.

A **tela de Pedidos (C3)** foi entregue em 09/11/2026 pela change
`implement-order-panel`, sem backend novo. A seção **Pedidos** está disponível a
FUNCIONARIO e ADMINISTRADOR ativos, com busca por código/nome do Cliente, filtro
de status, paginação de 20 e consumo de `GET orders`. O detalhe mostra Cliente e
e-mail mascarado, itens, endereço, Pagamento e valores; CPF, telefone, senha,
hash e token não são exibidos. Apenas ADMINISTRADOR avança o status, um passo por
vez (`PAGAMENTO_CONFIRMADO → EM_PREPARACAO → ENVIADO → ENTREGUE`), com repetição
idempotente e transições inválidas bloqueadas localmente e no backend. O contrato
`voltix/internal_orders.py` valida chaves exatas, status, datas, totais e máscara;
`XANO_INTERNAL_ORDERS_URL`, `XANO_INTERNAL_ORDER_DETAILS_URL` e
`XANO_INTERNAL_ORDER_STATUS_URL` vêm do ambiente e são usadas server-side. `401`
encerra a sessão; `403` em leitura também, enquanto `403`/`400` no avanço são
negação de operação e mantêm a sessão e o Pedido. 266 testes,
`openspec validate --all --strict` (24 itens), `git diff --check` e
`reflex compile` verdes, com `reflex.lock` restaurado.

### Edição administrativa de Cliente (C9)

A C9 foi **IMPLEMENTADA e PUBLICADA em 10/11/2026** pela change
`implement-internal-customer-edit`. O grupo `Voltix Internal Customers` ganhou
`PATCH customers/{customer_id}` com `auth = "user"` e autorização exclusiva de
ADMINISTRADOR `ATIVO`; FUNCIONARIO continua somente leitura. A edição é parcial:
`nome_completo` (1–300), `email` (válido, até 254 e único ignorando o próprio
Cliente), `telefone` (até 30) e `status` (`ATIVO`/`INATIVO`). CPF, senha,
`USER_ID` e vínculos não são aceitos. `updated_at` é atualizado em transação e a
resposta repete o contrato mascarado do detalhe. Inativar preserva pedidos,
atendimentos e endereços e apenas bloqueia novos logins; reativar é idempotente.
Na ficha do Cliente, o formulário aparece somente para ADMINISTRADOR, com nome
pré-preenchido e e-mail/telefone em branco para manter; a inativação exige
confirmação em dois passos. A URL vem de `XANO_INTERNAL_CUSTOMER_UPDATE_URL`
(placeholder `{customer_id}`), server-side. 348 testes,
`openspec validate --all --strict` (26 specs), `git diff --check` e
`reflex compile` verdes, com `reflex.lock` restaurado. Evidências:
[local](../openspec/changes/archive/2026-11-10-implement-internal-customer-edit/evidence/01-local-verification.md)
e
[publicação](../openspec/changes/archive/2026-11-10-implement-internal-customer-edit/evidence/02-publish-verification.md).

### Ajuste de estoque por variação

O ajuste de estoque foi **IMPLEMENTADO e PUBLICADO em 10/11/2026** pela change
`implement-variation-stock-adjustment`. O grupo `Product Management` ganhou
`POST variations/{variation_id}/stock-adjustments` com `auth = "user"` e
autorização exclusiva de ADMINISTRADOR `ATIVO`, recebendo `delta` decimal não
nulo (positivo adiciona, negativo remove). A aplicação usa `db.increment`
atômico com guarda de quantidade suficiente apenas na saída, impedindo estoque
negativo e sobrescrita de baixas concorrentes do checkout. Não há tabela,
histórico, motivo nem alteração de `updated_at`; delta zero, variação
inexistente e estoque insuficiente falham sem escrita. No painel de produtos, a
ação "Ajustar estoque" abre um formulário dedicado com quantidade atual,
entrada/saída e quantidade positiva, visível apenas para ADMINISTRADOR; falhas
preservam o formulário e não inventam sucesso. A URL reutiliza
`XANO_VARIATIONS_URL` com o sufixo `/stock-adjustments`, sem variável nova.
356 testes, `openspec validate --all --strict` (26 specs), `git diff --check` e
`reflex compile` verdes, com `reflex.lock` restaurado. Evidências:
[local](../openspec/changes/archive/2026-11-10-implement-variation-stock-adjustment/evidence/01-local-verification.md)
e
[publicação](../openspec/changes/archive/2026-11-10-implement-variation-stock-adjustment/evidence/02-publish-verification.md).

### Exclusão de Produto

A exclusão de Produto foi **IMPLEMENTADA e PUBLICADA em 10/11/2026** pela change
`implement-product-deletion`. O grupo `Product Management` ganhou
`DELETE products/{product_id}` com `auth = "user"` e autorização exclusiva de
ADMINISTRADOR `ATIVO`. A operação é definitiva e só é permitida quando nenhuma
variação do produto é referenciada por `ItemPedido` ou `ItemCarrinho`; a
verificação e a remoção das variações e do produto acontecem na mesma
`db.transaction`. Com histórico comercial, o backend responde `400`
(`badrequest`, pois o XanoScript não possui `409`) com mensagem que orienta a
inativação; produto inexistente responde `404`. No painel, a ação
"Excluir produto" exige confirmação em dois passos, identifica o produto e só
aparece para ADMINISTRADOR; o formulário de edição, a variação e o ajuste de
estoque são limpos quando o produto excluído estava selecionado. Imagem
armazenada, Pedido, Pagamento, Carrinho, Categoria e Marca não são alterados.
362 testes, `openspec validate --all --strict` (26 specs após arquivamento),
`git diff --check` e `reflex compile` verdes, com `reflex.lock` restaurado.
Evidências:
[local](../openspec/changes/archive/2026-11-10-implement-product-deletion/evidence/01-local-verification.md)
e
[publicação](../openspec/changes/archive/2026-11-10-implement-product-deletion/evidence/02-publish-verification.md).

### Imagens de produto

Há infraestrutura de imagens locais e créditos em `assets/demo/manifest.json`.
Quinze de vinte fotos foram aprovadas. Ainda faltam imagens com modelo/direitos
verificados para: G203 LIGHTSYNC, M90, WD SN580 1TB, Ryzen 5 5600 e Archer C6.
Não usar imagem genérica, modelo parecido ou imagem gerada por IA para representar
um SKU real sem licença/proveniência adequada.

## 6. Como executar e verificar localmente

Repositório local esperado:

```text
C:\Users\David Bastos\Downloads\PROJETO VOLTIX\PROJETO VOLTIX\voltix
```

Ambiente Python do projeto:

```text
.venv-windows\Scripts\python.exe
```

Verificação de testes a partir da raiz do repositório:

```powershell
& '.\.venv-windows\Scripts\python.exe' -m unittest discover -s tests -q
```

A suíte mais recente registrada teve **362 testes aprovados**. Execute somente
os testes pertinentes quando a change for documental; não gere ruído rodando
toda a aplicação sem necessidade.

O Reflex pode alterar arquivos de dependência gerados em `reflex.lock` durante
compilação local. Não comite uma migração acidental de Bun para npm. Preserve uma
cópia local em área não versionada, revise e restaure arquivos versionados caso
a change não seja uma migração de dependências aprovada.

Para validar uma change:

```powershell
openspec validate <change-id> --strict
```

Para validar tudo após arquivar:

```powershell
openspec validate --all --strict
git diff --check
git status --short --branch
```

## 7. Próximas prioridades recomendadas

1. **C1, C2, C3, C6, C7, C8, C9 e C10 concluídas e publicadas** (05/11/2026,
   09/11/2026 e 10/11/2026); as telas de histórico do Cliente, de Atendimentos,
   de Pedidos, do Dashboard e do CRM também foram entregues.
2. **Dashboard de CRM concluído em 10/11/2026** (change
   `implement-crm-dashboard`), sem backend novo. A seção CRM consolida Clientes
   ativos, Atendimentos por situação, Pedidos registrados, o resumo de vendas do
   backend e os últimos Atendimentos.
3. **Edição administrativa de Cliente concluída em 10/11/2026** (change
   `implement-internal-customer-edit`), com `PATCH customers/{customer_id}`
   publicado e restrito a ADMINISTRADOR. A visão 360 na ficha do Cliente foi
   recusada pelo usuário.
4. **Ajuste de estoque concluído em 10/11/2026** (change
   `implement-variation-stock-adjustment`), com
   `POST variations/{variation_id}/stock-adjustments` publicado, delta atômico
   guardado e formulário dedicado no painel, sem histórico de movimentações.
5. **Exclusão de Produto concluída em 10/11/2026** (change
   `implement-product-deletion`), com `DELETE products/{product_id}` publicado,
   bloqueio de histórico comercial e confirmação em dois passos no painel.
6. **Próxima change recomendada:** gestão de usuários internos com perfil e
   recuperação de senha — uma change por vez, cada uma com aprovação própria.
7. Manter testes de compra E2E bloqueados até haver ambiente Xano isolado e
   autorizado.
8. Retomar o trabalho mobile somente com uma change própria.

O CRM está completo no backend e no painel: consulta de clientes (C4), histórico
do Cliente (C6), atendimentos (C7), consulta/transição de pedidos (C3), o
relatório de vendas (C10), o dashboard de CRM e a edição/inativação de Cliente
(C9). Os entregáveis do professor (vídeo e README) foram suspensos pelo usuário
em 10/11/2026, e a auditoria de runtime foi movida para
`docs/deferred-changes/2026-11-10-runtime-screen-audit/`.

## 8. Comandos e decisões que exigem cuidado

Use `rg` para localizar arquivos. Para Git, evite `reset --hard` e checkout
destrutivo. Para Xano, não use push global ou flags destrutivas. Não inclua
`.env`, logs de credenciais, snapshots brutos ou artefatos temporários no Git.

Antes de criar uma nova change, confirme se algo equivalente já está arquivado
em `openspec/changes/archive/` ou registrado em `docs/deferred-changes/`.
Uma change adiada é uma limitação documentada, não um recurso entregue.

## 9. Referências rápidas

- Planejamento geral: `docs/roadmap-changes.md`
- Auditoria de sincronização Xano: `docs/auditorias/xano-sync-2026-10-30.md`
- Specs consolidadas: `openspec/specs/`
- Changes abertas: `openspec/changes/`
- Changes concluídas: `openspec/changes/archive/`
- Adiamentos: `docs/deferred-changes/`
- Regras permanentes: `AGENTS.md`

Ao terminar uma sessão, deixe o repositório limpo ou explique exatamente os
arquivos pendentes, o motivo e a próxima ação segura. O próximo agente deve
preferir evidência verificável a suposições, especialmente em Xano, dados de
clientes, permissões e estoque.
