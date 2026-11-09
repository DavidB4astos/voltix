## 1. Contrato e configuração

- [x] 1.1 Criar `voltix/internal_orders.py` com `OrderSummary`, `OrderCustomer`, `OrderDelivery`, `OrderPayment`, `OrderDetail`, `OrderStatusResult`, `order_filters`, `order_summary_page`, `order_detail` e `order_status_result` — verificação: testes unitários do módulo passam
- [x] 1.2 Validar a listagem exata `{items, page, per_page, items_total, page_total}` e o item exato `{id, codigo, data_pedido, status, cliente, itens_count, subtotal, valor_frete, valor_total}`, com `cliente` exatamente `{id, nome_completo}` — verificação: testes rejeitam campos extras, status inválido, totais inconsistentes, página divergente e duplicidade
- [x] 1.3 Validar o detalhe exato com `cliente {id, nome_completo, email_masked}`, `entrega` com oito campos, itens no contrato existente e `pagamento {metodo, valor, status}`; aceitar `email_masked`/endereço nulos e normalizar para "Indisponível" — verificação: testes cobrem nulos, máscara inválida e id divergente
- [x] 1.4 Validar a resposta de status `{pedido_id, codigo, status_anterior, status_atual, alterado}` e reutilizar `ORDER_STATUSES`, `positive_int`, `customer_date_display` e `order_item_record` — verificação: testes rejeitam campos extras, status inválido, `alterado` não booleano e `pedido_id` divergente
- [x] 1.5 Documentar `XANO_INTERNAL_ORDERS_URL`, `XANO_INTERNAL_ORDER_DETAILS_URL` e `XANO_INTERNAL_ORDER_STATUS_URL` em `.env.example` sem valores — verificação: nomes presentes e nenhum segredo exposto

## 2. Estado e handlers

- [x] 2.1 Adicionar ao `State` campos de listagem, busca, status aplicado/digitado, página, totais, mensagem, geração, detalhe e salvamento — verificação: `reflex compile` sem erros
- [x] 2.2 Implementar `load_internal_orders` com validação local de `q`/status/página, leitura server-side e descarte por geração/token/usuário — verificação: testes simulados confirmam gravação apenas da resposta atual e filtro inválido sem requisição
- [x] 2.3 Implementar `select_internal_order` e `close_internal_order` com validação de id, `notfound` e descarte de seleções obsoletas — verificação: testes cobrem sucesso, id divergente, ausência e resposta atrasada
- [x] 2.4 Implementar `advance_internal_order_status` calculando o único próximo alvo da sequência e recusando alvo inválido sem requisição — verificação: testes cobrem cada passo, `ENTREGUE`/`CANCELADO` sem próximo alvo e status repetido idempotente
- [x] 2.5 Restringir o avanço a `ADMINISTRADOR` no handler, mantendo o backend como autoridade — verificação: teste confirma que FUNCIONARIO não envia requisição e recebe mensagem de permissão
- [x] 2.6 Tratar `401`/`403` de leitura limpando sessão, listagem, detalhe e filtros; no status, `401` encerra a sessão, `403` mantém o estado e `400` informa transição inválida — verificação: testes cobrem expiração, negação de operação e `badrequest`
- [x] 2.7 Atualizar `select_internal_section` para aceitar `pedidos` nos dois papéis e disparar `load_internal_orders` ao trocar para a seção — verificação: testes de navegação confirmam o novo valor e a rejeição de seções administrativas pelo FUNCIONARIO

## 3. Interface e navegação

- [x] 3.1 Adicionar o item Pedidos à navegação lateral ao lado de Clientes e Atendimentos e o título/descrição no shell — verificação: inspeção de código e `reflex compile`
- [x] 3.2 Renderizar listagem com busca `q`, filtro `status`, total, tabela com Cliente/código/status/data/itens/valores e paginação anterior/próxima — verificação: `reflex compile` e revisão dos rótulos/`aria_label`
- [x] 3.3 Renderizar detalhe com Cliente e e-mail mascarado, endereço, itens, Pagamento e valores, sem CPF/telefone/senha/hash/token — verificação: inspeção de código confirma apenas os campos do contrato
- [x] 3.4 Renderizar o controle de avanço apenas para ADMINISTRADOR e apenas quando houver próximo alvo válido; mostrar o estado imutável em `ENTREGUE`/`CANCELADO` — verificação: teste de handler e inspeção das condições da UI
- [x] 3.5 Adicionar estados de carregamento, vazio, erro, sessão e mensagens em `role=status` — verificação: `reflex compile` e revisão dos fluxos
- [x] 3.6 Adicionar estilos `vx-orders` em `assets/voltix-internal.css` reutilizando a linguagem de `vx-customers`/`vx-attendance` — verificação: revisão visual desktop e quebra em tela estreita

## 4. Verificação e encerramento

- [x] 4.1 Rodar `python -m unittest discover -s tests -q` — verificação: suíte completa aprovada
- [x] 4.2 Rodar `openspec validate implement-order-panel --strict` e `openspec validate --all --strict` — verificação: todos os itens válidos
- [x] 4.3 Rodar `reflex compile` restaurando `reflex.lock` antes de qualquer commit — verificação: `git status` sem alterações em `reflex.lock`
- [x] 4.4 Revisar o diff e registrar evidência local — verificação: `git diff --check` limpo e evidência em `evidence/`
- [x] 4.5 Arquivar a change e atualizar `docs/roadmap-changes.md` e `docs/AI_AGENT_HANDOFF.md` — verificação: tela de Pedidos concluída e documentação consistente
- [ ] 4.6 Commit focado e push somente com autorização explícita — verificação: `git log --oneline -1` e `git status --short --branch`
