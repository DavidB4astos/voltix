## Why

Clientes já podem manter um Carrinho, mas ainda não conseguem concluir a compra nem consultar um Pedido resultante. Esta Change liga o Carrinho aos Pedidos do Domain Model, preservando endereço, itens e valores comerciais no momento da confirmação.

## What Changes

- Permitir que Cliente autenticado revise o próprio Carrinho, selecione Endereço próprio ativo e confirme um Pedido somente com itens válidos.
- Revalidar Produto, VariaçãoProduto, preço e estoque na confirmação; se preço ou conteúdo mudar desde a revisão, exigir nova revisão antes de criar o Pedido.
- Criar Pedido, ItemPedido e o registro obrigatório de Pagamento em estado `PENDENTE`, com valor igual ao total, sem cobrar, simular aprovação ou integrar gateway.
- Preservar quantidade, preço unitário, subtotais, total e snapshot dos dados de entrega usados na compra; nesta Change o frete será registrado como zero, sem cotação.
- Não baixar nem reservar estoque: o Domain Model não define o momento técnico da baixa e a decisão aprovada para esta Change é somente revalidar disponibilidade na confirmação.
- Esvaziar o Carrinho após a criação bem-sucedida do Pedido e permitir ao Cliente consultar somente seus próprios Pedidos e resumos.

Ficam fora do escopo pagamento real ou fluxo de aprovação, gateway, cotação/integração de frete, CRM e gerenciamento administrativo de Pedidos.

## Capabilities

### New Capabilities

- `checkout-orders`: confirmação do Carrinho, criação e consulta owner-scoped de Pedidos e histórico dos valores da compra.

### Modified Capabilities

Nenhuma. O fluxo novo consome o Carrinho, Endereços e catálogo existentes sem alterar os requisitos dessas capacidades.

## Impact

- Adiciona persistência Xano/XanoScript para Pedido, ItemPedido e Pagamento e endpoints autenticados de checkout e consulta.
- Acrescenta State/Python Reflex para revisão, confirmação, retorno de alterações comerciais e consulta de resumo do Pedido.
- Reutiliza a sessão de Cliente, o Carrinho, Endereços, Produto e VariaçãoProduto; só esvazia o Carrinho depois da criação atômica do Pedido, itens e pagamento pendente.
- Não altera `reflex.lock`, integrações externas, estoque, APIs administrativas ou processos de pagamento/frete.
