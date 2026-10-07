## 1. Contrato e provisionamento do UsuarioInterno

- [x] 1.1 Adaptar o schema Xano da tabela `user` para representar `UsuarioInterno`, mantendo senha protegida e e-mail único, restringindo `role` a `FUNCIONARIO`/`ADMINISTRADOR` e adicionando `status` com `ATIVO`/`INATIVO`; verificar a validação do XanoScript e confirmar que a tabela `cliente` não foi alterada
- [x] 1.2 Remover a dependência do fluxo público de signup para usuários internos e documentar/verificar que não existe endpoint ou interface pública de criação de `UsuarioInterno`
- [x] 1.3 Provisionar manualmente no Xano um usuário `FUNCIONARIO` ativo, um `ADMINISTRADOR` ativo e um usuário interno inativo; verificar os perfis/status no ambiente sem registrar credenciais ou tokens nos arquivos versionados

## 2. Autenticação e autorização no Xano

- [x] 2.1 Adaptar o endpoint de login para validar credenciais, perfil permitido e `status = ATIVO` antes de emitir token; verificar sucesso sem exposição de senha/token na identidade e rejeição de e-mail inexistente, senha inválida, perfil inválido e usuário inativo
- [x] 2.2 Adaptar o endpoint de identidade autenticada para revalidar token, existência, perfil e status no backend e retornar somente dados não sensíveis; verificar que senha, token e campos internos não aparecem na resposta
- [x] 2.3 Criar o endpoint técnico protegido da área interna, exigindo autenticação e autorizando somente `FUNCIONARIO` ou `ADMINISTRADOR` ativos; verificar respostas para ambos os perfis, ausência de sessão, token inválido, perfil inválido e usuário inativo
- [x] 2.4 Validar todos os endpoints Xano/XanoScript alterados ou criados e confirmar que o fluxo não consulta nem altera dados de `Cliente`, catálogo, carrinho, pedidos, pagamentos ou CRM

## 3. Sessão e State/lógica Python do Reflex

- [x] 3.1 Configurar URLs dos endpoints por variáveis de ambiente e implementar chamadas HTTP server-side no State, sem chamada direta do navegador ao Xano; verificar falha explícita com configuração ausente e ausência de credenciais, tokens ou URLs privadas no código versionado
- [x] 3.2 Implementar no State o login e o armazenamento da sessão/identidade não sensível, com estados de carregamento, sucesso e erro; verificar que credenciais inválidas, usuário inativo, perfil inválido, resposta incompatível e falha de rede não criam sessão
- [x] 3.3 Implementar no State a validação da sessão pelo endpoint de identidade e pelo endpoint protegido; verificar que a autorização não depende apenas de estado local ou de uma variável da interface
- [x] 3.4 Implementar logout no State removendo token e identidade e retornando ao estado não autenticado; verificar que uma tentativa posterior não envia sessão válida nem acessa a área protegida

## 4. Interface interna mínima

- [x] 4.1 Criar a interface de login e conectar sua ação aos eventos do State; verificar estados inicial, carregamento, sucesso e mensagens de falha sem exibir credenciais ou tokens
- [x] 4.2 Criar a página interna mínima exibida somente após autorização positiva do backend, mostrando confirmação de acesso e identidade não sensível; verificar acesso permitido para `FUNCIONARIO` e `ADMINISTRADOR` ativos
- [x] 4.3 Conectar a ação de logout à interface e ocultar a área protegida após a remoção da sessão; verificar que usuário não autenticado, inativo ou com sessão inválida permanece fora da página

## 5. Verificação ponta a ponta

- [x] 5.1 Compilar/verificar o projeto Reflex e validar os arquivos XanoScript após a implementação, corrigindo somente falhas relacionadas a esta Change
- [x] 5.2 Executar o fluxo ponta a ponta `Interface Reflex -> State/lógica Python -> Xano` para login, sessão, consulta de identidade, acesso protegido e logout com `FUNCIONARIO` ativo
- [x] 5.3 Repetir o fluxo ponta a ponta com `ADMINISTRADOR` ativo e verificar que ambos os perfis recebem o mesmo acesso mínimo aprovado
- [x] 5.4 Executar os cenários de erro de credenciais inválidas, ausência de configuração, backend indisponível, resposta incompatível, ausência de sessão, token inválido, usuário inativo e perfil inválido, confirmando que nenhum erro é tratado como sucesso
- [x] 5.5 Confirmar a ausência de expansão de escopo: nenhum cadastro público, recuperação de senha, CRUD de usuários, permissão comercial, CRM ou alteração de Cliente foi implementado
