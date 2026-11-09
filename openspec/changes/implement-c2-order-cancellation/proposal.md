## Why

Após a confirmação de um Pedido, o cliente não tem como desfazê-lo no sistema; não há
endpoint de cancelamento, a devolução de estoque guardado na C1 não acontece e o Pedido
permanece em um estado final não previsto no fluxo. Cancelamento inconsistente contamina
estoque, histórico e o comportamento do checkout e dos painéis internos.

## What Changes

- Expor cancelamento de pedido por **Cliente** (próprio Pedido, somente em
  `AGUARDANDO_PAGAMENTO`).
- Expor cancelamento de pedido por **Administrador** (estado `AGUARDANDO_PAGAMENTO` ou
  `PAGAMENTO_CONFIRMADO`); `FUNCIONARIO` não pode cancelar.
- Em ambos os caminhos, a operação é **transacional e idempotente**: devolve estoque
  das VariaçõesProduto (via `db.increment`, sem guarda — somente devolução), seta
  `Pedido.status = CANCELADO` e `Pagamento.status = CANCELADO`. Se já cancelado, retorna
  sucesso sem re-devolver estoque. Nenhum outro estado é alterável nesta change.
- Nenhum reembolso real, logística, painel operacional novo ou alteração de UI.
- Nova capability `order-cancellation`; sem alteração nas demais specs consolidadas.

## Capabilities

### New Capabilities
- `order-cancellation`: regras, permissões e efeitos transacionais do cancelamento de
  Pedido para Cliente e Administrador.

### Modified Capabilities
- Nenhuma.

## Impact

- **Xano**: nova função interna `CancelOrder` (lógica compartilhada entre os dois
  caminhos) e dois endpoints públicos/internos `customer/orders/{order_id}/cancel`
  (auth CLIENTE) e `internal/orders/{order_id}/cancel` (auth user, apenas
  ADMINISTRADOR).
- **Frontend**: nenhum (sem botão de cancelamento; o histórico é apenas leitura).
- **Specs**: nova capability; nenhuma spec existente alterada.
- **Publicação**: dry-run + confirmação explícita do usuário; ambiente Free, workspace
  compartilhado — nenhum teste de escrita em pedido real/demo sem dados sintéticos
  autorizados.
- **Fora do escopo**: uso por FUNCIONARIO (negado por regra de backend), cancelamento de
  pedidos em `EM_PREPARACAO`/`ENVIADO`/`ENTREGUE`, reembolso real, gestão de pedidos
  pelo painel (C3), dashboard (C10).
