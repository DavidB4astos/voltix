# 01 — Testes de acesso interno e integração: verificação local (10/11/2026)

## Escopo verificado

- `internal-access`: login, `submit_login`, `validate_session`, `enter_internal_area`,
  logout, troca de identidade e separação Cliente × UsuarioInterno.
- `reflex-xano-integration`: contrato de `_request_xano_health` e estados de
  `check_integration` (sucesso, configuração ausente, HTTP, rede, payload inválido
  e nova tentativa).
- Guardas estáticas dos XanoScripts `auth/login`, `auth/me`, `auth/internal-access`
  e `integration/health`.
- Nenhuma alteração de produção, Xano, dependências ou variáveis de ambiente.

## Verificação local

| Item | Resultado |
|---|---|
| `python -m unittest tests.test_internal_access tests.test_integration_health -q` | **32 testes**, OK |
| `python -m unittest discover -s tests -q` | **322 testes**, OK |
| `openspec validate add-internal-access-integration-tests --strict` | válido |
| `openspec validate --all --strict` | **26 passed**, 0 failed |
| `git diff --check` | limpo |
| `reflex.lock` | restaurado, sem alterações |

## Cobertura adicionada

### `tests/test_internal_access.py`

- Login válido grava token normalizado e identidade, sem rede real.
- Credenciais rejeitadas, respostas malformadas, token vazio, identificador
  ausente/não numérico e configuração ausente não autenticam.
- `submit_login` exige e-mail e senha e delega o formulário válido.
- `validate_session` aceita apenas perfil `FUNCIONARIO`/`ADMINISTRADOR` com status
  `ATIVO`, exige autorização explícita da área protegida e limpa a sessão em
  token ausente, identidade inválida, acesso negado e falha HTTP.
- Troca de identidade incrementa as gerações de Clientes, Atendimentos, Pedidos e
  Dashboard; a mesma identidade preserva os dados.
- `enter_internal_area` atualiza Produtos somente para ADMINISTRADOR.
- Logout remove token, identidade, seção e área protegida.
- Asserções estáticas confirmam perfis/status, `accessdenied`, identidade sem
  senha/token e ausência de endpoint público de cadastro interno.

### `tests/test_integration_health.py`

- Contrato exato `status=ok`, `service=voltix-xano`, `integration=available`.
- Rejeição de status não-2xx, payload não-objeto e contrato divergente.
- Requisição sem autenticação, corpo ou cookies.
- Sucesso mantém somente o payload técnico; configuração ausente falha sem
  requisição; HTTP/rede/valor inválido reportam erro.
- Payload de sucesso anterior não é reaproveitado após falha e nova tentativa
  pode voltar a ter sucesso.
- Definição `health_GET.xs` sem `auth`, `db` ou `table`.

## Limitações

- Os testes estáticos dos `.xs` não executam o runtime Xano; confirmam apenas o
  texto versionado das guardas e do contrato.
- Não houve verificação remota autenticada nem uso de dados reais.
- Os `ResourceWarning` de `HTTPError` observados na suíte completa vêm de testes
  existentes; os arquivos novos fecham explicitamente seus erros.
- Nenhum defeito de produção foi encontrado; portanto nenhuma alteração em
  `voltix/voltix.py` foi necessária.
