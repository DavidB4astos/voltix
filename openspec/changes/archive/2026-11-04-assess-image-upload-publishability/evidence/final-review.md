# Revisão final — publishability do contrato de upload

Data: 04/11/2026.

## Evidência

- O usuário confirmou novamente que o endpoint publicado usa `file? image_file`.
- O XanoScript local declara `file image_file`; o handler Reflex envia o arquivo nesse campo.
- O dry-run do Xano CLI v1.2.0, filtrado para um único arquivo, retornou `Matched: 1 of 97 files` e `No changes to push` (exit code 0).

## Conclusão e limite

Não havia diff para publicar, então nenhum push foi executado. A divergência
entre a fonte publicada fornecida e o preview do CLI permanece pendente. Não foi
feito pull do workspace inteiro para evitar exportar metadata alheia ao escopo.
O XanoScript publicado não foi alterado, não houve POST e nenhum registro foi
modificado. O upload continua sem validação operacional; a limitação histórica
de `storage.create_image` é separada.

Para reabrir a correção, é necessária uma leitura atual e restrita da rota que
reconcilie o campo opcional com o resultado do preview. O próximo item do
roadmap, C1, continua dependente de ambiente de teste isolado e autorizado.
