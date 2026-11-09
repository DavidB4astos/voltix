## Why

A C4 entrega a consulta de Clientes e a C6 o histórico de Pedidos, mas o time interno ainda
não possui um registro de relacionamento com o Cliente. O roadmap (C7) prevê o Atendimento
como o histórico básico do CRM: sempre vinculado a um Cliente e a um UsuarioInterno
responsável, opcionalmente ligado a um Pedido do mesmo Cliente.

Sem essa entrega, o painel interno não tem onde registrar uma solicitação, acompanhar seu
andamento ou encerrá-la preservando o histórico.

## What Changes

- Criar a tabela `atendimento` no Xano, com `cliente_id`, `usuario_interno_id`,
  `pedido_id` opcional, `assunto`, `descricao`, `status`, `data_atendimento`,
  `created_at` e `updated_at`.
- Criar o grupo de API `Voltix Internal CRM` com cinco endpoints sob `/atendimentos`:
  - `POST atendimentos`
  - `GET atendimentos`
  - `GET atendimentos/{attendance_id}`
  - `PATCH atendimentos/{attendance_id}`
  - `POST atendimentos/{attendance_id}/status`
- Exigir UsuarioInterno autenticado, `ATIVO` e com papel `FUNCIONARIO` ou `ADMINISTRADOR`
  em todos os endpoints; Cliente, visitante e interno `INATIVO` são negados no backend.
- Permitir que qualquer interno autorizado crie, liste, consulte e edite o conteúdo de
  Atendimentos em `ABERTO` ou `EM_ATENDIMENTO`.
- Definir o responsável como o UsuarioInterno que cria o Atendimento; o vínculo com
  Cliente, Pedido e responsável não é reatribuído nesta change.
- Permitir que qualquer interno autorizado inicie um Atendimento
  (`ABERTO → EM_ATENDIMENTO`).
- Exigir que a finalização ou o cancelamento seja feito pelo responsável ou por um
  `ADMINISTRADOR` ativo.
- Tratar `FINALIZADO` e `CANCELADO` como imutáveis; repetir o mesmo status é um no-op
  idempotente, sem escrita.
- Validar que o Cliente existe e que o Pedido opcional pertence ao mesmo Cliente.
- Responder somente identificadores, sem dados pessoais do Cliente, e não implementar
  tela, mensagens, SLA, automação ou reatribuição.
- Não alterar C2, C3, C4, C6 ou C10.

## Capabilities

### New Capabilities
- `attendance-management`: criação, consulta, edição e transição de status de
  Atendimentos do CRM interno, com vínculos válidos, autorização por papel/status,
  imutabilidade dos estados finais e histórico preservado.

### Modified Capabilities
- Nenhuma. A consulta de Clientes continua em `internal-customers` (C4), a consulta de
  Pedidos em `order-management` (C3) e o histórico do Cliente em
  `customer-order-history` (C6).

## Impact

- **Xano**: uma tabela nova (`atendimento`) e um grupo de API novo
  (`Voltix Internal CRM`) com cinco endpoints. Nenhum endpoint existente muda.
- **Frontend**: nenhum (backend + spec). A tela de atendimentos fica para change própria.
- **Dados**: escrita em `atendimento`; leitura de `CLIENTE`, `user` e `pedido` para
  validar vínculos. Nenhum dado de Cliente, Pedido ou UsuarioInterno é alterado.
- **Publicação**: depende da medição E5 (plano/consumo no dashboard Xano) e de gate
  explícito; dry-run restrito e verificação remota somente leitura.
