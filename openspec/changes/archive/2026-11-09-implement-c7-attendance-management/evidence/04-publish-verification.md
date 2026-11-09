# 04 — C7: publicação e verificação (09/11/2026)

## Publicação inicial (autorizada)

```
xano workspace push -d xano --force \
  -i "table/atendimento.xs" \
  -i "api/internal_crm/api_group.xs" \
  -i "api/internal_crm/attendances_POST.xs" \
  -i "api/internal_crm/attendances_GET.xs" \
  -i "api/internal_crm/attendance_id_GET.xs" \
  -i "api/internal_crm/attendance_id_PATCH.xs" \
  -i "api/internal_crm/attendance_id_status_POST.xs"
```

Resultado: `Matched: 7 of 113 files` · `Synced 7 GUIDs to local files` ·
`Pushed 7 documents to workspace 147981 from xano in 2.2s`.

O CLI emitiu "Unresolved References" para `user`, `CLIENTE`, `pedido` e `atendimento`,
o mesmo comportamento heurístico de push parcial já observado em C1–C3/C6/C10. O pull
independente confirmou que as FKs e os `db.get user` foram preservados.

## Correção encontrada na verificação de borda

A primeira checagem de `GET atendimentos` retornou **HTTP 400**:

```
{"code":"ERROR_CODE_INPUT_ERROR","message":"Value is less than the minimum value of 1","payload":{"param":"cliente_id"}}
```

Causa: `filters=min:1` em campos opcionais (`cliente_id` no GET e `pedido_id` no POST)
rejeitava a ausência do campo. Correção:

- `GET atendimentos`: `cliente_id?` sem filtro e `precondition` explícita
  (`cliente_id == null || cliente_id >= 1`).
- `POST atendimentos`: `pedido_id?` sem filtro e `precondition` explícita
  (`pedido_id == null || pedido_id >= 1`).

Dry-run da correção: `Matched: 2 of 113 files` · `~2 updated` (apenas os dois endpoints).
Publicação da correção: `Pushed 2 documents ... in 1.9s`, também com os avisos heurísticos
de referências parciais.

## Pull independente

O pull completo (sem `--records`, `--env` ou `--draft`) confirmou os 7 documentos:

| Tipo | Documento | GUID |
|---|---|---|
| table | `atendimento` | `tuUsTN1wH7wh6iOW8Z74r6eQcQA` |
| api_group | `Voltix Internal CRM` | `kJrXoHeqF9YsRw5-n_Q12VMB1-E` |
| query | `atendimentos POST` | `MTwvlzJ9cWlYaSJTuTOIVFQXpaA` |
| query | `atendimentos GET` | `nFCAzxgRwLtLIOd_YsfAhoBk5pQ` |
| query | `atendimentos/{attendance_id} GET` | `XwbqC-3eUD4eyF7_thTfrplxuGo` |
| query | `atendimentos/{attendance_id} PATCH` | `S_PIZBbZshHyMWDUDrM3rDFc27Y` |
| query | `atendimentos/{attendance_id}/status POST` | `5mI3RPdbX8pY79Rq3F7JtykQgnc` |

O remoto preserva:

- `auth = "user"` e precondição de `FUNCIONARIO`/`ADMINISTRADOR` ativo nos cinco endpoints;
- FK de `cliente_id` para `CLIENTE`, `usuario_interno_id` para `user` e `pedido_id` para
  `pedido`;
- enum de status e defaults `ABERTO`/`now`;
- índices por cliente, responsável, pedido, status e `data_atendimento desc`;
- regras de transição, imutabilidade e no-op idempotente;
- correção dos campos opcionais (`cliente_id?` e `pedido_id?`).

Diferenças apenas de serialização canônica (fences e alinhamento). Sem alteração de
comportamento.

## Verificação de borda (somente leitura, sem sessão)

| Rota | Resultado |
|---|---|
| `GET /api:voltix-internal-crm/atendimentos` | HTTP 401 |
| `GET /api:voltix-internal-crm/atendimentos/1` | HTTP 401 |
| `GET /api:voltix-internal-crm/atendimentos?cliente_id=1` | HTTP 401 |
| `GET /api:voltix-internal-customers/customers/1` (controle) | HTTP 401 |

As rotas existem na borda e exigem autenticação antes de qualquer leitura. Nenhum
Atendimento foi criado, lido de forma autenticada ou alterado.

## Limites

- Não houve consulta autenticada nem dados sintéticos; verificação somente leitura.
- Não havia credencial de FUNCIONARIO/ADMINISTRADOR no ambiente para exercitar
  autorização positiva/negativa, paginação real, edição ou transições.
- O consumo de registros não foi exposto pelo Xano (ver `03-e5-usage.md`); a tabela nova
  começa vazia e deve ser monitorada após a primeira carga real.
- Nenhum upgrade de plano foi realizado.

## Verificação local

- Language server oficial (`validate.mjs`) → `OK` nos 7 arquivos, inclusive após a correção.
- `openspec validate implement-c7-attendance-management --strict` → válido.
- `python -m unittest discover -s tests -q` → 205 testes, OK.
- `openspec validate --all --strict` → 22 passed.
- `git diff --check` → limpo.
- `reflex.lock` restaurado; não entrou nos commits.
