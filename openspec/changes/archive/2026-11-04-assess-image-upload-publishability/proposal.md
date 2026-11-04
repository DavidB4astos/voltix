## Why

O código de endpoint publicado fornecido pelo usuário declara `file? image_file`; o código local declara `file image_file` e o Reflex envia esse campo. A avaliação inicial recomendou alinhar o contrato. Antes de qualquer publicação, foi executado um dry-run limitado ao endpoint, mas o Xano CLI informou que não havia alterações a publicar. É necessário registrar esse resultado e evitar uma publicação vazia ou um push mais amplo para contorná-lo.

## What Changes

- Registrar o contrato enviado pelo usuário, a definição local e o comportamento do dry-run limitado a um arquivo.
- Manter a divergência do contrato como pendente até existir uma leitura atual que a reconcilie com o preview do CLI.
- Não alterar nem publicar o Xano; não executar POST ou alterar registros.

## Capabilities

Nenhuma capability alterada. Avaliação documental somente (`skip_specs: true`).

## Impact

Somente documentação desta avaliação. O endpoint publicado permanece sem correção comprovada; o upload não é declarado operacional. O HTTP 403 histórico de `storage.create_image` no plano Free é uma limitação separada e não foi retestado.
