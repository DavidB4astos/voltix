# 01 — Verificação local do ajuste de estoque (10/11/2026)

## Escopo implementado

- Endpoint `POST variations/{variation_id}/stock-adjustments` com delta assinado e
  `db.increment` guardado.
- Ação "Ajustar estoque" e formulário dedicado no painel de produtos, exclusivos de
  `ADMINISTRADOR`.
- Nenhuma tabela, coluna ou variável de ambiente nova.

## Comandos e resultados

```text
& '.\.venv-novo-pc\Scripts\python.exe' -m unittest tests.test_product_management -q
Ran 26 tests — OK
```

```text
& '.\.venv-novo-pc\Scripts\python.exe' -m unittest discover -s tests -q
Ran 356 tests — OK
```

```text
& '.\.venv-novo-pc\Scripts\python.exe' -m reflex compile
Success: App compiled successfully
```

`reflex.lock/bun.lock` e `reflex.lock/package.json` foram restaurados após a compilação
(`git checkout -- reflex.lock/bun.lock reflex.lock/package.json`).

```text
openspec validate implement-variation-stock-adjustment --strict
Change 'implement-variation-stock-adjustment' is valid
```

```text
git diff --check
sem erros de whitespace ou conflito
```

## Cobertura adicionada

- Delta de saída enviado como negativo, com `path_suffix="/stock-adjustments"`.
- Delta de entrada enviado como positivo.
- Quantidade zero rejeitada antes da requisição, preservando o formulário.
- Saída acima da quantidade atual rejeitada localmente com aviso, sem requisição.
- Ausência de variação selecionada e direção inválida rejeitadas sem requisição.
- Estoque insuficiente (`400`) exibido como falha observável, sem recarga e sem sucesso.
- XanoScript: autorização antes do negócio, `db.increment` guardado, delta não nulo,
  ausência de motivo/movimentação e allowlist de resposta.
- Interface: rótulos, nomes de campos, handlers e desabilitação durante a operação.

## Limitações

- Nenhuma chamada autenticada positiva foi executada; não houve escrita em estoque real.
- O comportamento transacional do `db.increment` neste endpoint foi validado pela
  publicação e pelo pull, não por teste concorrente com dados sintéticos.
