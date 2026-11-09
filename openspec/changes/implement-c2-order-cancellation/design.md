## Context

See `proposal.md`. O estoque de qualquer Pedido criado é baixado na confirmação (C1
implementada e publicada). Cancelamento sem devolução de estoque deixa a contagem
inconsistente. O domínio exige devolução integral das quantidades de ItemPedido, e a
decisão E1 distribui permissões: Cliente até `AGUARDANDO_PAGAMENTO`; Administrador
estende a `PAGAMENTO_CONFIRMADO`; FUNCIONARIO não cancela.

Restições:

- Plano Free, workspace compartilhado; publicação exige dry-run e confirmação do usuário.
- Padrão das demais rotas do projeto: `auth = "CLIENTE"` (painel do cliente) ou
  `auth = "user"` (painel interno) + `precondition` por papel no backend.

## Goals / Non-Goals

**Goals:**
- Dois caminhos de cancelamento (Cliente próprio em `AGUARDANDO_PAGAMENTO`; ADMIN em
  `AGUARDANDO_PAGAMENTO` e `PAGAMENTO_CONFIRMADO`), com a mesma semântica de efeitos:
  devolver estoque, cancelar Pedido e Pagamento, tudo numa transação, idempotente.
- Regras no backend, não no frontend (backend autoriza por sessão derivada + papel).

**Non-Goals:**
- Reembolso real, fluxo de logística, mudança no frontend ou no painel interno.
- FUNCIONARIO poder cancelar; cancelamento de estados terminais/avançados.
- Gestão de pedidos (C3) ou dashboard (C10).

## Decisions

1. **Função interna compartilhada `Voltix Orders/cancel_order`** (Xano function) com o
   núcleo transacional. Parâmetros: `order_id` (int) e `kind` ("cliente" | "admin").
   A função valida o pedido, decide se a janela permite e executa a devolução; retorna um
   relatório para a resposta do endpoint. A autorização (quem pode cancelar qual pedido)
   fica no endpoint que chama a função (sessão do Cliente ou papel do UsuarioInterno).
   - Alternativa considerada: duplicar o stack em dois queries — rejeitada (duplicação,
     divergência futura, fragilidade para manter idempotência igual).
   - Alternativa considerada: PostgresTrigger/webhook para cancelamento implícito —
     rejeitada (fora do padrão do projeto, não visível para o cliente, mais difícil de
     revisar e validar).
2. **Precondições e janela**:
   - `cliente`: `pedido.cliente_id == auth.id` e `status == "AGUARDANDO_PAGAMENTO"`.
   - `admin`: `internal user role == "ADMINISTRADOR"` e
     `status in ["AGUARDANDO_PAGAMENTO", "PAGAMENTO_CONFIRMADO"]`.
   - `pedido.status == "CANCELADO"` → sucesso idempotente (sem alterações).
   - Qualquer outro estado → erro (`inputerror` ou `accessdenied` conforme o contexto).
3. **Efeitos na transação** (mesma ordem):
   - leitura do Pedido e checagem do estado **dentro** da transação (idempotência);
   - `foreach` nos ItemPedido (ordenado por `id asc`): `db.increment "variacao_produto"
     { where = id == variacao_produto_id, field_name = "quantidade_disponivel",
     value = quantidade, return = {type: "count"} }`; se o retorno for 0, erro que
     reverte tudo;
   - `db.edit pedido` → `CANCELADO` (+ `updated_at`);
   - `db.edit pagamento` → `CANCELADO` (+ `updated_at`); ausência de Pagamento é erro de
     consistência que reverte tudo.
4. **Erros rejeitados sem efeito**: qualquer passo que falhe dentro da transação reverte
   tudo (transação contínua, como em C1).
5. **Resposta**: mesmo shape nos dois endpoints, com `pedido_id`, `codigo`,
   `pedido_status` e `efeito` (`cancelado` | `ja_cancelado`).
6. **Limite de sintaxe validado**: o language server oficial do XanoScript confirma que
   `db.edit` aceita apenas `field_name`/`field_value` (não aceita `where`) e que
   `db.increment` aceita `where` + `return = {type: "count"}`. Por isso a idempotência é
   feita pela leitura do estado dentro da transação, e não por um UPDATE condicional.

## Risks / Trade-offs

- [Devolução em duplicidade por 2 requisições simultâneas no mesmo pedido] → risco
  residual: `db.edit` não oferece UPDATE condicional por `where` no XanoScript, então a
  checagem de estado dentro da transação protege cancelamentos em série (idempotência),
  mas duas chamadas concorrentes no mesmo instante podem, em tese, devolver estoque duas
  vezes. Não há endpoint de UI nesta change e o cenário não está no escopo aprovado;
  mitigação futura (coluna de guarda com `db.increment` ou UPDATE condicional) exigiria
  mudança de schema e aprovação própria.
- [Sempre necessário regravar o pedido mesmo em `ja_cancelado`?] → não: quando o status já
  é `CANCELADO`, a transação apenas lê e retorna `efeito: "ja_cancelado"` sem alterações.
- [Erro de gravação no meio do caminho] → transação contínua; nenhum estado parcial persiste.

## Migration Plan

1. Criar a função Xano `Voltix Orders/cancel_order` no workspace.
2. Criar e publicar as queries `orders/{order_id}/cancel` (Voltix Customer) e
   `orders/{order_id}/cancel` (Voltix Internal Orders), com dry-run e confirmação antes
   de cada publicação.
3. `openspec validate` e `unittest` locais antes do commit; revisão
   pós-publicação via 1–2 chamadas assíncronas autorizadas (nenhum teste que escreva
   registros reais sem dados sintéticos e limpeza posterior).
4. Arquivar a change; atualizar roadmap/handoff/defer.

## Open Questions

- Exibir efeitos no retorno como string legível (ex.: `"pedido cancelado"`) ou objeto
  estruturado? Decisão de resposta deixada para o design de implementation; o contrato
  proposto usa as chaves já listadas.
