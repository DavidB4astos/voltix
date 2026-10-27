# Changes adiadas

Esta pasta preserva artefatos de changes que foram **adiadas** por bloqueio técnico, dependência externa ou decisão de priorização, sem serem concluídas nem arquivadas.

## Convenção

- Cada change adiada fica em `docs/deferred-changes/YYYY-MM-DD-<change-name>/`.
- O diretório deve conter os artefatos originais preservados e um `README.md` com:
  - status (ADIADA/BLOQUEADA, não concluída);
  - progresso de tarefas;
  - motivo do adiamento;
  - condição objetiva de retomada;
  - confirmação de que nenhum artefato foi descartado.
- Change adiada **não é change ativa** do OpenSpec e **não pode ser arquivada como concluída**.
- A retomada exige nova aprovação explícita e a movimentação de volta para `openspec/changes/<change-name>/`.
- Enquanto estiver adiada, não implementar tarefas, não alterar código relacionado e não recriar a mesma change como nova.
