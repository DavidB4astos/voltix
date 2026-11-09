## Context

Ver `proposal.md` — Why. A C7 já publicou `POST/GET /atendimentos`,
`GET/PATCH /atendimentos/{attendance_id}` e `POST /atendimentos/{attendance_id}/status`
com `auth = "user"` e precondição de FUNCIONARIO/ADMINISTRADOR `ATIVO`. A tela não altera o
Xano.

O painel interno é renderizado em `voltix/voltix.py` por `internal_workspace_shell`, com
seções controladas por `State.internal_section` e navegação montada em
`internal_workspace_shell`. O contrato de Clientes (`voltix/internal_customers.py`) já
oferece `positive_int`, `bounded_read` e `customer_date_display`; a UI de Clientes usa
`_server_side_xano_request` com token interno e `bounded_read` para 429.

Restrições:

- Sessão interna privada no servidor; nenhum token no navegador.
- Respostas de Atendimento expõem o Cliente apenas como `cliente_id`.
- Sem backend novo, schema, migração ou publicação Xano.
- `reflex.lock/*` não entra em commit.

## Goals / Non-Goals

**Goals:**
- Seção Atendimentos em largura total, acessível a FUNCIONARIO e ADMINISTRADOR ativos.
- Listagem filtrável por `cliente_id`/`status`, paginada em 20 e ordenada pelo backend.
- Criação, detalhe, edição e transições de status com contrato Python estrito.
- Controles de finalizar/cancelar coerentes com responsável e papel, sem substituir o backend.
- Estados de carregamento, vazio, erro e sessão, com descarte de respostas obsoletas.

**Non-Goals:**
- Mensagens, SLA, automação, anexos, exportação ou métricas.
- Editar vínculos, reatribuir responsável ou criar Atendimento por Cliente/visitante.
- Resolver nome do Cliente/Pedido na tela; a referência é por id.
- Alterar as telas de Clientes, Pedidos, Dashboard, Produtos, Catálogo ou Importação.
- Publicação ou validação remota autenticada no Xano.

## Decisions

1. **Contrato em módulo próprio.** Criar `voltix/internal_attendances.py` com
   `Attendance`, `ATTENDANCE_STATUSES`, `attendance_record`, `attendance_page`,
   `status_result` e `attendance_filters`. Importar `positive_int`, `bounded_read` e
   `customer_date_display` de `internal_customers` para não duplicar helpers. Alternativa
   descartada: ampliar `internal_customers.py`, que passaria a misturar dois domínios.

2. **Formato exato das respostas.** A listagem deve ter exatamente
   `{items, page, per_page, total_items, total_pages}` e cada item exatamente
   `{id, cliente_id, usuario_interno_id, pedido_id, assunto, descricao, status,
   data_atendimento, created_at, updated_at}`. O detalhe, a criação e a edição validam o
   mesmo registro. A resposta de status deve ter exatamente
   `{atendimento_id, status_anterior, status_atual, alterado}`. Campos extras, tipos
   inválidos, status desconhecido, `pedido_id` não inteiro/positivo, totais inconsistentes
   ou página com tamanho divergente são rejeitados. Alternativa descartada: aceitar campos
   extras, o que mascararia mudanças de contrato.

3. **Normalização de campos.**
   - `pedido_id` é `None` ou inteiro ≥ 1; na UI vira texto opcional.
   - `assunto` 1–200 e `descricao` 1–2000, preservados como texto aparado.
   - `data_atendimento`, `created_at` e `updated_at` usam `customer_date_display` para
     `dd/mm/aaaa às hh:mm (UTC)`; valor impróprio vira "Data indisponível" sem quebrar a
     tela.
   - O status é restrito a `ABERTO`, `EM_ATENDIMENTO`, `FINALIZADO` e `CANCELADO`.

4. **Ciclo de listagem.** `State.internal_attendance_*` guarda filtros, página, itens,
   totais, carregamento, mensagem e geração. `load_internal_attendances` exige sessão
   interna válida, valida filtros localmente, monta a URL com `urlencode`, faz a leitura
   server-side e grava somente se geração, token e usuário continuarem atuais. O botão
   "Carregar / atualizar" e a seleção da seção usam o mesmo handler.

5. **Criação.** Campos de formulário separados do estado aplicado. O handler valida
   `cliente_id` ≥ 1, assunto/descrição e `pedido_id` opcional antes de chamar o backend.
   O payload contém somente `cliente_id`, `pedido_id` (quando informado), `assunto`,
   `descricao` e `data_atendimento` (quando informada). `usuario_interno_id` e `status`
   nunca são enviados. Em sucesso: limpa o formulário, recarrega a lista e carrega o
   detalhe criado.

6. **Detalhe e edição.** `select_internal_attendance(id)` valida o id, carrega o detalhe e
   descarta respostas de seleções anteriores. `save_internal_attendance` envia somente
   `assunto`, `descricao` e `data_atendimento` e apenas quando o status atual é `ABERTO` ou
   `EM_ATENDIMENTO`. Os vínculos aparecem em campos somente leitura. `notfound` fecha o
   detalhe; `badrequest` mantém o registro somente leitura e informa imutabilidade.

7. **Transições de status.** `change_internal_attendance_status(status)` valida o alvo contra
   o status atual antes de chamar o backend. A tela oferece:
   - `EM_ATENDIMENTO` quando o status é `ABERTO`;
   - `FINALIZADO`/`CANCELADO` quando o status é `ABERTO` ou `EM_ATENDIMENTO` e o usuário é
     o responsável (`usuario_interno_id == State.user_id`) ou `ADMINISTRADOR`.
   A tela usa `alterado` para confirmar a operação, mas não presume autorização: respostas
   `accessdenied`/`badrequest` mantêm o estado e mostram a mensagem; `403` nessa rota é
   negação de operação e não encerra a sessão.

8. **Integração com a navegação.** `State.select_internal_section` passa a aceitar
   `atendimentos` para FUNCIONARIO e ADMINISTRADOR. O item de navegação Atendimentos fica
   ao lado de Clientes, visível aos dois papéis. O título/descrição da seção são incluídos
   no `rx.match` de `internal_workspace_shell`.

9. **Layout e estilos.** Reutilizar a linguagem de `vx-customers`/`vx-history` e adicionar
   um bloco `vx-attendance` em `assets/voltix-internal.css` para: barra de filtros e
   formulário de criação, tabela/lista de resultados, painel de detalhe, formulário de
   edição, botões de status, mensagens e paginação. O layout é desktop-first, com quebra
   em telas estreitas, sem redesenhar o restante do painel.

10. **Erros e sessão.** `401` e `403` de leitura/criação/edição chamam
    `_clear_authentication_state`, limpam listagem, detalhe, filtros e contadores. Na
    transição de status, `403` é negação de operação e mantém a sessão e o estado; `401`
    encerra a sessão. Demais falhas mostram mensagem genérica em português e permitem nova
    tentativa. O retry de 429 continua limitado a uma tentativa por `bounded_read`. Payload
    bruto nunca é exibido.

11. **Configuração.** Três variáveis:
    - `XANO_INTERNAL_ATTENDANCES_URL` — coleção `GET`/`POST`;
    - `XANO_INTERNAL_ATTENDANCE_DETAILS_URL` — contém `{attendance_id}`, usada em
      `GET`/`PATCH`;
    - `XANO_INTERNAL_ATTENDANCE_STATUS_URL` — contém `{attendance_id}`, usada no `POST` de
      status.
    Nomes documentados em `.env.example` sem valor; placeholder ausente é erro local.

12. **Acessibilidade.** Rótulos associados, `aria_label` por item e seção, `role=status`
    nas mensagens, foco visível e botões com nomes acessíveis. Nenhum dado pessoal do
    Cliente é renderizado.

13. **Verificação.** Testes unitários do contrato (listagem, detalhe, criação, edição e
    status), testes dos handlers com respostas simuladas, suíte existente,
    `openspec validate --all --strict`, `git diff --check` e `reflex compile` restaurando
    `reflex.lock`. Sem consulta autenticada e sem publicação Xano.

## Risks / Trade-offs

- [Referências por id] A tela mostra `cliente_id`/`pedido_id` sem nome, o que exige o
  operador conhecer os ids. Mitigação: rótulos explícitos e a seção Clientes existente
  continua disponível para consulta.
- [Regras duplicadas na UI] A tela esconde ações inválidas, mas o backend é a autoridade.
  Mitigação: todos os handlers tratam `accessdenied`/`badrequest` e recarregam o estado.
- [Volume de formulário] Criação, edição e status no mesmo painel aumentam a densidade.
  Mitigação: estados claros (somente leitura, editável, encerrado) e mensagens curtas.
- [Respostas privadas] `created_at`/`updated_at` podem variar em visibilidade. Mitigação:
  o contrato aceita exatamente o formato publicado na C7 e falha de forma segura se ele
  mudar.
- [Sem credencial de teste] A verificação remota autenticada fica fora desta change; a tela
  é validada por contrato, testes e compile.
- [Datas] Conversão local pode divergir de fusos; o backend continua sendo a autoridade e
  a UI apenas apresenta UTC.

## Migration Plan

1. Adicionar o contrato e os testes unitários.
2. Adicionar campos/handlers no `State` e liberar a seção na navegação.
3. Renderizar listagem, criação, detalhe, edição e status; adicionar estilos.
4. Documentar as três variáveis em `.env.example` e configurá-las no ambiente local.
5. Rodar testes, `openspec validate --all --strict`, `git diff --check` e `reflex compile`;
   restaurar `reflex.lock`.
6. Arquivar a change e atualizar roadmap/handoff. Sem publicação Xano.

Rollback: remover a seção da navegação e o bloco de renderização; o backend publicado e as
variáveis de ambiente podem permanecer sem afetar as demais telas.

## Open Questions

- Nenhuma bloqueante. A tela consome somente o contrato já publicado na C7.
