# Revisão do pacote — 30/10/2026

## Compatibilidade
O cadastro Reflex usa POST em XANO_CUSTOMER_URL, e save_customer_profile usa PATCH em XANO_CUSTOMER_URL/{customer_id}, com sessão privada de Cliente e somente nome_completo/email/telefone. Logo, não desativar o grupo nem a edição própria. POST de cadastro não integra o pacote. GET de coleção não é usado para listar clientes no frontend; a consulta interna usa outro grupo já protegido.

## Escopo pronto
Quatro arquivos XanoScript já versionados e protegidos, copiados byte a byte para diretório externo de publicação. Identidades de query e GUIDs coincidem com snapshot fresco dos 98 documentos. As quatro versões remotas continuam iguais às vistas na auditoria. Manifesto com hashes: package-manifest.json.

- GET /cliente: auth CLIENTE, identidade do próprio Cliente ativo, whitelist de resposta; sem lista global.
- GET /cliente/{cliente_id}: auth CLIENTE, propriedade antes da consulta, registro ativo e whitelist de resposta.
- PATCH /cliente/{cliente_id}: auth CLIENTE, propriedade, registro ativo, somente nome/e-mail/telefone; CPF/status/credenciais fora da entrada. Resposta explícita; verificação de e-mail existente preservada.
- DELETE /cliente/{cliente_id}: auth CLIENTE, propriedade e rejeição permanente; não contém db.del.

## Dry-run executado
CLI 1.2.0, perfil voltix, workspace 147981, transação padrão, --dry-run --no-guids, diretório contendo somente quatro queries. Resultado:

    API Endpoints ~4 updated
    UPDATE query cliente/{cliente_id} DELETE
    UPDATE query cliente/{cliente_id} GET
    UPDATE query cliente/{cliente_id} PATCH
    UPDATE query cliente GET

Nenhum group/table/record/env. Sem --force, --sync, --delete, --records, --env, --truncate ou --no-transaction. O dry-run apresenta escopo; não comprova publicação nem validação remota completa.

## Verificação local
185 testes passaram em 2,999 s, incluindo a suite customer-access que cobre ownership, whitelist, ausência de raw_input/dblink e ausência de exclusão permanente nos aliases. State/frontend não alterados. Artefatos OpenSpec validados strict. Snapshot bruto e credenciais fora do Git.

## Pendências obrigatórias
Publicação ainda NÃO executada. Aguardar autorização concreta após esta revisão; executar push interativo sem --force. Após publicar, novo pull: comparar os quatro códigos e conferir que identidades não alvo não foram alteradas. Só depois fazer provas negativas anônimas e com credencial inválida, usando ID fictício inexistente. Não baixar lista antiga de clientes nem executar atualização/exclusão válida em clientes reais. Registrar limites das provas autenticadas, sem declarar mutação positiva testada se não foi autorizada/executada. Arquivar somente após encerramento verificado.
