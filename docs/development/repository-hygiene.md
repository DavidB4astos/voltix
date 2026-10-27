# Organização dos arquivos locais — 27/10/2026

## Versionado
- Configuração opencode.json e comandos/skills OpenSpec em .opencode: sem chaves ou tokens. Autenticar os provedores individualmente em cada computador. Esta configuração não concede acesso pago ou ilimitado aos modelos.
- opencode.json preserva a configuração MCP existente: Chrome DevTools habilitado; Playwright e Figma desabilitados. Servidores locais usam npx.cmd (Windows), com pacotes @latest. A revisão foi documental/estrutural; servidores não foram iniciados nem dependências instaladas por esta organização. Revisar permissões ao usar ferramentas; não é exigência para executar o Voltix.
- Histórico adiado de baixa de estoque e histórico substituído de correção de imagens, preservados em docs/deferred-changes e docs/superseded-changes.
- Consulta administrativa preservada como rascunho adiado; seu README registra divergências e condições de retomada. Não é funcionalidade entregue.

## Mantido somente no computador
- .env, ambientes Python, node_modules, referências não aprovadas em docs/referencias, logs e diagnósticos listados especificamente no .gitignore.
- Scripts locais fix/check/read e capturas exploratórias não são a suíte oficial; não são executados por esta organização. Permanecem disponíveis no disco.
- Cópia dos package.json e package-lock.json do experimento npm em .local-backup/2026-10-27-lockfiles, com hashes SHA-256. O bun.lock já estava ausente nessa cópia local. Os arquivos versionados reflex.lock/package.json e reflex.lock/bun.lock foram recuperados; não houve migração aprovada nem alteração de dependências instaladas.

## Skills
As seis skills Reflex/setup de .claude e .grok foram recuperadas do HEAD por autorização do usuário. Essa restauração elimina exclusões locais, sem introduzir alterações nos arquivos versionados.

## Limites
Não foi feita limpeza destrutiva de logs/ambientes/referências, alteração de UI, deploy no Xano ou validação funcional do rascunho administrativo. A organização do repositório não significa conclusão das funcionalidades adiadas.

As importações executadas pela suíte regeneraram os arquivos locais de reflex.lock. Uma segunda cópia foi guardada em .local-backup/2026-10-27-lockfiles/after-tests e o baseline foi recuperado novamente após os testes. A cópia inicial também permanece preservada.

O servidor Reflex em execução também voltou a regenerar os lockfiles durante a organização. Essa alteração gerada não foi incluída nos commits; não usar skip-worktree/assume-unchanged para escondê-la. Para manter o baseline restaurado, encerrar o servidor no terminal do usuário e recuperar novamente os dois arquivos versionados antes de reiniciar. O package-lock local continua sendo material do experimento npm, não uma migração aprovada.
