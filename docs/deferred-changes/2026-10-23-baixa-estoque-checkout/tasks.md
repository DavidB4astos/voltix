## 1. Prova técnica do caminho candidato

- [ ] 1.1 Em ambiente separado, confirmar sintaxe/disponibilidade de `db.increment`, condição de estoque/status, contagem de linhas e uso dentro de `db.transaction` no runtime Xano autorizado.
- [ ] 1.2 Forçar falha no segundo item e provar rollback dos decrementos anteriores, Pedido, ItemPedido, Pagamento e Carrinho; confirmar mapeamento exclusivo de conflito para HTTP 200 `confirmado=false`.

## 2. Baixa atômica no backend (somente após prova e aprovação)

- [ ] 2.1 Implementar decremento guardado por ItemCarrinho com `db.increment`, usando `id`, quantidade suficiente e variação ativa; não usar `db.direct_query`, leitura seguida de `db.patch` nem `db.edit` para aritmética de estoque.
- [ ] 2.2 Em contagem zero, lançar conflito dentro da transação, reverter todos os efeitos e mapear somente esse caso para `confirmado=false`; preservar erro inesperado.
- [ ] 2.3 Preservar criação de Pedido/ItemPedido/Pagamento, limpeza do Carrinho, `valor_frete: 0` e todas as chaves da resposta, na mesma transação.

## 3. Testes isolados

- [ ] 3.1 Atualizar `tests/test_checkout_orders.py` para refletir a baixa guardada e sua presença na transação.
- [ ] 3.2 Cobrir contrato, item sem estoque, rollback multi-item e ausência de reserva no Carrinho.
- [ ] 3.3 Validar compras concorrentes da última unidade: apenas uma confirma, a outra responde HTTP 200 `confirmado=false`, estoque permanece zero.

## 4. Verificação e escopo

- [ ] 4.1 Validar sintaxe XanoScript no runtime isolado e executar verificações locais pertinentes, sem alterar dependências.
- [ ] 4.2 Registrar versão/plano isolado, consultas, resultados sanitizados, rollback, concorrência e deadlocks.
- [ ] 4.3 Confirmar que nenhuma mutação ocorreu no workspace Voltix, não houve reserva/movimentação/cancelamento/front-end e `gestao-produtos` permaneceu intacta.
