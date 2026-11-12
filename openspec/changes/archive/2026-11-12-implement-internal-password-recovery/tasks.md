## 1. Preparação

- [x] 1.1 Conferir a tabela `user`, o campo `password_reset`, o login interno e os
      endpoints de reset do template — verificação: leitura sem alteração
- [x] 1.2 Confirmar que o fluxo template não será reutilizado por responder `notfound`,
      criar auto-login e depender de `account_id` — verificação: decisão registrada no design
- [x] 1.3 Confirmar que recuperação de `Cliente`, provedor externo e rate limiting ficam
      fora do escopo — verificação: escopo aprovado conferido

## 2. Backend Xano

- [x] 2.1 Criar `xano/api/internal_password_recovery/api_group.xs` para o grupo
      `Voltix Internal Password Recovery` — verificação: canonical
      `voltix-internal-password-recovery`, tags e sem segredo
- [x] 2.2 Criar `request_POST.xs` público com e-mail validado e resposta sempre genérica —
      verificação: mesmo status/mensagem para conta existente e inexistente
- [x] 2.3 Gerar token UUID de uso único com expiração de 60 minutos e gravar
      `password_reset` apenas para `FUNCIONARIO`/`ADMINISTRADOR` com status `ATIVO` —
      verificação: inativo e perfil não aprovado não recebem token
- [x] 2.4 Montar o e-mail com link absoluto a partir de `voltix_app_url` e token como
      texto de apoio, usando `util.send_email` — verificação: nenhuma credencial em log
- [x] 2.5 Criar `confirm_POST.xs` público que valida e-mail, token por
      `security.check_password`, expiração, uso único e regras da nova senha —
      verificação: erros genéricos e senha inalterada em falha
- [x] 2.6 Em sucesso, gravar a nova senha e marcar `password_reset.used = true` sem emitir
      token de sessão — verificação: nenhum `security.create_auth_token`
- [x] 2.7 Validar os arquivos com dry-run/importação do Xano — verificação: apenas os
      `CREATE` esperados no preview

## 3. Frontend

- [x] 3.1 Adicionar Estado, contrato e handlers de solicitação e confirmação de
      recuperação, com chamadas server-side às URLs do ambiente — verificação: token e
      senha nunca renderizados
- [x] 3.2 Adicionar o link "Esqueci minha senha" ao login interno — verificação: rótulo e
      destino observáveis
- [x] 3.3 Criar a página `/interno/recuperar-senha` com e-mail e mensagem genérica —
      verificação: mesma resposta para qualquer e-mail
- [x] 3.4 Criar a página `/interno/redefinir-senha` lendo `email`/`token` da URL e
      permitindo preenchimento manual — verificação: token não visível como texto
- [x] 3.5 Preservar os campos em falha, limpar em sucesso e retornar ao login sem simular
      autenticação — verificação: mensagens observáveis
- [x] 3.6 Adicionar estilos escopados em `assets/voltix-internal.css` — verificação: sem
      afetar a loja pública

## 4. Testes

- [x] 4.1 Criar `tests/test_internal_password_recovery.py` cobrindo contrato e handlers —
      verificação: request genérico, confirmação, token inválido, senha fraca e
      confirmação divergente
- [x] 4.2 Cobrir o XanoScript: endpoints públicos, ausência de auto-login, expiração,
      uso único e ausência de credenciais nas respostas — verificação: asserções estáticas
- [x] 4.3 Ajustar o teste de login interno para o novo link — verificação: suíte existente
      preservada
- [x] 4.4 Executar a suíte completa — verificação:
      `python -m unittest discover -s tests -q` (411 testes OK)

## 5. Verificação e publicação

- [x] 5.1 `openspec validate implement-internal-password-recovery --strict` —
      verificação: válido
- [x] 5.2 `reflex compile` e restauração de `reflex.lock/*` não relacionado — verificação:
      `git status` sem migração acidental
- [x] 5.3 `git diff --check` — verificação: sem whitespace/conflito
- [x] 5.4 Dry-run restrito do grupo e dos dois endpoints — verificação: preview com apenas
      os `CREATE` esperados
- [x] 5.5 **GATE** — autorização explícita recebida ("vamos") antes de publicar no Xano —
      verificação: `xano workspace push --force` OK, 3 documentos
- [x] 5.6 Pull independente pós-publicação — verificação: grupo, `voltix-internal-password-recovery`,
      ausência de auto-login e `used` confirmados (apenas normalização `query "x"` → `query x`)
- [x] 5.7 Verificação remota somente leitura — verificação: `request` responde 200 genérico
      para e-mail inexistente, 400 para e-mail inválido; `confirm` rejeita senha curta
      (min:8), senha sem dígito, confirmação divergente e conta inexistente com erro
      genérico — nenhum e-mail enviado, nenhum token criado. Correção de input filters
      aplicada e republicada (ver nota).
- [x] 5.8 **GATE opcional** — teste autenticado real de ponta a ponta com e-mail — NÃO
      executado com autorização do usuário; limitação do plano Free (envio só ao e-mail
      do dono da instância) registrada no design e no handoff.

## 6. Encerramento

- [x] 6.1 Sincronizar as deltas com `openspec/specs/` e confirmar
      `openspec validate --all --strict` — verificação: validação global (29 itens, 0 falhas)
- [x] 6.2 Atualizar `.env.example`, `docs/roadmap-changes.md` e
      `docs/AI_AGENT_HANDOFF.md` — verificação: consistente com a evidência (`.env` local
      também recebeu `XANO_PASSWORD_RESET_REQUEST_URL`/`XANO_PASSWORD_RESET_CONFIRM_URL`)
- [x] 6.3 Arquivar a change — verificação: diretório em `openspec/changes/archive/`
      (`2026-11-12-implement-internal-password-recovery`)
- [x] 6.4 Commit/push somente com autorização explícita — verificação: autorização
      registrada; `1b0ff6f` em `main`
