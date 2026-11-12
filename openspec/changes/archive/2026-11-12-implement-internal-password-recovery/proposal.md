## Why

Um `UsuarioInterno` que esquece a senha não possui hoje nenhum caminho de recuperação
pela aplicação: só um `ADMINISTRADOR` poderia redefini-la fora do produto, e a troca
autenticada exige a senha atual. O item 11 da fila aprovada cobre essa lacuna com um
fluxo de link de recuperação por e-mail, sem auto-login e sem revelar se um e-mail
existe.

## What Changes

- Criar o grupo Xano público `Voltix Internal Password Recovery`
  (`voltix-internal-password-recovery`) com dois endpoints sem sessão:
  - `POST request` para solicitar a recuperação por e-mail.
  - `POST confirm` para validar o token e gravar a nova senha.
- Gerar token de uso único com expiração de 60 minutos, armazenado no campo
  `password_reset` já existente na tabela `user`, comparado por hash.
- Responder sempre de forma genérica na solicitação, exista ou não o e-mail, para
  impedir enumeração de usuários; ignorar usuários inativos ou com perfil não aprovado.
- Não emitir token de autenticação e não autenticar automaticamente: após redefinir, o
  usuário volta ao login normal.
- Nunca retornar o token de recuperação, senha, hash ou outro dado de credencial.
- Adicionar ao login interno o link "Esqueci minha senha" e duas páginas públicas:
  - `/interno/recuperar-senha` para informar o e-mail.
  - `/interno/redefinir-senha` para informar a nova senha, lendo `email` e `token` da URL
    ou permitindo preenchimento manual.
- Reutilizar `util.send_email` do Xano, registrando como limitação conhecida que, no
  plano Free, o envio chega apenas ao e-mail do dono da instância.
- Documentar e configurar a URL pública do frontend usada no link do e-mail; se ela não
  estiver configurada, o e-mail ainda traz o token como texto de apoio.

## Capabilities

### New Capabilities

- `internal-password-recovery`: solicitação e confirmação de recuperação de senha de
  `UsuarioInterno` por token de uso único, com respostas que não revelam a existência do
  e-mail e sem auto-login.

### Modified Capabilities

<!-- Nenhuma capability existente tem requisito alterado. -->

## Impact

- Xano: novo grupo `xano/api/internal_password_recovery/api_group.xs` e dois endpoints
  públicos; publicação restrita, pendente de autorização explícita.
- Configuração Xano: URL pública do frontend para montar o link do e-mail. Se o envio real
  não for comprovável no plano Free, a limitação fica registrada.
- Código: `voltix/voltix.py` (estado, handlers, link no login e duas páginas) e
  `assets/voltix-internal.css` (estilos escopados das páginas de recuperação).
- Testes: novo `tests/test_internal_password_recovery.py` e ajustes pontuais no teste de
  login interno.
- Docs: `.env.example`, `docs/roadmap-changes.md` e `docs/AI_AGENT_HANDOFF.md` após a
  verificação.
- Fora do escopo: recuperação para `Cliente`, envio por provedor externo (Resend etc.),
  upgrade de plano, auto-login por link, revogação global de sessões, rate limiting
  dedicado, código numérico curto e alteração de e-mail.
