## Context

Ver `proposal.md`. A C10 depende de C1/C2/C3: o checkout grava Pedido e Pagamento, a C2
cancela e a C3 garante os estados operacionais. O schema não muda e a tela do painel fica
para uma change própria (mesmo critério de C2/C3).

Restrições:

- Plano Free e workspace compartilhado: publicação com dry-run e confirmação do usuário.
- O padrão interno do projeto é `auth = "user"` + `precondition` de papel/status no
  backend; o frontend nunca é fonte de autorização.
- Nenhum dado sensível na resposta; a capability é somente leitura.
- As métricas não podem virar regra contábil nova: seguem a decisão E3 e os estados
  existentes.

## Goals / Non-Goals

**Goals:**
- `GET reports/sales` com faturamento, quantidade de Pedidos, ticket médio e série diária.
- Período padrão de 30 dias em UTC, com `from`/`to` inclusivos e limite de 366 dias.
- Status incluídos explícitos: `PAGAMENTO_CONFIRMADO`, `EM_PREPARACAO`, `ENVIADO`,
  `ENTREGUE`.
- Acesso de leitura para FUNCIONARIO e ADMINISTRADOR ativos.
- Resposta determinística para período vazio e limites inclusivos.

**Non-Goals:**
- Tela/aba de dashboard no reflex, gráficos avançados, exportação, metas ou previsões.
- Faturamento por item, por produto, por Cliente ou margem/lucro.
- Reembolso, estorno, relatório contábil ou fechamento de caixa.
- Mudança de schema, de regras de pedido ou de cancelamento.

## Decisions

1. **Endpoint e grupo**: `GET reports/sales` no grupo existente
   `Voltix Internal Orders`. A descrição do grupo passa a
   "Internal order consultation, cancellation and sales reporting.", refletindo o uso
   real desde a C3. Alternativa considerada: novo grupo "Dashboard" — rejeitada para não
   duplicar escopo de pedidos.
2. **Definição de receita** (aprovada pelo usuário em 09/11/2026): soma de `valor_total`
   e contagem de Pedidos em `PAGAMENTO_CONFIRMADO`, `EM_PREPARACAO`, `ENVIADO` ou
   `ENTREGUE`. Ficam fora `AGUARDANDO_PAGAMENTO` (ainda não é receita) e `CANCELADO`
   (não conta como venda). É um retrato do estado atual, não um razão de eventos: um
   Pedido cancelado depois deixa de aparecer também em períodos passados. Alternativa
   considerada: ledger de eventos — rejeitada nesta change (exigiria tabela/eventos
   novos).
3. **Base temporal**: `pedido.data_pedido` (data comercial do Pedido), não `created_at`.
   Limites em UTC, inclusivos: `from` 00:00:00 até `to` 23:59:59.
4. **Período padrão e derivação**:
   - sem `from`/`to`: `to` = hoje (UTC), `from` = hoje − 29 dias;
   - só `to`: `from` = `to` − 29 dias;
   - só `from`: `to` = hoje (UTC);
   - validação: formato `YYYY-MM-DD`, `from <= to`, intervalo máximo de 366 dias
     inclusivos; caso contrário `inputerror` sem executar a consulta.
5. **Agregação**: uma `db.query pedido` com `return = {type: "list"}` e `output` restrito a
   `id`, `data_pedido`, `status` e `valor_total`, ordenada por `data_pedido asc, id asc`.
   Os totais e a série diária são calculados em XanoScript, com mapa por dia e
   `entries|sort`.
   - Alternativa considerada: `return = {type: "aggregate", group, eval}`. O parser oficial
     aceita o tipo, mas a documentação pública não detalha `group`/`eval` e o runtime não
     pode ser exercitado sem sessão. Preferimos o caminho documentado e determinístico.
   - Trade-off: uma consulta de até 366 dias pode trazer muitos Pedidos. O projeto está em
     escala pequena e só quatro colunas são lidas; se o volume crescer, migrar para
     agregação no banco em change própria, depois de validar o runtime.
6. **Série diária**: apenas dias com Pedidos contabilizados, em ordem crescente de
   `YYYY-MM-DD`. Dias sem venda são omitidos (o consumidor pode preencher lacunas). Isso
   evita iteração de calendário no backend e mantém a resposta enxuta.
7. **Arredondamento**: valores monetários arredondados para duas casas na resposta
   (`faturamento`, `ticket_medio`, `serie_diaria[].faturamento`). `ticket_medio` é zero
   quando `pedidos=0`, evitando divisão por zero.
8. **Sem dados sensíveis**: a resposta não inclui Cliente, e-mail, CPF, telefone, endereço,
   itens ou Pagamento. Nenhum `db.get CLIENTE` é executado.
9. **Verificação**: language server oficial + `openspec validate` + suíte de 188 testes +
   dry-run restrito + pull independente + 401 sem sessão. Sem ciclo sintético de vendas,
   salvo autorização explícita em outra change.

## Risks / Trade-offs

- [Volume de Pedidos em 366 dias] → consulta única com quatro colunas e agregação em
  memória; monitorar se o volume crescer. Migração para agregação no banco fica preparada
  como evolução.
- [Fuso horário] → UTC explícito. Se a operação precisar de America/Sao_Paulo, será uma
  change própria com regra de negócio aprovada.
- [Cancelamento altera o passado] → o relatório reflete o estado atual; Pedido cancelado
  sai de todos os períodos. Documentado e coerente com E3; um razão histórico exigiria
  eventos, fora do escopo.
- [Datas impossíveis como 2026-02-31] → o formato é validado e o parse normaliza; não há
  calendário dedicado nesta change. O risco é baixo para uma entrada de dashboard.
- [País/arredondamento] → arredondamento simples de duas casas, sem regra fiscal.

## Migration Plan

1. Criar `reports_sales_GET.xs` e atualizar a descrição de `api_group.xs`.
2. Validar com o language server oficial e `openspec validate --strict`.
3. Dry-run restrito aos dois arquivos; gate explícito do usuário.
4. Pull independente + 401 na rota sem sessão.
5. Arquivar a change, consolidar `sales-dashboard` e atualizar roadmap/handoff.

## Open Questions

- Nenhuma bloqueante. A tela do dashboard, o fuso local e relatórios por produto ficam
  para changes próprias.
