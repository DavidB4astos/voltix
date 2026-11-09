## Context

Ver `proposal.md`. A C2 encerrou o fluxo de cancelamento e a C1 garante a baixa de estoque
no checkout. Falta a operação interna do Pedido depois do pagamento. O grupo
`Voltix Internal Orders` já existe (criado na C2), o schema não muda e não há tela
aprovada para esta fase.

Restrições:

- Plano Free, workspace compartilhado: publicação com dry-run e confirmação do usuário.
- Padrão interno do projeto: `auth = "user"` + `precondition` de papel/status no backend.
- Segredos e dados sensíveis nunca vão para a resposta (C4 já mascara e-mail/telefone/CPF).

## Goals / Non-Goals

**Goals:**
- Lista paginada e detalhe de Pedidos para `FUNCIONARIO` e `ADMINISTRADOR` ativos.
- Avanço de status estrito, um passo por requisição, apenas `ADMINISTRADOR`.
- Reutilizar o cancelamento da C2, sem duplicar regra.
- Sem alteração de schema e sem expor dados sensíveis.

**Non-Goals:**
- Tela no painel Reflex, dashboard, CRM, transportadora/rastreio.
- Edição de itens, valores, endereço ou Pagamento.
- Mudanças em estoque por transição de status.
- Cancelamento em `EM_PREPARACAO`/`ENVIADO`/`ENTREGUE`.

## Decisions

1. **Três endpoints no grupo existente `Voltix Internal Orders`:**
   - `GET orders` — lista paginada e filtros.
   - `GET orders/{order_id}` — detalhe.
   - `POST orders/{order_id}/status` — avanço de status com `status` no corpo.
   - Alternativa considerada: um endpoint por transição — rejeitada (três rotas
     equivalentes, validação duplicada, pior para evoluir a sequência).
2. **Permissões** (verificadas no backend, nunca no frontend):
   - lista e detalhe: `FUNCIONARIO` ou `ADMINISTRADOR`, ambos `ATIVO`.
   - transição: `ADMINISTRADOR` `ATIVO` apenas.
   - `CLIENTE` não usa esse grupo/sessão; visitante e interno inativo recebem
     `accessdenied`.
3. **Sequência de transição** (um passo por chamada):

   | Status atual | Alvo permitido |
   |---|---|
   | `PAGAMENTO_CONFIRMADO` | `EM_PREPARACAO` |
   | `EM_PREPARACAO` | `ENVIADO` |
   | `ENVIADO` | `ENTREGUE` |
   | alvo igual ao atual | sucesso `alterado=false` (no-op) |
   | qualquer outro par | `badrequest` |

   `CANCELADO` e `ENTREGUE` são terminais para avanço. `AGUARDANDO_PAGAMENTO` não avança
   sem confirmação de pagamento.
4. **Busca textual** (`q`) combina código do Pedido **ou** nome do Cliente. Para não
   depender de `where` sobre tabela juntada, o endpoint resolve primeiro os `cliente_id`
   por nome (`db.query CLIENTE`), e usa a lista na condição do Pedido
   (`cliente_id in $ids`). O nome exibido na lista vem de `db.get CLIENTE` por item da
   página (máximo 50).
5. **Lista**: `sort = {data_pedido: "desc", id: "desc"}`, paginação `{page, per_page,
   totals: true}` (mesmo padrão de `internal_customers/customers_GET.xs`), `per_page`
   entre 1 e 50, `q` até 100 caracteres.
6. **Detalhe**: Pedido, Cliente (nome + e-mail mascarado), endereço de entrega, itens
   (com SKU/nome da variação) e Pagamento. Sem CPF, telefone, senha, hash ou token.
7. **Transição transacional**: leitura do Pedido dentro de `db.transaction`, validação da
   sequência e `db.edit` apenas em `status`/`updated_at`. Nada mais é escrito.
8. **Cancelamento reutilizado**: nenhuma rota nova; o painel (change futura) chamará
   `POST orders/{order_id}/cancel` da C2. O endpoint de status rejeita `CANCELADO` como
   alvo.

## Risks / Trade-offs

- [Busca por nome do Cliente com muitos resultados] → lista de ids pode crescer; aceitável
  no volume do projeto (limite Free de 100k registros). Alternativa futura: join com
  `where` na tabela juntada.
- [Nome do Cliente por item da página gera N leituras] → no máximo 50 por página;
  simplicidade preferida a otimização prematura.
- [Sequência fixa pode não cobrir exceções operacionais] → ampliar exige nova change com
  regra explícita; não criar transição livre.
- [Pedido cancelado durante a mesma janela que uma transição] → a transição lê o status
  dentro da transação e rejeita `CANCELADO`; não há escrita de estoque aqui.

## Migration Plan

1. Criar os três endpoints no grupo `Voltix Internal Orders` (arquivos novos).
2. Dry-run restrito aos três arquivos; gate explícito do usuário.
3. Pull independente + checagens somente leitura (401 sem sessão; papéis negados quando
   houver credencial).
4. Arquivar a change, consolidar a capability `order-management` e atualizar
   roadmap/handoff.

## Open Questions

- Nenhuma bloqueante. A tela do painel e o filtro por período ficam para change própria.
