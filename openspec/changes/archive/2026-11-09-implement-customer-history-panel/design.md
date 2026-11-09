## Context

Ver `proposal.md`. A C6 já está publicada e verificada; a tela reutiliza
`GET customers/{customer_id}/orders` sem tocar no Xano. O painel atual é renderizado em
`internal_customer_panel` (`voltix/voltix.py`) com a ficha em uma coluna lateral de
300px. O contrato de Clientes (`voltix/internal_customers.py`) já oferece
`positive_int`, `bounded_read` e `customer_date_display`.

Restrições:

- Sessão interna privada no servidor; nunca token de Cliente no navegador.
- Resposta do backend sem dados pessoais do Cliente; o painel não deve inventar campos.
- Sem backend novo, sem schema, sem publicação Xano.
- `reflex.lock/*` não entra em commit.

## Goals / Non-Goals

**Goals:**
- Seção de histórico em largura total abaixo da lista/detalhe.
- Carregamento automático ao selecionar o Cliente.
- Filtros de status/período e paginação 20.
- Itens sempre expandidos com valores persistidos.
- Estados de carregamento, vazio, erro e sessão distintos.
- Contrato Python estrito e testável.

**Non-Goals:**
- Edição, exportação, revelação de dados, atendimentos (C7).
- Novo endpoint, schema, publicação ou métricas.
- Alterar os fluxos existentes de Clientes, Pedidos, Checkout ou Dashboard.
- Paginação de itens dentro de um Pedido ou exportação de CSV.

## Decisions

1. **Contrato no módulo existente.** `InternalOrderItem`, `InternalOrder`,
   `history_parameters` e `order_history_page` entram em `voltix/internal_customers.py`.
   Motivo: o histórico é uma leitura de Cliente e reutiliza `positive_int`,
   `bounded_read` e `customer_date_display`; criar outro módulo duplicaria helpers.
2. **Formato do contrato.** A resposta deve ter exatamente
   `{cliente_id, items, page, per_page, total_items, total_pages}`. Cada Pedido deve ter
   exatamente `{id, codigo, data_pedido, status, subtotal, valor_frete, valor_total,
   itens}`. Cada item deve ter exatamente `{variacao_id, sku, nome_ou_descricao,
   quantidade, preco_unitario, subtotal}`. Campos extras, ids duplicados, status
   inválido, totais inconsistentes ou página fora do tamanho esperado são rejeitados.
3. **Valores monetários.** `subtotal`, `valor_frete`, `valor_total`, `preco_unitario` e
   o subtotal de item são preservados como texto normalizado a partir de string, int ou
   float finito; a UI reutiliza `_cart_money_text`, sem recalcular preços.
4. **Datas.** `data_pedido` aceita milissegundos do Xano ou ISO com timezone e é
   convertida em `dd/mm/aaaa às hh:mm (UTC)` por `customer_date_display`. Valor
   impróprio vira "Data indisponível", sem quebrar a página.
5. **Estado da tela.** Novos campos no `State`:
   `internal_customer_history` (lista de Pedidos),
   `internal_customer_history_customer_id`,
   `internal_customer_history_status`, `internal_customer_history_from`,
   `internal_customer_history_to`,
   `internal_customer_history_status_input`, `internal_customer_history_from_input`,
   `internal_customer_history_to_input`,
   `internal_customer_history_page`, `internal_customer_history_total`,
   `internal_customer_history_pages`, `internal_customer_history_loading`,
   `internal_customer_history_message` e `_internal_history_generation`.
6. **Ciclo de carregamento.** `show_internal_customer` valida a ficha; em sucesso,
   define o Cliente do histórico, zera filtros/página e retorna
   `State.load_internal_customer_history`. Fechar o detalhe, trocar o Cliente,
   atualizar a lista ou limpar filtros incrementa a geração e limpa o histórico.
   `load_internal_customer_history` exige sessão válida, Cliente na ficha, placeholder
   `{customer_id}` na URL e geração/token/usuário ainda atuais antes de gravar.
7. **Filtros.** Aplicar filtros valida `history_parameters` localmente; inválido mostra
   mensagem e não faz requisição. Válido grava os filtros, volta à página 1 e carrega.
   "Limpar filtros" volta a `TODOS` e sem período. A seção inicia sem filtros.
8. **Layout.** A ficha continua na coluna lateral. O histórico é uma `<section>`
   full-width abaixo de `.vx-customers__results`, com:
   - cabeçalho e resumo de contagem;
   - formulário de status + `from`/`to` + aplicar/limpar;
   - mensagens de carregamento/vazio/erro;
   - cartões de Pedido com cabeçalho, totais e tabela de itens;
   - paginação com "Página X de Y" e anterior/próxima.
9. **Acessibilidade.** `aria_label` na seção, rótulos associados aos campos, foco
   visível, tabela semântica de itens, status com `rx.badge` e mensagens em `role=status`.
10. **Erros e sessão.** 401/403 chamam `_clear_authentication_state`, limpam lista,
    ficha, histórico e contadores. Demais erros mostram mensagem genérica e permitem
    nova tentativa; o retry de 429 continua limitado a uma tentativa por `bounded_read`.
11. **Configuração.** `XANO_INTERNAL_CUSTOMER_ORDERS_URL` deve terminar com
    `.../customers/{customer_id}/orders`. Nome documentado em `.env.example` sem valor.
12. **Verificação.** Testes unitários do contrato e dos handlers, suíte existente,
    `openspec validate`, `reflex compile` (restaurando `reflex.lock`). Sem consulta
    autenticada e sem publicação Xano.

## Risks / Trade-offs

- [Volume visual] 20 Pedidos com itens sempre expandidos produzem uma página longa. O
  requisito do usuário é leitura direta; paginação limita o volume. Se crescer, uma
  change própria pode adicionar recolhimento ou paginação de itens.
- [Duas fontes de formatação] A UI reutiliza `_cart_money_text` para não recalcular
  valores; o contrato normaliza apenas a representação textual.
- [Variação removida] SKU/descrição podem vir nulos; a tela mostra "Indisponível" em vez
  de falhar.
- [Datas inválidas] A validação local usa o mesmo formato do backend; o backend continua
  sendo a autoridade final.
- [Sem credencial de teste] A verificação remota autenticada fica fora desta change; a
  tela é validada por contrato, testes e compile.

## Migration Plan

1. Adicionar o contrato e os testes unitários.
2. Adicionar campos/handlers no `State`.
3. Renderizar a seção e os estilos.
4. Configurar `XANO_INTERNAL_CUSTOMER_ORDERS_URL` em `.env.example` e no ambiente local.
5. Rodar testes, `openspec validate` e `reflex compile`; restaurar `reflex.lock`.
6. Arquivar a change e atualizar roadmap/handoff. Sem publicação Xano.

## Open Questions

- Nenhuma bloqueante. A tela consome somente o contrato publicado na C6.
