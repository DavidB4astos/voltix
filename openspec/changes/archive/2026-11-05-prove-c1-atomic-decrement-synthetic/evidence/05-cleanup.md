# 05 — Limpeza e integridade

Data: 04/11/2026 (execução) / 05/11/2026 (remoção completa).

## Remoção completa (05/11/2026) — concluída

O usuário excluiu no editor do Xano: a tabela `test_c1_estoque`, o grupo
`C1 Proof Temp` (rotas `baixa`, `estado`, `reset`) e a função
`C1 Proof / preparar`. Pull independente posterior confirma: 98 documentos no
workspace, nenhum artefato `c1*`/`test_c_1*` presente, tabelas demo
(`variacao_produto`, `pedido`, `item_carrinho`, `produto`, etc.) intactas.
`GET /c1_prova/estado` → 404 `ERROR_CODE_NOT_FOUND`. A tabela `tmp_rollback_test`
(pré-existente, de terceiros) não foi tocada.

## Histórico de limpeza (04/11/2026)

- Limpeza parcial via CLI era a única opção segura (o CLI não remove documentos
  individualmente; `--sync`/`--delete` seriam destrutivos e não foram usados).
- Artefatos locais removidos na mesma sessão: `xano/api/c1_prova_temp/`,
  `xano/table/test_c1_estoque.xs`, `xano/function/c1_prova_preparar.xs`.
- Baseline restaurada por UPSERT antes da remoção da tabela (registros sintéticos
  excluídos junto com a tabela pela UI).

## Integridade dos dados reais/demo

- As únicas escritas no workspace foram: criação de 1 tabela, 5 registros e 1 grupo
  com rotas, todos sintéticos.
- Nenhum Pedido, ItemPedido, Pagamento, Cliente, endereço, estoque ou SKU real foi
  lido ou alterado para a prova; `ItemCarrinho` e o checkout real não foram tocados.
- Nenhuma evidência desta change contém dados pessoais — apenas SKUs sintéticos e
  respostas HTTP dos casos A–E.
