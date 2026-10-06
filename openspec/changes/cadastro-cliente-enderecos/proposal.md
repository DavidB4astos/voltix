## Why

A Voltix precisa de identidade autenticada de Cliente e endereços próprios antes de implementar compras. A estrutura `CLIENTE` existente é legada e incompleta em relação ao Domain Model, e suas rotas genéricas não aplicam isolamento por proprietário; esta Change a estende preservando dados e caminhos existentes, enquanto estabelece autenticação e autorização próprias para Cliente.

## What Changes

- Estender cuidadosamente a tabela Xano `CLIENTE` com os atributos do Domain Model, credenciais protegidas, status `ATIVO`/`INATIVO` e unicidade de CPF/e-mail entre Clientes, preservando campos e dados legados.
- Implementar cadastro e login de Cliente, sessão independente de `UsuarioInterno`, consulta/edição de seus próprios dados e bloqueio de Cliente inativo.
- Criar persistência e operações de Endereco com os campos definidos no Domain Model, escopo obrigatório ao Cliente autenticado e regras de endereço principal, status e preservação quando houver referência em Pedido.
- Preservar caminhos e métodos das rotas legadas `DB_XANO_BASTOS/cliente`, endurecendo autorização, escopo do registro e projeção de campos; impedir que operações genéricas alterem credenciais ou CPF.
- Encaminhar ações da interface Reflex à lógica State/Python, que realiza chamadas HTTP server-side ao Xano.

Ficam fora do escopo: recuperação de senha, exclusão de Cliente, carrinho, checkout, pedidos, pagamento, CRM, alteração das funções administrativas, gestão de `UsuarioInterno` e migração destrutiva de dados legados.

## Capabilities

### New Capabilities

- `customer-access`: Cadastro, autenticação, sessão e acesso do Cliente aos próprios dados, independente de `UsuarioInterno`.
- `customer-addresses`: Cadastro, consulta, edição, status e remoção segura dos Endereços próprios do Cliente.

### Modified Capabilities

Nenhuma spec consolidada existente cobre essas capacidades; os contratos serão novos.

## Impact

- Afeta a tabela existente `CLIENTE` e suas rotas sob `DB_XANO_BASTOS/cliente`; preserva os caminhos legados, mas substitui acesso genérico por autorização de Cliente e operações com campos permitidos.
- Adiciona tabela `Endereco` e endpoints Xano/XanoScript de autenticação, identidade e gestão de endereços.
- Acrescenta fluxos independentes de Cliente ao State e às rotas públicas Reflex; não altera `user`, login interno, gestão administrativa ou catálogo.
- Requer auditar dados legados antes de aplicar índices únicos ou migrar credenciais; conflitos não serão resolvidos por sobrescrita ou exclusão automática.
- Não adiciona dependências nem integrações externas.
