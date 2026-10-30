## Scope
Avaliar somente como executar uma comparação entre joins sem type e com type inner. Não interpretar SQL simulado local, mocks de respostas ou parser como prova do runtime Xano.
## Findings
CLI instalada 1.2.0 possui sandbox, unit_test e workflow_test. sandbox get cria ambiente caso não exista; por isso não foi invocado como se fosse uma consulta neutra. A documentação oficial do Developer MCP declara que sandbox automático exige plano pago e não pode ser provisionado no Free build.
workspace list no perfil voltix retornou somente o workspace 147981. O usuário confirmou não possuir outro ambiente. A listagem não é uma auditoria de todos os planos/contas; não se afirma que criar outro ambiente gratuito seja impossível.
Decisão: não criar nem contratar recursos, não alterar licença, não usar branch como prova de isolamento de dados, não publicar tabelas/queries temporárias no workspace atual. E6 preservada. A execução de runtime permanece adiada; documentação desta avaliação pode ser concluída e arquivada separadamente.
## Verification
Conferir ajuda da CLI e documentação oficial; lista de ambientes; fixtures sintéticas sem credenciais ou registros reais. Validar OpenSpec documental. Não repetir suíte funcional porque nada executável muda. Não marcar o teste remoto como passou.
## References
- https://github.com/xano-inc/xano-developer-mcp/blob/main/src/cli_docs/topics/sandbox.ts — paid plans only; Free build cannot provision sandbox.
- https://github.com/xano-inc/xano-developer-mcp/blob/main/src/xanoscript_docs/database.md — exemplos com e sem type; não estabelece nessa seção o default efetivo deste workspace.
- docs/roadmap-changes.md E6 — ambiente isolado aprovado para testes com mutações.
