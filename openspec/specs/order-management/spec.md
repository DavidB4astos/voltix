# order-management Specification

## Purpose

Definir como usuários internos consultam Pedidos e como o ADMINISTRADOR avança o status
operacional em sequência estrita, sem alterar itens, valores, endereço, Pagamento ou
estoque e sem substituir as regras de cancelamento.

## Requirements

### Requirement: Active internal users can list and inspect orders

Um UsuarioInterno autenticado, `ATIVO` e com papel `FUNCIONARIO` ou `ADMINISTRADOR` SHALL
poder listar Pedidos com paginação e filtros por status e por busca textual (código do
Pedido ou nome do Cliente). A lista SHALL ser ordenada de forma determinística e estável
(data do Pedido decrescente, depois `id` decrescente). O mesmo perfil SHALL poder abrir o
detalhe de um Pedido, com dados do Cliente, itens, endereço de entrega e Pagamento.
Cliente, visitante e UsuarioInterno inativo SHALL ser negados no backend.

#### Scenario: Funcionario lists orders with pagination
- **WHEN** um FUNCIONARIO ativo consulta a lista sem filtros
- **THEN** o backend devolve a primeira página de Pedidos, com metadados de paginação e ordenação estável, sem exigir papel administrativo

#### Scenario: Filters combine status and text search
- **WHEN** o usuário filtra por `status` e informa um termo de busca
- **THEN** o resultado contém apenas Pedidos que atendem aos dois critérios, comparando o termo com o código do Pedido e com o nome do Cliente

#### Scenario: Invalid pagination or filters are rejected
- **WHEN** `page` for menor que 1, `per_page` fora de 1–50, termo acima de 100 caracteres ou status desconhecido
- **THEN** o backend responde erro de entrada e não executa a consulta

#### Scenario: Order detail does not expose sensitive data
- **WHEN** um usuário interno abre o detalhe de um Pedido
- **THEN** a resposta traz nome do Cliente, e-mail mascarado, itens, endereço de entrega e Pagamento, e nunca CPF, telefone, senha, hash ou token

#### Scenario: Inactive internal user is denied
- **WHEN** um UsuarioInterno `INATIVO` tenta listar ou abrir Pedidos
- **THEN** o backend nega o acesso e nada é retornado

#### Scenario: Missing order returns not found
- **WHEN** o usuário interno informa um `order_id` inexistente
- **THEN** o backend responde `notfound` sem revelar outros dados

### Requirement: Only administrators advance order status, in strict sequence

Somente UsuarioInterno `ATIVO` com papel `ADMINISTRADOR` SHALL alterar o status de um
Pedido. O avanço SHALL seguir exatamente a sequência operacional
`PAGAMENTO_CONFIRMADO → EM_PREPARACAO → ENVIADO → ENTREGUE`, um passo por requisição.
`FUNCIONARIO` SHALL NOT alterar status. Pedidos em `AGUARDANDO_PAGAMENTO`, `CANCELADO` ou
`ENTREGUE` SHALL NOT ser avançados. Nenhuma transição SHALL pular etapas ou retroceder.

#### Scenario: Administrator advances one step
- **WHEN** um ADMINISTRADOR ativo envia `EM_PREPARACAO` para um Pedido em `PAGAMENTO_CONFIRMADO`
- **THEN** o Pedido passa a `EM_PREPARACAO`, `updated_at` é atualizado e a resposta informa status anterior e atual

#### Scenario: Full operational sequence
- **WHEN** um ADMINISTRADOR avança sucessivamente `EM_PREPARACAO`, `ENVIADO` e `ENTREGUE`
- **THEN** cada requisição aplica exatamente um passo e o Pedido termina em `ENTREGUE`

#### Scenario: Skipping or reversing is rejected
- **WHEN** o alvo não é o próximo status da sequência (ex.: `PAGAMENTO_CONFIRMADO → ENVIADO` ou `ENVIADO → EM_PREPARACAO`)
- **THEN** o backend rejeita com erro de requisição e o Pedido permanece no status anterior

#### Scenario: Repeated target is a no-op
- **WHEN** o alvo enviado é igual ao status atual do Pedido
- **THEN** o backend responde sucesso com `alterado=false`, sem gravar nada

#### Scenario: Funcionario cannot change status
- **WHEN** um FUNCIONARIO ativo tenta alterar o status de um Pedido
- **THEN** o backend nega com `accessdenied` e nada é alterado

#### Scenario: Cancelled or delivered orders are terminal for transitions
- **WHEN** o Pedido está em `CANCELADO` ou `ENTREGUE`
- **THEN** qualquer tentativa de avanço é rejeitada sem efeito colateral

### Requirement: Status changes never bypass cancellation rules

O avanço de status SHALL NOT alterar estoque, valores, itens, Pagamento ou endereço. O
cancelamento SHALL continuar disponível apenas pelo endpoint da capability
`order-cancellation`, respeitando suas janelas (`AGUARDANDO_PAGAMENTO` e
`PAGAMENTO_CONFIRMADO`). Um Pedido já cancelado SHALL NOT voltar a estados operacionais.

#### Scenario: Advancing status keeps order data intact
- **WHEN** um Pedido é avançado para `EM_PREPARACAO`
- **THEN** itens, preços, subtotal, frete, total, endereço, Pagamento e estoque permanecem exatamente como estavam

#### Scenario: Admin cannot cancel through the status endpoint
- **WHEN** um ADMINISTRADOR envia `CANCELADO` para o endpoint de status
- **THEN** o backend rejeita o valor e nada é alterado; o cancelamento só ocorre pelo endpoint próprio
