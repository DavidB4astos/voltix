## Context

See `proposal.md` — Why. A suíte atual tem 290 testes, mas `internal-access` e `reflex-xano-integration` não possuem nenhum teste dedicado. Os handlers relevantes vivem em `voltix/voltix.py` e chamam `_server_side_xano_request`, `_required_environment_url`, `_request_xano_health` e `os.getenv`; os contratos do backend vivem em `xano/api/authentication/auth/*.xs` e `xano/api/integration/health_GET.xs`. Os testes existentes usam `unittest`, `unittest.mock.patch`, `SimpleNamespace` e `MethodType` para isolar o `State`, sem rede.

## Goals / Non-Goals

**Goals:**

- Exercitar os comportamentos observáveis de login, identidade, acesso protegido, logout e separação Cliente × interno.
- Exercitar o contrato de saúde e os estados de `check_integration`, incluindo ausência de configuração e nova tentativa.
- Manter os testes rápidos, determinísticos e independentes de Xano, Reflex em execução ou dados reais.
- Preservar a rastreabilidade entre cada cenário de spec e pelo menos um teste.

**Non-Goals:**

- Alterar `voltix/voltix.py`, XanoScripts, contratos de API ou variáveis de ambiente.
- Publicar ou executar chamadas remotas no Xano.
- Cobrir E2E Playwright, testes visuais ou axe-core.
- Refatorar a suíte existente ou duplicar cenários já cobertos por outros arquivos.

## Decisions

- **Usar `unittest.IsolatedAsyncioTestCase` com `State` real e métodos vinculados.** Os testes de `internal-access` precisam dos campos e da lógica de limpeza do próprio `State`; `SimpleNamespace` com `MethodType` é usado apenas onde o handler depende de métodos auxiliares, seguindo o padrão de `tests/test_internal_sales.py`. Alternativa descartada: mockar o `State` inteiro, que reduziria a fidelidade dos testes.
- **Substituir apenas as fronteiras externas.** `_required_environment_url`, `_server_side_xano_request`, `_request_xano_health` e `os.getenv` são os pontos de stub; nada além disso é mockado. Isso mantém os testes focados no comportamento e evita espelhar a implementação linha a linha.
- **Asserções estáticas sobre os `.xs`.** Como os testes Python não executam XanoScript, os arquivos `.xs` são lidos como texto para confirmar perfis, status, `accessdenied`, campos públicos e contrato de saúde. É o mesmo recurso já usado em `tests/test_customer_access.py`. Alternativa descartada: teste remoto autenticado, proibido pelo escopo e pela regra de verificação somente leitura.
- **Verificar estados, não detalhes internos.** As asserções olham token, identidade, flags de sessão, mensagens, payload e campos de dados internos, evitando acoplamento a nomes de variáveis locais ou ordem de chamadas não observável.
- **Sem alteração de produção.** Se um teste falhar por defeito real, a implementação para e o achado é reportado; nenhuma correção é feita nesta change sem novo escopo.

## Risks / Trade-offs

- **Testes acoplados à implementação** → mitigado por asserções em comportamento observável e por stubs apenas nas fronteiras externas.
- **Falsa sensação de cobertura Xano** → os testes estáticos não executam o runtime; a limitação fica registrada na evidência.
- **Duplicação com testes existentes** → os cenários novos cobrem apenas handlers e contratos hoje sem teste; a revisão final compara com os arquivos existentes.
- **Dependência de `os.getenv` global** → cada teste controla o ambiente com `patch.dict` e restaura o estado automaticamente.

## Migration Plan

Não há migração. A change adiciona arquivos de teste e deltas de spec; nenhum artefato publicado é alterado. Reversão consiste em remover os dois arquivos de teste e os deltas.
