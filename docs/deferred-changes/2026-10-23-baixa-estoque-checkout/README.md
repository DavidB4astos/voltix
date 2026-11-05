# Baixa de estoque no checkout (C1) — STATUS: IMPLEMENTADA E PUBLICADA (05/11/2026)

## Estado atual

A C1 está **CONCLUÍDA** como mudança de escopo:

- Implementação: decremento atômico de estoque por item do Carrinho dentro da mesma
  transação que cria Pedido/ItemPedido/Pagamento, usando `db.increment` com guarda
  (`id == variacao_id && quantidade_disponivel >= quantidade && status == "ATIVO"`,
  `return = {type: "count"}`).
- Em caso de falha de qualquer decremento, o sistema responde HTTP 200 `confirmado=false`
  sem persistir Pedido/itens/Pagamento, sem baixar estoque e com o Carrinho intacto.
- A resposta 200 `confirmado=false` é mantida para o cliente em caso de estoque
  insuficiente, ficando a decisão de retentativa a cargo da UI (como já ocorre hoje).
- Publicação: somente `checkout_confirm_POST.xs` no XanoFree (change
  `implement-c1-atomic-decrement`, commits `854fa8b`, `af2e959`, `95747f6`).
- Pull independente pós-publicação confere o documento; rota responde à validação
  esperada (400 `Missing param: endereco_id` para requisição vazia).
  Nenhum Pedido, ItemPedido, Pagamento ou estoque real foi escrito nesta etapa.
- Verificados: 188 testes unitários verdes; `openspec validate --all --strict`; spec
  consolidada `checkout-orders` atualizada (delta aplicada).
- Verificação remota = **somente leitura** (decisão do usuário em 05/11/2026;
  o ciclo de compra sintético completo foi adiado).

## Histórico (04/11/2026)

A prova de runtime da C1 foi CONCLUÍDA em 04/11/2026 com veredito GO. Usuário
autorizou, em 04/11/2026, **exceção documentada à decisão E6**: a prova foi publicada e
executada no workspace `147981` exclusivamente com registros sintéticos (`TEST-C1-*`) na
tabela `test_c1_estoque`, sem dados reais nem SKUs demo, e sem exportação prévia
(escolha explícita do usuário). Nenhum dado real foi alterado ou lido.

Resultado (detalhes em
`openspec/changes/archive/2026-11-05-prove-c1-atomic-decrement-synthetic/evidence/04-run-results.md`):

- `db.increment` com guarda (`quantidade_disponivel >= quantidade`, `status = "ATIVO"`)
  é aceito e atômico no runtime Free;
- funciona dentro de `db.transaction` com `throw`: rollback multi-item integral quando um
  item não tem estoque (Caso C);
- disputa concorrente pela última unidade: exatamente um confirma (Caso D);
- concorrência reversa cross-item sem deadlock (Caso E);
- resposta HTTP 200 com `confirmado=false` preservada nos conflitos.

Artefatos de teste foram excluídos (tabela, grupo de rotas e função) em 05/11/2026 após a
prova — base de dados e rotas voltaram ao estado normal, sem sobras.

## Pendências conhecidas (desta e fases anteriores)

- Ciclo de compra sintético pelo endpoint real (com limpeza UI) não executado —
  decisão do usuário (somente leitura).
- A baixa de estoque não tem reserva nem tabela de movimentação (por escopo aprovado).
- Cancelamento/devolução de estoque permanece em C2 (ainda não implementada).
- A borda Xano Free não registrou novas rotas em pushes posteriores (registrado no
  handoff); atualizações de rotas existentes funcionam normalmente.
