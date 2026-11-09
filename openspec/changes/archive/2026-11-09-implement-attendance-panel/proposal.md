## Why

A C7 publicou a tabela `atendimento` e cinco endpoints no grupo `Voltix Internal CRM`,
mas o painel interno ainda não oferece nenhuma tela para registrar ou acompanhar
Atendimentos. Hoje o time só consegue usar a capability por chamadas diretas à API, o que
impede o uso operacional do CRM. O roadmap prevê a tela de atendimentos como a próxima
entrega visual de CRM.

## What Changes

- Adicionar a seção **Atendimentos** no painel interno (Reflex), disponível para
  FUNCIONARIO e ADMINISTRADOR ativos.
- Listar Atendimentos com filtros opcionais por `cliente_id` e `status`, paginação de 20
  itens e ordenação já definida pelo backend (`data_atendimento` e `id` decrescentes).
- Criar Atendimento informando `cliente_id` obrigatório, `pedido_id` opcional, `assunto`,
  `descricao` e `data_atendimento` opcional; o responsável é sempre o interno autenticado.
- Abrir o detalhe de um Atendimento e editar `assunto`, `descricao` e `data_atendimento`
  somente em `ABERTO` ou `EM_ATENDIMENTO`.
- Executar as transições de status (`EM_ATENDIMENTO`, `FINALIZADO`, `CANCELADO`) com os
  botões limitados pelo status atual, pelo papel e pela responsabilidade exibidos na tela,
  mantendo o backend como autoridade final.
- Exibir estados distintos de carregamento, vazio, erro e sessão não autorizada, e
  descartar respostas obsoletas quando filtros, página, Atendimento ou sessão mudarem.
- Adicionar contrato Python estrito para validar as respostas antes de levá-las ao
  navegador e variáveis de ambiente para as URLs internas de Atendimento.
- **Sem** alteração, publicação ou schema novo no Xano: a tela consome os endpoints já
  publicados na C7.
- **Sem** mensagens, SLA, automação, anexos, exportação, métricas ou atribuição de outro
  responsável.

## Capabilities

### New Capabilities
- `attendance-panel`: seção desktop do painel interno que lista, cria, detalha, edita e
  transiciona Atendimentos, respeitando vínculos, status e autorização publicados na C7.

### Modified Capabilities
- `internal-workspace`: a navegação interna passa a oferecer Atendimentos a FUNCIONARIO e
  ADMINISTRADOR e deixa de tratar CRM como funcionalidade não implementada.

## Impact

- **Frontend**: `voltix/voltix.py` (State, handlers, navegação e renderização), novo
  contrato em `voltix/internal_attendances.py`, estilos em `assets/voltix-internal.css`.
- **Configuração**: novas variáveis de URL interna de Atendimento em `.env` e
  `.env.example` (somente nomes documentados).
- **Backend/Xano**: nenhuma alteração, publicação ou migração.
- **Testes**: novos testes de contrato e dos handlers da tela; suíte existente
  preservada.
- **Segurança**: requisições server-side com token interno; nenhum token exposto ao
  navegador; respostas limitadas a ids e conteúdo do Atendimento, sem dados pessoais do
  Cliente.
