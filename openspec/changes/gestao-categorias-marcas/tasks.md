## 1. Estruturas de Categoria e Marca no Xano

- [x] 1.1 Criar e validar o schema Xano de Categoria com nome obrigatório e único, descrição opcional, status `ATIVO`/`INATIVO` com novo registro ativo e campos de auditoria; confirmar que nenhuma entidade fora do escopo foi alterada
- [x] 1.2 Criar e validar o schema Xano de Marca com nome obrigatório e único, descrição opcional, status `ATIVO`/`INATIVO` com novo registro ativo e campos de auditoria; confirmar que nenhuma entidade fora do escopo foi alterada

## 2. Operações e autorização no backend

- [x] 2.1 Criar operações Xano para listar, criar, editar e alterar status de Categoria; validar nome e unicidade também contra registros inativos, preservar registros existentes em falhas e confirmar que não há exclusão definitiva
- [x] 2.2 Criar operações Xano para listar, criar, editar e alterar status de Marca; validar nome e unicidade também contra registros inativos, preservar registros existentes em falhas e confirmar que não há exclusão definitiva
- [x] 2.3 Exigir sessão válida, usuário `ATIVO` e perfil `ADMINISTRADOR` em cada operação de Categoria e Marca; testar rejeição no backend para FUNCIONARIO, sessão ausente/inválida e usuário inativo sem leitura ou alteração de dados

## 3. Integração server-side no State Reflex

- [x] 3.1 Configurar os destinos Xano de gestão por ambiente e implementar chamadas HTTP server-side reutilizando o padrão existente; verificar erro explícito para configuração ausente e ausência de destino privado ou credencial no código versionado
- [x] 3.2 Implementar no State a listagem, criação, edição e mudança de status para Categoria e Marca usando `_auth_token` somente no backend; testar sucesso, validações, autorização negada, falha HTTP/rede e ausência de exposição do token

## 4. Interface interna de gestão

- [x] 4.1 Adicionar seções simples de Categoria e Marca à área interna existente, visíveis somente para ADMINISTRADOR; verificar que FUNCIONARIO continua sem controles e que nenhuma página protegida é renderizada sem sessão validada
- [x] 4.2 Conectar formulários e listagens aos eventos do State para criar, editar, inativar e reativar; verificar nomes/descrições/status, campos obrigatórios, loading, mensagens de erro e que nenhuma ação de exclusão definitiva é oferecida

## 5. Verificação ponta a ponta e escopo

- [x] 5.1 Executar `python -m py_compile voltix/voltix.py`, `reflex compile`, validação dos XanoScript alterados e `git diff --check`; resolver somente falhas desta Change
- [x] 5.2 Executar o fluxo com ADMINISTRADOR ativo para listar, criar, editar, inativar e reativar Categoria e Marca; verificar unicidade de nomes e persistência dos dados após recarregar as listas
- [x] 5.3 Validar chamadas reais ou testes automatizados suficientes para FUNCIONARIO, sessão ausente/inválida e usuário inativo; confirmar rejeição no backend, ausência de dados/alterações e mensagens seguras na interface
- [x] 5.4 Auditar o escopo final: somente gestão de Categoria e Marca; nenhum Produto, relação com Produto, catálogo público, Cliente, carrinho, pedido, dashboard ou CRM; confirmar que nenhuma credencial ou token foi versionado
