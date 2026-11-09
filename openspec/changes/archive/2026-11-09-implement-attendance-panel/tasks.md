## 1. Contrato e configuração

- [x] 1.1 Criar `voltix/internal_attendances.py` com `Attendance`, `ATTENDANCE_STATUSES`, `attendance_filters`, `attendance_record`, `attendance_page` e `status_result` — verificação: testes unitários do módulo passam
- [x] 1.2 Validar exatamente `{items, page, per_page, total_items, total_pages}`, o registro de 10 campos e a resposta de status `{atendimento_id, status_anterior, status_atual, alterado}` — verificação: testes rejeitam campos extras, status inválido, `pedido_id` inválido e totais inconsistentes
- [x] 1.3 Reutilizar `positive_int`, `bounded_read` e `customer_date_display` de `internal_customers` e formatar datas em UTC — verificação: testes cobrem data em milissegundos, ISO e valor inválido
- [x] 1.4 Documentar `XANO_INTERNAL_ATTENDANCES_URL`, `XANO_INTERNAL_ATTENDANCE_DETAILS_URL` e `XANO_INTERNAL_ATTENDANCE_STATUS_URL` em `.env.example` sem valores — verificação: nomes presentes e nenhum segredo exposto

## 2. Estado e handlers

- [x] 2.1 Adicionar ao `State` campos de listagem, filtros, página, totais, mensagem, geração, detalhe, criação, edição e status — verificação: `reflex compile` sem erros
- [x] 2.2 Implementar `load_internal_attendances` com validação local de filtros, leitura server-side e descarte por geração/token/usuário — verificação: testes simulados confirmam gravação apenas da resposta atual e filtro inválido sem requisição
- [x] 2.3 Implementar `select_internal_attendance` e `close_internal_attendance` com validação de id, `notfound` e descarte de seleções obsoletas — verificação: testes cobrem sucesso, ausência e resposta atrasada
- [x] 2.4 Implementar `create_internal_attendance` enviando somente `cliente_id`, `pedido_id`, `assunto`, `descricao` e `data_atendimento` válidos — verificação: teste confirma ausência de `usuario_interno_id`/`status` e recarga após sucesso
- [x] 2.5 Implementar `save_internal_attendance` somente para `ABERTO`/`EM_ATENDIMENTO` enviando apenas `assunto`, `descricao` e `data_atendimento` — verificação: teste confirma bloqueio de registro encerrado e vínculos não enviados
- [x] 2.6 Implementar `change_internal_attendance_status` validando alvo e status atual e tratando `accessdenied`/`badrequest` — verificação: testes cobrem `EM_ATENDIMENTO`, finalização, cancelamento, repetição e transição inválida
- [x] 2.7 Tratar 401/403 limpando sessão, listagem, detalhe e filtros; demais erros com mensagem genérica — verificação: testes cobrem expiração de sessão e falha de rede

## 3. Interface e navegação

- [x] 3.1 Liberar `atendimentos` em `select_internal_section` para FUNCIONARIO e ADMINISTRADOR e adicionar o item à navegação lateral — verificação: teste confirma funcionário com Clientes e Atendimentos e sem seções administrativas
- [x] 3.2 Renderizar listagem com filtros `cliente_id`/`status`, total, tabela e paginação anterior/próxima — verificação: inspeção de código e `reflex compile`
- [x] 3.3 Renderizar formulário de criação com validação local e estados de sucesso, erro e carregamento — verificação: `reflex compile` e revisão dos `aria_label`/rótulos
- [x] 3.4 Renderizar detalhe com vínculos somente leitura, edição condicionada ao status e mensagens de imutabilidade — verificação: `reflex compile` e revisão dos fluxos
- [x] 3.5 Renderizar controles de status limitados por status, responsável e papel — verificação: teste confirma que funcionário não responsável não vê finalizar/cancelar
- [x] 3.6 Adicionar estilos `vx-attendance` em `assets/voltix-internal.css` reutilizando a linguagem de `vx-customers`/`vx-history` — verificação: revisão visual desktop e quebra em tela estreita

## 4. Verificação e encerramento

- [x] 4.1 Rodar `python -m unittest discover -s tests -q` — verificação: suíte completa aprovada
- [x] 4.2 Rodar `openspec validate implement-attendance-panel --strict` e `openspec validate --all --strict` — verificação: todos os itens válidos
- [x] 4.3 Rodar `reflex compile` restaurando `reflex.lock` antes de qualquer commit — verificação: `git status` sem alterações em `reflex.lock`
- [x] 4.4 Revisar o diff e registrar evidência local — verificação: `git diff --check` limpo e evidência em `evidence/`
- [x] 4.5 Arquivar a change e atualizar `docs/roadmap-changes.md` e `docs/AI_AGENT_HANDOFF.md` — verificação: C7 UI concluída e documentação consistente
- [x] 4.6 Commit focado e push somente com autorização explícita — verificação: `git log --oneline -1` e `git status --short --branch`
