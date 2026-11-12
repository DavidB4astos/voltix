## 1. Preparação

- [x] 1.1 Localizar no código todos os links de texto "Carregar / atualizar …" no workspace — verificação: ocorrências em `voltix.py` (`vx-customers__refresh`)
- [x] 1.2 Confirmar que handlers, guards e permissões não mudam; somente o elemento de renderização/estilo — verificação: escopo conferido no proposal/design
- [x] 1.3 Confirmar que `.env` local recebeu as URLs internas canônicas — verificação: `XANO_INTERNAL_SALES_URL` etc. presentes

## 2. Hierarquia de ações unificada

- [x] 2.1 Trocar os links textuais de atualização/refresh pelo mesmo botão usado nas ações primárias, preservando rótulos, handlers e `disabled` — verificação: todos compartilham `.vx-customers__refresh`, agora com tratamento de botão secundário (altura 40px, borda, hover)
- [x] 2.2 Garantir que ações destrutivas mantêm o tratamento destrutivo e confirmações existentes — verificação: nenhuma classe de refresh/atualização alterada para primário/destrutivo

## 3. Densidade, sidebar e pílula de sessão

- [x] 3.1 Compactar `.vx-internal__nav-item` (padding, tipografia) e reforçar `is-selected` no `assets/voltix-internal.css` — verificação: itens compactos com estado ativo `#123c4f` sobre borda `#2c6479`
- [x] 3.2 Reduzir altura/padding de painéis de erro, aviso e empty states sem remover mensagens — verificação: `.vx-customers__feedback` 26/22px, `.vx-orders__empty-detail`/`.vx-attendance__empty-detail` 96px, `.vx-taxonomy__notice` menor
- [x] 3.3 Ajustar tabelas (`.vx-internal__content table`) para legibilidade consistente — verificação: fonte 12px; overflow-x auto nas tabelas com min-width
- [x] 3.4 Substituir a pílula "Acesso interno" por indicador "Sessão ativa" no `internal_workspace_shell` — verificação: pílula antiga ausente; indicador novo visível em sessão real

## 4. Responsividade

- [x] 4.1 Verificar/fortalecer empilhamento do workspace em ≤800px (sidebar acima do conteúdo, nav com scroll/wrap) — verificação: media query preservada; overflow-x nas tabelas adicionado
- [x] 4.2 Verificar tabelas e formulários em 768/1280 px — verificação: `.vx-crm__table`/`.vx-team__table` com `min-width` e containers com `overflow-x:auto`

## 5. Testes

- [x] 5.1 Adicionar testes estruturais: ausência da pílula redundante, presença do indicador de sessão, refresh actions como botão consistente — verificação: `tests/test_internal_workspace_design.py` criado
- [x] 5.2 Preservar suíte existente — verificação: 428 testes verdes
- [x] 5.3 `openspec validate refine-internal-workspace --strict` — verificação: válido

## 6. Verificação e encerramento

- [x] 6.1 `reflex compile` — verificação: `compile --dry` OK
- [x] 6.2 Servidor local e sessão funcional somente leitura (login manual) — verificação: desktop 1280 px — sidebar compacta, pílula "Sessão ativa", botões de atualização como botões, estados de erro/vazio compactos; sem overflow. Ressalva: os painéis de dados exibem erro de carregamento no ambiente local (as leituras autenticadas aos endpoints internos nunca foram testadas de ponta a ponta — limitação registrada; fora do escopo desta change). Mobile (375 px) verificável apenas por CSS estático (viewport emula contexto novo e encerra a sessão)
- [x] 6.3 `git diff --check` e restaurar `reflex.lock/*` — verificação: árvore limpa
- [x] 6.4 `openspec validate --all --strict` — verificação: todas as specs válidas
- [x] 6.5 Sincronizar specs, arquivar e atualizar docs (`docs/roadmap-changes.md`, `docs/AI_AGENT_HANDOFF.md`) — verificação: diretório em `openspec/changes/archive/2026-11-12-refine-internal-workspace/`
- [ ] 6.6 Commit/push somente com autorização explícita — verificação: árvore limpa e sincronizada com `origin/main`
