# Domain Model — Voltix

## 1. Objetivo

Este documento descreve o **modelo de domínio conceitual** da Voltix, apresentando os principais conceitos do sistema, suas responsabilidades, atributos relevantes, relacionamentos, cardinalidades e regras estruturais.

O objetivo é estabelecer uma visão compartilhada do domínio antes da implementação.

> Este documento **não representa o modelo físico do banco de dados**, não define tabelas, tipos SQL, chaves estrangeiras, índices ou detalhes específicos da infraestrutura do Xano.

Regras de comportamento mais detalhadas, fluxos de tela, permissões específicas, transições completas de estados e decisões de implementação devem ser detalhadas posteriormente nas **Specs e Changes do OpenSpec**.

---

## 2. Visão geral do domínio

A Voltix é um e-commerce de produtos de tecnologia com funcionalidades de catálogo, carrinho, pedidos, pagamento simulado e CRM integrado.

O domínio está organizado em quatro áreas principais:

- **Catálogo:** Categoria, Marca, Produto e VariacaoProduto.
- **Clientes e acesso interno:** Cliente, Endereco e UsuarioInterno.
- **Compra:** Carrinho, ItemCarrinho, Pedido, ItemPedido e Pagamento.
- **CRM:** Atendimento.

---

# 3. Catálogo

## 3.1 Categoria

### Descrição

Representa uma classificação utilizada para organizar os produtos disponíveis na Voltix.

Exemplos: Monitores, Teclados, Placas de vídeo e Notebooks.

### Responsabilidade

Organizar produtos em grupos de navegação e administração.

### Atributos conceituais principais

- Nome
- Descrição
- Status
- Data de criação
- Data de atualização

### Status

- `ATIVO`
- `INATIVO`

### Relacionamentos

- Uma Categoria pode possuir **zero ou muitos Produtos**.
- Todo Produto pertence a **exatamente uma Categoria**.

### Regras estruturais

- O nome da Categoria é obrigatório e único.
- Uma Categoria pode existir sem Produtos associados.
- Uma Categoria inativa deve ser preservada para manter relações históricas existentes.

---

## 3.2 Marca

### Descrição

Representa o fabricante ou marca comercial associada a um Produto.

Exemplos: Logitech, Samsung, ASUS e Corsair.

### Responsabilidade

Permitir a identificação e organização dos produtos por fabricante ou marca.

### Atributos conceituais principais

- Nome
- Descrição
- Status
- Data de criação
- Data de atualização

### Status

- `ATIVO`
- `INATIVO`

### Relacionamentos

- Uma Marca pode estar associada a **zero ou muitos Produtos**.
- Todo Produto pertence a **exatamente uma Marca**.

### Regras estruturais

- O nome da Marca é obrigatório e único.
- Uma Marca pode existir sem Produtos associados.
- Marcas inativas devem permanecer registradas para preservar relações históricas.

---

## 3.3 Produto

### Descrição

Representa um item conceitual do catálogo da Voltix. O Produto descreve o item comercial de forma geral; as versões efetivamente comercializadas são representadas por `VariacaoProduto`.

### Responsabilidade

Centralizar as informações gerais utilizadas para apresentar um produto no catálogo.

### Atributos conceituais principais

- Nome
- Descrição
- Especificações técnicas
- Imagem principal
- Status
- Data de criação
- Data de atualização

### Status

- `ATIVO`
- `INATIVO`

### Relacionamentos

- Todo Produto pertence a **uma Categoria**.
- Todo Produto pertence a **uma Marca**.
- Todo Produto possui **uma ou mais VariacoesProduto**.

### Regras estruturais

- Um Produto deve possuir pelo menos uma VariacaoProduto.
- O Produto possui apenas uma imagem principal no escopo inicial.
- As especificações técnicas são mantidas diretamente no Produto.
- Não existe uma entidade específica para atributos técnicos dinâmicos.
- Produtos não devem ser removidos definitivamente quando já fizerem parte do histórico comercial.
- Produto inativo não deve estar disponível para novas compras.

---

## 3.4 VariacaoProduto

### Descrição

Representa uma versão comercializável de um Produto. Exemplos: Preto, Branco, 16 GB / 512 GB, 32 GB / 1 TB ou simplesmente `Padrão`.

Mesmo quando um Produto não possui diferenças visíveis de cor, capacidade ou configuração, ele deve possuir pelo menos uma variação.

### Responsabilidade

Representar a unidade efetivamente vendida, contendo SKU, preço e quantidade disponível.

### Atributos conceituais principais

- Nome ou descrição da variação
- SKU
- Preço
- Quantidade disponível
- Status
- Data de criação
- Data de atualização

### Status

- `ATIVO`
- `INATIVO`

### Relacionamentos

- Toda VariacaoProduto pertence a **exatamente um Produto**.
- Uma VariacaoProduto pode aparecer em diferentes ItemCarrinho e ItemPedido ao longo do tempo.

### Regras estruturais

- O SKU é obrigatório e único globalmente.
- O preço deve ser maior que zero.
- A quantidade disponível deve ser maior ou igual a zero.
- O estoque nunca pode assumir valor negativo.
- Estoque igual a zero não torna a variação inativa.
- Uma variação ativa com estoque zero permanece existente, porém indisponível para compra.
- Uma variação inativa não deve ser comercializada.
- SKU, preço e quantidade disponível pertencem à VariacaoProduto, e não ao Produto.

---

# 4. Clientes e acesso interno

## 4.1 Cliente

### Descrição

Representa a pessoa que utiliza a Voltix para realizar compras e acessar seus pedidos e atendimentos.

### Responsabilidade

Manter a identidade do consumidor e servir como responsável pelos seus endereços, carrinho, pedidos e registros de atendimento.

### Atributos conceituais principais

- Nome completo
- CPF
- E-mail
- Telefone
- Dados de autenticação
- Status
- Data de criação
- Data de atualização

### Status

- `ATIVO`
- `INATIVO`

### Relacionamentos

Um Cliente pode possuir zero ou muitos Enderecos, zero ou um Carrinho ativo, zero ou muitos Pedidos e zero ou muitos Atendimentos. Todo Pedido pertence a exatamente um Cliente.

### Regras estruturais

- O CPF é obrigatório e único entre Clientes.
- O CPF não pode ser alterado livremente após o cadastro.
- O e-mail é obrigatório e único entre Clientes.
- O Cliente possui um único telefone no escopo inicial.
- Não existe checkout como visitante.
- Todo Pedido deve possuir um Cliente autenticado responsável.
- Um Cliente inativo deve continuar existindo para preservação de seu histórico.
- O mesmo endereço de e-mail pode existir simultaneamente em Cliente e UsuarioInterno, pois são conceitos separados.

---

## 4.2 Endereco

### Descrição

Representa um endereço cadastrado por um Cliente e que pode ser utilizado para entrega de Pedidos.

### Responsabilidade

Manter os dados estruturados necessários para identificação do local de entrega.

### Atributos conceituais principais

- CEP
- Logradouro
- Número
- Complemento
- Bairro
- Cidade
- Estado
- Identificação do endereço
- Indicador de endereço principal
- Status
- Data de criação
- Data de atualização

Exemplos de identificação: Casa e Trabalho.

### Status

- `ATIVO`
- `INATIVO`

### Relacionamentos

- Todo Endereco pertence a **exatamente um Cliente**.
- Um Cliente pode possuir **zero ou muitos Enderecos**.
- Um Pedido referencia **um Endereco de entrega**.

### Regras estruturais

- Um Cliente pode possuir no máximo um endereço principal.
- Um endereço inativo não pode ser selecionado para novos Pedidos.
- Um Endereco utilizado em um Pedido não pode ser excluído definitivamente.
- Enderecos nunca utilizados em Pedidos podem ser removidos.
- Ao inativar um endereço principal, ele deixa automaticamente de ser principal.
- O Cliente não é obrigado a possuir outro endereço principal imediatamente.
- O Endereco selecionado em um Pedido deve pertencer ao mesmo Cliente responsável pelo Pedido.

---

## 4.3 UsuarioInterno

### Descrição

Representa uma pessoa autorizada a acessar funcionalidades internas da Voltix. O sistema não utiliza conceitos separados de Funcionario e Administrador; ambos são representados por UsuarioInterno e diferenciados por perfil.

### Responsabilidade

Representar os usuários responsáveis pela operação administrativa e pelo atendimento aos Clientes.

### Atributos conceituais principais

- Nome
- E-mail
- Dados de autenticação
- Perfil
- Status
- Data de criação
- Data de atualização

### Perfis

- `FUNCIONARIO`
- `ADMINISTRADOR`

### Status

- `ATIVO`
- `INATIVO`

### Relacionamentos

- Um UsuarioInterno pode ser responsável por **zero ou muitos Atendimentos**.
- Todo Atendimento possui **exatamente um UsuarioInterno responsável**.

### Regras estruturais

- O e-mail é obrigatório e único entre UsuariosInternos.
- A unicidade do e-mail é independente da unicidade existente em Cliente.
- Um UsuarioInterno inativo perde acesso operacional, porém continua registrado para preservar o histórico dos Atendimentos.
- O perfil `FUNCIONARIO` representa acesso operacional.
- O perfil `ADMINISTRADOR` representa acesso administrativo ampliado.
- As permissões exatas de cada perfil serão especificadas posteriormente.

---

# 5. Compra

## 5.1 Carrinho

### Descrição

Representa o conjunto temporário de itens que um Cliente pretende comprar.

### Responsabilidade

Organizar as VariacoesProduto selecionadas antes da criação de um Pedido.

### Atributos conceituais principais

- Data de criação
- Data de atualização

### Relacionamentos

- Todo Carrinho pertence a **exatamente um Cliente**.
- Um Cliente pode possuir **no máximo um Carrinho ativo**.
- Um Carrinho possui **zero ou muitos ItemCarrinho**.

### Regras estruturais

- O Carrinho pode existir vazio.
- O Carrinho não reserva estoque.
- Após a criação de um Pedido, o Carrinho é esvaziado e pode ser reutilizado.
- A disponibilidade de estoque deve ser verificada novamente no momento apropriado da finalização da compra.

---

## 5.2 ItemCarrinho

### Descrição

Representa uma VariacaoProduto adicionada ao Carrinho de um Cliente.

### Responsabilidade

Registrar qual variação foi selecionada e em qual quantidade.

### Atributos conceituais principais

- Quantidade
- Data de criação
- Data de atualização

### Relacionamentos

- Todo ItemCarrinho pertence a **exatamente um Carrinho**.
- Todo ItemCarrinho referencia **exatamente uma VariacaoProduto**.

### Regras estruturais

- A quantidade deve ser um número inteiro maior que zero.
- A mesma VariacaoProduto pode aparecer no máximo uma vez em um mesmo Carrinho.
- Adicionar novamente uma variação já existente atualiza sua quantidade.
- A quantidade não pode ultrapassar o estoque disponível no momento da operação.
- A inclusão no Carrinho não reserva estoque.
- Se a quantidade for reduzida a zero, o ItemCarrinho deve ser removido.

---

## 5.3 Pedido

### Descrição

Representa uma compra formalizada por um Cliente.

### Responsabilidade

Preservar as informações comerciais da compra, incluindo itens, valores, endereço de entrega, pagamento e estado do processo.

### Atributos conceituais principais

- Código do Pedido
- Data do Pedido
- Status
- Subtotal
- Valor do frete
- Valor total
- Data de criação
- Data de atualização

### Status

- `AGUARDANDO_PAGAMENTO`
- `PAGAMENTO_CONFIRMADO`
- `EM_PREPARACAO`
- `ENVIADO`
- `ENTREGUE`
- `CANCELADO`

### Relacionamentos

Todo Pedido pertence a exatamente um Cliente, utiliza exatamente um Endereco de entrega, possui um ou muitos ItemPedido, possui exatamente um Pagamento e pode estar relacionado a zero ou muitos Atendimentos.

### Regras estruturais

- O código do Pedido deve ser único.
- O código comercial é separado do identificador interno do sistema.
- Todo Pedido possui pelo menos um ItemPedido.
- O Endereco selecionado deve pertencer ao mesmo Cliente responsável pelo Pedido.
- O subtotal representa a soma dos valores dos ItemPedido.
- O valor total corresponde ao subtotal acrescido do frete.
- O Pedido não possui entidade separada de Transportadora ou Entrega no escopo inicial.
- Informações de transporte são simplificadas no próprio Pedido.
- Cliente e UsuarioInterno autorizado podem cancelar um Pedido quando as regras de cancelamento permitirem.
- As etapas exatas em que o cancelamento será permitido serão definidas nas Specs.
- Quando um Pedido que já reduziu estoque for cancelado, as quantidades devem ser devolvidas às VariacoesProduto correspondentes.

---

## 5.4 ItemPedido

### Descrição

Representa uma VariacaoProduto incluída em um Pedido.

### Responsabilidade

Preservar os dados necessários para reconstruir comercialmente o conteúdo do Pedido.

### Atributos conceituais principais

- Quantidade
- Preço unitário no momento da compra
- Data de criação
- Data de atualização

### Relacionamentos

- Todo ItemPedido pertence a **exatamente um Pedido**.
- Todo ItemPedido referencia **exatamente uma VariacaoProduto**.

### Regras estruturais

- A quantidade deve ser um número inteiro maior que zero.
- O preço unitário deve representar o preço praticado no momento da compra.
- Alterações posteriores no preço da VariacaoProduto não podem alterar Pedidos antigos.
- Uma mesma VariacaoProduto aparece no máximo uma vez dentro de um mesmo Pedido.
- Caso sejam compradas várias unidades da mesma variação, a quantidade deve ser consolidada no mesmo ItemPedido.

---

## 5.5 Pagamento

### Descrição

Representa o pagamento associado a um Pedido. No escopo inicial da Voltix, o pagamento será simulado e não dependerá de integração real com instituição financeira ou gateway de pagamento.

### Responsabilidade

Registrar método, valor e situação do pagamento da compra.

### Atributos conceituais principais

- Método de pagamento
- Valor
- Status
- Data de criação
- Data de atualização

### Métodos iniciais

- `PIX`
- `CARTAO`
- `BOLETO`

### Status

- `PENDENTE`
- `APROVADO`
- `RECUSADO`
- `CANCELADO`

### Relacionamentos

- Todo Pagamento pertence a **exatamente um Pedido**.
- Todo Pedido possui **exatamente um Pagamento**.

### Regras estruturais

- O Pagamento é criado juntamente com o Pedido.
- Não existe Pedido persistido sem Pagamento associado.
- O valor do Pagamento deve ser igual ao valor total do Pedido.
- Não existem pagamentos parciais.
- Não existe divisão de um Pedido entre diferentes métodos de pagamento.
- Uma tentativa recusada não cria outro Pagamento.
- O mesmo Pagamento pode passar novamente por um fluxo de tentativa, mantendo a relação um-para-um com o Pedido.
- Não será mantido histórico detalhado de tentativas de pagamento no escopo inicial.

---

# 6. CRM

## 6.1 Atendimento

### Descrição

Representa um registro de atendimento realizado para um Cliente dentro do CRM da Voltix. O Atendimento pode estar relacionado a um Pedido específico ou representar uma solicitação geral.

### Responsabilidade

Registrar o histórico básico de relacionamento entre a equipe da Voltix e seus Clientes.

### Atributos conceituais principais

- Assunto
- Descrição
- Status
- Data do atendimento
- Data de criação
- Data de atualização

### Status

- `ABERTO`
- `EM_ATENDIMENTO`
- `FINALIZADO`
- `CANCELADO`

### Relacionamentos

Todo Atendimento pertence a exatamente um Cliente, possui exatamente um UsuarioInterno responsável e pode estar relacionado a zero ou um Pedido. Um Cliente pode possuir vários Atendimentos, um UsuarioInterno pode ser responsável por vários Atendimentos e um Pedido pode ser mencionado em vários Atendimentos.

### Regras estruturais

- Um Atendimento sempre possui um Cliente.
- Um Atendimento sempre possui um UsuarioInterno responsável.
- A associação com Pedido é opcional.
- Quando existir Pedido associado, ele deve pertencer ao mesmo Cliente do Atendimento.
- Não existe uma entidade separada de interações ou mensagens dentro do Atendimento no escopo inicial.
- O histórico básico é mantido pelo próprio registro de Atendimento.
- Atendimentos em `ABERTO` ou `EM_ATENDIMENTO` podem ser atualizados.
- Atendimentos em `FINALIZADO` ou `CANCELADO` são preservados como registros históricos e não podem ser alterados normalmente.

---

# 7. Resumo dos relacionamentos

```text
Categoria 1 ───────── 0..N Produto
Marca 1 ───────────── 0..N Produto

Produto 1 ─────────── 1..N VariacaoProduto

Cliente 1 ─────────── 0..N Endereco
Cliente 1 ─────────── 0..1 Carrinho
Cliente 1 ─────────── 0..N Pedido
Cliente 1 ─────────── 0..N Atendimento

Carrinho 1 ────────── 0..N ItemCarrinho
ItemCarrinho N ────── 1 VariacaoProduto

Pedido 1 ──────────── 1..N ItemPedido
ItemPedido N ──────── 1 VariacaoProduto

Pedido 1 ──────────── 1 Pagamento
Pedido 1 ──────────── 1 Endereco
Pedido 1 ──────────── 0..N Atendimento

UsuarioInterno 1 ──── 0..N Atendimento
```

---

# 8. Regras estruturais globais

1. Todo Produto pertence a exatamente uma Categoria e uma Marca.
2. Todo Produto possui pelo menos uma VariacaoProduto.
3. Toda VariacaoProduto possui SKU único, preço maior que zero e estoque não negativo.
4. Produto, VariacaoProduto, Categoria e Marca utilizam inativação em vez de exclusão histórica indiscriminada.
5. Cliente possui CPF e e-mail obrigatórios e únicos dentro do conjunto de Clientes.
6. UsuarioInterno possui e-mail obrigatório e único dentro do conjunto de UsuariosInternos.
7. Cliente e UsuarioInterno são conceitos separados.
8. Um Cliente pode possuir vários Enderecos, porém no máximo um principal.
9. Endereco utilizado em Pedido deve ser preservado.
10. Todo Pedido pertence a um Cliente autenticado.
11. Todo Pedido possui ao menos um ItemPedido.
12. Todo Pedido possui exatamente um Pagamento.
13. O valor do Pagamento deve ser igual ao valor total do Pedido.
14. Um Carrinho não reserva estoque.
15. Quantidades de ItemCarrinho e ItemPedido são inteiras e maiores que zero.
16. A mesma VariacaoProduto não pode aparecer duplicada no mesmo Carrinho ou Pedido.
17. Cancelamento de Pedido deve devolver ao estoque as unidades que já tiverem sido baixadas.
18. Todo Atendimento possui Cliente e UsuarioInterno responsável.
19. Quando um Atendimento referencia um Pedido, ambos devem pertencer ao mesmo Cliente.
20. Atendimentos encerrados são preservados como histórico.

---

# 9. Conceitos propositalmente fora do modelo inicial

Para manter o escopo acadêmico controlado, os seguintes conceitos não fazem parte do Domain Model inicial:

- Estoque como entidade independente.
- MovimentacaoEstoque.
- Transportadora.
- Entrega como entidade independente.
- Rastreamento logístico real.
- ImagemProduto como galeria.
- AvaliacaoProduto.
- Lista de desejos ou favoritos.
- Cupom.
- Sistema de descontos avançado.
- InteracaoAtendimento.
- Histórico individual de tentativas de Pagamento.
- Marketplace com vendedores externos.

Esses conceitos poderão ser avaliados futuramente por meio de novas Changes do OpenSpec caso o escopo do projeto evolua.

---

# 10. Limites deste documento

Este Domain Model define **o que existe conceitualmente no domínio da Voltix e como os conceitos se relacionam**.

Não são responsabilidades deste documento:

- Definir tabelas físicas.
- Definir chaves primárias ou estrangeiras.
- Definir tipos de dados do PostgreSQL.
- Definir endpoints da API.
- Definir XanoScript.
- Definir estrutura das telas em Reflex.
- Definir todas as transições de status.
- Definir permissões detalhadas por operação.
- Definir o momento técnico exato da baixa de estoque.
- Definir validações de formulário em nível de interface.
- Definir implementação de autenticação.

Essas decisões serão detalhadas nas etapas apropriadas das especificações e Changes do projeto.

---

## 11. Conceitos principais do Domain Model

O modelo inicial da Voltix é composto por 13 conceitos:

1. Categoria
2. Marca
3. Produto
4. VariacaoProduto
5. Cliente
6. Endereco
7. UsuarioInterno
8. Carrinho
9. ItemCarrinho
10. Pedido
11. ItemPedido
12. Pagamento
13. Atendimento

Este conjunto representa o domínio necessário para a primeira versão acadêmica do sistema sem introduzir complexidade desnecessária.
