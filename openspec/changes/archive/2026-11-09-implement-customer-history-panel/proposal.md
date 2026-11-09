## Why

A C6 publicou `GET customers/{customer_id}/orders`, mas o painel interno ainda mostra
apenas a ficha cadastral do Cliente. Para consultar compras, o time precisa sair da
ficha e cruzar manualmente a lista geral de Pedidos. O roadmap prevê que o histórico
do Cliente seja acessível a partir do próprio Cliente.

## What Changes

- Adicionar a seção **Histórico de pedidos** abaixo da lista/detalhe de Clientes no
  painel interno (Reflex), em largura total.
- Carregar o histórico automaticamente ao abrir o detalhe de um Cliente, usando o
  endpoint publicado na C6; nenhum backend novo é criado.
- Exibir cada Pedido com código, data, status, subtotal, frete, total e **itens
  sempre expandidos** (SKU, descrição, quantidade, preço unitário e subtotal).
- Oferecer filtros por status (padrão `TODOS`) e período opcional (`from`/`to`,
  `YYYY-MM-DD`, UTC, inclusivos), com paginação de 20 Pedidos por página.
- Exibir estados distintos de carregamento, vazio, erro e sessão não autorizada.
- Descartar respostas obsoletas quando o Cliente, os filtros ou a sessão mudarem.
- Adicionar a variável `XANO_INTERNAL_CUSTOMER_ORDERS_URL` e um contrato Python
  estrito para validar a resposta antes de levá-la ao navegador.
- **Sem** edição, revelação de dados, exportação, atendimentos ou mutações.
- **Sem** publicação no Xano: a tela consome o endpoint já publicado.

## Capabilities

### New Capabilities
- `customer-history-panel`: seção desktop somente leitura que apresenta o histórico de
  Pedidos de um Cliente, com filtros, paginação, itens e tratamento seguro de estados.

### Modified Capabilities
- `internal-customers`: a consulta de Clientes passa a permitir a seção de histórico,
  que antes era explicitamente proibida no escopo da tela.

## Impact

- **Frontend**: `voltix/voltix.py` (State, handlers e renderização), contrato Python em
  `voltix/internal_customers.py`, estilos em `assets/voltix-internal.css`.
- **Configuração**: nova variável `XANO_INTERNAL_CUSTOMER_ORDERS_URL` em `.env` e
  `.env.example` (somente nomes em documentação).
- **Backend/Xano**: nenhuma alteração, publicação ou schema novo.
- **Testes**: novos testes do contrato de histórico e dos handlers da tela; suíte
  existente preservada.
- **Segurança**: requisições server-side com token interno; nenhum token de Cliente ou
  credencial exposta ao navegador; resposta sem dados pessoais.
