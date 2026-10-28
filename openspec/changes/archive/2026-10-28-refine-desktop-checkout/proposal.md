## Why
O checkout atual empilha endereço, itens, pagamento e total sem hierarquia, usa seletores sem rótulo explícito e oferece confirmação mesmo para itens que o handler rejeitará por indisponibilidade. A revisão desktop deve tornar claras as etapas sem alterar criação de pedido ou pagamento.

## What Changes
- Layout desktop em duas colunas: endereço/revisão à esquerda, resumo e confirmação à direita.
- Rótulos associados para endereço e método de pagamento, somente endereços ATIVO elegíveis e opções PIX/CARTAO/BOLETO existentes.
- Quantidades, preços, subtotais, frete e total vindos da revisão; formatação textual reutilizada do carrinho.
- Confirmação desabilitada sem revisão elegível, durante carga, sem itens ou com indisponibilidade (regra já exigida pelo handler).
- Estados de revisão pendente, sem endereço ativo, loading e feedback claros, com links para conta/carrinho.
- Componentes puros para prévia isolada sem conta, dados pessoais ou escrita Xano.

## Capabilities
### Modified Capabilities
- checkout-orders: revisão e confirmação desktop acessíveis.

## Impact
Somente UI e CSS escopado. Preservar State, handlers, payloads, revisão assinada, invalidação ao trocar endereço, nova confirmação após mudança de valores e redirecionamento de sucesso. Não criar pedidos/pagamentos reais durante testes, não alterar Xano ou demais páginas, não iniciar cobrança ou simulação, não prometer reserva/frete externo. Mobile apenas empilhamento seguro.
