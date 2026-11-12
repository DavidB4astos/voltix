# Verificação local — 12/11/2026

## Escopo verificado

- Contratos e payloads em `voltix/internal_password_recovery.py`: e-mail (254
  caracteres, padrão estrito), token (16–128 caracteres, sem espaços), senha (8+,
  letra e número, via `password_rules` reutilizado de `internal_users`), confirmação
  igual e parsing/validação das respostas genéricas e `{updated: true}`.
- Handlers em `voltix/voltix.py`: solicitação com resposta sempre genérica (sucesso e
  falha), confirmação com campos preservados em falha e limpos em sucesso, leitura e
  sanitização de `email`/`token` da URL em `enter_internal_reset`, ausência de sessão
  e de auto-login, e limpeza em `_clear_authentication_state`/logout.
- Navegação: link "Esqueci minha senha" no login interno; páginas
  `/interno/recuperar-senha` e `/interno/redefinir-senha` registradas com
  `on_load=State.enter_internal_reset`; token renderizado como `type="password"`;
  preenchimento manual permitido; estilos escopados em `assets/voltix-internal.css`.
- XanoScript: endpoints públicos, guardas de perfil/status antes de qualquer escrita,
  token UUID de uso único com expiração de 60 minutos, comparação por
  `security.check_password`, sem `security.create_auth_token`, sem log de token e
  sem `db.del`.

## Comandos e resultados

```text
.venv-novo-pc\Scripts\python.exe -m unittest discover -s tests -q
Ran 411 tests in 6.882s
OK

reflex compile --dry
Success: App compiled successfully in 3.662 seconds

openspec validate implement-internal-password-recovery --strict
Change 'implement-internal-password-recovery' is valid

openspec validate --all --strict
Totals: 29 passed, 0 failed

git diff --check
sem erros (apenas avisos de normalização LF/CRLF)
```

`reflex.lock/bun.lock` e `reflex.lock/package.json` não foram alterados pelo
compile; nenhuma migração de dependências foi incluída.

## Limitações

- O envio real do e-mail para usuários arbitrários não é comprovável no plano Free:
  `util.send_email` com `service_provider = "xano"` entrega apenas ao e-mail do dono
  da instância. O teste E2E com e-mail não foi executado (decisão do usuário em
  12/11/2026).
- `voltix_app_url` não está configurada no workspace Xano; o e-mail sai com o token
  como texto de apoio, ainda funcional para preenchimento manual. A configuração
  exige ação e autorização separadas.
- A validação visual responsiva (375/768/1280) não foi executada nesta change.
