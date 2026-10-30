## Decisions
Snapshot novo externo ao Git, sem records/env/draft/verbose. Preservar grupos e GUIDs existentes. A implementação local de proteção já existe; não reescrever handlers ou adicionar endpoints.

Allowlist de produtos: id, nome, descricao, especificacoes_tecnicas, imagem_principal, categoria_id, marca_id, status, created_at, updated_at. Variações: id, produto_id, nome_ou_descricao, sku, preco, quantidade_disponivel, status, created_at, updated_at. Usuário de autorização: somente id/role/status. Não restringir respostas ao status ATIVO: a manutenção deve continuar mostrando produtos e variações inativos.

Sort nome asc e sku asc, conforme fonte local. Não introduzir desempate/paginação ou afirmar ordenação estável para nomes iguais. Erros de acesso explícitos; mensagens podem mudar para as já usadas no contrato local. Auth user e verificação de Administrador ativo permanecem.

Pacote somente duas queries; sem metadados de grupo/tabelas/records/env. Dry-run deve mostrar exatamente duas atualizações; apresentar revisão antes de publicação autorizada. Sem --force/--sync/--delete/--records/--env/--no-transaction.
## Verification
Testes existentes e regressão focada da allowlist/ordenamento/ausência de escrita; conferir compatibilidade dos campos com o parser Reflex. Hash/GUID do pacote. Após publicação autorizada: pull e comparação, verificar ausência de alterações fora do escopo e negativas anônimo/token inválido, sem salvar corpos privados. Leituras positivas autenticadas dependem de conta de teste e devem ser documentadas conforme executadas, não presumidas. Não executar mutações para conferir GET.
