# shopping-cart Specification

## Purpose
Permitir que um Cliente autenticado mantenha um Carrinho persistente com variações de produtos, quantidades e valores calculados a partir dos dados comerciais atuais. A capability limita-se à preparação da compra e não cria Pedidos nem reserva estoque.

## Requirements

### Requirement: Customers can maintain a persistent personal cart
O sistema SHALL permitir que um Cliente autenticado e `ATIVO` mantenha seu Carrinho e SHALL impedir que um Cliente leia ou altere o Carrinho de outro. O Carrinho SHALL poder permanecer vazio e ser preservado entre consultas e sessões do mesmo Cliente.

#### Scenario: Customer opens an empty cart
- **WHEN** um Cliente autenticado consulta o próprio Carrinho sem itens
- **THEN** o sistema apresenta um Carrinho vazio sem criar itens ou exigir dados de checkout

#### Scenario: Customer returns to a previously used cart
- **WHEN** o mesmo Cliente autentica-se novamente e consulta o Carrinho
- **THEN** o sistema apresenta os itens e quantidades anteriormente confirmados

#### Scenario: Customer cannot access another cart
- **WHEN** um Cliente tenta consultar ou alterar itens de outro Cliente usando um identificador recebido pela interface
- **THEN** o backend rejeita a operação e não revela nem altera o Carrinho alheio

#### Scenario: Unauthenticated or inactive customer cannot access a cart
- **WHEN** uma requisição de Carrinho não possui sessão válida de Cliente `ATIVO`
- **THEN** o backend rejeita a leitura e a alteração sem retornar dados do Carrinho

### Requirement: Customers can add, update, and remove cart items
O sistema SHALL permitir que um Cliente adicione uma VariaçãoProduto ao Carrinho, consulte os itens, altere sua quantidade e remova o item. Quantidades SHALL ser números inteiros maiores que zero e não poderão exceder o estoque disponível no momento da operação. Cada variação poderá aparecer no máximo uma vez no mesmo Carrinho; adicionar uma variação já presente SHALL atualizar a quantidade total solicitada, em vez de criar linha duplicada ou somar implicitamente. Solicitar quantidade zero SHALL remover o ItemCarrinho.

#### Scenario: Customer adds an available active variation
- **WHEN** o Cliente adiciona uma variação cuja VariaçãoProduto e Produto estão `ATIVO` e há estoque suficiente para a quantidade solicitada
- **THEN** o backend salva um ItemCarrinho pertencente ao Carrinho daquele Cliente com a quantidade solicitada

#### Scenario: Adding an existing variation updates its quantity
- **WHEN** o Cliente adiciona uma variação já presente no Carrinho com uma quantidade válida
- **THEN** o sistema atualiza a quantidade do ItemCarrinho existente e não cria uma linha duplicada

#### Scenario: Customer updates an item quantity
- **WHEN** o Cliente altera a quantidade para um inteiro positivo que não excede o estoque atualmente disponível
- **THEN** o backend persiste a nova quantidade do ItemCarrinho próprio

#### Scenario: Zero quantity removes the item
- **WHEN** o Cliente altera a quantidade de um item para zero
- **THEN** o backend remove esse ItemCarrinho do Carrinho e mantém o Carrinho

#### Scenario: Customer removes an item
- **WHEN** o Cliente solicita remover um item próprio
- **THEN** o sistema remove somente esse ItemCarrinho e preserva os demais itens e o Carrinho

#### Scenario: Fractional, negative, or excessive quantity is rejected
- **WHEN** o Cliente informa quantidade fracionária, negativa ou maior que o estoque disponível
- **THEN** o backend rejeita a operação e preserva a quantidade anteriormente confirmada

### Requirement: Cart operations respect current product, variation, and stock status
O backend SHALL validar no momento de adicionar ou alterar uma quantidade que o Produto e a VariaçãoProduto estejam `ATIVO` e que haja estoque suficiente, sem reservar nem baixar estoque. Itens já registrados SHALL ser preservados quando seu Produto ou VariaçãoProduto se tornar `INATIVO`, ou quando o estoque atual cair abaixo da quantidade no Carrinho; a interface SHALL identificá-los como indisponíveis, não SHALL alegar que estão disponíveis para compra e SHALL permitir removê-los. Para uma variação ativa cujo estoque tenha diminuído, o Cliente poderá reduzir a quantidade para um valor positivo que caiba no estoque atual ou remover o item.

#### Scenario: Inactive product or variation cannot be added
- **WHEN** o Cliente tenta adicionar uma variação cujo Produto ou VariaçãoProduto está `INATIVO`
- **THEN** o backend rejeita a operação e não cria nem altera o Carrinho

#### Scenario: Zero stock is unavailable
- **WHEN** uma variação `ATIVO` possui estoque zero e o Cliente tenta adicioná-la ou definir quantidade positiva
- **THEN** o backend rejeita a operação sem alterar o estoque nem criar ou atualizar o ItemCarrinho

#### Scenario: Existing cart item becomes unavailable
- **WHEN** um Produto ou VariaçãoProduto do Carrinho fica `INATIVO`, ou o estoque cai abaixo da quantidade salva
- **THEN** o item permanece no Carrinho, é apresentado como indisponível e pode ser removido sem ser silenciosamente excluído ou anunciado como disponível

#### Scenario: Customer reduces an over-stock cart quantity
- **WHEN** um item ativo possui quantidade salva maior que o estoque atual e o Cliente solicita uma quantidade positiva que cabe nesse estoque
- **THEN** o backend persiste a quantidade reduzida e o item deixa de estar indisponível por excesso de quantidade

#### Scenario: Adding to cart does not reserve stock
- **WHEN** uma variação é adicionada ao Carrinho ou sua quantidade é atualizada
- **THEN** o estoque da VariaçãoProduto permanece inalterado

### Requirement: Cart subtotals and total use current variation prices
O sistema SHALL calcular para cada item o subtotal como preço atual da VariaçãoProduto multiplicado pela quantidade inteira e SHALL calcular o total do Carrinho como a soma dos subtotais apresentados. Os cálculos SHALL usar os valores comerciais retornados pelo backend, sem aceitar preço enviado pela interface nem persistir preço histórico no ItemCarrinho.

#### Scenario: Customer views cart totals
- **WHEN** o Cliente consulta um Carrinho com itens
- **THEN** cada item apresenta quantidade, preço atual e subtotal, e o Carrinho apresenta a soma desses subtotais

#### Scenario: Variation price changes while in cart
- **WHEN** o preço da VariaçãoProduto é atualizado após sua inclusão no Carrinho
- **THEN** a consulta seguinte utiliza o preço atual para o subtotal e o total sem alterar a quantidade salva

#### Scenario: Client-supplied price is ignored
- **WHEN** uma solicitação de inclusão ou alteração contém preço ou subtotal enviado pelo Cliente
- **THEN** o backend calcula os valores com o preço persistido da VariaçãoProduto e não confia nos valores enviados

### Requirement: Cart interface uses server-side State and reports failures
A interface SHALL encaminhar as operações e consultas de Carrinho ao State/lógica Python Reflex, que SHALL realizar as chamadas HTTP ao Xano. Tokens SHALL permanecer fora do código executado diretamente no navegador. Falhas HTTP, de rede, validação ou resposta SHALL ser apresentadas como falha e SHALL preservar os últimos dados confirmados.

#### Scenario: Cart action uses the customer session through State
- **WHEN** um Cliente consulta ou modifica o Carrinho pela interface
- **THEN** o State/Python chama o Xano usando somente a sessão de Cliente e não há chamada de dados direta do navegador ao backend

#### Scenario: Cart operation fails
- **WHEN** o backend rejeita uma operação ou ocorre falha de rede ou resposta inválida
- **THEN** a interface informa a falha e não apresenta a alteração como persistida

#### Scenario: Internal-user session is not a customer cart session
- **WHEN** somente existe uma sessão de `UsuarioInterno` e o usuário tenta acessar o Carrinho
- **THEN** o sistema exige uma sessão de Cliente e não reutiliza token ou identidade interna
