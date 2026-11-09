# 01 — Tela de Atendimentos: verificação local (09/11/2026)

## Escopo verificado

- Seção **Atendimentos** no painel interno, em largura total, acessível a
  FUNCIONARIO e ADMINISTRADOR ativos.
- Listagem com filtros `cliente_id`/`status`, total e paginação de 20, consumindo
  `GET atendimentos` (C7 já publicado).
- Criação com `cliente_id` obrigatório, `pedido_id` opcional, assunto, descrição e
  `data_atendimento` opcional, sem enviar `usuario_interno_id` ou `status`.
- Detalhe com vínculos somente leitura, edição condicionada a `ABERTO`/
  `EM_ATENDIMENTO` e controles de status limitados por status, responsável e papel.
- Estados de carregamento, vazio, erro e sessão não autorizada.
- Nenhuma alteração de backend, schema, rota ou publicação Xano.

## Verificação local

| Item | Resultado |
|---|---|
| `python -m unittest discover -s tests -q` | **235 testes**, OK |
| `reflex compile` | **App compiled successfully** (7,1 s) |
| `openspec validate implement-attendance-panel --strict` | válido |
| `openspec validate --all --strict` | **23 passed**, 0 failed |
| `git diff --check` | limpo (apenas avisos de LF/CRLF) |
| `git status` após compile | sem alterações em `reflex.lock` |

## Contrato Python

`voltix/internal_attendances.py`:

- `attendance_filters` valida `cliente_id` positivo opcional, status
  (`TODOS`/`ABERTO`/`EM_ATENDIMENTO`/`FINALIZADO`/`CANCELADO`), página e
  `per_page` (1–50).
- `attendance_record` exige exatamente `{id, cliente_id, usuario_interno_id,
  pedido_id, assunto, descricao, status, data_atendimento, created_at,
  updated_at}`, valida tipos, status, vínculos e limites de texto.
- `attendance_page` exige exatamente `{items, page, per_page, total_items,
  total_pages}`, confere página, tamanho, totais e duplicidade.
- `status_result` exige exatamente `{atendimento_id, status_anterior,
  status_atual, alterado}`.
- Datas são apresentadas em UTC (`dd/mm/aaaa às hh:mm (UTC)`) e convertidas para
  `datetime-local` sem recálculo no navegador.
- `positive_int` e `customer_date_display` são reutilizados de
  `internal_customers`; `bounded_read` continua limitando o retry de 429.

## Handlers e segurança

- Requisições server-side com token interno (`Bearer`); nenhum token ou URL
  privada chega ao navegador.
- Criação envia somente `cliente_id`, `pedido_id` (quando informado), `assunto`,
  `descricao` e `data_atendimento` (quando informada).
- Edição envia somente `assunto`, `descricao` e `data_atendimento` e recusa
  registros `FINALIZADO`/`CANCELADO`.
- Transições validadas localmente antes da escrita; o backend permanece a
  autoridade.
- `401` encerra a sessão; `403` em leitura/criação/edição também encerra. `403`
  na transição de status é negação de operação e mantém a sessão e o registro.
- Respostas obsoletas são descartadas por geração, token, usuário e seleção.

## Configuração

Três variáveis, documentadas em `.env.example` sem valores:

- `XANO_INTERNAL_ATTENDANCES_URL` — coleção `GET`/`POST`.
- `XANO_INTERNAL_ATTENDANCE_DETAILS_URL` — contém `{attendance_id}`, `GET`/`PATCH`.
- `XANO_INTERNAL_ATTENDANCE_STATUS_URL` — contém `{attendance_id}`, `POST` de status.

## Limites

- Não houve publicação ou verificação remota autenticada: a tela reutiliza os
  cinco endpoints publicados na C7.
- Não houve QA visual autenticada por falta de credencial interna nesta execução;
  a validação ficou limitada a contrato, handlers, navegação, renderização e
  `reflex compile`.
- O consumo total de registros do Xano continua não exposto; permanece a
  limitação registrada na C7.
- `reflex.lock/bun.lock` e `reflex.lock/package.json` foram alterados pelo compile
  local e restaurados; não entram no commit.
