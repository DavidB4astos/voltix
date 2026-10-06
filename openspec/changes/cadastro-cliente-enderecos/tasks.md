## 1. Schema e compatibilidade legada

- [x] 1.1 Auditar no Xano autorizado a tabela `CLIENTE`, índices, dados que possam conflitar com CPF/e-mail únicos e referências legadas de Endereco/Pedido; registrar achados sem editar dados e bloquear migração destrutiva ou exclusão física se houver referências não verificáveis.
- [x] 1.2 Estender a tabela existente `CLIENTE` com campos do Domain Model, senha protegida, status e índices de unicidade, preservando todos os campos legados; validar XanoScript e verificar que `user` e seus campos/índices não mudaram.
- [x] 1.3 Criar a tabela `endereco` com atributos do Domain Model, vínculo ao Cliente e status; validar XanoScript e confirmar que não foram introduzidas entidades ou regras de Pedido.

## 2. Autenticação e APIs Xano

- [x] 2.1 Criar endpoints de cadastro, login e identidade de Cliente com token associado a `CLIENTE`, status `ATIVO`, unicidade CPF/e-mail entre Clientes e respostas sem credenciais; validar XanoScript e testar credenciais válidas, inválidas, duplicidade e separação de `user`.
- [x] 2.2 Preservar caminhos e verbos das rotas legadas `DB_XANO_BASTOS/cliente`, substituindo `dblink`/escrita genérica por cadastro explícito e operações autenticadas owner-scoped, com projeções seguras e DELETE de Cliente rejeitado; validar XanoScript e testar ausência de acesso anônimo, IDOR e alteração de CPF/credenciais.
- [x] 2.3 Criar endpoints autenticados para listar, criar, editar, inativar/reativar e remover Endereços próprios; garantir máximo de um principal por Cliente, limpar principal ao inativar e bloquear remoção com referência a Pedido; validar XanoScript e testar propriedade, transação de principal e preservação histórica.

## 3. State e sessão Reflex

- [x] 3.1 Configurar URLs Xano por ambiente e implementar cadastro/login/identidade/logout em State/Python com token separado de `UsuarioInterno`; testar que as chamadas são server-side, que tokens não são misturados e que erros não criam sessão.
- [x] 3.2 Implementar no State as operações de Endereco vinculadas à sessão de Cliente, atualizando estado somente após confirmação do backend; testar falhas HTTP/rede e que chamadas não enviam ID de proprietário fornecido pela interface.

## 4. Interface Cliente

- [x] 4.1 Criar fluxo Reflex independente de `UsuarioInterno` para cadastro, login, identidade e logout de Cliente; verificar estados de sucesso/erro sem renderizar senha, hash ou token e confirmar que falha de autenticação não revela área autenticada.
- [x] 4.2 Criar interface para listar, cadastrar, editar, tornar principal, inativar/reativar e remover Endereços próprios; verificar apresentação de endereço principal, ausência de principal após inativação e mensagens de falha sem sucesso simulado.

## 5. Verificação final

- [x] 5.1 Executar testes automatizados para cadastro, CPF/e-mail únicos, login, sessão ativa/inativa, separação Cliente/UsuarioInterno, proteção das rotas legadas, isolamento de perfil/endereço, endereço principal e remoção histórica; confirmar ausência de carrinho, pedidos, pagamento, CRM e mudanças administrativas.
- [ ] 5.2 Compilar a aplicação Reflex, validar XanoScript da Change e executar validação OpenSpec estrita; validar o E2E no Xano autorizado sem criar dados desnecessários, ou registrar explicitamente qualquer bloqueio externo sem alegar E2E não executado.

### Registro da auditoria prévia

- Workspace Xano autorizado consultado em modo somente leitura: `CLIENTE` está com `auth = false`, campos legados `USER_ID`, `CELULAR_CLIENT`, `cpf` e `status_cliente_id`, e índices `primary(id)` e `btree(created_at)`.
- A tabela `CLIENTE` não possui campo de e-mail e contém zero registros; portanto, não há conflitos de CPF/e-mail nos dados atuais. Nenhum dado foi alterado ou exibido.
- O workspace não contém tabelas `Endereco`/`Pedido` nem referências a elas nas definições Xano consultadas. Nenhum endpoint ou dado remoto foi alterado.

### Bloqueio de E2E

- A validação real de cadastro/login/endereço no Xano não foi executada: os endpoints desta Change permanecem somente locais, e a publicação no ambiente já foi bloqueada anteriormente pelo Xano com `allow_push: false`. Não foi feita nova tentativa de publicação nem foram criados registros de teste. A validação automatizada local e as validações de XanoScript/OpenSpec foram executadas.
