# Auditoria de runtime das telas — adiada

## Origem

Change `audit-runtime-screens-and-flows`, criada em 10/11/2026 e não executada. Os artefatos originais (`proposal.md`, `design.md`, `tasks.md`, `.openspec.yaml`) estão preservados nesta pasta.

## Motivo do adiamento

A auditoria foi motivada pela gravação do vídeo de entrega. Em 10/11/2026 o usuário decidiu suspender os entregáveis do professor e priorizar a implementação de produto (CRM, gestão de usuários internos, estoque, edição de Cliente, exclusão de Produto, recuperação de senha e perfil interno).

## Condição de retomada

Retomar somente quando houver decisão de gravar o vídeo ou de validar a aplicação em execução de ponta a ponta. A retomada exige:

- autorização para subir o app e autenticar com as contas de teste;
- janela de execução contra o Xano configurado;
- compromisso de manter o modo somente leitura (sem compra, upload, importação, inativação ou exclusão).

## O que a auditoria cobriria

1. Inventário das 7 rotas públicas e 7 seções internas.
2. Jornadas de Visitante, Cliente, FUNCIONARIO e ADMINISTRADOR.
3. Larguras 375, 768 e 1280 px.
4. Lista de defeitos classificada por severidade, com evidência sanitizada.

## Observação

A validação de runtime de cada nova capability continua sendo feita dentro da própria change, com testes automatizados. Esta auditoria é complementar, não substituta.
