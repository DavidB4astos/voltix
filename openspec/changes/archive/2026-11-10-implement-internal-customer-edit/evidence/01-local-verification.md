# 01 — Edição administrativa de Cliente: verificação local (10/11/2026)

## Escopo implementado

- Endpoint local `xano/api/internal_customers/customer_id_PATCH.xs` no grupo
  `Voltix Internal Customers`, com `auth = "user"` e autorização exclusiva de
  `ADMINISTRADOR` ativo.
- Edição parcial de `nome_completo`, `email`, `telefone` e `status`; CPF, senha,
  `USER_ID` e vínculos fora da entrada.
- Validação de nome (1–300), e-mail válido até 254, telefone até 30, e-mail único
  ignorando o próprio Cliente, `updated_at` em transação e resposta sanitizada
  equivalente ao detalhe.
- Contrato Python `customer_update_payload` e `customer_status_payload`, reutilizando
  `customer_record(..., detail=True)`.
- Ficha do Cliente com formulário e ações de status somente para `ADMINISTRADOR`;
  `FUNCIONARIO` permanece em consulta somente leitura.
- Confirmação em dois passos para inativar; reativação direta; feedback `role=status`;
  recarga da lista preservando o detalhe após sucesso.
- Nova variável server-side `XANO_INTERNAL_CUSTOMER_UPDATE_URL` documentada sem valor.

## Verificação local

| Item | Resultado |
|---|---|
| `python -m unittest tests.test_internal_customers -q` | **44 testes**, OK |
| `python -m unittest discover -s tests -q` | **348 testes**, OK |
| `reflex compile` | **App compiled successfully** (2,66 s) |
| `openspec validate implement-internal-customer-edit --strict` | válido |
| `openspec validate --all --strict` | **27 passed**, 0 failed (26 specs + change ativa; 26 specs após o arquivamento) |
| `git diff --check` | limpo (apenas avisos de LF/CRLF) |
| `git status` após compile | `reflex.lock` restaurado, sem alterações versionadas |

## Cobertura de testes adicionada

- Payload parcial: campos em branco preservam valores, e-mail normalizado para
  minúsculas, nome inalterado omitido.
- Rejeição de nome acima de 300, e-mail inválido/acima de 254, telefone acima de 30 e
  entrada não textual.
- Status aceita somente `ATIVO`/`INATIVO`.
- `ADMINISTRADOR` atualiza via `PATCH`, token interno, `retry_rate_limit=False`,
  placeholder `{customer_id}` substituído e lista recarregada preservando o detalhe.
- `FUNCIONARIO` não gera requisição; payload vazio/inalterado não gera requisição.
- Inativação exige confirmação; cancelamento restaura; reativação é direta.
- `400` de e-mail duplicado mantém a ficha; `403` encerra a sessão; resposta descartada
  após logout durante a atualização.

## Pendências

- Publicação do endpoint no Xano depende de autorização explícita (dry-run restrito,
  publicação e pull de verificação).
- Verificação visual responsiva 375/768/1280 permanece não executada.
- Commit e push dependem de autorização explícita.
