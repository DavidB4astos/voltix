# 05 — Limpeza e integridade

Data: 04/11/2026.

## O que permanece no workspace (decisão do usuário: limpeza parcial via CLI)

- Tabela `test_c1_estoque` — 5 registros sintéticos, baseline restaurada
  (OK=5, SEM-ESTOQUE=0, MULTI-A=1, MULTI-B=0, LIMITE=1).
- Grupo `C1 Proof Temp` com 3 rotas (`baixa`, `estado`, `reset`) — **inalcançáveis na
  borda** (404 HTTP estável desde a criação; ver `evidence/03-edge-registration-debug.md`).
- Função `C1 Proof / preparar` — invocável apenas via metadata; `xano function run` falha
  para todo o profile/workspace (inclusive funções pré-existentes), logo inutilizada.

O CLI não oferece remoção segura por documento (`--sync --delete` apagaria tudo o que não
fosse incluído no push; não foi usado). A remoção completa dos três itens acima exige
exclusão no editor do Xano (UI) — pendente e documentada; sem impacto no Voltix porque as
rotas não são roteáveis e a tabela só contém dados sintéticos.

## O que NÃO permanece no repositório local

- `xano/api/c1_prova_temp/` (rotas e grupo) — removido.
- `xano/table/test_c1_estoque.xs` — removido.
- `xano/function/c1_prova_preparar.xs` — removido.

## Integridade dos dados reais/demo

- As únicas escritas no workspace foram: criação de 1 tabela, 5 registros e 1 grupo com
  rotas, todos sintéticos; e os pushs constantes no histórico de comandos desta change.
- Nenhum Pedido, ItemPedido, Pagamento, Cliente, endereço, estoque ou SKU real foi lido
  ou alterado para a prova; `ItemCarrinho` e o checkout real não foram tocados.
- `tmp_rollback_test` (tabela pré-existente no workspace, de testes anteriores de terceiros)
  não foi tocada.
- Nenhuma evidência desta change contém dados pessoais — apenas SKUs sintéticos e respostas
  HTTP dos casos A–E.

## Baseline atual da tabela de teste (para quem quiser conferir)

| id | sku | quantidade_disponivel | status |
|---|---|---|---|
| 1 | TEST-C1-OK | 5 | ATIVO |
| 2 | TEST-C1-SEM-ESTOQUE | 0 | ATIVO |
| 3 | TEST-C1-MULTI-A | 1 | ATIVO |
| 4 | TEST-C1-MULTI-B | 0 | ATIVO |
| 5 | TEST-C1-LIMITE | 1 | ATIVO |
