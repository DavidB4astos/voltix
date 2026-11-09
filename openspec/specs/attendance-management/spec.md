# attendance-management Specification

## Purpose

Definir o registro e o acompanhamento de Atendimentos de CRM por usuários internos ativos,
sempre vinculados a um Cliente e a um responsável, com Pedido opcional do mesmo Cliente,
edição limitada aos estados abertos, transições de status autorizadas e imutabilidade após
finalização ou cancelamento.

## Requirements

### Requirement: Active internal users can create and read attendances

Um UsuarioInterno autenticado, `ATIVO` e com papel `FUNCIONARIO` ou `ADMINISTRADOR` SHALL
poder criar um Atendimento em `POST atendimentos`, listar Atendimentos em
`GET atendimentos` e abrir o detalhe em `GET atendimentos/{attendance_id}`. O Atendimento
SHALL ser criado com status `ABERTO` e `usuario_interno_id` igual ao UsuarioInterno
autenticado. A resposta SHALL conter `id`, `cliente_id`, `usuario_interno_id`, `pedido_id`,
`assunto`, `descricao`, `status`, `data_atendimento`, `created_at` e `updated_at`.
Cliente, visitante e UsuarioInterno `INATIVO` SHALL ser negados no backend antes de
qualquer leitura ou escrita.

#### Scenario: Funcionario creates an attendance

- **WHEN** um FUNCIONARIO ativo envia `cliente_id`, `assunto` e `descricao`
- **THEN** o backend cria um Atendimento `ABERTO`, com o FUNCIONARIO como responsável, e responde os campos do registro

#### Scenario: Administrator creates an attendance for a specific order

- **WHEN** um ADMINISTRADOR ativo informa um `pedido_id` que pertence ao Cliente do Atendimento
- **THEN** o Atendimento é criado com esse Pedido associado

#### Scenario: Attendance detail

- **WHEN** um interno autorizado consulta `GET atendimentos/{attendance_id}`
- **THEN** o backend responde o Atendimento correspondente ou `notfound` quando ele não existir

#### Scenario: Inactive internal user is denied

- **WHEN** um UsuarioInterno `INATIVO` tenta criar, listar ou consultar Atendimentos
- **THEN** o backend nega com `accessdenied` e nada é lido ou gravado

#### Scenario: Customer and visitor are denied

- **WHEN** um Cliente autenticado ou um visitante sem sessão chama um endpoint interno de Atendimentos
- **THEN** o backend nega o acesso antes de qualquer leitura ou escrita

### Requirement: Attendance links are valid and preserve the customer

Todo Atendimento SHALL pertencer a exatamente um Cliente existente e a exatamente um
UsuarioInterno responsável. O `pedido_id` SHALL ser opcional; quando informado, o Pedido
SHALL existir e pertencer ao mesmo Cliente do Atendimento. Um vínculo inválido SHALL ser
rejeitado com `notfound` para Cliente ou Pedido inexistente e com `badrequest` para Pedido
de outro Cliente, sem criar ou alterar o Atendimento. O responsável SHALL ser o criador do
Atendimento e SHALL NOT ser reatribuído nesta capability.

#### Scenario: Order from another customer is rejected

- **WHEN** o `pedido_id` informado pertence a um Cliente diferente do `cliente_id`
- **THEN** o backend responde `badrequest` e nenhum Atendimento é criado

#### Scenario: Unknown customer or order is rejected

- **WHEN** o `cliente_id` ou o `pedido_id` informado não existe
- **THEN** o backend responde `notfound` e nenhum Atendimento é criado

#### Scenario: Attendance without an order

- **WHEN** o `pedido_id` não é informado
- **THEN** o Atendimento é criado com `pedido_id` nulo e os demais vínculos preservados

#### Scenario: Responsible is the creator

- **WHEN** um interno autorizado cria um Atendimento
- **THEN** `usuario_interno_id` corresponde ao UsuarioInterno autenticado e não ao valor enviado pelo cliente da API

### Requirement: Attendance listing is filtered and paginated deterministically

`GET atendimentos` SHALL aceitar filtros opcionais `cliente_id` e `status`, além de `page`
e `per_page`. O filtro `status` SHALL aceitar `TODOS` (padrão) ou um dos quatro estados do
Atendimento. A página SHALL conter no máximo 50 itens, com 20 por padrão, e a resposta
SHALL conter `items`, `page`, `per_page`, `total_items` e `total_pages`. A ordenação SHALL
ser `data_atendimento` decrescente e, em empate, `id` decrescente. Quando não houver
Atendimentos, a resposta SHALL ser sucesso com `items=[]` e totais zerados. Filtros ou
paginação inválidos SHALL ser rejeitados com `inputerror` sem executar a consulta.

#### Scenario: Status and customer filters

- **WHEN** o usuário informa `cliente_id` e `status=EM_ATENDIMENTO`
- **THEN** somente Atendimentos daquele Cliente e naquele status entram na página e nos totais

#### Scenario: Pagination metadata

- **WHEN** um interno autorizado informa `page=2` e `per_page=50`
- **THEN** o backend responde até 50 Atendimentos e os totais de itens e páginas

#### Scenario: Invalid filters are rejected

- **WHEN** `page` é menor que 1, `per_page` está fora de 1–50 ou o `status` é desconhecido
- **THEN** o backend responde `inputerror` e não executa a consulta

#### Scenario: Empty listing

- **WHEN** nenhum Atendimento atende aos filtros
- **THEN** a resposta é sucesso com `items=[]` e `total_items=0`

### Requirement: Open attendances can be edited, closed attendances are immutable

`PATCH atendimentos/{attendance_id}` SHALL permitir que qualquer interno autorizado altere
`assunto`, `descricao` e `data_atendimento` enquanto o Atendimento estiver em `ABERTO` ou
`EM_ATENDIMENTO`. O backend SHALL atualizar `updated_at`. Atendimentos em `FINALIZADO` ou
`CANCELADO` SHALL NOT ser alterados e a tentativa SHALL ser rejeitada com `badrequest`.
`cliente_id`, `usuario_interno_id` e `pedido_id` SHALL NOT ser alterados após a criação.

#### Scenario: Edit an open attendance

- **WHEN** um interno autorizado altera `assunto`, `descricao` ou `data_atendimento` de um Atendimento `ABERTO`
- **THEN** o backend persiste os novos valores, atualiza `updated_at` e responde o registro atualizado

#### Scenario: Edit an in-progress attendance

- **WHEN** um interno autorizado altera o conteúdo de um Atendimento `EM_ATENDIMENTO`
- **THEN** o backend persiste os novos valores e mantém os vínculos originais

#### Scenario: Closed attendance cannot be edited

- **WHEN** um interno autorizado tenta alterar um Atendimento `FINALIZADO` ou `CANCELADO`
- **THEN** o backend responde `badrequest` e o registro permanece inalterado

#### Scenario: Links are immutable

- **WHEN** a requisição de edição informa `cliente_id`, `usuario_interno_id` ou `pedido_id`
- **THEN** o backend ignora ou rejeita esses campos e os vínculos originais permanecem

### Requirement: Status transitions respect responsibility and idempotency

`POST atendimentos/{attendance_id}/status` SHALL aceitar `EM_ATENDIMENTO`, `FINALIZADO` ou
`CANCELADO`. A transição `ABERTO → EM_ATENDIMENTO` SHALL ser permitida a qualquer interno
autorizado. `FINALIZADO` e `CANCELADO` SHALL ser permitidos a partir de `ABERTO` ou
`EM_ATENDIMENTO` somente ao UsuarioInterno responsável ou a um `ADMINISTRADOR` ativo.
Repetir o status atual SHALL ser sucesso idempotente com `alterado=false`, sem escrita.
Qualquer outra transição, inclusive a partir de `FINALIZADO` ou `CANCELADO`, SHALL ser
rejeitada com `badrequest`. A transição SHALL ocorrer em transação e atualizar `updated_at`.

#### Scenario: Any authorized internal user starts an attendance

- **WHEN** um FUNCIONARIO ativo que não é o responsável envia `status=EM_ATENDIMENTO` para um Atendimento `ABERTO`
- **THEN** o status passa para `EM_ATENDIMENTO` e `alterado=true`

#### Scenario: Responsible finishes an attendance

- **WHEN** o UsuarioInterno responsável envia `status=FINALIZADO` para um Atendimento `ABERTO` ou `EM_ATENDIMENTO`
- **THEN** o status passa para `FINALIZADO` e `updated_at` é atualizado

#### Scenario: Administrator cancels an attendance

- **WHEN** um ADMINISTRADOR ativo envia `status=CANCELADO` para um Atendimento `ABERTO` ou `EM_ATENDIMENTO`
- **THEN** o status passa para `CANCELADO` na mesma transação

#### Scenario: Non-responsible employee cannot finish or cancel

- **WHEN** um FUNCIONARIO ativo que não é o responsável envia `status=FINALIZADO` ou `CANCELADO`
- **THEN** o backend responde `accessdenied` e o status permanece inalterado

#### Scenario: Same status is idempotent

- **WHEN** o status enviado é igual ao status atual do Atendimento
- **THEN** o backend responde sucesso com `alterado=false` e não escreve no banco

#### Scenario: Closed attendance cannot transition

- **WHEN** um interno autorizado tenta mover um Atendimento `FINALIZADO` ou `CANCELADO` para qualquer status diferente do atual
- **THEN** o backend responde `badrequest` e o registro permanece inalterado

### Requirement: Responses expose no personal customer data

As respostas dos endpoints de Atendimento SHALL identificar o Cliente apenas por
`cliente_id` e SHALL NOT conter nome, e-mail, CPF, telefone, endereço, senha, token ou
qualquer identificador de autenticação do Cliente. As operações de escrita SHALL ocorrer
em transação e SHALL NOT alterar Cliente, Pedido, UsuarioInterno, Pagamento, estoque ou
qualquer outro dado fora de `atendimento`.

#### Scenario: No sensitive customer data is exposed

- **WHEN** qualquer endpoint de Atendimento responde
- **THEN** o Cliente aparece apenas como `cliente_id`, sem dados pessoais ou credenciais

#### Scenario: Writes are limited to attendance

- **WHEN** um Atendimento é criado, editado ou tem o status alterado
- **THEN** somente `atendimento` é gravado e Cliente, Pedido, UsuarioInterno, Pagamento e estoque permanecem inalterados
