## Why

O helper `_cart_money_text` renderiza valores monetários com aspas literais em toda a
aplicação (`R$ "119,90"`), porque faz `rx.Var.create(texto).to_string()`, que o Reflex
emite como `JSON.stringify("119.90")` — a saída inclui as aspas do literal JSON. Todos
os preços, subtotais, fretes, totais, faturamentos e tickets exibidos ao usuário estão
pontuados incorretamente. Descoberto na auditoria de 13/11/2026 ao corrigir a leitura
do dashboard (`.env` com URL errada, já corrigida).

## What Changes

- Reescrever `_cart_money_text` como função pura em Python: recebe o texto decimal do
  backend, separa inteiro e fração, padroniza a fração em duas casas e retorna
  `R$ <inteiro>,<fração>` — sem `rx.Var`, sem cálculo float, preservando a semântica
  atual para `119`, `119.5` e `119.90` (frações com 0/1/2+ casas).
- Sem alteração de rotas, handlers, dados, Xano, State ou tipos; somente a apresentação.

Sem **BREAKING** changes.

## Capabilities

### New Capabilities

<!-- Nenhuma capability nova. -->

### Modified Capabilities

- `visual-interface`: passa a exigir que valores monetários sejam exibidos no formato `R$ inteiro,fração` sem caracteres literais de aspas/escapes.

## Impact

- Código: `voltix/voltix.py` (função `_cart_money_text`).
- Testes: nova `tests/test_money_display.py` cobrindo `119`, `119.5`, `119.90`, `0.00`,
  valores com sufixo; suíte existente preservada (nenhum teste atual referencia o helper).
- Verificação: suíte, `reflex compile`, `openspec validate`, inspeção visual das superfícies
  de dinheiro em 1280 px (dashboard e, se possível, dados no carrinho).
- Fora do escopo: formatação/locale alternativa (ex.: separador de milhar),
  exibição de moeda diferente de BRL, qualquer mudança no formato dos dados do backend.
