## Context

A integração técnica já validada estabelece o padrão `Interface Reflex -> State/lógica Python -> Xano`. O Xano possui uma tabela autenticável `user` e endpoints de exemplo para login e identidade, mas o modelo atual usa a semântica genérica `admin/member`, não possui o status de acesso interno da Voltix e inclui um cadastro público incompatível com esta Change.

O domínio da Voltix trata `UsuarioInterno` como uma entidade distinta de `Cliente`, com os perfis `FUNCIONARIO` e `ADMINISTRADOR` e os status `ATIVO` e `INATIVO`. As permissões detalhadas de negócio serão definidas posteriormente; nesta Change, ambos os perfis ativos terão somente acesso à área interna mínima protegida.

## Goals / Non-Goals

**Goals:**

- Adaptar a tabela Xano `user` para representar oficialmente `UsuarioInterno`.
- Implementar autenticação, consulta de identidade, autorização da área interna e logout no fluxo Reflex -> State/lógica Python -> Xano.
- Fazer o Xano decidir se a sessão e o usuário podem acessar a área protegida.
- Reaproveitar a verificação de senha e a emissão de token existentes sem preservar a semântica `admin/member`.
- Manter a página interna mínima, sem introduzir operações de negócio.

**Non-Goals:**

- Criar uma tabela de usuários internos paralela ou alterar a tabela conceitual de `Cliente`.
- Oferecer signup público, convite, CRUD, alteração de perfil ou provisionamento pela interface.
- Implementar recuperação ou alteração de senha, MFA, OAuth, SSO ou revogação distribuída de tokens.
- Definir permissões específicas para operações administrativas, comerciais ou de CRM.
- Fazer chamadas de autenticação diretamente do código executado no navegador.

## Decisions

### Adaptar `user` como `UsuarioInterno`

A tabela Xano `user` será mantida como a única fonte de identidade para esta capability, pois já suporta senha protegida, e-mail único e tokens de autenticação. O campo `role` será adaptado para aceitar somente `FUNCIONARIO` e `ADMINISTRADOR`, e a tabela receberá um campo `status` com os valores `ATIVO` e `INATIVO`.

Os campos de senha, token e metadados internos continuarão com visibilidade restrita. A resposta de identidade poderá expor somente os dados não sensíveis necessários à área interna, como `id`, `name`, `email`, `role` e `status`. Campos do template, como `account_id`, não serão usados para transformar cliente em usuário interno nem para definir permissões desta Change.

Uma tabela paralela foi considerada, mas aumentaria a duplicação de autenticação e poderia criar duas fontes concorrentes de identidade. A alteração da tabela `cliente` também foi descartada porque `Cliente` e `UsuarioInterno` permanecem conceitos separados.

### Adaptar login e identidade no Xano

O endpoint de login continuará recebendo e-mail e senha, buscará o registro em `user`, verificará a senha e validará `status = ATIVO` e um perfil permitido antes de emitir o token. Credenciais inválidas, registros inexistentes, status `INATIVO` e perfis fora do contrato resultarão em falha de autenticação sem sessão autorizada.

O endpoint de identidade autenticada (`me`) validará o token, buscará novamente o usuário e repetirá as validações de perfil e status. Sua resposta não conterá senha nem token. O token retornado pelo login será consumido pelo State, não apresentado como dado da interface.

O endpoint de signup público existente não será conectado à interface e não será usado para provisionar usuários internos. Os primeiros registros serão criados manualmente no Xano.

### Autorizar a área interna no backend

Será disponibilizado um endpoint técnico mínimo para a área interna. Ele exigirá autenticação Xano, recuperará o usuário associado ao token e permitirá somente os perfis `FUNCIONARIO` ou `ADMINISTRADOR` com status `ATIVO`. A autorização será feita novamente em cada requisição protegida; não será suficiente confiar em uma variável de rota, em um estado local do Reflex ou em dados antigos da sessão.

Nesta Change, os dois perfis válidos terão o mesmo nível de acesso à página protegida. A hierarquia genérica `admin/member` e o helper de RBAC do template não serão reutilizados sem adaptação, pois não representam os nomes nem as permissões aprovadas para Voltix.

### Manter o fluxo de comunicação mediado pelo State

A interface Reflex acionará eventos do State. O State realizará as chamadas HTTP ao Xano, interpretará os resultados e controlará os estados de autenticação, carregamento e erro:

```text
Interface Reflex
        |
        v
State/lógica Python
        |
        v
Xano: login / me / endpoint protegido
```

O token ficará somente no armazenamento de sessão controlado pela aplicação no lado Python/State, sem ser embutido no código versionado ou enviado por uma chamada direta do navegador ao Xano. A URL dos endpoints será fornecida por configuração de ambiente.

### Usar logout local nesta Change

O logout removerá o token e os dados de identidade do State e fará a interface retornar ao estado não autenticado. Não será criado um endpoint de revogação remota nesta Change. Como compensação, o acesso protegido sempre dependerá de um token válido e da revalidação de usuário, perfil e status no backend; a expiração do token continuará sendo aplicada pelo Xano.

### Exibir uma página interna mínima

Após o endpoint protegido autorizar a sessão, a interface exibirá somente uma confirmação de acesso e dados não sensíveis da identidade autenticada, além da ação de logout. Uma sessão ausente, expirada, inválida ou recusada pelo backend manterá a interface fora da área protegida.

## Risks / Trade-offs

- [A tabela `user` contém contratos do template `admin/member`] -> Alterar somente os campos e endpoints necessários, validar os enums Voltix e não reutilizar cegamente o signup ou o RBAC genérico.
- [Um token emitido pode continuar válido depois que o usuário se torna `INATIVO`] -> Revalidar o status no endpoint de identidade e em todo endpoint protegido, rejeitando o acesso no backend.
- [O logout local não revoga tokens já emitidos] -> Remover imediatamente a sessão do State, respeitar a expiração do Xano e manter a revalidação server-side; revogação distribuída permanece fora do escopo.
- [A interface pode parecer protegida sem uma autorização real] -> A página só será considerada acessível após resposta positiva do endpoint protegido, com testes de ausência de token, token inválido, perfil inválido e usuário inativo.
- [Dados de `Cliente` podem ser confundidos com dados de `UsuarioInterno`] -> Usar exclusivamente a tabela `user` nesta capability e não consultar nem alterar o modelo de clientes.
- [Provisionamento manual pode gerar registros inconsistentes] -> Validar no Xano registros de teste para `FUNCIONARIO` ativo, `ADMINISTRADOR` ativo e usuário inativo antes da verificação ponta a ponta.
- [Credenciais ou destinos privados podem ser expostos] -> Manter URLs e credenciais em configuração de ambiente e verificar o repositório antes de concluir a Change.

## Migration Plan

1. Adaptar o schema da tabela `user` para perfil e status Voltix, preservando a proteção de senha e a unicidade do e-mail.
2. Adaptar os endpoints de login e identidade e criar o endpoint técnico protegido, sem conectar o signup público.
3. Provisionar manualmente no Xano os usuários necessários para validação, sem registrar suas credenciais nos arquivos do projeto.
4. Implementar no State as chamadas server-side, a sessão, os estados de erro e o logout, e conectar a interface de login e a página protegida.
5. Validar os fluxos de login, identidade, autorização, bloqueio de inativo e logout com ambos os perfis.
6. Para rollback, remover os endpoints e a interface desta Change e restaurar o contrato anterior da tabela `user` somente se isso puder ser feito sem misturar identidades ou perder a proteção das senhas.

## Open Questions

Nenhuma decisão necessária para o fluxo especificado permanece em aberto. URLs, credenciais e registros concretos de provisionamento serão definidos no ambiente de execução e não farão parte dos artefatos versionados.
