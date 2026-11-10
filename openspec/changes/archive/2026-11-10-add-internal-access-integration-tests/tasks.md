## 1. Internal access tests

- [x] 1.1 Criar `tests/test_internal_access.py` com login válido, credenciais inválidas, resposta malformada, token ausente e identificador inválido — verificação: testes confirmam sessão autenticada apenas no caso válido
- [x] 1.2 Cobrir `submit_login` com campos vazios e `validate_session` com perfil/status aprovados, perfil não aprovado, status inativo, token ausente, acesso negado e falha HTTP — verificação: cada cenário limpa ou mantém a sessão conforme a spec
- [x] 1.3 Cobrir troca de identidade limpando dados internos, `logout` e separação Cliente × UsuarioInterno — verificação: estado interno e área protegida ficam limpos
- [x] 1.4 Adicionar asserções estáticas de `auth/login`, `auth/me` e `auth/internal-access` para perfis, status, `accessdenied` e ausência de senha/token na resposta — verificação: os testes passam lendo os `.xs` locais
- [x] 1.5 Confirmar que a suíte usa apenas stubs, sem rede ou registros reais — verificação: testes passam com Xano inacessível

## 2. Integration health tests

- [x] 2.1 Criar `tests/test_integration_health.py` cobrindo contrato exato de `_request_xano_health`, status não-2xx, payload não-objeto e contrato divergente — verificação: testes confirmam sucesso somente para o contrato aprovado
- [x] 2.2 Cobrir `check_integration` com sucesso, variável ausente sem requisição, HTTP, rede, valor inválido, payload anterior não reaproveitado e nova tentativa — verificação: estados e mensagens distinguem sucesso de falha
- [x] 2.3 Adicionar asserção estática do `health_GET.xs` e do escopo técnico da requisição — verificação: contrato exato e ausência de autenticação/dados de domínio
- [x] 2.4 Confirmar isolamento total de Reflex em execução e Xano — verificação: testes passam sem backend disponível

## 3. Verificação e encerramento

- [x] 3.1 Rodar os dois arquivos novos isoladamente — verificação: todos os testes novos aprovados
- [x] 3.2 Rodar `python -m unittest discover -s tests -q` — verificação: suíte completa aprovada sem regressões
- [x] 3.3 Rodar `openspec validate add-internal-access-integration-tests --strict`, `openspec validate --all --strict` e `git diff --check` — verificação: tudo válido e diff limpo
- [x] 3.4 Registrar evidência local, atualizar `docs/roadmap-changes.md` e `docs/AI_AGENT_HANDOFF.md` e arquivar a change — verificação: documentação consistente e change arquivada
- [x] 3.5 Commit focado e push somente com autorização explícita — verificação: `git log --oneline -1` e `git status --short --branch`
