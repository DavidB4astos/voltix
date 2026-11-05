## Why

O checkout do Voltix revalida carrinho, endereço, itens e revisão dentro de uma transação,
mas **não baixa estoque** — a spec consolidada `checkout-orders` impede explicitamente a
redução de estoque ("It SHALL NOT introduce stock reduction or reservation"). Isso permite
que dois clientes confirmem a compra da última unidade do mesmo SKU, deixando o estoque
inconsistente. O primitivo `db.increment` com guarda foi comprovado no runtime em
04/11/2026 (evidência `2026-11-05-prove-c1-atomic-decrement-synthetic`), eliminando o
bloqueio técnico da C1.

## What Changes

- O checkout passa a **baixar estoque de forma atômica e guardada** para cada item do
  Carrinho na confirmação, dentro da mesma transação que cria Pedido, ItemPedido e
  Pagamento;
- se qualquer item não tiver estoque suficiente (ou a Variação não estiver ATIVA), a compra
  inteira é revertida: nenhum Pedido, ItemPedido ou Pagamento é criado/persistido, nenhum
  estoque é alterado, o Carrinho permanece intacto e a resposta é HTTP 200 com
  `confirmado=false`;
- **BREAKING (comportamento de spec)**: a regra "Checkout does not reduce or reserve
  stock" é substituída por "estoque é baixado atomicamente na confirmação";
- a resposta do endpoint mantém as mesmas chaves e semântica (`confirmado`,
  `revisao_alterada`, `pedido_id`, `codigo`, `itens`, `revisao`, `endereco*`),
  apenas passando a confirmar somente quando a baixa foi efetivada;
- nenhuma alteração em Reflex, no frontend ou em outros endpoints.

## Capabilities

### New Capabilities
- Nenhuma.

### Modified Capabilities
- `checkout-orders`: o requisito de histórico de pedidos confirmados passa a exigir a
  baixa atômica de estoque com guarda por item, dentro da transação, e a reversão integral
  em caso de falta de estoque; a resposta `confirmado=false` em insuficiência é preservada.

## Impact

- **Xano**: alteração restrita a `xano/api/customer/checkout_confirm_POST.xs`;
  `db.increment` por item na tabela `variacao_produto`; rollback multi-item já comprovado
  no runtime (ex.: Caso C da prova).
- **Specs**: delta `MODIFIED` na capability `checkout-orders`.
- **Verificação**: testes unitários/integração existentes devem continuar passando
  (188 testes); publicação do endpoint exige dry-run e confirmação explícita do usuário
  (ambiente Free, workspace compartilhado — qualquer teste de compra real exige dados
  sintéticos e limpeza posterior, sujeita a nova autorização).
- **Fora do escopo**: cancelamento/devolução de estoque (C2), reserva de estoque, tabela de
  movimentação, painéis internos (C3), dashboard (C10), frete, pagamento real, UI Reflex.
- **Riscos residuais**: baixa de estoque real em produção controlada; limpeza posterior dos
  testes sintéticos e verificação remota serão limitadas ao estritamente necessário.
