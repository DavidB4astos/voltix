# Design — correção dos bloqueadores de demonstração

## Context

A auditoria de 20/11/2026 (`evidence/02-defects.md`) encontrou seis defeitos visíveis em execução.
Cinco têm correção local (D2 em parte, D3–D6); D2 depende de um campo novo no endpoint público e
D1 é uma operação de dados no Xano. O objetivo é uma demonstração honesta: sem resíduo de teste,
com preço real no card, sem selo cobrindo o rodapé, com placeholder intencional, com acesso interno
alcançável no mobile e com valores inteiros em tabelas internas. Nenhuma foto nova é gerada.

## Goals / Non-Goals

**Goals:** exibir o menor preço real de variação ativa nos cards; tratar a ausência de imagem de
forma uniforme; remover o selo do runtime; manter "Acesso interno" visível em 375 px; não quebrar
valores monetários em tabelas internas; retirar os três resíduos de teste do catálogo público.

**Non-Goals:** gerar/adquirir fotos, alterar regras de estoque/carrinho/checkout, alterar o painel
de detalhes, rever D7 (falso positivo), criar ambiente Xano isolado para E2E de compra, alterar
credenciais ou fluxo de recuperação de senha.

## Decisions

- **D3 — configuração do runtime.** `rxconfig.py` passa a declarar
  `show_built_with_reflex=False`. O compiler local só chama `_setup_sticky_badge()` em produção
  quando o valor é `True`, então a configuração elimina o selo sem CSS quebradiço e sem mexer no
  DOM. Alternativa rejeitada: `display:none` no elemento do badge (depende de classe interna do
  runtime e pode voltar em atualização).
- **D2 — preço no backend.** `xano/api/public_catalog/products_GET.xs` acrescenta `preco_minimo`
  usando `db.query variacao_produto` com `where = produto_id && status == "ATIVO"`,
  `sort = {preco: "asc"}` e `return = {type: "single"}`, LIMITED ao output `preco`. Sem variação
  ativa, o valor é `null`. Alternativa rejeitada: calcular o preço no frontend a partir do detalhe
  (exigiria uma requisição por produto, contrariando a spec de requests limitados).
- **D2 — contrato no frontend.** `PublicProductEntry` ganha `min_price: str = ""` (valor canônico
  `119.90`, vazio quando ausente) e `_public_product_entry` valida `preco_minimo` com `Decimal`
  já usado no módulo. O card usa a mesma técnica de `detail_variation` (`+ "R$ " + Var.replace`)
  para renderizar `a partir de R$ 119,90` sem aspas. Campo com default evita quebrar construtores
  existentes nos testes. Nenhum valor é inventado quando o campo falta.
- **D4 — placeholder.** Mantém-se o texto honesto `Imagem não disponível`; o bloco recebe
  tratamento visual único (ícone, moldura tracejada e fundo neutro) em card e detalhe. Não há
  substituição por foto de outro produto nem crédito inventado. A pendência de oito fotos continua
  registrada como limitação de conteúdo/direitos.
- **D5 — cabeçalho mobile.** A fileira `.vx-nav__mobile-nav` passa a aceitar quebra de linha e
  deixa de mascarar a borda direita; as pílulas mantêm tamanho e estado ativo. A categorias da home
  mantêm rolagem horizontal própria (requisito separado). Alternativa rejeitada: reduzir fonte a
  ponto de caber em uma linha (prejudica legibilidade).
- **D6 — tabela interna.** A célula do Total em `order_row` recebe `vx-internal__money-cell`, com
  `white-space: nowrap`, `tabular-nums` e alinhamento à direita. O contêiner da tabela já tem
  `overflow-x: auto`, então colunas largas não criam overflow na página.
- **D1 — dados.** Os três produtos (`TMP-VALIDB-…`, `Notebook Voltix Teste Hp`, `mouse`) serão
  **inativados** (`status = "INATIVO"`) via `PATCH /products/{id}` com sessão de ADMINISTRADOR,
  não excluídos: inativação é reversível e preserva histórico de pedidos. A execução depende de
  autorização explícita de gravação e de uma sessão administrativa válida.

## Risks / Trade-offs

- [Risco] `preco_minimo` ainda não existe no endpoint publicado → o frontend trata campo ausente
  como ausência de preço, sem erro; a publicação Xano só acontece com autorização.
- [Risco] `single` com `sort` pode não ordering garantido em todas as versões do Xano → validar
  no `--dry-run` e na chamada ao endpoint após publicação; se falhar, usar `list` + primeiro item.
- [Risco] `white-space: nowrap` pode alargar a coluna Total → verificar em 1280/768/375 px; o
  contêiner com `overflow-x: auto` absorve o excesso.
- [Trade-off] Cabeçalho mobile com duas linhas em telas estreitas: aceito para manter o destino
  interno visível sem gesto e sem reduzir fonte.
- [Trade-off] D1 inativa em vez de excluir: resíduo deixa de aparecer no catálogo, mas permanece
  no painel interno como INATIVO (legítimo e reversível).

## Migration Plan

1. Artefatos OpenSpec validados (`openspec validate fix-demo-blockers --strict`).
2. Correções locais (D3, D5, D6, D4) + contrato/parser/card (D2) + testes.
3. Suíte, `reflex compile`, inspeção visual e chamada somente leitura ao endpoint público.
4. `xano workspace push -d xano --dry-run -i "api/public_catalog/products_GET.xs"`, mostrar o
   preview e publicar somente com autorização explícita.
5. Inativação dos três produtos com autorização explícita e sessão de ADMINISTRADOR; verificar
   depois que o catálogo público não os exibe.
6. Sync das specs, arquivamento, docs e commit/push somente com autorização explícita.
   Rollback: `git revert` no frontend; no Xano, republicar a versão anterior do endpoint e
   reativar os produtos via PATCH.

## Open Questions

- A sessão de ADMINISTRADOR necessária para D1 está disponível no navegador (foi usada na
  auditoria); a confirmação de gravação será pedida no momento da execução.
- A publicação do endpoint D2 será pedida separadamente, após o dry-run.
