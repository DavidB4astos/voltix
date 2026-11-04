# Change adiada: baixa-estoque-checkout (C1)

Atualização documental: 03/11/2026. A implementação segue **ADIADA/BLOQUEADA**; a revisão encontrou um caminho nativo candidato (`db.increment`) na documentação oficial atual do XanoScript.

## Estado

- 0/11 tarefas concluídas; não é uma change ativa do OpenSpec.
- Nenhum código, endpoint, tabela, teste ou registro Xano foi alterado nesta avaliação.
- O bloqueio antigo de `db.direct_query` permanece real para esse recurso, mas não basta para concluir que não existe solução nativa.

## Conclusão da avaliação

`db.increment` é documentado como operação numérica atômica com condição `where`, guarda de estoque e contagem de linhas alteradas. `db.transaction` é documentado para agrupar operações com atomicidade. Isso torna plausível uma baixa guardada sem SQL direto, com erro específico e rollback se algum item falhar.

Ainda não há prova de que o runtime atual do Voltix aceite essa operação dentro da transação, reverta baixa multi-item quando um item falha, nem preserve a resposta HTTP 200 `confirmado=false` sob concorrência. O plano Free e a disponibilidade no workspace não foram verificados no dashboard nesta avaliação.

## Condição de retomada

A C1 só poderá voltar para `openspec/changes/` com nova aprovação e após uma prova em ambiente separado, gratuito, autorizado e sem dados reais. A prova deve incluir rollback multi-item, disputa concorrente pela última unidade, mapeamento do conflito para a resposta aprovada e avaliação de deadlock. Não fazer teste de compra ou publicar mudanças no workspace Voltix para fechar essa lacuna.

## Referências oficiais consultadas

- [Xano Developer MCP — operações de banco, `db.increment`, transação e try/catch](https://github.com/xano-inc/xano-developer-mcp/blob/main/src/xanoscript_docs/database.md).
- [Planos Xano](https://www.xano.com/pricing).

A documentação indica viabilidade como **candidata**, não comprova a execução no workspace deste projeto.
