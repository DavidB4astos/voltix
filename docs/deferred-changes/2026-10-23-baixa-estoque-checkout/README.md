# Change adiada: baixa-estoque-checkout (2026-10-23)

Esta pasta preserva integralmente os artefatos da change `baixa-estoque-checkout` (C1), que foi **adiada**, não concluída.

## Status

- **ADIADA/BLOQUEADA**, não concluída.
- **Progresso:** 0/11 tarefas.
- **Não é uma change ativa do OpenSpec.**
- Nenhum código de aplicação, endpoint, banco, teste ou dependência foi alterado por este adiamento.

## Bloqueio

A tarefa 1.1 não pôde ser concluída porque `db.direct_query` não está disponível no plano Xano Free (`ERROR_CODE_ACCESS_DENIED`). Sem esse primitivo, não há alternativa nativa comprovada para garantir baixa atômica de estoque, rollback conjunto e estoque nunca negativo sob concorrência.

A implementação de uma solução insegura não está autorizada.

## Condição de retomada

A change poderá ser retomada somente quando:

1. existir uma solução compatível com o plano gratuito do Xano que preserve atomicidade, rollback conjunto e estoque nunca negativo; e
2. houver nova aprovação explícita para movê-la de volta para `openspec/changes/` e iniciar a implementação.

## Conteúdo preservado

- `.openspec.yaml`
- `proposal.md`
- `design.md`
- `tasks.md`
- `specs/checkout-orders/spec.md`

Os arquivos foram movidos sem alteração de conteúdo. Este diretório é apenas um registro de adiamento e não deve ser tratado como change ativa nem arquivada como concluída.
