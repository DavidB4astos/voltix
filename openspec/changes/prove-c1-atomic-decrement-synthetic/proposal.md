## Why

A C1 (baixa atômica de estoque no checkout) é a dependência crítica de todo o núcleo
transacional do Voltix (C2 cancelamento, C3 gestão de pedidos, C10 dashboard). O bloqueio
atual não é de implementação, e sim de **prova**: não está verificado que o runtime Xano
do Voltix aceita `db.increment` com guarda dentro de transação, que reverte baixa
multi-item em caso de falha parcial, e que preserva a resposta aprovada
(HTTP 200 `confirmado=false`) sob concorrência pela última unidade.

O plano Free não oferece ambiente isolado próprio (1 workspace, sem branching, sem sandbox
do CLI — confirmado na página oficial de preços em 04/11/2026). O usuário autorizou
(04/11/2026) uma **exceção documentada à decisão E6**: executar a prova no workspace
Voltix exclusivamente com **dados sintéticos**, sem tocar nos SKUs demo, sem dados reais,
sem registros de clientes e com limpeza posterior. O usuário optou explicitamente por
**não fazer exportação/snapshot prévio**, aceitando esse risco residual; o isolamento
depende exclusivamente da disciplina de usar somente dados sintéticos.

## What Changes

- Publicação **temporária e mínima** no workspace Xano Voltix de um pacote próprio de
  prova da C1 (tabelas sintéticas `TEST_*` e rotas/queries de demonstração do decremento
  guardado), sempre com dry-run prévio, confirmação explícita do usuário e sem flags
  perigosas (`--force`, `--sync`, `--delete`, `--records`, `--env`, `--truncate`,
  `--no-transaction`).
- Execução dos casos sintéticos definidos como condição de retomada (referência:
  `docs/deferred-changes/2026-10-23-baixa-estoque-checkout/README.md`):
  1. `db.increment` com guarda aceito pelo runtime e atômico (estoque não fica negativo);
  2. transação multi-item (`db.transaction`) com rollback completo quando um item falha;
  3. disputa concorrente pela última unidade do mesmo SKU sintético;
  4. mapeamento do conflito para a resposta aprovada (HTTP 200 com `confirmado=false`);
  5. avaliação de deadlock/concorrência cross-item.
- Limpeza posterior dos artefatos e registros sintéticos; verificação de que nenhum SKU
  demo, pedido, cliente ou estoque real foi alterado.
- Registro da evidência sanitizada em `evidence/` e atualização das decisões e do roadmap
  (`docs/roadmap-changes.md`, `docs/deferred-changes/2026-10-23-baixa-estoque-checkout/README.md`,
  `docs/AI_AGENT_HANDOFF.md`) com o resultado — **sem implementar a C1 definitiva**.
- Esta change **não** altera o checkout real, o Reflex, os endpoints de produção nem as
  specs consolidadas. Se a prova passar, uma change seguinte implementará a C1.
- `skip_specs`: nenhuma exigência de spec muda nesta change; é uma atividade de prova e a
  C1 definitiva terá a sua própria change com delta em `checkout-orders`.

## Capabilities

### New Capabilities
- Nenhuma.

### Modified Capabilities
- Nenhuma.

## Impact

- **Xano (workspace Voltix, plano Free)**: publicação temporária de pacote mínimo de prova
  (tabelas e rotas sintéticas). Rate limit ativo (10 req/20 s); sem branching e sem backup
  automático no Free. Mitigação: somente dados sintéticos, pacote mínimo, dry-run e
  confirmação antes de publicar, limpeza ao final. Risco residual aceito pelo usuário
  (sem snapshot prévio).
- **Git/OpenSpec**: nova change `prove-c1-atomic-decrement-synthetic` (artifacts e
  evidências versionadas). Nenhum endpoint de produção, spec consolidada ou código Reflex
  é alterado nesta change.
- **Documentação**: roadmap, defer de C1 e handoff passam a registrar a exceção a E6 e o
  resultado da prova. A implementação da C1 continua bloqueada até a conclusão desta prova
  e nova aprovação.
- **Fora do escopo**: implementação da baixa no checkout real, devolução de estoque,
  cancelamento de pedido (C2), gestão de pedidos (C3), dashboard (C10), testes E2E de
  compra e qualquer alteração em dados demo/reais.
