## Why

A administração da Voltix precisa consultar clientes cadastrados para gestão de relacionamento, histórico de compras e atendimentos. Atualmente não há uma tela administrativa dedicada para listagem e busca de clientes no painel interno, o que torna a operação manual e propensa a erros. Esta Change responde à necessidade de centralizar a consulta de clientes com filtros e preservando a segurança de dados sensíveis.

## What Changes

- Tela administrativa de listagem de clientes no painel interno, com pesquisa por nome e e-mail.
- Filtro por status (ATIVO/INATIVO).
- Colunas exibidas: ID, nome, e-mail (mascarado), telefone, data de cadastro, status.
- Botão "Ver detalhes" que abre modal com informações completas (sem senhas/tokens).
- Autorização restrictiva: apenas perfis `ADMINISTRADOR` ativos podem acessar.
- Endpoint GET /admin/customers (XanoScript) com parâmetros opcionais `q` (busca nome/e-mail) e `status`.
- Não alterar endpoints existentes, apenas adicionar novo endpoint de leitura administrativa.
- Preservar compatibilidade com Xano Free (limite de requisições, 429 handling).

## Capabilities

### New Capabilities

- `admin-customers`: consulta administrativa de clientes com filtros e máscara de e-mail.

### Modified Capabilities

Nenhuma. Este endpoint é novo e não altera specs existentes.

## Impact

- **Backend**: `xano/api/admin/customers_GET.xs` - novo endpoint de leitura administrativa de clientes, com input `status?` e `q?`, resposta sem senhas/tokens, máscara de e-mail.
- **Frontend**: Painel administrativo (já existente em `/admin`) recebendo novo endpoint; tabela de listagem; modal de detalhes; evento de busca; respeitar perfil ADMINISTRADOR.
- **Segurança**: Máscara de e-mail (apenas primeiros 3 caracteres + "*****"); nenhum dado sensível exposto; autorização via profile ADMINISTRADOR ativo.
- **Documentação**: specs em `openspec/specs/admin-customers/spec.md`; delta nas specs se houver mudança de requisito existente.
- **Limites**: não alterar dependências/lockfiles; respeitar limites Xano Free.

## Impacto Restrito

- Este Change **não** altera: endpoints de cliente público, carrinho, checkout, auth, admin de produtos/categorias, carrinho, checkout, CRUD de produtos, upload de imagem, regras de estoque, fluxo de pedidos.
- **SKU, preço, variação, estoque** permanecem fora do escopo.
- **Histórico de pedidos e atendimentos** permanecem fora do escopo (já cobertos por C2, C7 respectivamente).