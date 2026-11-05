## Context

See `proposal.md` — Motivation section. Estado atual e invariantes que moldam a abordagem:

- `checkout_confirm_POST.xs` revalida endereço, carrinho, itens, preços, status e a
  revisão enviada pelo cliente **dentro de `db.transaction`**; cria Pedido, ItemPedido,
  Pagamento e remove os itens do Carrinho no mesmo bloco. Estoque é apenas lido
  (`quantidade_disponivel`) e comparado à quantidade; **não é decrementado**.
- A prova de runtime (`2026-11-05-prove-c1-atomic-decrement-synthetic`) confirmou que
  `db.increment` com guarda composta aceita o filtro
  `id == ? && quantidade_disponivel >= ? && status == "ATIVO"` dentro de `db.transaction`,
  decrementa atomicamente e participa do rollback multi-item.
- Decisões preservadas do defer histórico (`docs/deferred-changes/2026-10-23-
  baixa-estoque-checkout/`): sem tabela de movimentação; sem reserva no Carrinho; estoque
  nunca negativo; Pedido e baixas persistem ou revertem juntos; chaves/semântica da
  resposta inalteradas; insuficiência → HTTP 200 `confirmado=false`.

## Goals / Non-Goals

**Goals:**
- Baixar estoque de cada item atomicamente na confirmação, com reversão integral em falha.
- Manter `confirmado=false` (HTTP 200) como resposta de insuficiência, sem estados parciais.
- Manter ordering, stale-review e demais pré-condições intactos; mudar apenas o necessário.

**Non-Goals:**
- Cancelamento/devolução (C2), reserva de estoque, tabela de movimentação.
- Reconcile de preços/status adicionais além dos já feitos na reconciliação do cart.
- Testes de compra em produção Xano além dos expressamente autorizados.

## Decisions

1. **Decremento com `db.increment` e verificação por contagem** (igual ao primitivo
   comprovado). Alternativa considerada: ler depois `db.patch` com aritmética — rejeitada
   (corrida de leitura/escrita, risco de estoque negativo).

2. **Decrementar ANTES de gravar o Pedido, dentro da mesma transação.** Qualquer falha
   posterior (item sem estoque, erro de persistência) reverte estoque e pedido juntos.
   Alternativa: gravar Pedido antes e decrementar depois com compensação — rejeitada
   (viola atomicidade; falharia no requisito de reversão parcial).

3. **Erro com nome `EstoqueInsuficiente`** lançado quando um `db.increment` afeta 0 linhas.
   `try_catch` envolve a transação; somente esse nome é convertido em resposta
   `confirmado=false`; quaisquer outros erros continuam propagando (visíveis) — preserva a
   semântica atual para falhas inesperadas.

4. **Ordem de baixa = mesma ordem dos itens no Carrinho (id asc)**, já usada e ordenada
   pela mudança de reconciliação do cart (`2026-10-30-reconcile-cart-checkout-ordering`);
   mantém determinismo sem ampliar a superfície de alteração. Deadlock entre compras com
   múltiplas variações é mitigado pelo guarda de estoque (aborta curto) e pela transação
   curta; nenhum observado na prova (Caso E); documentado como não observado, não como
   impossível.

5. **Produto/Variação inativos continuam bloqueados** pelo caminho já existente (a guarda
   do `db.increment` cobre `status == "ATIVO"` apenas na Variação; a checagem de Produto
   ATIVO permanece a que já existe). A janela de concorrência de status entre Produto e
   Variação foi documentada na revisão do defer e permanece sem mudança de comportamento.

6. **Sem arquivos de teste com dados reais**; verificação remota mínima por dry-run e
   limitada a cenários sintéticos se aprovados pelo usuário na execução.

## Risks / Trade-offs

- [Baixa acidental sobre dados demo/reais em testes remotos] → nenhum teste de compra sem
  autorização específica e sem dados sintéticos com limpeza reservada na UI do Xano.
- [Cenários negativos persistirem após falha no meio do fluxo] → a transação única envolve
  todas as escritas; qualquer falha reverte tudo (provado na prova: Caso C).
- [Deadlock em compras com muitas variações sobrepostas] → guardada por estoque curto e
  transação enxuta; ordem determinística (item id asc). Não observado sob concorrência
  limitada (2 chamadas). Se observado em produção, tratar com retry curto por carrinho.
- [Specs consolidadas desatualizadas] → delta `MODIFIED` obrigatório; arquivamento exige
  sincronia da spec consolidada antes do arquivamento.
- [HTTP 200 para conflito de negócio] → mantido por compatibilidade da resposta aprovada;
  documentado; cliente continua vendo erro via feedback existente.

## Migration Plan

1. Implementar no `checkout_confirm_POST.xs` (decrementos dentro da transação, antes do
   `db.add pedido`; `try_catch` externo convertendo `EstoqueInsuficiente`).
2. `openspec validate --strict`; suíte `python -m unittest discover -s tests -q` (188
   testes) preservada.
3. Revisar diff local; commit (não push automático).
4. **GATE do usuário**: dry-run do pacote e confirmação explícita antes de publicar
   (publicação restrita de 1 documento).
5. Verificação remota mínima aprovada (leitura/estado; qualquer teste de compra exige nova
   autorização e dados sintéticos).
6. Arquivar a change com spec sincronizada; atualizar roadmap/defer; commit e push somente
   com autorização.

## Open Questions

- Escopo exato da verificação remota após a publicação (só leitura vs. ciclo de compra
  sintético completo) será decidido pelo usuário na execução, dado o estado do workspace
  compartilhado. Não bloqueia specs nem abordagem.
