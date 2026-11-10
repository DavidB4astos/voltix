## Why

As capabilities `internal-access` e `reflex-xano-integration` concentram regras de segurança e de contrato técnico que hoje não possuem nenhum teste automatizado. Uma regressão no login interno, na checagem de perfil/status, no encerramento de sessão ou no contrato de saúde do Xano passaria despercebida pela suíte de 290 testes.

## What Changes

- Adicionar `tests/test_internal_access.py` cobrindo login, validação de identidade e sessão, área protegida, logout e separação entre Cliente e UsuárioInterno.
- Adicionar `tests/test_integration_health.py` cobrindo o contrato de saúde do Xano, o handler `check_integration` e os estados de sucesso, configuração ausente, erro HTTP, erro de rede, resposta inválida e nova tentativa.
- Adicionar asserções estáticas sobre os XanoScripts `auth/login`, `auth/me`, `auth/internal-access` e `integration/health` para preservar guardas de perfil/status e o formato público da resposta.
- Registrar nas specs `internal-access` e `reflex-xano-integration` os requisitos de verificação automatizada desses comportamentos.
- Sem alteração de comportamento em produção, sem publicação Xano, sem novas variáveis de ambiente e sem dados reais.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `internal-access`: acrescentar requisito de verificação automatizada para autenticação, identidade, acesso protegido, logout e separação Cliente × interno.
- `reflex-xano-integration`: acrescentar requisito de verificação automatizada para o contrato de saúde e para os estados de sucesso, falha e configuração ausente.

## Impact

- Testes: novos `tests/test_internal_access.py` e `tests/test_integration_health.py`.
- Specs: deltas em `internal-access` e `reflex-xano-integration`.
- Produção: nenhuma alteração prevista em `voltix/voltix.py`; se um teste revelar defeito real, a implementação para e o achado é reportado antes de qualquer correção.
- Xano: nenhuma alteração, publicação ou execução remota; apenas leitura estática dos arquivos `.xs`.
- Dependências e configuração: nenhuma nova.
