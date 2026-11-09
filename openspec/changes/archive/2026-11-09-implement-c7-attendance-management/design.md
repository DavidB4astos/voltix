## Context

Ver `proposal.md`. A C7 completa o CRM iniciado em C4/C6: o Atendimento é o registro
básico de relacionamento com o Cliente, sempre vinculado a um UsuarioInterno responsável e
opcionalmente a um Pedido do mesmo Cliente (`docs/domain-model.md`, seção 6.1).

Restrições:

- Plano Free e workspace compartilhado: a publicação depende da medição E5 no dashboard
  Xano e de gate explícito do usuário.
- O padrão interno do projeto é `auth = "user"` + `precondition` de papel/status no
  backend; o frontend nunca é fonte de autorização.
- Nenhum dado pessoal do Cliente nas respostas; apenas identificadores.
- Escopo backend + spec: sem tela, mensagens, SLA, automação ou reatribuição.
- Não alterar endpoints, tabelas ou capabilities já publicados.

## Goals / Non-Goals

**Goals:**

- Tabela `atendimento` com vínculos para Cliente, UsuarioInterno e Pedido opcional.
- Grupo `Voltix Internal CRM` com cinco endpoints em `/atendimentos`.
- Criação com responsável = criador e status inicial `ABERTO`.
- Lista paginada com filtros por Cliente e status, ordenada por data e id decrescentes.
- Detalhe e edição de conteúdo enquanto `ABERTO`/`EM_ATENDIMENTO`.
- Transições `ABERTO → EM_ATENDIMENTO`, `→ FINALIZADO` e `→ CANCELADO` com regra de
  responsável/ADMIN e idempotência.
- Imutabilidade de `FINALIZADO`/`CANCELADO`.
- Validação de Cliente existente e de Pedido pertencente ao mesmo Cliente.
- Respostas determinísticas para vínculos inválidos, imutabilidade e lista vazia.

**Non-Goals:**

- Tela/seção de atendimentos no painel Reflex.
- Mensagens, interações, anexos, SLA, filas, prioridade, notificações ou automação.
- Reatribuição de responsável, transferência de Cliente ou troca de Pedido vinculado.
- Reabertura de Atendimento `FINALIZADO`/`CANCELADO`.
- Alterar C2, C3, C4, C6 ou C10.
- Excluir Atendimentos; o histórico é preservado por status.

## Decisions

1. **Tabela e schema**: `atendimento` com `cliente_id` (FK `CLIENTE`), `usuario_interno_id`
   (FK `user`), `pedido_id?` (FK `pedido`), `assunto`, `descricao`, `status` enum com
   padrão `ABERTO`, `data_atendimento` com padrão `now`, `created_at` e `updated_at`
   privados. Índices por Cliente, responsável, Pedido, status e `data_atendimento desc.
   - Alternativa considerada: reaproveitar `pedido` ou criar tabela de mensagens.
     Rejeitadas por misturar responsabilidades e por estarem fora do escopo aprovado.
2. **Grupo e rotas**: `api_group "Voltix Internal CRM"` (`canonical =
   "voltix-internal-crm"`) com `POST atendimentos`, `GET atendimentos`,
   `GET atendimentos/{attendance_id}`, `PATCH atendimentos/{attendance_id}` e
   `POST atendimentos/{attendance_id}/status`.
   - O caminho usa `/atendimentos` para manter o domínio explícito e evitar colisão com
     os grupos já publicados.
3. **Autorização**: todos os endpoints usam `auth = "user"` e um `db.get user` restrito a
   `id`, `role` e `status`, com `precondition` de `ATIVO` e papel `FUNCIONARIO` ou
   `ADMINISTRADOR`. A regra é reavaliada no backend em toda chamada.
4. **Criação**: entradas `cliente_id`, `pedido_id?`, `assunto`, `descricao` e
   `data_atendimento?`. O backend valida o Cliente e, quando houver Pedido, se ele
   pertence ao mesmo Cliente. `usuario_interno_id` recebe `$auth.id`; `status` recebe
   `ABERTO`; `data_atendimento` recebe `now` quando ausente. A escrita ocorre em
   `db.transaction`.
   - Alternativa considerada: aceitar `usuario_interno_id` no payload. Rejeitada por
     permitir falsificação de responsável.
5. **Lista**: filtros `cliente_id?`, `status?=TODOS`, `page?=1` e `per_page?=20`.
   `status` aceita `TODOS` ou os quatro estados; `per_page` máximo 50. Ordenação
   `data_atendimento desc, id desc`. Totais `itemsTotal`/`pageTotal` são expostos como
   `total_items`/`total_pages`, com `total_pages=0` quando não há itens (mesmo padrão de
   C4/C6).
6. **Detalhe**: `db.get atendimento` por `id`; ausência → `notfound`. A resposta usa o
   mesmo formato da criação e da edição, sem joins de dados pessoais.
7. **Edição**: `PATCH` aceita somente `assunto`, `descricao` e `data_atendimento?`, em
   `db.transaction`. O registro é relido para checar existência e status; se estiver
   `FINALIZADO` ou `CANCELADO`, `badrequest`. `updated_at` é atualizado. Vínculos não são
   editáveis.
   - Alternativa considerada: `PATCH` com substituição completa do recurso. Rejeitada por
     aumentar o risco de alterar vínculos e por divergir do padrão de edição parcial já
     usado no projeto.
8. **Transição de status**: entrada `status` com `EM_ATENDIMENTO`, `FINALIZADO` ou
   `CANCELADO`. Regras:
   - status igual ao atual → sucesso idempotente com `alterado=false`, sem escrita;
   - `ABERTO → EM_ATENDIMENTO` → permitido a qualquer interno autorizado;
   - `ABERTO`/`EM_ATENDIMENTO → FINALIZADO` ou `CANCELADO` → somente responsável ou
     `ADMINISTRADOR` ativo;
   - `FINALIZADO`/`CANCELADO →` qualquer outro status → `badrequest`;
   - qualquer outra combinação → `badrequest`.
   Tudo em `db.transaction`, atualizando `updated_at` apenas quando houver mudança. A
   resposta segue o padrão de C3: `atendimento_id`, `status_anterior`, `status_atual` e
   `alterado`.
9. **Contrato de resposta**: o Atendimento é exposto como `id`, `cliente_id`,
   `usuario_interno_id`, `pedido_id`, `assunto`, `descricao`, `status`,
   `data_atendimento`, `created_at` e `updated_at`. Nenhum nome, e-mail, CPF, telefone,
   endereço, senha ou token do Cliente é retornado.
10. **Validação de entrada**: `assunto` de 1 a 200 caracteres e `descricao` de 1 a 2000
    caracteres, com `strlen` em `precondition` (mesmo padrão de C4/C6). `cliente_id` e
    `pedido_id` com `filters=min:1`. Violações → `inputerror`/`badrequest` sem escrita.
11. **Verificação**: language server oficial + `openspec validate --strict` + suíte de
    testes + dry-run restrito + pull independente + checagem 401 sem sessão. O ciclo
    autenticado completo só ocorre com autorização explícita e após a medição E5.

## Risks / Trade-offs

- [Consumo do plano Free] → a C7 adiciona uma tabela e cinco endpoints; publicar apenas
  após medir E5 e obter gate. Nenhum teste remoto autenticado sem autorização.
- [Atendimento sem responsável ativo depois] → o vínculo é preservado mesmo se o
  UsuarioInterno for inativado; a autorização é reavaliada a cada chamada. Tratar
  reatribuição fica para change futura.
- [Pedido alterado/excluído depois] → o vínculo é histórico; a FK preserva o id. Exclusão
  não faz parte do domínio atual (Pedido é cancelado, não excluído).
- [Edição parcial] → `PATCH` aceita apenas conteúdo; clientes que enviarem vínculos terão
  os campos ignorados/rejeitados, conforme a spec. Documentar no contrato do frontend
  futuro.
- [Escopo de CRM] → sem mensagens, SLA ou automação; a simplicidade é intencional para o
  Free e para o escopo acadêmico.

## Migration Plan

1. Criar `xano/table/atendimento.xs` com FKs, enum, timestamps e índices.
2. Criar `xano/api/internal_crm/api_group.xs` e os cinco endpoints.
3. Validar com o language server oficial e `openspec validate --strict`.
4. Rodar a suíte local e `git diff --check`; restaurar `reflex.lock/*`.
5. Medir E5 no dashboard Xano; apresentar plano/consumo e aguardar gate explícito.
6. Dry-run restrito, publicação e pull independente + 401 na rota sem sessão.
7. Arquivar a change, consolidar `attendance-management` e atualizar roadmap/handoff.

## Open Questions

- Nenhuma bloqueante. Tela de atendimentos, reatribuição e mensagens ficam para changes
  próprias.
