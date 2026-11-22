## Context

`select_internal_section` dispara `State.load_internal_dashboard` e `State.load_internal_crm` sempre que `changed` é verdadeiro, mesmo quando os dados acabaram de ser carregados segundos antes.

## Goals / Non-Goals

- **Goals:**
  - Tornar a troca entre `Dashboard` e `CRM` instantânea dentro da janela de 20 s.
  - Reduzir de 7 para 6 as chamadas do `CRM` quando o `Dashboard` sem filtros já foi carregado nos últimos 20 s.
  - Distinguir claramente `HTTP 429` de erros de acesso (`401`/`403`) na mensagem exibida ao usuário.
- **Non-Goals:**
  - Alterar endpoints Xano ou desabilitar o botão manual de atualização.

## Decisions

1. **Timestamps privados em `State` (`_internal_dashboard_loaded_at`, `_internal_crm_loaded_at`):** armazenados com `time.monotonic()` e limpos no logout / `_clear_authentication_state` para nunca vazar entre sessões.
2. **Preservação de `401`/`403`:** qualquer `401`/`403` continua limpando sessão e dados imediatamente.
