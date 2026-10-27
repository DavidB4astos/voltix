## Decisions
- Usar padrões específicos de arquivos de diagnóstico na raiz; não ignorar genericamente todos os scripts Python ou todos os arquivos de texto.
- Preservar arquivos excluídos de skills via git restore, autorizado pelo usuário.
- Guardar cópia de package.json e package-lock.json locais antes de recuperar o baseline de reflex.lock. A migração npm não é aprovada como atualização de dependências neste escopo.
- Manter os artefatos administrativos originais intactos dentro de docs/deferred-changes, acompanhados de uma revisão que prevalece sobre alegações anteriores de conclusão. Nenhum deploy.
- Preservar bytes da documentação histórica movida; validar checksums.

## Verification
Validação OpenSpec desta organização; comparação dos backups; restauração das skills e locks; checagem de arquivos ignorados e dos arquivos staged; busca de padrões conhecidos de credenciais sem imprimir valores. Suíte existente como controle, sem confundi-la com testes do endpoint administrativo.

## Risks
O rascunho administrativo não possui frontend integrado nem prova de funcionamento no Xano; isso deve permanecer explícito. Configuração MCP existente pode executar pacotes por npx; documentar instalação opcional e revisar permissões. Não registrar credenciais de autenticação.
