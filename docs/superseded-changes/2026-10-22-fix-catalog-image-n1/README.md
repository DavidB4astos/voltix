# Change substituída: fix-catalog-image-n1 (2026-10-22)

Esta pasta preserva os artefatos originais da change `fix-catalog-image-n1`, que não foi implementada como change independente.

## Motivo da substituição

O roadmap exige **uma change por vez**, sem paralelismo nem intercalamento. A change `refine-storefront-home` estava em encerramento e sua verificação 5.3 (`/catalogo`) foi bloqueada por HTTP 429 causado pelo fan-out de uma requisição de imagem por produto. Abrir e implementar outra change antes de encerrar a Home violaria essa regra.

## Decisão

A correção mínima de imagens do catálogo foi **absorvida** por `refine-storefront-home`:

- o delta `public-catalog` foi copiado para `openspec/changes/refine-storefront-home/specs/public-catalog/spec.md`;
- o escopo, o design e as tarefas da Home foram atualizados com as tarefas 7.1–7.8;
- os artefatos originais permanecem aqui apenas como referência histórica.

## Estado

- A change original **não foi implementada, publicada no Xano, testada nem arquivada**.
- O código e a publicação do Xano serão tratados dentro de `refine-storefront-home`.
- Este diretório não é uma change ativa do OpenSpec e não deve ser movido de volta para `openspec/changes/`.

## Conteúdo preservado

- `proposal.md`
- `design.md`
- `tasks.md`
- `specs/public-catalog/spec.md`
- `.openspec.yaml`
