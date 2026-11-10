# Design — gestão de usuários internos e perfil próprio

## Contexto

`UsuarioInterno` é representado na tabela Xano `user`, com `name`, `email`, `password`,
`role`, `status` e `password_reset`. A autenticação existente já aceita apenas
`FUNCIONARIO`/`ADMINISTRADOR` com status `ATIVO`, e o e-mail é único por índice. O domínio
exige e-mail obrigatório e único entre usuários internos, inativação sem exclusão para
preservar Atendimentos e separação entre Cliente e UsuarioInterno.

Hoje não existe endpoint Voltix para listar, criar ou editar usuários internos. Os endpoints
do template Xano (`Members & Accounts`) usam `account_id` e o perfil legado `admin`, não
seguem o domínio e não verificam status. Também não existe edição do perfil próprio; o
`reset/update_password` do template altera a senha sem exigir a senha atual e não deve ser
reutilizado.

## Decisão

Criar o grupo `Voltix Internal Users` com cinco endpoints:

| Método | Rota | Acesso | Finalidade |
|---|---|---|---|
| `GET` | `users` | ADMINISTRADOR ativo | Listar usuários internos |
| `POST` | `users` | ADMINISTRADOR ativo | Criar usuário interno |
| `PATCH` | `users/{user_id}` | ADMINISTRADOR ativo | Editar nome, e-mail, perfil e status |
| `PATCH` | `profile` | FUNCIONARIO/ADMINISTRADOR ativo | Editar o próprio nome e e-mail |
| `POST` | `profile/password` | FUNCIONARIO/ADMINISTRADOR ativo | Trocar a própria senha |

Nenhum endpoint exclui usuários. A inativação remove o acesso operacional e preserva
Atendimentos e demais referências históricas.

## Autorização

- Todos os endpoints usam `auth = "user"`.
- Gestão de usuários: `db.get user` pelo `$auth.id` e precondição
  `role == "ADMINISTRADOR" && status == "ATIVO"` antes de qualquer leitura de negócio.
- Perfil próprio: `db.get user` pelo `$auth.id` e precondição de perfil
  `FUNCIONARIO`/`ADMINISTRADOR` com status `ATIVO` antes de qualquer escrita.
- Respostas nunca incluem `password`, `password_reset`, `account_id` ou tokens.

## Contratos

### `GET users`

- Sem filtros obrigatórios; retorna todos os usuários internos ordenados por `name` asc.
- Allowlist: `id`, `name`, `email`, `role`, `status`, `created_at`.
- Inclui usuários inativos, pois a gestão precisa reativá-los.

### `POST users`

- Entrada: `name` (1–300), `email` válido, `password` (mínimo 8, ao menos uma letra e um
  dígito, conforme o schema), `role` (`FUNCIONARIO`/`ADMINISTRADOR`).
- Verificar e-mail existente antes de criar; e-mail duplicado responde `400`
  (`badrequest`), inclusive contra usuário inativo. O índice único permanece como última
  defesa.
- Criar com `status = "ATIVO"` e sem `account_id`.
- Responder com a allowlist administrativa. Não autenticar automaticamente e não retornar
  senha nem token.

### `PATCH users/{user_id}`

- Entrada parcial: `name`, `email`, `role`, `status`; pelo menos um campo é obrigatório.
- `404` quando o usuário não existir.
- E-mail novo deve ser único, excluindo o próprio usuário; duplicidade responde `400`.
- O endpoint não aceita `password`; troca de senha de terceiros fica fora do escopo.
- O administrador autenticado não pode alterar o próprio `role` nem o próprio `status`;
  nome e e-mail próprios são editáveis pelo perfil. Tentativa responde `400`.
- Se a alteração retirar o status `ATIVO` ou o perfil `ADMINISTRADOR` do último
  administrador ativo, responder `400` e não escrever. A verificação consulta outro
  administrador ativo antes da atualização.
- A resposta usa a mesma allowlist de `GET users`.

### `PATCH profile`

- Entrada parcial: `name`, `email`; pelo menos um campo é obrigatório.
- Não aceita `role`, `status`, `password`, `account_id` ou outro campo.
- E-mail novo deve ser único, excluindo o próprio usuário; duplicidade responde `400`.
- Responder com `id`, `name`, `email`, `role`, `status`.

### `POST profile/password`

- Entrada: `current_password`, `new_password`, `confirm_password`.
- `new_password` deve atender ao schema (mínimo 8, letra e dígito) e ser diferente da senha
  atual; `new_password` e `confirm_password` devem coincidir.
- Validar `current_password` com `security.check_password` contra o hash atual.
- Senha atual incorreta, confirmação divergente ou nova senha inválida respondem `400` sem
  escrita.
- Atualizar somente `password`; o hash é aplicado pelo Xano ao gravar o campo de
  autenticação.
- Responder `{updated: true}` e não retornar senha, hash ou token.
- Sessões já emitidas não são revogadas globalmente; a revogação de tokens existentes está
  fora do escopo e permanece uma limitação documentada.

## Concorrência e integridade

- Cada operação altera um único registro; não há transação multi-tabela.
- A pré-checagem de e-mail oferece mensagem amigável, e o índice único impede duplicidade
  concorrente.
- A checagem de último administrador é feita antes do `db.patch`; uma corrida entre dois
  administradores ainda mantém ao menos o administrador autenticado, pois ele não pode
  rebaixar a si mesmo.
- Usuários inativos permanecem na tabela e continuam disponíveis para reativação.

## Interface

### Seção "Usuários" — somente ADMINISTRADOR

- Nova entrada de navegação "Usuários", disponível apenas para `ADMINISTRADOR`.
- Lista com nome, e-mail, perfil, status e ações de editar e inativar/reativar.
- Formulário de criação: nome, e-mail, senha inicial, perfil; status inicial `ATIVO`.
- Formulário de edição: nome, e-mail, perfil e status. O próprio administrador vê os campos
  de perfil/status desabilitados com explicação, pois essas alterações são bloqueadas no
  backend.
- Inativação/reativação exige confirmação em dois passos.
- Sucesso só é exibido após resposta confirmada e recarga da lista.
- Falhas (`400`, `403`, `404`, rede) mantêm os dados confirmados e mostram feedback
  observável; `400` de e-mail duplicado e de proteção do administrador têm mensagens
  distintas.

### "Meu perfil" — ambos os perfis

- O bloco de identidade do usuário na barra lateral torna-se acionável e abre a seção
  "Meu perfil", sem criar uma nova entrada na navegação principal.
- Exibe nome, e-mail, perfil e status em modo leitura, com formulário para nome/e-mail.
- Formulário de senha separado com senha atual, nova senha e confirmação.
- Após editar nome/e-mail, atualizar `user_name`/`user_email` somente com a resposta
  confirmada; após trocar a senha, limpar os campos e mostrar sucesso.
- Falhas mantêm os campos e não alteram os dados exibidos. A seção é rejeitada no backend
  para sessão inativa ou perfil não aprovado.

## Alternativas descartadas

- **Reutilizar `Members & Accounts`**: depende de `account_id` e do perfil legado `admin`,
  não aplica `FUNCIONARIO`/`ADMINISTRADOR`/status e criaria inconsistência de domínio.
- **Excluir usuário**: quebraria o vínculo histórico de Atendimentos; a inativação já é a
  regra do domínio.
- **Permitir que administrador troque a senha de outro usuário**: aumenta o risco de
  apropriação de conta sem um fluxo de recuperação aprovado; fica fora do escopo.
- **Reutilizar `reset/update_password` para o perfil**: não exige a senha atual e não valida
  perfil/status; seria uma regressão de segurança.
- **Revogar todos os tokens ao trocar a senha**: exigiria versionamento de token ou schema
  novo; não foi aprovado e fica documentado como limitação.

## Fora do escopo

Recuperação de senha por e-mail (item 11), exclusão de usuário, verificação de e-mail,
alteração de senha de terceiros, revogação global de sessões, auditoria detalhada, `account`
multi-tenant, cadastro público, login social, upload de avatar e mudanças no login atual.

## Verificação

- Testes de contrato, handlers, permissões, proteções e mensagens em
  `tests/test_internal_user_management.py`.
- Asserções estáticas dos XanoScripts: autorização antes do negócio, allowlists, ausência de
  exclusão, validação de e-mail, proteção do último administrador e ausência de senha em
  respostas.
- Suíte completa, `openspec validate --all --strict`, `reflex compile` e `git diff --check`.
- Dry-run e publicação restrita somente com autorização explícita.
- Pull independente e verificação remota somente leitura (`401` sem sessão).
- Teste autenticado positivo com usuário sintético é um gate separado e só ocorre com
  autorização explícita para escrita real.
