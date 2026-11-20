## Why

Antes da entrega e demonstração do Voltix, é necessário executar uma auditoria independente e verificável em worktree separado (`audit-delivery-readiness`), mantendo `main` intacta, para confirmar a prontidão do sistema nas frentes de runtime, código/specs/gates, contratos Xano somente leitura e segurança/autorização, consolidando os achados por jornada e o roteiro seguro de ensaio.

## What Changes

- Executar auditoria somente leitura em cinco frentes sequenciais, gerando evidências em `evidence/`:
  1. **`01-runtime`:** verificar instâncias locais disponíveis (portas 3090, 3091, 3092) e inspecionar rotas públicas e internas aplicáveis em 1280/768/375 px via Chrome DevTools MCP, registrando limitações de sessão (ex.: 403 conhecido no login de Cliente ou eventual ausência de sessão ADMIN) sem resetar credenciais nem submeter pedidos/pagamentos.
  2. **`02-code-specs-gates`:** conferir aderência entre `AGENTS.md`, `docs/`, OpenSpec, suíte completa (`python -m unittest discover -s tests -q`), `reflex compile` (restaurando `reflex.lock/*`), `git diff --check` e `openspec validate --all --strict`.
  3. **`03-xano-readonly`:** executar `xano workspace pull` sem `--env` nem `--records` (espaçando leituras dentro do limite Free de 10 req/20 s) e comparar contratos locais vs publicados sem nenhuma escrita.
  4. **`04-security`:** verificar autorização no backend, separação de papéis (`CLIENTE`, `FUNCIONARIO`, `ADMINISTRADOR`) e ausência de exposição de CPF, e-mail, telefone, senha, hash, token, `.env` ou credenciais.
  5. **`05-demo-readiness`:** consolidar matriz `achado → jornada → classificação → próxima ação` (`bloqueador de demo`, `pós-entrega`, `limitação documentada`, `falso positivo`) e roteiro de ensaio com o que NÃO deve ser executado.
- Após conclusão e revisão, arquivar com `openspec archive audit-delivery-readiness -y --skip-specs` e atualizar `docs/AI_AGENT_HANDOFF.md` e `docs/roadmap-changes.md` com links para a evidência.
- **Fora do escopo:**
  - Qualquer mutação no Xano (`push`, `POST`, `PATCH`, `DELETE`), publicação de endpoints ou alteração de registros reais.
  - Varredura de 23 detalhes de produto (risco de HTTP 429), compra E2E, upload de imagem, importação real, inativação, exclusão, reset de senha ou e-mail real.
  - Resolução de pendências Xano conhecidas (joins de carrinho/checkout, defaults de schema, upload 403, `tmp_rollback_test`, prova isolada bloqueada por E6).
  - Alteração de código funcional, testes ou specs consolidadas (`skip_specs: true`).
  - Commit ou push sem autorização explícita do usuário.

## Capabilities

### New Capabilities

- Nenhuma. Change de auditoria e documentação sem alteração de comportamento.

### Modified Capabilities

- Nenhuma. `skip_specs: true` definido em `.openspec.yaml`.

## Impact

- **Worktree:** `.worktrees/audit-delivery-readiness` (branch `audit-delivery-readiness`), preservando `main` intacta.
- **Artefatos:** `proposal.md`, `design.md`, `tasks.md`, `.openspec.yaml` e `evidence/01-runtime.md` .. `evidence/05-demo-readiness.md`, além da atualização final de `docs/AI_AGENT_HANDOFF.md` e `docs/roadmap-changes.md` no encerramento.
- **Código e specs:** nenhuma alteração em código de aplicação, testes ou `openspec/specs/`.
