## Context

`checkout_confirm_POST.xs` confirma o Pedido dentro de um `db.transaction`, mas não baixa estoque. O Domain Model exige:

- 3.4 / 8.3: quantidade disponível inteira e estoque nunca negativo.
- 5.1 / 8.14: o Carrinho não reserva estoque.
- 5.3 / 8.17: cancelamento devolve unidades **já baixadas** (dependência futura da C2).

Decisões já aprovadas (roadmap C1 + aprovação da Change):

1. Estoque insuficiente retorna **HTTP 200 com `confirmado=false`**, sem criar Pedido (contrato atual preservado).
2. **Sem** tabela de movimentação de estoque.
3. A baixa ocorre **atomicamente dentro da transação do checkout**, impedindo estoque negativo e compras concorrentes da última unidade.
4. Preservar frontend e contratos existentes sempre que possível.
5. O Carrinho continua **sem** reservar estoque.

## Investigação do primitivo XanoScript

| Recurso | Situação | Conclusão |
|---|---|---|
| `db.direct_query { sql, arg, response_type }` | Documentado nas referências oficiais do XanoScript | **Adotado** — permite `UPDATE` guardado com aritmética na coluna |
| `db.transaction { stack { ... } }` | Documentado; já usado pelo checkout | **Adotado** — atomicidade/rollback |
| `db.transaction { isolation = ... }` | Documentado | Plano B (não usado) |
| `lock` em `db.get` / `db.query` | Existe no construtor visual, **sem sintaxe documentada em XanoScript** | Rejeitado |
| `db.patch` / `db.edit` com `where` | Não existe: apenas `field_name`/`field_value` | Rejeitado |
| `db.bulk.update` / `db.bulk.patch` com `where` | Documentação conflitante (forma oficial usa `items=[...]`) | Rejeitado |
| Aritmética do valor atual da coluna em `data` | Não documentada | Rejeitado (evitaria *lost update* apenas por sorte) |

### Por que o `UPDATE` guardado é seguro

```sql
UPDATE variacao_produto
   SET quantidade_disponivel = quantidade_disponivel - ?, updated_at = now()
 WHERE id = ? AND quantidade_disponivel >= ? AND status = 'ATIVO'
RETURNING id, quantidade_disponivel
```

- Statement único → atômico.
- O `WHERE` é reavaliado contra a versão atual da linha após a aquisição do lock (semântica Postgres READ COMMITTED) → **sem oversell** e **sem estoque negativo**.
- A aritmética é feita **na coluna** (`col - q`), não a partir de uma leitura prévia → **sem lost update**.
- Dentro de `db.transaction` → rollback cobre Pedido, ItemPedido, Pagamento, Carrinho e estoque.

## Fluxo proposto (dentro da `db.transaction` existente)

1. Re-leitura de endereço, Carrinho e `item_carrinho` (já existente).
2. **Fase 1 — leitura travada:** `SELECT id, quantidade_disponivel, status FROM variacao_produto WHERE id = ? FOR UPDATE;` para cada variação do Carrinho (um `db.direct_query` por item; o Carrinho garante no máximo um item por variação).
3. **Fase 2 — avaliação:** recalcular a disponibilidade (`$all_available`) usando os valores **travados** e os status de Produto/Variação. Se indisponível → **nenhuma escrita** → `confirmado=false` (HTTP 200).
4. **Fase 3 — persistência:** se disponível, criar Pedido, ItemPedido e Pagamento (fluxo atual) e, em seguida, aplicar a **baixa guardada** por item.
5. **Falha defensiva:** se algum `UPDATE` guardado retornar zero linhas, abortar a transação inteira (`throw`).

### Ordem da baixa (por que no fim)

Se o `db.direct_query` **não** participar da transação (lacuna a confirmar), a pior falha seria "baixa sem Pedido" — em vez de "Pedido sem baixa". Como o guard de zero linhas impede estoque negativo em qualquer cenário, essa ordem é a mais conservadora. Essa premissa é confirmada pela tarefa 1.

### Por que `FOR UPDATE` (fase 1)

Quem perde a corrida pela última unidade precisa enxergar `estoque=0` **sob lock** para seguir o caminho limpo de HTTP 200 / `confirmado=false`, em vez de abortar com erro HTTP. Sem a leitura travada, a detecção só ocorreria no guard e o perdedor receberia erro.

## Invariantes e resultados inválidos

- `baixa sem Pedido` é **resultado inválido**.
- `Pedido sem baixa` é **resultado inválido**.
- Estoque nunca pode assumir valor negativo.
- Estoque igual a zero **não** torna a variação `INATIVO`.

## Verificação obrigatória (bloqueante — tarefa 1)

Antes de qualquer implementação, confirmar que `db.direct_query` participa da mesma transação do checkout e é revertido junto com Pedido, ItemPedido, Pagamento e estoque. Sem essa confirmação:

- não implementar a baixa;
- registrar o bloqueio no próprio `design.md` para decisão;
- avaliar o plano B (`db.transaction { isolation = "serializable" }` com escrita nativa e retry), sem adotá-lo por suposição.

## Preservação de contrato

- Chaves de resposta inalteradas: `confirmado`, `revisao_alterada`, `pedido_id`, `codigo`, `subtotal`, `valor_frete` (0), `valor_total`, `itens`, `revisao`, `endereco_id`, `endereco`.
- `itens[].estoque_disponivel` continua refletindo a leitura usada na decisão.
- Nenhuma mudança em `voltix/voltix.py` nem no frontend.
- `checkout_review_POST.xs`, `cart_*.xs` e as tabelas não são alterados.

## Riscos

1. **Participação do `db.direct_query` na transação** — lacuna crítica; mitigada pela tarefa 1 bloqueante.
2. **Argumentos múltiplos em `arg`** — a documentação oficial mostra um argumento; um espelho mostra array. Confirmar sintaxe na implementação; se necessário, ajustar a forma do comando.
3. **Rate limit (Xano Free, 10 req/20 s)** — a baixa usa statements internos, não requisições da API; a validação ao vivo deve respeitar o limite.
4. **Coluna decimal** — `quantidade_disponivel` é `decimal`; as quantidades do Carrinho são inteiras positivas, então a baixa permanece inteira.
5. **Status do Produto** — o guard cobre variação `ATIVO` e estoque; o status do Produto continua avaliado na fase 2 (comportamento atual), sem garantia de lock.

## Fora de escopo

Cancelamento/devolução (C2), reserva de estoque, tabela de movimentação, painel de pedidos (C3), dashboard (C10), frete, aprovação/simulação de pagamento e alteração de frontend.

## Dependências

- `checkout_confirm_POST.xs` e `tests/test_checkout_orders.py`.
- Nenhuma dependência de outras changes.
