## Why

A C1 continua bloqueada porque o projeto não dispõe de ambiente isolado aprovado. O Xano CLI instalado oferece comandos Sandbox, mas a disponibilidade depende do plano e o comando `xano sandbox get` cria um ambiente quando ainda não existe. É necessário reavaliar a condição de retomada sem provisionar recursos nem alterar o workspace.

## What Changes

- Conferir a disponibilidade do sandbox no CLI local e na documentação pública da Xano.
- Registrar os requisitos conhecidos, dependência de plano e limites de uso do sandbox para a C1.
- Atualizar o registro de adiamento da C1; não provisionar ambiente, não enviar documentos e não executar testes com dados.

## Capabilities

Nenhuma capability alterada. Change de avaliação documental (`skip_specs: true`).

## Impact

Somente `docs/deferred-changes/2026-10-23-baixa-estoque-checkout/README.md` e os artefatos desta change. A situação do plano da conta não será consultada; nenhum ambiente Xano será criado. A C1 continuará adiada até o usuário confirmar acesso a ambiente isolado sem custo adicional e aprovar seu uso.
