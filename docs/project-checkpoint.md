# Project Checkpoint — Voltix

## Finalidade

Este arquivo registra o andamento atual do projeto **Voltix** e serve como backup de contexto e continuidade.

Ao retomar o projeto, consultar este arquivo junto com:

- `docs/project-overview.md`
- `docs/domain-model.md`

Este checkpoint não substitui a documentação oficial, Specs ou Changes do OpenSpec.

## Estado atual

A preparação conceitual inicial está concluída. Até este checkpoint, nenhuma implementação da aplicação foi iniciada.

Ainda não foram iniciados: Git local, GitHub, OpenSpec, Specs, Changes, frontend em Reflex ou backend em Xano/XanoScript.

O próximo passo planejado é **configurar e validar o Git local**.

## Etapas concluídas

### Project Overview — concluído

A visão geral da Voltix, problema, objetivos, usuários, escopo, funcionalidades, arquitetura tecnológica, princípios, segurança e estratégia de desenvolvimento foram consolidados em `docs/project-overview.md`.

### Domain Model — concluído

O modelo conceitual foi discutido decisão por decisão. A etapa foi encerrada após 72 decisões de construção e validação.

O resultado está consolidado em `docs/domain-model.md`.

O Domain Model é conceitual e não representa o modelo físico do banco de dados.

### Estrutura documental inicial — concluída

```text
voltix/
└── docs/
    ├── project-overview.md
    ├── domain-model.md
    └── project-checkpoint.md
```

Neste momento, a pasta `voltix` está sendo mantida no Google Drive para organização e backup. Quando o desenvolvimento com Git começar, será utilizada uma cópia local adequada para versionamento.

## Tecnologias definidas

- Frontend: Reflex
- Backend: Xano + XanoScript
- Dados: infraestrutura gerenciada pelo Xano
- Versionamento: Git + GitHub
- Desenvolvimento orientado por especificações: OpenSpec

## Conceitos do Domain Model

O modelo inicial possui 13 conceitos:

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

## Principais decisões consolidadas

### Catálogo

- Produto pertence a exatamente uma Categoria e uma Marca.
- Categoria e Marca possuem nomes obrigatórios e únicos.
- Produto possui uma ou mais VariacoesProduto.
- Todo Produto possui pelo menos uma VariacaoProduto, inclusive `Padrão` quando necessário.
- SKU, preço e quantidade disponível pertencem à VariacaoProduto.
- SKU é obrigatório e único globalmente.
- Preço da VariacaoProduto é maior que zero.
- Estoque nunca pode ser negativo.
- Estoque zero não inativa automaticamente a variação.
- Produto, VariacaoProduto, Categoria e Marca utilizam `ATIVO`/`INATIVO`.
- Produto possui uma imagem principal.
- Especificações técnicas ficam diretamente no Produto.
- Não existe entidade independente de Estoque ou MovimentacaoEstoque no escopo inicial.

### Cliente e Endereco

- Cliente e UsuarioInterno são conceitos separados.
- Cliente possui CPF obrigatório e único.
- CPF não pode ser alterado livremente após o cadastro.
- Cliente possui e-mail obrigatório e único entre Clientes.
- Cliente possui um telefone no escopo inicial.
- Cliente utiliza `ATIVO`/`INATIVO`.
- Não existe checkout como visitante.
- Cliente pode possuir zero ou muitos Enderecos.
- No máximo um Endereco pode ser principal.
- Endereco utiliza `ATIVO`/`INATIVO`.
- Endereco inativo não pode ser usado em novos Pedidos.
- Endereco utilizado em Pedido não pode ser excluído definitivamente.
- Ao inativar o endereço principal, ele deixa automaticamente de ser principal.
- O Endereco de um Pedido deve pertencer ao mesmo Cliente responsável.

### UsuarioInterno

- Funcionario e Administrador são representados por `UsuarioInterno`.
- Perfis: `FUNCIONARIO` e `ADMINISTRADOR`.
- E-mail é obrigatório e único entre UsuariosInternos.
- O mesmo e-mail pode existir em Cliente e UsuarioInterno.
- UsuarioInterno utiliza `ATIVO`/`INATIVO`.
- UsuarioInterno inativo perde acesso, preservando o histórico.
- Permissões detalhadas serão definidas posteriormente nas Specs.

### Carrinho

- Cliente possui no máximo um Carrinho ativo.
- Carrinho pode existir vazio.
- Carrinho é esvaziado e reutilizado após a criação do Pedido.
- Carrinho não reserva estoque.
- Estoque é verificado novamente na finalização.
- ItemCarrinho possui quantidade inteira maior que zero.
- Uma VariacaoProduto aparece no máximo uma vez no mesmo Carrinho.
- Adicionar novamente a mesma variação atualiza a quantidade.
- Quantidade não pode ultrapassar o estoque disponível no momento da operação.
- Se a quantidade chegar a zero, o ItemCarrinho é removido.

### Pedido

- Todo Pedido pertence a um Cliente autenticado.
- Pedido possui código comercial único separado do identificador interno.
- Pedido possui pelo menos um ItemPedido.
- Uma VariacaoProduto aparece no máximo uma vez no mesmo Pedido.
- ItemPedido possui quantidade inteira maior que zero.
- ItemPedido preserva o preço unitário praticado na compra.
- Pedido armazena subtotal, frete e valor total.
- Valor total = subtotal + frete.
- Status: `AGUARDANDO_PAGAMENTO`, `PAGAMENTO_CONFIRMADO`, `EM_PREPARACAO`, `ENVIADO`, `ENTREGUE`, `CANCELADO`.
- Cliente e UsuarioInterno autorizado poderão cancelar Pedidos conforme regras futuras.
- Condições exatas de cancelamento ficarão nas Specs.
- Cancelamento devolve ao estoque unidades que já tenham sido baixadas.
- Não existe entidade separada de Transportadora ou Entrega no escopo inicial.

### Pagamento

- Todo Pedido possui exatamente um Pagamento.
- Pagamento é criado junto com o Pedido.
- Não existe Pedido persistido sem Pagamento.
- Métodos: `PIX`, `CARTAO`, `BOLETO`.
- Status: `PENDENTE`, `APROVADO`, `RECUSADO`, `CANCELADO`.
- Valor do Pagamento = valor total do Pedido.
- Não existem pagamentos parciais ou divididos.
- Tentativa recusada não cria outro Pagamento.
- Não existe histórico detalhado de tentativas no escopo inicial.

### CRM

- Atendimento pertence a exatamente um Cliente.
- Atendimento possui exatamente um UsuarioInterno responsável.
- Atendimento pode opcionalmente referenciar um Pedido.
- Se referenciar um Pedido, ele deve pertencer ao mesmo Cliente.
- Um Pedido pode estar relacionado a vários Atendimentos.
- Não existe InteracaoAtendimento no escopo inicial.
- Status: `ABERTO`, `EM_ATENDIMENTO`, `FINALIZADO`, `CANCELADO`.
- `ABERTO` e `EM_ATENDIMENTO` podem ser atualizados.
- `FINALIZADO` e `CANCELADO` são preservados como histórico e não podem ser alterados normalmente.

## Fora do escopo inicial

- Marketplace com vendedores externos
- Integração fiscal real
- Integração real com transportadoras
- Recomendação avançada por IA
- Chatbot
- Aplicativo móvel nativo
- Avaliações de produtos
- Favoritos/lista de desejos
- Cupons e descontos avançados
- Galeria independente de imagens
- Estoque como entidade independente
- MovimentacaoEstoque
- InteracaoAtendimento
- Histórico detalhado de tentativas de pagamento

## Método de trabalho

Regra obrigatória do projeto:

> **Uma etapa deve ser completamente entendida, executada, revisada e aprovada antes do início da próxima.**

```text
Entender
   ↓
Decidir em conjunto
   ↓
Executar
   ↓
Revisar
   ↓
Corrigir, se necessário
   ↓
Validar
   ↓
Marcar como concluído
   ↓
Somente então iniciar a próxima etapa
```

Não avançar duas etapas simultaneamente.

## Checkpoint

```text
[CONCLUÍDO] Definição geral da Voltix
      ↓
[CONCLUÍDO] docs/project-overview.md
      ↓
[CONCLUÍDO] Domain Model
      ↓
[CONCLUÍDO] docs/domain-model.md
      ↓
[CONCLUÍDO] Estrutura documental inicial
      ↓
[CONCLUÍDO] Backup/checkpoint do andamento
      ↓
[PRÓXIMO]  Configurar e validar Git local
      ↓
[FUTURO]   Criar/conectar GitHub
      ↓
[FUTURO]   Preparar OpenSpec
      ↓
[FUTURO]   Criar primeiras Specs
      ↓
[FUTURO]   Criar primeira Change
      ↓
[FUTURO]   Implementar primeira funcionalidade
      ↓
[FUTURO]   Testar e validar
      ↓
[FUTURO]   Versionar e continuar incrementalmente
```

## Como retomar

Ao retomar o projeto:

1. Confirmar a presença de `project-overview.md`, `domain-model.md` e `project-checkpoint.md`.
2. Não refazer decisões consolidadas sem necessidade.
3. Ler os documentos antes de alterar decisões permanentes.
4. Iniciar exclusivamente a etapa de configuração do Git local.
5. Validar o Git local antes de iniciar GitHub ou OpenSpec.

**Estado no momento deste checkpoint:** documentação conceitual inicial concluída. Próximo passo técnico: **Git local**.
