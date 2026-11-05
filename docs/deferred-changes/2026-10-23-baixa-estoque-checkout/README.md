# Change adiada: baixa-estoque-checkout (C1)

Atualização documental: 04/11/2026. **A prova de runtime da C1 foi CONCLUÍDA em 04/11/2026,
com veredito GO para a implementação** — ver seção abaixo. A implementação definitiva ainda
não foi iniciada; C1 voltará para `openspec/changes/` apenas com nova change e aprovação
explícita.

## Prova de runtime — 04/11/2026 (CONCLUÍDA)

O usuário autorizou, em 04/11/2026, uma **exceção documentada à decisão E6**: a prova foi
publicada e executada no workspace `147981` exclusivamente com registros sintéticos
(`TEST-C1-*`) na tabela `test_c1_estoque`, sem dados reais nem SKUs demo, e sem exportação
prévia (escolha explícita do usuário). Nenhum dado real foi alterado ou lido.

Resultado (detalhes em [prove-c1-atomic-decrement-synthetic/evidence/04-run-results.md](../../../openspec/changes/prove-c1-atomic-decrement-synthetic/evidence/04-run-results.md)):

- `db.increment` com guarda (`quantidade_disponivel >= quantidade`, `status = "ATIVO"`)
  **é aceito e atômico** no runtime Free;
- funciona dentro de `db.transaction` com `throw`: rollback multi-item integral quando um
  item não tem estoque (Caso C);
- disputa concorrente pela última unidade: exatamente um confirma (Caso D);
- concorrência reversa cross-item sem deadlock (Caso E);
- resposta HTTP 200 com `confirmado=false` preservada nos conflitos.

Limitações da prova: sem carga/estresse; concorrência com 2 chamadas por cenário; executada
no workspace compartilhado com dados sintéticos, sem snapshot prévio (risco aceito pelo
usuário). A C1 definitiva exige nova change, delta na spec `checkout-orders`, dry-run e nova
aprovação — não é autorização automática. Evidência e artefatos:
[prove-c1-atomic-decrement-synthetic](../../../openspec/changes/prove-c1-atomic-decrement-synthetic/).

Artefatos de teste permanecem no workspace até exclusão na UI do Xano: tabela
`test_c1_estoque` (5 registros sintéticos em baseline), grupo
`C1 Proof Temp` com rotas `c1_prova/*` (**inalcançáveis na borda Free** — novos pushes via
CLI não registram rotas no roteador do edge; achado relevante para as próximas publicações).

## Estado histórico

- 0/11 tarefas da change original concluídas; o plano original continua válido como
  referência, com a prova agora aprovada.
- O bloqueio histórico de `db.direct_query` (`ERROR_CODE_ACCESS_DENIED`) permanece real.
- Nenhum código, endpoint de produção, tabela demo ou registro real foi alterado.

## Conclusão da avaliação documental (03/11/2026, superada pela prova de 04/11/2026)

`db.increment` é documentado como operação numérica atômica com condição `where`, guarda de
estoque e contagem de linhas alteradas. `db.transaction` é documentado para agrupar
operações atomicamente. A prova de 04/11/2026 confirmou esses comportamentos no runtime
para este workspace.

## Revisão de sandbox Xano — 04/11/2026

O Xano CLI local v1.2.0 inclui `sandbox get`, que cria um ambiente se ainda não existir; a
ajuda de `sandbox push` exige preview e não aceita filtros por arquivo. A página oficial de
preços consultada lista `CLI sandbox environments` no plano Essential, não no Free. O plano
atual da conta não foi consultado; o último registro do projeto dizia Free. Nenhum ambiente
foi criado, nenhum pacote foi enviado e nenhum teste de escrita foi executado nessa
avaliação. A prova posterior (04/11/2026) contornou a ausência de sandbox com a exceção a
E6 autorizada pelo usuário. Ver a avaliação OpenSpec
[assess-c1-sandbox-plan-availability](../../../openspec/changes/archive/2026-11-04-assess-c1-sandbox-plan-availability/evidence/feasibility-review.md).

## Referências oficiais consultadas

- [Xano Developer MCP — operações de banco, `db.increment`, transação e try/catch](https://github.com/xano-inc/xano-developer-mcp/blob/main/src/xanoscript_docs/database.md).
- [Planos Xano](https://www.xano.com/pricing).
