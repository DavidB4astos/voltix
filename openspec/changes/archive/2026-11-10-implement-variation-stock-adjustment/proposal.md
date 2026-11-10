## Why

A gestão de produtos só altera o estoque dentro do formulário completo de variação, que
exige reenviar nome, SKU e preço para mudar apenas a quantidade. Não existe ação dedicada de
entrada/saída de unidades, e o `PATCH variations/{variation_id}` grava um valor absoluto
calculado no cliente: se um checkout baixar o estoque entre a leitura e a gravação, o valor
absoluto sobrescreve a baixa (lost update). O ajuste de estoque é o próximo item aprovado da
fila de produto (item 8), explicitamente sem histórico de movimentações.

## What Changes

- Criar o endpoint Xano `POST variations/{variation_id}/stock-adjustments` no grupo já
  publicado `Product Management`, com `auth = "user"` e autorização exclusiva de
  `ADMINISTRADOR` ativo, recebendo somente `delta` decimal não nulo (positivo = entrada,
  negativo = saída).
- Aplicar o delta com `db.increment` atômico, com guarda de estoque suficiente apenas quando
  a saída for negativa, garantindo que a quantidade nunca fique negativa e que baixas
  concorrentes de checkout não sejam sobrescritas.
- Rejeitar sem qualquer escrita: delta zero, variação inexistente, estoque insuficiente e
  sessão sem autorização. Não alterar metadados, preço, SKU, status ou vínculos, e não criar
  registro de movimentação de estoque.
- Responder com a variação atualizada usando os campos administrativos já existentes.
- Adicionar ao painel de produtos uma ação "Ajustar estoque" por variação, visível apenas
  para `ADMINISTRADOR`, exibindo a quantidade atual, a direção (entrada/saída) e uma
  quantidade positiva informada.
- Reutilizar a URL base `XANO_VARIATIONS_URL` com o sufixo
  `/{variation_id}/stock-adjustments`, sem criar nova variável de ambiente.

## Capabilities

### New Capabilities

Nenhuma capability nova.

### Modified Capabilities

- `product-management`: acrescenta o ajuste atômico de estoque por variação e a ação
  dedicada no painel, preservando as regras existentes de SKU único, preço positivo, status
  e estoque não negativo.

## Impact

- Xano: novo arquivo
  `xano/api/product_management/variation/variation_id_stock_adjustments_POST.xs`; publicação
  restrita ao endpoint, pendente de autorização explícita.
- Código: `voltix/voltix.py` (Estado, handlers, sufixo opcional em `_catalog_request` e
  painel de produtos). Nenhuma variável de ambiente nova.
- Testes: contrato, handler e checagens do XanoScript em
  `tests/test_product_management.py`.
- Specs: delta em `product-management`.
- Docs: `docs/roadmap-changes.md` e `docs/AI_AGENT_HANDOFF.md` após a verificação.
- Fora do escopo: histórico de movimentações, tabela nova, motivo/observação persistidos,
  alteração de schema, reserva de estoque, exclusão de produto, importação em massa e
  qualquer alteração em checkout, pedidos, pagamentos ou preços.
