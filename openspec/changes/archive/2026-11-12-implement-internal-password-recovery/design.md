# Design — recuperação de senha interna

## Contexto

`UsuarioInterno` vive na tabela Xano `user`, com `name`, `email`, `password`, `role`,
`status` e o objeto `password_reset { token, expiration, used }`. O campo `token` é do
tipo `password`, portanto o Xano aplica hash automaticamente na escrita. O login interno
já exige perfil `FUNCIONARIO`/`ADMINISTRADOR` com status `ATIVO`. O e-mail é único por
índice. `Cliente` é uma tabela e uma autenticação separadas.

O template Xano já possui `reset/request-reset-link`, `reset/magic-link-login`,
`reset/update_password` e `generate_magic_link`, mas foi feito para a página de demo:
responde `notfound` para e-mail inexistente (enumeração), cria token de login (auto-login),
depende de `account_id` e usa uma rota de demo. Reutilizá-lo ampliaria o escopo e manteria
os problemas. Por isso o fluxo é reimplementado em um grupo próprio.

## Decisão

Criar o grupo público `Voltix Internal Password Recovery`
(`voltix-internal-password-recovery`) com dois endpoints:

| Método | Rota | Acesso | Finalidade |
|---|---|---|---|
| `POST` | `request` | público | Solicitar recuperação por e-mail |
| `POST` | `confirm` | público | Validar token e gravar nova senha |

Nenhum endpoint é autenticado e nenhum emite token de sessão. O fluxo termina com o
usuário voltando ao login normal.

### Ajuste descoberto na verificação remota (5.7)

Inputs `text` no Xano não aceitam os filtros `minAlpha`/`minDigit` (existem apenas em
colunas/inputs `password`, que por sua vez hasham o valor no bind e inviabilizam as
comparações). Por isso `confirm` recebe `password` como `text filters=min:8` e exige
letra e dígito na stack via `regex_test`, mantendo toda falha de confirmação com a
mensagem genérica "Link inválido ou expirado.". O mesmo padrão incorreto
(`text password filters=min:8|minAlpha:1|minDigit:1`) existe em `internal_users`
`users_POST` e `profile/password_POST`, publicados anteriormente; reportado em separado.

## Contratos

### `POST request`

- Entrada: `email` válido, obrigatório, até 254 caracteres.
- Resposta: sempre `{ message: "Se o e-mail estiver cadastrado, enviaremos as instruções." }`,
  com o mesmo status, exista ou não a conta.
- Internamente:
  - busca `user` por e-mail;
  - só gera token se `role` for `FUNCIONARIO`/`ADMINISTRADOR` e `status` for `ATIVO`;
  - gera UUID, monta `password_reset { token, expiration: now + 3600, used: false }` e
    grava com `db.edit` e objeto literal;
  - monta o link com a URL pública do frontend e envia por `util.send_email`.
- Se o e-mail não for elegível, não grava nada e não envia mensagem, mantendo a resposta
  genérica.

### `POST confirm`

- Entrada: `email` válido, `token` (texto), `password` (mínimo 8, letra e número) e
  `confirm_password`.
- Rejeita com `400` e mensagem genérica "Link inválido ou expirado." quando:
  - `password` não atende às regras, é igual à senha atual ou difere da confirmação;
  - o usuário não existe, está inativo ou tem perfil não aprovado;
  - o token não confere, expirou ou já foi usado.
- Valida o token com `security.check_password`, pois o campo é hash.
- Em sucesso, grava a nova senha e marca `password_reset.used = true` no mesmo
  `db.edit`, preservando token e expiração.
- Resposta: `{ updated: true }`.
- Não emite `security.create_auth_token` e não retorna token, senha ou hash.

## Token e segurança

- Token UUID aleatório, validade de 60 minutos, uso único.
- Comparação por hash; o valor em texto só existe no link enviado por e-mail.
- Respostas de `request` e `confirm` não distinguem e-mail inexistente, conta inativa,
  token errado, expirado ou usado.
- Nenhum log registra token ou senha.
- Sem auto-login: o usuário precisa entrar com a nova senha.
- Sem revogação global de sessões: tokens já emitidos continuam válidos, conforme o
  escopo aprovado.
- Rate limiting dedicado não é implementado no Xano Free; a limitação fica documentada.

## E-mail e configuração

O Xano expõe `$env.$api_baseurl`, que aponta para a API, não para o frontend. Para montar
um link absoluto, o endpoint usa uma variável de ambiente do workspace
`voltix_app_url` (URL pública do Reflex). Regras:

- Se `voltix_app_url` estiver configurada, o e-mail contém o link
  `{voltix_app_url}/interno/redefinir-senha?email=...&token=...`.
- O corpo do e-mail também traz o token como texto de apoio, permitindo preenchimento
  manual na página de redefinição.
- `util.send_email` usa `service_provider = "xano"`. No plano Free, o envio chega apenas
  ao e-mail do dono da instância; isso é uma limitação de entrega, não do fluxo.
- A configuração de `voltix_app_url` e de um provedor externo, se desejado, exige ação e
  autorização separadas. Nada é configurado via `--env` no CLI.

## Frontend

- Link "Esqueci minha senha" no formulário de login interno.
- Página `/interno/recuperar-senha`:
  - campo de e-mail;
  - chama `POST request` server-side com `XANO_PASSWORD_RESET_REQUEST_URL`;
  - mostra sempre a mesma mensagem genérica, sem indicar se o e-mail existe.
- Página `/interno/redefinir-senha`:
  - lê `email` e `token` de `router.url.query_parameters` no `on_load`;
  - exibe e-mail e token em campos editáveis (o token em `type="password"`), permitindo
    preenchimento manual;
  - valida localmente senha (8+, letra, número) e confirmação;
  - chama `POST confirm` server-side com `XANO_PASSWORD_RESET_CONFIRM_URL`;
  - em sucesso, limpa os campos e oferece retorno ao login; em falha, preserva os campos e
    mostra erro genérico.
- O token nunca é renderizado como texto visível nem gravado em estado persistente além do
  necessário para o envio.
- Novas variáveis no `.env`: `XANO_PASSWORD_RESET_REQUEST_URL` e
  `XANO_PASSWORD_RESET_CONFIRM_URL`.
- Estilos em `assets/voltix-internal.css`, escopados por classes próprias.

## Testes

- Contrato Python: validação de e-mail, token e senha; payloads.
- Handlers: request genérico, confirm com sucesso, token inválido, senha fraca,
  confirmação divergente, falha de rede, `401`/`403` não aplicáveis (público), `400`
  mapeado para mensagem genérica.
- XanoScript: endpoints públicos, ausência de `security.create_auth_token`, uso de
  `security.check_password`, expiração, `used`, resposta sem credenciais, ausência de
  `db.del user` e de log de token.
- Frontend: link no login, leitura de query params, preenchimento manual e mensagens.

## Limitações

- Entrega real de e-mail para usuários arbitrários não é comprovável no plano Free.
- Sem rate limiting dedicado.
- Sem revogação de sessões já emitidas.
- Recuperação de `Cliente` e envio por provedor externo ficam fora do escopo.
