# Evidência do endpoint publicado — fornecida pelo usuário

Data: 04/11/2026.

O usuário copiou do Xano o código do endpoint `POST /products/{product_id}/image`, grupo `Product Management`. O código fornecido declara `file? image_file`, portanto o campo é opcional no contrato publicado consultado pelo usuário.

O endpoint mantém `auth = "user"`, carrega `user` por `$auth.id`, exige `role == "ADMINISTRADOR"` e `status == "ATIVO"`, confirma que o produto existe, salva a imagem com `storage.create_image` usando acesso privado, atualiza `imagem_principal` e `updated_at` e retorna `$updated_product`.

O endpoint não verifica explicitamente se `image_file` está presente antes de acessar `$input.image_file.name` e passar `$input.image_file` a `storage.create_image`. A consequência de chamar o endpoint sem arquivo não foi testada. O Reflex, por sua vez, exige exatamente um arquivo e o envia no multipart com o campo `image_file`; para o fluxo atual do painel, o nome do campo coincide.

A definição local declara `file image_file` como obrigatório. Portanto, a diferença do publicado é confirmada pelo trecho fornecido: o contrato publicado aceita ausência do campo, enquanto o processamento depende de um arquivo. Isso não explica o HTTP 403 histórico da instância Free, que a evidência de 18/10/2026 atribui à indisponibilidade do `storage.create_image` naquele plano.

## Proveniência e limites
- Fonte: trecho do endpoint publicado copiado pelo usuário diretamente do Xano nesta conversa.
- O agente não fez uma leitura direta do endpoint remoto; a exportação ampla do workspace foi bloqueada por revisão automática.
- Nenhum POST, upload, teste de ausência do arquivo, mudança de schema ou publicação foi executado.
- Nenhuma conclusão de funcionamento operacional atual é feita; o bloqueio do plano Free permanece documentado.

## Conclusão
O contrato deve declarar `image_file` obrigatório, alinhado ao uso do endpoint e do painel. A divergência publicada é uma inconsistência de contrato; a falha de upload HTTP 403 registrada é uma limitação separada do armazenamento da instância. Uma correção ou nova validação remota deve ser proposta numa change funcional OpenSpec própria, com aprovação e ambiente/serviço que suporte `storage.create_image`.
