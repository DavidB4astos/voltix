## 1. Confirmação técnica obrigatória do primitivo de estoque

- [ ] 1.1 Confirmar que `db.direct_query` executa dentro da mesma transação de `checkout_confirm_POST.xs` e é revertido pelo rollback de Pedido, ItemPedido, Pagamento e estoque; confirmar também que `arg` aceita múltiplos placeholders. Registrar a evidência no `design.md`.
- [ ] 1.2 Se a participação na transação/rollback não for confirmada, suspender a implementação e registrar o bloqueio no `design.md` para decisão; não implementar solução sujeita a concorrência.

## 2. Baixa atômica no backend

- [ ] 2.1 Adicionar em `checkout_confirm_POST.xs`, dentro da transação existente, a leitura travada (`FOR UPDATE`) das variações do Carrinho e a avaliação de disponibilidade com os valores travados, mantendo HTTP 200 com `confirmado=false` quando indisponível.
- [ ] 2.2 Adicionar a baixa guardada (`UPDATE ... SET quantidade_disponivel = quantidade_disponivel - q WHERE id = ? AND quantidade_disponivel >= q AND status = 'ATIVO'`) na mesma transação, uma por item, com falha defensiva que aborta a transação inteira quando nenhuma linha é afetada.
- [ ] 2.3 Preservar a criação de Pedido/ItemPedido/Pagamento, a limpeza do Carrinho, `valor_frete: 0` e todas as chaves do contrato de resposta.

## 3. Testes

- [ ] 3.1 Atualizar `tests/test_checkout_orders.py`: substituir a asserção que proibia a baixa (`assertNotIn("db.patch variacao_produto", ...)`) por asserções da baixa guardada e de sua presença dentro da transação.
- [ ] 3.2 Adicionar testes de contrato (chaves da resposta inalteradas), de rollback (nada persistido quando a baixa falha) e de que o Carrinho continua sem reservar estoque.
- [ ] 3.3 Confirmar que `tests/test_shopping_cart.py` e as demais suítes permanecem verdes, sem regressão.

## 4. Verificação ponta a ponta e de escopo

- [ ] 4.1 Executar a suíte aplicável completa, `python -m py_compile voltix/voltix.py`, `reflex compile`, validação dos XanoScript alterados e `git diff --check`.
- [ ] 4.2 Validar ao vivo o cenário da última unidade: duas confirmações concorrentes ⇒ uma vence e a outra recebe `confirmado=false`, sem estoque negativo; registrar a evidência ou a pendência quando depender de sessões reais.
- [ ] 4.3 Auditar o escopo final: sem cancelamento/devolução, reserva, movimentação de estoque, nova tabela, painel ou alteração de frontend; confirmar que `gestao-produtos` permanece intacta com 13/15 tarefas e pendências 5.2/5.3 documentadas.
