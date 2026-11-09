## Context

Ver `proposal.md` — Why. A C3 já publicou `GET orders`, `GET orders/{order_id}` e
`POST orders/{order_id}/status` no grupo `Voltix Internal Orders`, com `auth = "user"` e
precondições de FUNCIONARIO/ADMINISTRADOR `ATIVO`; o status exige ADMINISTRADOR. A tela não
altera o Xano.

O painel interno é renderizado em `voltix/voltix.py` por `internal_workspace_shell`, com
seções controladas por `State.internal_section`. A tela de Atendimentos (C7 UI) já
estabeleceu o padrão de contrato estrito em módulo próprio, handlers server-side com token
interno, descarte por geração e composição de seção. `voltix/internal_customers.py` já
oferece `positive_int`, `bounded_read`, `customer_date_display`, `ORDER_STATUSES` e
`order_item_record`, reutilizáveis.

Restrições:

- Sessão interna privada no servidor; nenhum token no navegador.
- A resposta de detalhe contém nome do Cliente, e-mail mascarado e endereço de entrega;
  CPF, telefone, senha, hash e token nunca são exibidos.
- Sem backend novo, schema, migração, cancelamento ou publicação Xano.
- `reflex.lock/*` não entra em commit.

## Goals / Non-Goals

**Goals:**

- Seção Pedidos em largura total, acessível a FUNCIONARIO e ADMINISTRADOR ativos.
- Listagem com busca por código/nome, filtro por status e paginação de 20.
- Detalhe com Cliente, itens, entrega e Pagamento, usando valores persistidos.
- Avanço de status exclusivo de ADMINISTRADOR, um passo por vez.
- Estados de carregamento, vazio, erro e sessão, com descarte de respostas obsoletas.

**Non-Goals:**

- Cancelamento, reembolso, edição de itens/endereço/Pagamento, criação de Pedido.
- Alterar valores, estoque, frete ou vínculos.
- Buscar nome do Cliente no frontend ou resolver dados além dos retornados.
- Alterar Clientes, Atendimentos, Produtos, Catálogo, Importação ou Home.
- Publicação, pull ou validação remota autenticada no Xano.

## Decisions

1. **Contrato em módulo próprio.** Criar `voltix/internal_orders.py` com
   `OrderSummary`, `OrderCustomer`, `OrderDelivery`, `OrderPayment`, `OrderDetail`,
   `OrderStatusResult`, `order_filters`, `order_summary_page`, `order_detail` e
   `order_status_result`. Importar `ORDER_STATUSES`, `positive_int`,
   `customer_date_display` e `order_item_record` de `internal_customers`. Alternativa
   descartada: ampliar `internal_customers.py`, que já concentra clientes e histórico.

2. **Formato exato da listagem.** A resposta deve ter exatamente `{items, page, per_page,
   items_total, page_total}` — nomes próprios da C3, diferentes de Clientes/Atendimentos. Cada
   item exatamente `{id, codigo, data_pedido, status, cliente, itens_count, subtotal,
   valor_frete, valor_total}`, com `cliente` exatamente `{id, nome_completo}`. A validação
   confere página, `per_page`, totais (`page_total = ceil(items_total/per_page)`), tamanho da
   página, status, datas, inteiros e valores monetários; campos extras ou duplicidade são
   rejeitados.

3. **Formato exato do detalhe.** A resposta deve ter exatamente `{id, codigo, data_pedido,
   status, cliente, entrega, itens, subtotal, valor_frete, valor_total, pagamento}`, com
   `cliente` exatamente `{id, nome_completo, email_masked}`, `entrega` exatamente `{cep,
   logradouro, numero, complemento, bairro, cidade, estado, identificacao}`, itens no formato
   já usado por `order_item_record` e `pagamento` exatamente `{metodo, valor, status}`.
   `email_masked` aceita `null` ou o padrão mascarado publicado; campos de endereço e
   complemento aceitam `null` e viram "Indisponível" na tela. O `id` retornado deve ser igual
   ao solicitado.

4. **Formato exato do status.** A resposta deve ter exatamente `{pedido_id, codigo,
   status_anterior, status_atual, alterado}`; `alterado` é booleano e os status pertencem ao
   conjunto publicado. O `pedido_id` deve ser igual ao solicitado.

5. **Ciclo de listagem.** `State.internal_orders_*` guarda busca, status aplicado e digitado,
   página, itens, totais, carregamento, mensagem e geração. `load_internal_orders` exige
   sessão interna válida, valida `q` (≤100) e status localmente, monta a URL com `urlencode`,
   lê server-side e grava somente se geração, token e usuário continuarem atuais. Aplicar
   filtros reinicia na página 1; limpar restaura `TODOS` e vazio.

6. **Detalhe.** `select_internal_order(id)` valida inteiro positivo, lê
   `XANO_INTERNAL_ORDER_DETAILS_URL` com `{order_id}`, valida o contrato e descarta respostas
   de seleções anteriores. `close_internal_order` limpa o detalhe. `notfound` fecha o detalhe
   e informa que o Pedido não existe.

7. **Avanço de status.** `advance_internal_order_status()` calcula o único próximo alvo a
   partir do status atual (`PAGAMENTO_CONFIRMADO → EM_PREPARACAO → ENVIADO → ENTREGUE`).
   Status fora da sequência não oferece ação. O handler recusa a operação se o papel não for
   `ADMINISTRADOR`, valida o alvo contra o status atual e chama o endpoint publicado. A UI
   esconde o controle de FUNCIONARIO, mas o backend continua a autoridade: `403` mantém a
   sessão e o Pedido; `400` mantém o status anterior e informa transição inválida. Em
   sucesso, atualiza o detalhe, recarrega a listagem e informa se houve alteração.

8. **Integração com a navegação.** `State.select_internal_section` passa a aceitar `pedidos`
   para FUNCIONARIO e ADMINISTRADOR. O item Pedidos fica ao lado de Clientes e Atendimentos;
   o título/descrição da seção entram no `rx.match` do shell. Trocar para Pedidos dispara
   `load_internal_orders`.

9. **Layout e estilos.** Reutilizar a linguagem de `vx-customers`/`vx-attendance` e adicionar
   o bloco `vx-orders` em `assets/voltix-internal.css` para filtros, tabela, detalhe, itens,
   endereço, Pagamento, controles de status, mensagens e paginação. Desktop-first, com quebra
   em telas estreitas, sem redesenhar o restante do painel.

10. **Erros e sessão.** `401` encerra a sessão em qualquer operação. `403` em leitura encerra
    a sessão; `403` no avanço de status é operação negada e mantém sessão e estado. Demais
    falhas mostram mensagem genérica em português e permitem nova tentativa. O retry de `429`
    continua limitado a uma tentativa por `bounded_read`. Payload bruto nunca é exibido.

11. **Configuração.** Três variáveis, sem valores versionados:
    - `XANO_INTERNAL_ORDERS_URL` — coleção `GET`;
    - `XANO_INTERNAL_ORDER_DETAILS_URL` — contém `{order_id}`, usada em `GET`;
    - `XANO_INTERNAL_ORDER_STATUS_URL` — contém `{order_id}`, usada no `POST` de status.
    Placeholder ausente é erro local.

12. **Privacidade e acessibilidade.** Rótulos associados, `aria_label` por item e seção,
    `role=status` nas mensagens, foco visível e botões com nomes acessíveis. A tela exibe
    apenas os campos do contrato; CPF, telefone, senha, hash e token não são renderizados nem
    inventados. A busca textual é enviada ao backend; nenhum nome é resolvido no navegador.

13. **Verificação.** Testes unitários do contrato (listagem, detalhe e status), testes dos
    handlers com respostas simuladas, navegação, suíte existente,
    `openspec validate --all --strict`, `git diff --check` e `reflex compile` restaurando
    `reflex.lock`. Sem consulta autenticada e sem publicação Xano.

## Risks / Trade-offs

- [Dados pessoais no detalhe] Nome, e-mail mascarado e endereço aparecem para o interno;
  Mitigação: somente campos publicados, sem CPF/telefone, sem log de payload e sem captura
  com dados reais.
- [Nomes de paginação divergentes] A C3 usa `items_total`/`page_total`; Mitigação: contrato
  próprio e testes que rejeitam `total_items`/`total_pages`.
- [Regras duplicadas na UI] A tela esconde controles inválidos, mas o backend é a autoridade;
  Mitigação: handlers tratam `403`/`badrequest` e recarregam o estado.
- [Volume de detalhe] Itens, endereço e Pagamento aumentam a densidade; Mitigação: seções
  rotuladas e resumo de valores.
- [Sem credencial de teste] A validação remota autenticada fica fora desta change;
  Mitigação: contrato, testes simulados e compile.
- [Datas] A conversão para UTC pode divergir do fuso local; Mitigação: exibir UTC explícito
  e manter o backend como fonte de verdade.

## Migration Plan

1. Adicionar o contrato e os testes unitários.
2. Adicionar campos/handlers no `State` e liberar a seção na navegação.
3. Renderizar listagem, detalhe e avanço de status; adicionar estilos.
4. Documentar as três variáveis em `.env.example` e configurá-las no ambiente local.
5. Rodar testes, `openspec validate --all --strict`, `git diff --check` e `reflex compile`;
   restaurar `reflex.lock`.
6. Arquivar a change e atualizar roadmap/handoff. Sem publicação Xano.

Rollback: remover a seção da navegação e o bloco de renderização; os endpoints publicados e
as variáveis podem permanecer sem afetar as demais telas.

## Open Questions

- Nenhuma bloqueante. A tela consome somente o contrato já publicado na C3.
