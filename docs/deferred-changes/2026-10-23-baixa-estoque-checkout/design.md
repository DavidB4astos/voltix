# Design — C1 baixa atômica de estoque

## Contexto e invariantes

`checkout_confirm_POST.xs` já revalida Carrinho, endereço, itens e revisão dentro de `db.transaction`, cria Pedido/ItemPedido/Pagamento e remove itens do Carrinho. Ainda não baixa estoque.

Preservar estas decisões aprovadas:

1. Estoque insuficiente responde HTTP 200 com `confirmado=false`, sem Pedido, itens, Pagamento, limpeza do Carrinho ou mudança de estoque.
2. Não criar tabela de movimentação.
3. O Carrinho não reserva estoque.
4. Pedido e todas as baixas dos itens devem persistir ou ser revertidos juntos; estoque não pode ficar negativo.
5. Manter as chaves e semântica atuais da resposta.

## Descoberta documental — 03/11/2026

A documentação oficial atual do XanoScript descreve `db.increment` como uma operação atômica sobre um campo numérico, executada em uma única instrução, com filtro `where`, valor negativo para decrementar e retorno opcional de contagem. O exemplo oficial limita a baixa por `stock >= 1` e verifica se a contagem foi maior que zero. A mesma referência descreve `db.transaction` como a forma de agrupar operações atomicamente e mostra `try_catch` envolvendo uma transação.

- [Xano Developer MCP — referência de operações de banco](https://github.com/xano-inc/xano-developer-mcp/blob/main/src/xanoscript_docs/database.md)
- [Planos Xano](https://www.xano.com/pricing)

A página pública de planos lista lógica de negócio no Free e acesso direto ao banco como recurso Essential. Isso sugere que `db.increment`, uma operação nativa de lógica Xano, pode ser diferente do acesso SQL direto; a página não confirma especificamente a disponibilidade dessa operação em toda versão/workspace Free. Não consultar o dashboard nesta avaliação.

## Caminho candidato (não aprovado para implementação)

1. Preservar a releitura de endereço, Carrinho, itens, preços, status, estoque e comparação da revisão que já ocorre dentro da transação.
2. Se a verificação atual detectar indisponibilidade antes de qualquer escrita, manter o caminho existente: responder `confirmado=false` (HTTP 200) e deixar dados intactos.
3. Para cada ItemCarrinho, chamar `db.increment` na tabela `variacao_produto` com uma condição equivalente a `id == variacao_id && quantidade_disponivel >= quantidade && status == "ATIVO"`, `field_name = "quantidade_disponivel"`, `value = -quantidade` e `return = {type: "count"}`.
4. Se qualquer contagem for zero, lançar um erro específico de conflito de estoque. A transação deve reverter decrementos anteriores e todas as gravações do Pedido. Um `try_catch` fora da transação deve converter somente esse erro na resposta já aprovada `confirmado=false`; erros inesperados devem continuar sendo propagados.
5. Criar Pedido, ItemPedido e Pagamento e limpar o Carrinho somente no mesmo bloco transacional. Preferencialmente executar os decrementos antes das gravações do pedido, para que qualquer falha posterior reverta estoque e pedido juntos.

A condição da atualização é a proteção contra corrida; uma leitura anterior, por si só, não autoriza decremento. O índice único de `(carrinho_id, variacao_produto_id)` garante no máximo uma linha por variação em cada Carrinho. Ainda será necessário escolher uma ordem determinística de atualização entre diferentes Carrinhos e tratar deadlocks sem persistência parcial.

## Provas bloqueantes antes da implementação

Executar somente em ambiente Xano separado, gratuito, autorizado e sem dados reais:

1. Validar que a versão/runtime aceita `db.increment`, o filtro composto, `return = {type: "count"}` e `try_catch` envolvendo a transação.
2. Confirmar que `db.increment` dentro da transação participa do mesmo commit/rollback que `db.add`, `db.del` e `db.patch`.
3. Forçar o segundo decremento de um Carrinho multi-item a retornar zero depois de o primeiro ter sido aplicado; provar que ambos os estoques, Pedido, ItemPedido, Pagamento e Carrinho são revertidos.
4. Concorrer duas confirmações pela última unidade; exatamente uma deve confirmar, a outra deve responder HTTP 200 `confirmado=false`, e estoque final deve ser zero.
5. Confirmar que conflito esperado é traduzido em `confirmado=false`, enquanto falhas inesperadas continuam observáveis.
6. Avaliar ordem de locks/deadlock quando duas compras com múltiplas variações atualizam conjuntos sobrepostos.
7. Confirmar que Produto/Variação inativos continuam sem compra; o status do Produto é uma tabela relacionada e o guard de `db.increment` só protege a linha da Variação. Documentar a janela de concorrência do status do Produto.

Um parser ou mock local pode verificar forma, não comportamento transacional do runtime Xano. Sem workspace isolado, manter C1 adiada e não executar a confirmação no workspace Voltix.

## Disponibilidade de plano

O bloqueio histórico de `db.direct_query` (`ERROR_CODE_ACCESS_DENIED`) continua válido para esse primitivo. Ele não prova que `db.increment` esteja indisponível. A documentação consultada não marca `db.increment` como recurso pago, mas somente o runtime autorizado pode confirmar sua disponibilidade neste workspace/plano.

## Fora do escopo

Cancelamento/devolução (C2), reserva de estoque, tabela de movimentação, painel de pedidos (C3), dashboard (C10), frete, aprovação/simulação de pagamento e frontend.
