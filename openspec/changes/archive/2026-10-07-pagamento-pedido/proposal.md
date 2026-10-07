## Why

O checkout já cria um Pagamento `PENDENTE`, mas a compra ainda não completa o ciclo de pagamento e o Pedido não avança para `PAGAMENTO_CONFIRMADO`. O Domain Model exige pagamento simulado, sem instituição financeira ou gateway real.

## What Changes

- Permitir que o Cliente autenticado solicite a simulação do pagamento do próprio Pedido pendente.
- Como decidido para esta Change, a ação explícita “Simular pagamento” aprova o pagamento, atualiza o mesmo registro para `APROVADO` e avança o Pedido para `PAGAMENTO_CONFIRMADO`.
- Preservar o método escolhido no checkout (`PIX`, `CARTAO` ou `BOLETO`), o valor igual ao total do Pedido e o relacionamento único entre Pedido e Pagamento.
- Exibir a situação atualizada no resumo do Pedido, sem criar outro Pagamento ou histórico de tentativas.

Ficam fora do escopo gateway ou serviço financeiro real, coleta de dados de cartão, geração/cobrança real de PIX ou boleto, recusa simulada, pagamentos parciais, reembolso, cancelamento de Pedido, baixa/reserva de estoque e administração/CRM.

## Capabilities

### New Capabilities

- `order-payment`: simulação da aprovação do Pagamento pendente de um Pedido próprio e atualização do respectivo estado do Pedido.

### Modified Capabilities

Nenhuma. A Change acrescenta o ciclo de pagamento sem alterar os requisitos de checkout e consulta de Pedidos já aprovados.

## Impact

- Adiciona uma operação autenticada no Xano para simular a aprovação, validar propriedade e estado, e persistir Pagamento e Pedido consistentemente.
- Acrescenta a ação correspondente no State/UI Reflex e atualiza o resumo do Pedido após resposta confirmada do Xano.
- Reutiliza as tabelas Pagamento/Pedido, o método e o valor já registrados no checkout; não requer novo serviço, dependência ou alteração de schema.
