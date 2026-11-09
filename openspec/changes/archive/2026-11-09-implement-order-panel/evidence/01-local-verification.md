# 01 — Tela de Pedidos: verificação local (09/11/2026)

## Escopo verificado

- Seção **Pedidos** no painel interno, em largura total, acessível a FUNCIONARIO e
  ADMINISTRADOR ativos.
- Listagem com busca `q` (código do Pedido ou nome do Cliente), filtro por status,
  total e paginação de 20, consumindo `GET orders` (C3 já publicado).
- Detalhe com Cliente (nome e e-mail mascarado), itens, endereço de entrega,
  Pagamento e valores persistidos; sem CPF, telefone, senha, hash ou token.
- Avanço de status somente para ADMINISTRADOR, um passo por vez:
  `PAGAMENTO_CONFIRMADO → EM_PREPARACAO → ENVIADO → ENTREGUE`.
- Estados de carregamento, vazio, erro e sessão não autorizada.
- Nenhuma alteração de backend, schema, rota ou publicação Xano.

## Verificação local

| Item | Resultado |
|---|---|
| `python -m unittest discover -s tests -q` | **266 testes**, OK |
| `reflex compile` | **App compiled successfully** (4,3 s) |
| `openspec validate implement-order-panel --strict` | válido |
| `openspec validate --all --strict` | **24 passed**, 0 failed |
| `git diff --check` | limpo (apenas avisos de LF/CRLF) |
| `git status` após compile | sem alterações em `reflex.lock` |

## Contrato Python

`voltix/internal_orders.py`:

- `order_filters` valida `q` (até 100 caracteres), status
  (`TODOS`/`AGUARDANDO_PAGAMENTO`/`PAGAMENTO_CONFIRMADO`/`EM_PREPARACAO`/
  `ENVIADO`/`ENTREGUE`/`CANCELADO`), página e `per_page` (1–50).
- `order_summary_record` exige exatamente `{id, codigo, data_pedido, status,
  cliente, itens_count, subtotal, valor_frete, valor_total}`, com `cliente`
  exatamente `{id, nome_completo}`.
- `order_summary_page` exige exatamente `{items, page, per_page, items_total,
  page_total}`, confere página, tamanho, totais e duplicidade.
- `order_detail` exige exatamente `{id, codigo, data_pedido, status, cliente,
  entrega, itens, subtotal, valor_frete, valor_total, pagamento}`, com
  `cliente {id, nome_completo, email_masked}`, `entrega` de oito campos, itens no
  contrato existente e `pagamento {metodo, valor, status}`. `email_masked`,
  complemento e identificação nulos são normalizados para `Indisponível`.
- `order_status_result` exige exatamente `{pedido_id, codigo, status_anterior,
  status_atual, alterado}` e confere o id solicitado.
- `ORDER_STATUSES`, `positive_int`, `customer_date_display` e
  `order_item_record` são reutilizados de `internal_customers`; `bounded_read`
  continua limitando o retry de 429.

## Handlers e segurança

- Requisições server-side com token interno (`Bearer`); nenhum token ou URL
  privada chega ao navegador.
- `advance_internal_order_status` calcula o único próximo alvo localmente,
  recusa `ADMINISTRADOR` ausente, status terminal e alvo inválido sem requisição.
- A mensagem de sucesso distingue alteração efetiva de repetição idempotente.
- `401` encerra a sessão em leitura e escrita; `403` em leitura também encerra.
  `403`/`400` no avanço de status são negação de operação e mantêm a sessão e o
  Pedido apresentado.
- Respostas obsoletas são descartadas por geração da listagem, geração do
  detalhe, token e usuário.
- A listagem é recarregada após avanço bem-sucedido.

## Configuração

Três variáveis, documentadas em `.env.example` sem valores:

- `XANO_INTERNAL_ORDERS_URL` — coleção `GET`.
- `XANO_INTERNAL_ORDER_DETAILS_URL` — contém `{order_id}`, `GET`.
- `XANO_INTERNAL_ORDER_STATUS_URL` — contém `{order_id}`, `POST` de status.

## Limites

- Não houve publicação ou verificação remota autenticada: a tela reutiliza os
  três endpoints publicados na C3.
- Não houve QA visual autenticada por falta de credencial interna nesta execução;
  a validação ficou limitada a contrato, handlers, navegação, renderização e
  `reflex compile`.
- O consumo total de registros do Xano continua não exposto; permanece a
  limitação registrada na C7.
- `reflex.lock/bun.lock` e `reflex.lock/package.json` foram verificados e
  restaurados quando necessário; não entram no commit.
- A dataclass interna `OrderSummary` foi importada como `InternalOrderSummary`
  para não colidir com o `OrderSummary` do checkout já existente em
  `voltix/voltix.py`; o contrato e o comportamento permanecem os definidos.
