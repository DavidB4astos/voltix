# Design — exclusão definitiva de produto sem uso comercial

## Contexto

Não existe endpoint de exclusão de Produto: o painel só cria, edita e alterna status. O
domínio determina que Produto, Variação, Categoria e Marca usam inativação em vez de
exclusão histórica indiscriminada (`docs/domain-model.md` §8.4), e a spec consolidada exige
preservar qualquer produto ou variação associado a histórico comercial. Ao mesmo tempo,
cadastros criados por engano e ainda sem vínculo precisam de uma saída definitiva.

As referências comerciais passam por `ItemPedido.variacao_produto_id` e
`ItemCarrinho.variacao_produto_id`. As variações apontam para o produto por
`VariacaoProduto.produto_id`. Não há `ON DELETE CASCADE` declarado no schema; a exclusão
precisa remover as variações explicitamente.

## Decisão

Criar `DELETE products/{product_id}` exclusivo de `ADMINISTRADOR` ativo, que exclui
definitivamente o produto **somente** quando nenhuma de suas variações aparece em
`ItemPedido` ou `ItemCarrinho`. Com qualquer referência, a operação é recusada e a
inativação continua sendo o caminho para retirar o produto de circulação.

A verificação de referências e as exclusões ficam na mesma `db.transaction`: se uma
referência aparecer entre a checagem e a escrita, a precondição falha e a transação é
revertida sem exclusão parcial. Isso evita deixar variações órfãs ou apagar um produto que
acabou de entrar em um carrinho.

### Código de erro para referências comerciais

O conjunto fechado de `error_type` do XanoScript não possui `409 Conflict`; os valores
disponíveis são `standard` (500), `inputerror` (400), `badrequest` (400), `unauthorized`
(401), `accessdenied` (403), `notfound` (404) e `toomanyrequests` (429). A recusa por
histórico comercial usa `badrequest` (HTTP 400), com mensagem explícita orientando a
inativação. Isso é uma limitação do runtime, registrada aqui para não ser confundida com
erro de validação do formulário.

## Contrato do endpoint

`DELETE products/{product_id}` — grupo `Product Management`, `auth = "user"`.

- Entrada: `int product_id` (`min:1`).
- Autorização: usuário autenticado existente, `role == "ADMINISTRADOR"` e
  `status == "ATIVO"`, verificada antes de ler o produto.
- Produto inexistente: `404` (`notfound`), sem escrita.
- Autorização ausente ou insuficiente: `403` (`accessdenied`), sem leitura de negócio.
- Referência em `ItemPedido` ou `ItemCarrinho` a qualquer variação do produto: `400`
  (`badrequest`) com mensagem informando histórico comercial e sugerindo inativação; nada
  é excluído.
- Sem referências: `db.del` de todas as variações com `produto_id` igual ao produto e
  `db.del` do produto, dentro de uma transação.
- Resposta de sucesso: `{id: <product_id>, deleted: true}`. Nenhum campo sensível é
  exposto.
- Produto sem variações: pode ser excluído; a ausência de variações não é referência
  comercial.
- Produto `INATIVO` sem referências: pode ser excluído, pois a inativação prévia não cria
  histórico.

## Concorrência e integridade

- A transação lê as variações, verifica as duas tabelas de itens e somente então exclui.
- Não há atualização de `updated_at`: os registros deixam de existir.
- A exclusão de variações usa `produto_id`, cobrindo variações ativas e inativas.
- Não há exclusão em cascata de Carrinho ou Pedido; qualquer referência bloqueia.
- Uma tentativa concorrente de adicionar o produto ao carrinho não pode resultar em
  variação órfã: a checagem pertence à mesma transação da exclusão.

## Interface

- A ação "Excluir produto" aparece no cartão do produto apenas no painel de
  `ADMINISTRADOR`, ao lado de editar, inativar e adicionar variação.
- A ação abre uma confirmação em dois passos no próprio cartão: primeiro o botão de
  exclusão, depois um bloco que identifica o produto pelo nome e explica que a exclusão é
  definitiva e só é permitida sem histórico comercial. Há "Confirmar exclusão" e
  "Cancelar".
- Enquanto a operação estiver pendente, os controles ficam desabilitados.
- Sucesso só é exibido após resposta confirmada e recarga da lista; se o produto excluído
  estava em edição, o formulário e `product_editing_id` são limpos.
- Falhas (`400` de histórico, `401`, `403`, `404`, rede) mantêm a lista e o formulário
  atuais, mostram mensagem observável e não apresentam sucesso. O `400` de histórico é
  distinguido pela mensagem do backend para orientar a inativação.
- A confirmação é local ao cartão; não é criado modal global nem nova dependência.

## Alternativas descartadas

- **Inativar em vez de excluir**: já existe e não resolve cadastros sem uso que precisam
  sair da listagem.
- **Excluir e limpar itens de carrinho**: permitiria excluir produtos em carrinhos, mas
  esvaziaria carrinhos de Clientes silenciosamente e contraria a preservação de dados.
- **Excluir mesmo com histórico**: quebraria Pedidos e a regra de domínio §8.4.
- **`409 Conflict`**: não existe no XanoScript; usar um código indisponível faria o import
  falhar.
- **Soft delete com campo novo**: exigiria schema e revisão de todas as leituras; a
  inativação já cobre o caso de retirada sem exclusão.

## Fora do escopo

Produto com histórico comercial, Categoria, Marca, itens de Pedido ou Carrinho, arquivo de
imagem armazenado, exclusão em massa, restauração, alteração de checkout, pagamentos,
relatórios e schema Xano.

## Verificação

- Testes unitários de contrato, handler, mensagens de falha e conteúdo do XanoScript.
- `openspec validate implement-product-deletion --strict`.
- Suíte completa, `reflex compile` e `git diff --check`.
- Dry-run do arquivo Xano; publicação e push somente com autorização explícita.
- Pull independente pós-publicação e verificação remota somente leitura. Nenhuma exclusão
  real sem autorização e dados sintéticos.
