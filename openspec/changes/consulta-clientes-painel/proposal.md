## Why
A operação interna não possui consulta dedicada de clientes integrada ao frontend. O rascunho consulta-clientes-admin foi adiado por falhas de schema, filtros, autorização e privacidade. A C4 do roadmap prevê leitura para FUNCIONARIO e ADMINISTRADOR ativos.

## What Changes
- Propor consulta interna de lista e detalhe, somente leitura, com busca por nome/e-mail, status e paginação limitada.
- Autorizar FUNCIONARIO e ADMINISTRADOR ativos no Xano; negar visitante, Cliente e interno inativo.
- Usar campos locais reais: CLIENTE.id, nome_completo, email, telefone, cpf, status, created_at. Confirmar metadados reais antes de publicar.
- Retornar somente campos aprovados, com e-mail/telefone mascarados e CPF mascarado apenas no detalhe. Nunca credenciais, endereço ou dados de pedidos nesta C4.
- Integrar uma área Clientes à superfície interna /interno, mantendo a sessão de Cliente separada.

## Capabilities
### New Capabilities
- internal-customers: consulta interna de clientes com autorização, minimização, filtros, paginação e detalhe.
### Modified Capabilities
Nenhuma; complementa o acesso interno existente sem alterar sua autenticação.

## Impact
Futura implementação: novo grupo Xano Voltix Internal Customers com GET customers e GET customers/{customer_id}; módulo Python dedicado para contrato/normalização, integração de State e UI Reflex, testes e exemplos de configuração sem segredos. Não copiar/publicar o draft antigo. Aprovação desta proposta deve preceder a implementação do contrato proposto.

Fora do escopo: editar/inativar/excluir clientes, revelar contatos completos, exportação, histórico de compras, atendimentos, dashboard, pedidos, estoque, criação de tabelas, mudanças de plano ou autenticação, dependências e mobile como foco de design. Não consultar dados pessoais reais para evidências.
