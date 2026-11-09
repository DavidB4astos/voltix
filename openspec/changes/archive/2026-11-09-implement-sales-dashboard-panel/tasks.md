## 1. Contrato e configuração

- [x] 1.1 Criar `voltix/internal_sales.py` com `SalesDashboard`, `DailySales`, `dashboard_filters` e `sales_dashboard` — verificação: testes unitários do módulo passam
- [x] 1.2 Validar filtros `from`/`to` opcionais em `YYYY-MM-DD`, datas reais, ordem ascendente e limite de 366 dias, retornando apenas as chaves informadas — verificação: testes cobrem padrão, intervalo explícito, data inválida, ordem invertida e excesso de dias
- [x] 1.3 Validar a resposta exata com `{periodo, faturamento, pedidos, ticket_medio, status_incluidos, serie_diaria}`, `periodo {inicio, fim, timezone}`, `timezone="UTC"` e os quatro status na ordem aprovada — verificação: testes rejeitam campo extra, ausente, tipo inválido e status divergente
- [x] 1.4 Validar a série diária `{data, faturamento, pedidos}` com datas crescentes e dentro do período, coerência de totais, ticket médio e caso vazio (`pedidos=0`) — verificação: testes rejeitam data duplicada/decrescente, soma divergente, ticket incompatível e série não vazia sem Pedidos
- [x] 1.5 Documentar `XANO_INTERNAL_SALES_URL` em `.env.example` sem valor — verificação: nome presente e nenhum segredo exposto

## 2. Estado e handlers

- [x] 2.1 Adicionar ao `State` campos de Dashboard (dados, `from`/`to` aplicados e digitados, carregamento, mensagem, geração) — verificação: `reflex compile` sem erros
- [x] 2.2 Implementar `load_internal_dashboard` com validação local dos filtros, leitura server-side do token interno e descarte por geração/token/usuário — verificação: testes confirmam gravação apenas da resposta atual e filtro inválido sem requisição
- [x] 2.3 Implementar `apply_internal_dashboard_filters` e `clear_internal_dashboard_filters` normalizando os limites e recarregando o período — verificação: testes confirmam valores aplicados, limpeza para o padrão e descarte de resultados anteriores
- [x] 2.4 Tratar `401`/`403` limpando sessão e Dashboard, `400` informando período inválido com sessão preservada e falhas genéricas sem dados parciais — verificação: testes cobrem expiração, período rejeitado e erro de rede
- [x] 2.5 Atualizar `select_internal_section` para aceitar `dashboard` nos dois papéis, disparar a carga ao trocar e incluir `_clear_internal_dashboard` nos fluxos de logout/troca de identidade — verificação: testes de navegação e de limpeza de sessão passam

## 3. Interface e navegação

- [x] 3.1 Adicionar Dashboard à navegação (primeira seção, ícone próprio), título/descrição no shell e composição da seção — verificação: inspeção de código e `reflex compile`
- [x] 3.2 Renderizar cartões de faturamento, Pedidos e ticket médio, período aplicado e status incluídos com rótulos legíveis — verificação: `reflex compile` e revisão dos rótulos/`aria_label`
- [x] 3.3 Renderizar a série diária em tabela crescente e os estados de carregamento, vazio, erro e sessão em `role=status` — verificação: `reflex compile` e revisão dos fluxos
- [x] 3.4 Adicionar estilos `vx-dashboard` em `assets/voltix-internal.css` reutilizando a linguagem de `vx-customers`/`vx-orders` — verificação: revisão visual desktop e quebra em tela estreita

## 4. Verificação e encerramento

- [x] 4.1 Criar `tests/test_internal_sales.py` cobrindo contrato, filtros, handlers, navegação, 401/403/400 e descarte de respostas obsoletas — verificação: suíte nova aprovada
- [x] 4.2 Rodar `python -m unittest discover -s tests -q` — verificação: suíte completa aprovada
- [x] 4.3 Rodar `reflex compile` restaurando `reflex.lock` antes de qualquer commit — verificação: `git status` sem alterações em `reflex.lock`
- [x] 4.4 Rodar `openspec validate implement-sales-dashboard-panel --strict`, `openspec validate --all --strict` e `git diff --check` — verificação: tudo válido e diff limpo
- [x] 4.5 Registrar evidência local, atualizar `docs/roadmap-changes.md` e `docs/AI_AGENT_HANDOFF.md` e arquivar a change — verificação: documentação consistente e change arquivada
- [x] 4.6 Commit focado e push somente com autorização explícita — verificação: `git log --oneline -1` e `git status --short --branch`
