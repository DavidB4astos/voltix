# 01 — C7: dry-run restrito (09/11/2026)

## Comando

```
xano workspace push -d xano --dry-run \
  -i "table/atendimento.xs" \
  -i "api/internal_crm/api_group.xs" \
  -i "api/internal_crm/attendances_POST.xs" \
  -i "api/internal_crm/attendances_GET.xs" \
  -i "api/internal_crm/attendance_id_GET.xs" \
  -i "api/internal_crm/attendance_id_PATCH.xs" \
  -i "api/internal_crm/attendance_id_status_POST.xs"
```

## Resultado

```
Matched: 7 of 113 files

=== Push Preview: workspace 147981 ===
  instance: x8ki-letl-twmt.n7.xano.io  |  workspace: David's Workspace  |  cli: v1.2.0

  Tables               +1 created
  API Groups           +1 created
  API Endpoints        +5 created
```

| Tipo | Documento |
|---|---|
| table | `atendimento` |
| api_group | `Voltix Internal CRM` |
| query | `atendimentos POST` |
| query | `atendimentos GET` |
| query | `atendimentos/{attendance_id} GET` |
| query | `atendimentos/{attendance_id} PATCH` |
| query | `atendimentos/{attendance_id}/status POST` |

Nenhum schema, grupo, tabela ou endpoint existente foi incluído no dry-run.

## Limites

- O dry-run é somente preview: nada foi publicado e nenhum registro foi gravado.
- A medição E5 (plano/consumo no dashboard Xano) ainda não foi registrada nesta change.
- A publicação permanece bloqueada até a evidência E5 e o gate explícito do usuário.
- O aviso de atualização da CLI (1.2.0 → 1.3.4) não foi aplicado.
