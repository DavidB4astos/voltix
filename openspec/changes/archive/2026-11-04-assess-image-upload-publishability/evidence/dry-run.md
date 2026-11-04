# Prévia restrita de publicação — upload de imagem

Data: 04/11/2026.

## Escopo da consulta

- Perfil: `voltix`.
- Pasta local: `xano`.
- Único arquivo incluído: `api/product_management/product/product_id_image_POST.xs`.
- Operação executada: `workspace push --dry-run`; nenhuma publicação foi feita.

## Resultado observado

O CLI Xano v1.2.0 informou `Matched: 1 of 97 files` e `No changes to push` (exit code 0).

## Interpretação e limite

O preview não oferece uma alteração para publicar. Isso contradiz o trecho de
código publicado fornecido pelo usuário (`file? image_file`) em relação ao
XanoScript local (`file image_file`). O resultado do dry-run demonstra somente
que o CLI não encontrou diferenças locais para enviar naquele momento; não é
uma leitura isolada do input publicado e não comprova qual forma está ativa.
Nenhum push foi executado. Para avançar com segurança, obter uma leitura atual
somente dessa rota no Xano e reconciliar a divergência antes de gerar outro
preview. Não usar push global ou `--sync` para contornar o resultado.

A diferença de obrigatoriedade continua separada da limitação histórica de
`storage.create_image` no plano Free; o upload não foi testado.
