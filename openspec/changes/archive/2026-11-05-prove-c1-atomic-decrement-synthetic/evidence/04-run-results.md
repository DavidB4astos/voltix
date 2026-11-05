# 04 — Resultados da prova de baixa atômica (C1)

Data: 04/11/2026 (execução) / documento gerado após os testes.
Ambiente: workspace Xano `147981` ("David's Workspace"), plano Free. Dados: exclusivamente
registros sintéticos `TEST-C1-*` na tabela `test_c1_estoque`. Nenhum SKU demo, pedido,
cliente ou estoque real foi tocado.

## Pacote temporário usado

- Grupo `C1 Proof Temp` (apaga: grupo + rotas `baixa`, `estado`, `reset`)
- Tabela `test_c1_estoque` (apaga: tabela)
- Rotas publicadas e **case-sensitive nas borda**: somente `baixa`/`estado` ficaram
  alcançáveis via HTTP; `seed`/`reset` e funções push posteriores retornam 404 na borda
  Free (instantâneo de roteamento preso à criação do grupo). Registros foram inseridos via
  `xano workspace push --records` (UPSERT por id, sem `--truncate`).

## Casos executados

| Caso | Operação | Resultado esperado | Resultado observado | Veredito |
|---|---|---|---|---|
| A | baixa(TEST-C1-OK, 2) | confirmado=true, estoque 5→3 | confirmado=true, estado: OK=3 | ✅ |
| B | baixa(TEST-C1-SEM-ESTOQUE=0, 1) | confirmado=false, estoque inalterado | confirmado=false, EstoqueInsuficiente, estado: 0 | ✅ |
| C | baixa(MULTI-A=1 disp, MULTI-B=0) | transação reverte tudo | erro "Item B sem estoque", MULTI-A permaneceu 1 | ✅ rollback multi-item |
| D | duas chamadas concorrentes p/ última unidade de LIMITE | exatamente uma confirma; estoque final 0 | 1× confirmado=true, 1× EstoqueInsuficiente, LIMITE=0 | ✅ sem oversell |
| E | duas transações concorrentes, mesmos SKUs em ordem invertida (OK=2,LIMITE=1 ⇄ LIMITE=1,OK=2) | sem deadlock, sem estado corrompido | 1× confirmado=true (OK 5→3, LIMITE 1→0); perdedora revertida por completo (OK intacto) | ✅ concorrência reversa consistente |

## Evidências de runtime

- `db.increment` com `where` composto (sku + `quantidade_disponivel >= quantidade` +
  `status == "ATIVO"`) e `return = {type: "count"}` **é aceito pelo runtime** do Free e
  atômico: o guard corta antes de travar a linha.
- Funciona dentro de `db.transaction` com `throw`: a transação multi-item foi revertida
  integralmente quando o segundo `db.increment` afetou 0 linhas (Caso C).
- Sem `db.direct_query`; caminho nativo confirmado no runtime (apenas candidato antes,
  conforme avaliação de 03/11).
- Resposta HTTP 200 com `confirmado=false` preservada nos casos de conflito/insuficiência
  (B, C, D, E).

## Achado no caminho (importante para o projeto)

No plano Free, rotas HTTP novas publicadas após a criação do grupo **não são registradas
pela borda** (404 estável, mesmo após mudar o caminho do documento, recriar o documento e
recriar o grupo com tudo num único push). Apenas as rotas do conjunto do primeiro push
(`baixa`/`estado`) ficaram alcançáveis. `xano function run` também falha para este profile
(inclui funções pré-existentes do workspace → 404). Implicação: **qualquer publicação de
rota nova no Xano Free pode não ficar acessível** — avaliar padrão de publicação (UI, ou
criação atômica do grupo com todas as rotas) antes das próximas changes do Xano.

## Limitações da prova

- Concorrência testada com 2 chamadas paralelas por cenário, sem carga/estresse.
- Deadlock não foi provocado (guard curto-circuita antes de disputa lenta de locks);
  registrado como não observado, não como impossível.
- Prova executada no workspace compartilhado com dados sintéticos, sem snapshot prévio
  (decisão explícita do usuário, risco aceito). Dados demo não foram tocados.
- Não representa a implementação da C1 no checkout real; é apenas a prova de viabilidade
  do primitivo no runtime.

## Veredito

**GO para a fase de implementação da C1** (mudança própria, com delta na spec
`checkout-orders`, dry-run e nova aprovação), com as limitações acima registradas.
