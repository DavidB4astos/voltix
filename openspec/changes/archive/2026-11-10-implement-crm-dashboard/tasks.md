## 1. Contrato do dashboard

- [x] 1.1 Criar `voltix/internal_crm.py` com `CrmDashboard`, os rótulos de situação e o construtor `crm_dashboard` — verificação: testes unitários do módulo passam
- [x] 1.2 Validar contagens inteiras não negativas, situações exatas (`ABERTO`, `EM_ATENDIMENTO`, `FINALIZADO`), lista recente com no máximo 10 itens, IDs únicos e vendas no contrato `SalesDashboard` — verificação: testes rejeitam contagem negativa ou booleana, situação extra/ausente e lista acima do limite
- [x] 1.3 Garantir que a lista recente não exceda o total de Atendimentos retornado — verificação: teste rejeita lista maior que o total
- [x] 1.4 Criar `tests/test_internal_crm.py` para o contrato — verificação: suíte nova aprovada

## 2. Estado e handler

- [x] 2.1 Adicionar ao `State` os campos do CRM (snapshot, carregamento, mensagem, sinalização de carga, geração) e a limpeza em `_clear_authentication_state` — verificação: testes de logout confirmam limpeza
- [x] 2.2 Implementar `_clear_internal_crm` e `_internal_crm_allowed` reutilizando a guarda interna existente — verificação: teste confirma que Cliente e interno inativo não geram requisição
- [x] 2.3 Implementar `load_internal_crm` com sete leituras sequenciais usando exclusivamente endpoints publicados, `per_page=1` para totais e `per_page=10` para recentes — verificação: teste inspeciona URLs e parâmetros enviados
- [x] 2.4 Aplicar descarte por geração, token e usuário, tudo ou nada em caso de falha, e encerramento de sessão em `401`/`403` — verificação: testes cobrem falha parcial sem números, resposta obsoleta e sessão encerrada
- [x] 2.5 Aceitar `crm` em `select_internal_section` para os dois papéis e disparar `load_internal_crm` ao entrar na seção — verificação: testes de navegação cobrem FUNCIONARIO, ADMINISTRADOR e valor desconhecido

## 3. Interface e navegação

- [x] 3.1 Adicionar CRM à navegação após Dashboard, com ícone, título e descrição no shell — verificação: inspeção de código e `reflex compile`
- [x] 3.2 Compor `internal_crm_panel` com blocos Relacionamento, Vendas no período e Últimos Atendimentos, além dos atalhos para Clientes, Atendimentos e Pedidos — verificação: `reflex compile` e revisão de rótulos/`aria_label`
- [x] 3.3 Renderizar carregamento, erro, ausência de Atendimentos e ausência de vendas em regiões anunciadas — verificação: revisão dos fluxos e teste de handlers
- [x] 3.4 Adicionar estilos `vx-crm` em `assets/voltix-internal.css` reutilizando a linguagem de `vx-dashboard`/`vx-customers`, com quebra em telas estreitas — verificação: revisão de CSS e `reflex compile`

## 4. Verificação e encerramento

- [x] 4.1 Rodar `python -m unittest discover -s tests -q` — verificação: suíte completa aprovada
- [x] 4.2 Rodar `reflex compile` e restaurar `reflex.lock` — verificação: `git status` sem alterações em `reflex.lock`
- [x] 4.3 Rodar `openspec validate implement-crm-dashboard --strict`, `openspec validate --all --strict` e `git diff --check` — verificação: tudo válido e diff limpo
- [x] 4.4 Registrar evidência local em `evidence/01-local-verification.md`, atualizar `docs/roadmap-changes.md` e `docs/AI_AGENT_HANDOFF.md` e arquivar a change — verificação: documentação consistente e change arquivada
- [ ] 4.5 Commit e push somente com autorização explícita — verificação: `git status --short --branch` e `git log --oneline -1`
