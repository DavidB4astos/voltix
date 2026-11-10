# Design — ajuste atômico de estoque por variação

## Contexto

A `quantidade_disponivel` pertence à `VariacaoProduto` e deve ser maior ou igual a zero
(`docs/domain-model.md` §3.4). O `PATCH variations/{variation_id}` já aceita
`quantidade_disponivel`, mas grava um valor absoluto; o painel envia esse valor lendo o
estoque exibido. O checkout C1 decrementa com `db.increment` guardado na mesma transação do
Pedido. Um ajuste absoluto concorrente com uma venda pode sobrescrever a baixa.

Decisões preservadas:

1. `MovimentacaoEstoque` e "estoque como entidade independente" continuam fora do modelo
   inicial (`docs/domain-model.md` §9; `docs/ap2/04-priorizacao-moscow.md`).
2. O design da C1 permanece sem tabela de movimentação.
3. Alterações sensíveis de produto/variação são exclusivas de `ADMINISTRADOR` (E2).
4. SKU único, preço positivo, status `ATIVO`/`INATIVO` e estoque não negativo não mudam.

## Decisão

Criar um endpoint dedicado que recebe um **delta assinado** e o aplica com `db.increment`
atômico e guarda de estoque suficiente. Nenhuma tabela ou coluna nova; nenhuma alteração em
`docs/domain-model.md` ou na priorização MoSCoW.

O delta elimina o lost update: baixas de checkout e ajustes passam a ser operações que se
compõem sobre o valor atual, em vez de substituí-lo. A guarda impede estoque negativo mesmo
sob concorrência. O motivo/observação não é aceito porque não haveria onde persistí-lo sem a
entidade descartada; aceitar e descartar seria um falso registro de auditoria.

## Contrato do endpoint

`POST variations/{variation_id}/stock-adjustments` — grupo `Product Management`,
`auth = "user"`.

- Entrada: `int variation_id` (`min:1`) e `decimal delta` obrigatório.
- Autorização: usuário autenticado existente, `role == "ADMINISTRADOR"` e
  `status == "ATIVO"`, verificada antes de ler a variação.
- `delta > 0`: entrada de unidades; `delta < 0`: saída de unidades; `delta == 0`: rejeitado.
- Guarda: para `delta < 0`, exige `quantidade_disponivel >= -delta`; para `delta > 0`,
  o mínimo exigido é zero.
- `db.increment "variacao_produto"` com
  `where = id == variation_id && quantidade_disponivel >= required`, `value = delta`,
  `return = {type: "count"}`.
- Contagem zero após uma variação existente significa estoque insuficiente: erro `400`
  (`badrequest`), sem escrita.
- Variação inexistente: `404` (`notfound`).
- Autorização ausente/insuficiente: `403` (`accessdenied`), sem leitura de negócio.
- Resposta: `id`, `produto_id`, `nome_ou_descricao`, `sku`, `preco`,
  `quantidade_disponivel`, `status`, `created_at`, `updated_at`.

Ajustar uma variação `INATIVO` é permitido: a operação corrige inventário e não altera o
status. O status não entra na guarda porque o ajuste não é venda.

## Atomicidade e concorrência

`db.increment` é uma única instrução atômica; a condição de estoque suficiente é avaliada na
mesma operação. Duas saídas simultâneas, ou uma saída simultânea a um checkout, não podem
produzir quantidade negativa: no máximo uma delas afeta a linha quando resta apenas uma
unidade, e a outra falha a guarda sem escrita parcial.

O endpoint não atualiza `updated_at` nem qualquer outro campo. Um segundo `db.patch` de
metadados poderia deixar quantidade e resposta inconsistentes se falhasse; o ajuste de
estoque é registrado apenas pela quantidade resultante. Isso não altera a regra de domínio
nem o contrato administrativo de variações.

## Interface

- A tabela de variações exibe a ação "Ajustar estoque" apenas no painel de `ADMINISTRADOR`,
  ao lado de "Editar variação" e do status.
- A ação abre um formulário dedicado com: identificação da variação, quantidade atual,
  seleção de direção (entrada/saída) e quantidade positiva.
- Validação no cliente: quantidade maior que zero e, para saída, aviso quando exceder o
  estoque atual; o backend continua sendo a autoridade.
- Enquanto a operação estiver pendente, os controles ficam desabilitados.
- Sucesso só é exibido após resposta confirmada e recarga da lista; a quantidade exibida vem
  do backend.
- Falhas (`400` de estoque, `403`, `404`, rede) mantêm o formulário com os valores
  informados, mostram mensagem observável e não atualizam a quantidade exibida.

## Alternativas descartadas

- **Somente frontend com PATCH absoluto**: menor esforço, mas mantém o lost update e não
  oferece semântica de entrada/saída.
- **`MovimentacaoEstoque` com histórico**: maior valor de auditoria, porém exige nova
  entidade, endpoints e revisão das decisões documentadas; não foi o escopo aprovado.
- **Campo `motivo` sem persistência**: descartado por criar expectativa de histórico
  inexistente.

## Fora do escopo

Histórico de movimentações, tabela/coluna nova, motivo/observação, reserva de estoque,
alteração de checkout ou pedidos, exclusão de produto, importação em massa, edição de preço
ou SKU nesta ação e qualquer alteração de schema Xano.

## Verificação

- Testes unitários de contrato, handler, mensagens de falha e conteúdo do XanoScript.
- `openspec validate implement-variation-stock-adjustment --strict`.
- Suíte completa, `reflex compile` e `git diff --check`.
- Dry-run do arquivo Xano; publicação e push somente com autorização explícita.
- Pull independente pós-publicação e verificação remota somente leitura. Nenhuma escrita em
  estoque real sem autorização e dados sintéticos.
