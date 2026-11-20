## 1. Preparação e frente 01 — Runtime e telas

- [x] 1.1 Verificar instâncias locais ativas nas portas 3090, 3091 e 3092 com `Invoke-WebRequest`
- [x] 1.2 Inspecionar rotas públicas e internas acessíveis em 1280/768/375 px via Chrome DevTools MCP (sem mutações, sem submeter pedido/pagamento e sem resetar senha)
- [x] 1.3 Registrar evidências e limitações de sessão em `evidence/01-runtime.md`

## 2. Frente 02 — Código, specs e gates

- [x] 2.1 Conferir coerência entre `AGENTS.md`, `docs/`, `openspec/specs/` e código-fonte do frontend/testes
- [x] 2.2 Executar `python -m unittest discover -s tests -q`, `reflex compile` (restaurando `reflex.lock/*` em seguida), `git diff --check` e `openspec validate --all --strict`
- [x] 2.3 Registrar saídas e verificações em `evidence/02-code-specs-gates.md`

## 3. Frente 03 — Xano somente leitura

- [x] 3.1 Executar `xano workspace pull` sem `--env` nem `--records` em área isolada de comparação, espaçando leituras conforme limite Free (10 req/20 s)
- [x] 3.2 Comparar contratos locais e publicados sem executar `push`, `POST`, `PATCH` ou `DELETE`, preservando pendências conhecidas apenas como registro
- [x] 3.3 Registrar evidências em `evidence/03-xano-readonly.md`

## 4. Frente 04 — Segurança e autorização

- [x] 4.1 Verificar regras de autenticação e autorização no backend (XanoScript) para `CLIENTE`, `FUNCIONARIO` e `ADMINISTRADOR` e consistência com o frontend
- [x] 4.2 Conferir ausência de exposição de CPF sem máscara, e-mail, telefone, senha, hash, token, `.env` ou credenciais em código, respostas e evidências
- [x] 4.3 Registrar evidências em `evidence/04-security.md`

## 5. Frente 05 — Consolidação, roteiro e encerramento

- [x] 5.1 Consolidar matriz `achado → jornada → classificação → próxima ação` (`bloqueador de demo`, `pós-entrega`, `limitação documentada`, `falso positivo`) e roteiro de ensaio com o que NÃO deve ser executado em `evidence/05-demo-readiness.md`
- [x] 5.2 Executar gates finais (`unittest`, `reflex compile` + restauração de `reflex.lock/*`, `git diff --check`, `openspec validate --all --strict`)
- [x] 5.3 Arquivar a change com `openspec archive audit-delivery-readiness -y --skip-specs` e atualizar `docs/AI_AGENT_HANDOFF.md` e `docs/roadmap-changes.md` com links para as evidências
- [x] 5.4 Apresentar working tree revisável, resumo final e solicitar autorização explícita antes de qualquer `git commit` ou `git push`
