# 01 — Publicação e verificação da C1 (05/11/2026)

## Publicação restrita (realizada)

- Arquivo publicado: `xano/api/customer/checkout_confirm_POST.xs` (somente ele; 97
  documentos no workspace antes do push).
- Modo: `xano workspace push -i "api/customer/checkout_confirm_POST.xs" --force`
  após dry-run aprovado pelo usuário e confirmação explícita ("confirmo").
- Saída: `API Endpoints ~1 updated` — `query checkout/confirm POST` → workspace `147981`.
- O CLI reportou "Unresolved References" (CLIENTE, endereco, carrinho, item_carrinho,
  pedido, item_pedido, pagamento "não existem"). Esses avisos são heurística do CLI
  para pushs parciais; o import resolveu — a rota responde corretamente (ver abaixo) e o
  pull independente confere o documento publicado.

## Verificação remota (apartamento leve, sem escrita)

- `POST <checkout-confirm>` sem parâmetros → HTTP 400
  `{"code":"ERROR_CODE_INPUT_ERROR","message":"Missing param: endereco_id"}`
  — comportamento idêntico ao HEAD anterior, rota viva na borda (`X-App: hit`).
- Pull independente: o snapshot remoto de `confirm_POST.xs` contém
  - `var $erro_estoque`, `try_catch` e `db.increment variacao_produto` (guarda por
    `id`, `quantidade_disponivel >= quantidade` e `status = "ATIVO"`),
  - conversão `if ($erro_estoque)` → `confirmado=false` no catch,
  - a estrutura completa coincide com o local.

## Limite da verificação

O ciclo de compra completo (review → confirm) com mutação real no workspace **não**
foi executado; permanece sujeito à autorização explícita do usuário (decisão 1.1 das
tarefas). Nenhum `Pedido`/`ItemPedido`/`Pagamento`/`VariacaoProduto` foi tocado nesta
verificação. Os 188 testes locais e `openspec validate --all --strict` seguem verdes.

## Observações operacionais

- Valores exatos de URL permanecem só no `.env` local (não impressos nesta evidência).
- O endpoint responde na borda e o push mostrou `X-App: hit`, indicando que a borda
  também promoveu a versão atual do documento.
