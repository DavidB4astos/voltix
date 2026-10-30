## Decisions
Pull novo externo ao Git, perfil voltix/workspace 147981, sem env/records/draft/verbose. Extrair somente canonical e guid dos dois grupos, sem copiar Swagger ou outros valores privados. Preservar metadados editoriais locais; sua diferença com remoto continuará explicitamente documentada.

Pacote temporário contendo somente dois descritores para dry-run; exigir atualização das duas identidades existentes, nunca criação/rename/exclusão. Não executar push real. Conferir que os endpoints configurados desses grupos usam o canonical publicado; verificar hash de .env inalterado. Nenhuma substituição global de URLs ou fixtures.
## Verification
Diff limitado aos dois descritores e documentação; 16 specs strict válidas. Testes de aplicação não precisam ser repetidos para identidade local sem alteração de runtime; conferir configuração por leitura, manifesto sanitizado e dry-run. Arquivar com limites explícitos: contratos, ordenações, schemas e outras diferenças não são resolvidos aqui.
