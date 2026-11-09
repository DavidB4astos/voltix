## Context

Ver `proposal.md`. A C6 depende de C4 (Cliente e máscaras) e C3 (Pedido, itens e
detalhe). O schema não muda e a tela do painel fica para uma change própria, no mesmo
critério de C2/C3/C10.

Restrições:

- Plano Free e workspace compartilhado: publicação com dry-run e confirmação do usuário.
- O padrão interno do projeto é `auth = "user"` + `precondition` de papel/status no
  backend; o frontend nunca é fonte de autorização.
- Nenhum dado pessoal do Cliente na resposta; a capability é somente leitura.
- O histórico deve refletir os valores persistidos na compra, não o catálogo atual.

## Goals / Non-Goals

**Goals:**
- `GET customers/{customer_id}/orders` no grupo `Voltix Internal Customers`.
- Lista paginada dos Pedidos do Cliente, do mais recente para o mais antigo.
- Resumo do Pedido + itens inline com valores persistidos.
- Filtros opcionais por `status` e período (`from`/`to`) em UTC, inclusivos.
- Paginação 20/50 com totais.
- Acesso de leitura para FUNCIONARIO e ADMINISTRADOR ativos.
- Resposta determinística para Cliente inexistente, período inválido e histórico vazio.

**Non-Goals:**
- Tela/seção de histórico no painel Reflex.
- Atendimentos (C7), edição/inativação de Cliente, exportação.
- Métricas agregadas de faturamento, ticket médio ou ranking de Clientes.
- Alterar C3, C4, C2 ou C10.
- Filtro por produto, categoria ou forma de pagamento.

## Decisions

1. **Endpoint e grupo**: `GET customers/{customer_id}/orders` no grupo existente
   `Voltix Internal Customers`. O Cliente é o recurso central e a propriedade é explícita
   no caminho, evitando ampliar o contrato já publicado de `GET orders` (C3).
2. **Existência do Cliente**: `db.get CLIENTE` restrito a `id`; se nulo, `notfound`.
   Nenhum outro campo do Cliente é lido ou retornado.
3. **Conteúdo**: cada Pedido traz `id`, `codigo`, `data_pedido`, `status`, `subtotal`,
   `valor_frete`, `valor_total` e `itens`. Cada item traz `variacao_id`, `sku`,
   `nome_ou_descricao`, `quantidade`, `preco_unitario` e `subtotal`
   (`preco_unitario * quantidade`). Os valores vêm de `pedido`/`item_pedido`; nenhum
   preço atual de catálogo é usado.
4. **Consultas agrupadas (sem N+1)**: para a página retornada, o endpoint faz:
   1. `db.query pedido` com paginação e `output` restrito ao resumo;
   2. `db.query item_pedido` com `pedido_id in $order_ids`;
   3. `db.query variacao_produto` com `id in $variation_ids`.
   Os itens são agrupados em memória por `pedido_id` e as variações por `id`.
   - Alternativa considerada: consultar itens e variações dentro de cada Pedido.
     Rejeitada por gerar até ~50 queries adicionais por página e pressionar o Free.
   - Guarda: as consultas 2 e 3 só são executadas quando as listas de ids não estão
     vazias; Pedido sem item retorna `itens: []`.
5. **Filtros**:
   - `status` (texto, padrão `TODOS`) aceita `TODOS` ou os seis estados do Pedido.
   - `from`/`to` opcionais em `YYYY-MM-DD`, interpretados como dias inteiros em UTC,
     inclusivos (`from` 00:00:00, `to` 23:59:59).
   - Sem `from`/`to`, não há recorte de período: todo o histórico é paginado.
   - Formato inválido ou `from > to` → `inputerror` sem executar a consulta.
   - Alternativa considerada: período padrão de 30 dias. Rejeitada porque histórico de
     CRM deve mostrar o relacionamento inteiro por padrão.
6. **Paginação**: `page` (padrão 1) e `per_page` (padrão 20, máximo 50). Ordenação
   `data_pedido desc, id desc`. Totais `itemsTotal`/`pageTotal` do `db.query` são
   expostos como `total_items`/`total_pages`; `total_pages` é zero quando não há itens
   (mesmo padrão da C4).
7. **Sem métricas**: a resposta não soma faturamento nem calcula ticket médio; os únicos
   totais são de paginação. A C10 continua sendo a fonte de métricas.
8. **Sem dados sensíveis**: a resposta identifica o Cliente apenas por `cliente_id` e não
   inclui nome, e-mail, CPF, telefone, endereço, senha ou token.
9. **Verificação**: language server oficial + `openspec validate` + suíte de 188 testes +
   dry-run restrito + pull independente + 401 sem sessão. Sem ciclo sintético de compra,
   salvo autorização explícita em outra change.

## Risks / Trade-offs

- [Volume de itens em 50 Pedidos] → três consultas agrupadas por página, com `output`
  restrito; se o volume crescer, migrar para agregação/paginação de itens em change
  própria.
- [Chaves de mapa por id] → os ids são convertidos para texto antes de montar os mapas,
  evitando diferença entre chave numérica e chave textual do JSON.
- [Pedido histórico sem item] → retorna `itens: []`, sem falhar; o dado é inconsistente
  com o domínio, mas a leitura não deve quebrar a tela.
- [Fuso horário] → UTC explícito. Se a operação precisar de America/Sao_Paulo, será uma
  change própria.
- [Escopo de CRM] → sem atendimentos e sem edição; C7 continua dependente de C6 e da
  medição E5.

## Migration Plan

1. Criar `customer_id_orders_GET.xs` no grupo `Voltix Internal Customers`.
2. Validar com o language server oficial e `openspec validate --strict`.
3. Dry-run restrito ao arquivo; gate explícito do usuário.
4. Publicação e pull independente + 401 na rota sem sessão.
5. Arquivar a change, consolidar `customer-order-history` e atualizar roadmap/handoff.

## Open Questions

- Nenhuma bloqueante. A tela de histórico, atendimentos e exportação ficam para changes
  próprias.
