# Verificação — 13/11/2026

## Problema

Valores monetários exibidos com aspas literais (`R$ "119,90"`) em toda a aplicação. Salientado na auditoria de 13/11/2026 ao validar os painéis internos no navegador: o helper `_cart_money_text` usava `rx.Var.create(texto).to_string()`, que o Reflex compila para `JSON.stringify("119.90")` — a saída inclui as aspas do literal JSON. Os valores alcançam o usuário via Vars `faturamento`/`subtotal`/etc. anotados como `str` nas dataclasses.

## Correção

`_cart_money_text` reescrito:

- entrada `rx.Var` (ex.: campos `str` das dataclasses, placeholders de `foreach`) é
  respeitada como Var e operada sobre o próprio texto (`split(".")`, `rx.cond` para o
  padding), sem `to_string()` — o valor nunca passa por quoting de JSON;
- entrada Python (`str`/`int`/`float`) formatada em Python puro: separa no primeiro `.`,
  normaliza a fração para duas casas, concatena `R$ <int>,<fra>`;
- entrada inválida lança `ValueError` (as camadas de contrato já entregam texto decimal válido).

## Comandos e resultados

```text
.venv-novo-pc\Scripts\python.exe -m unittest tests.test_money_display -q
Ran 5 tests in 0.001s
OK

.venv-novo-pc\Scripts\reflex.exe compile --dry
Success: App compiled successfully

openspec validate fix-money-display --strict
Change 'fix-money-display' is valid

openspec validate --all --strict
Totals: 30 passed, 0 failed (30 items)

openspec validate --specs --strict
Totals: 28 passed, 0 failed (28 items)
```

## Verificação visual (servidor de produção local, sessão funcional do usuário)

- Dashboard: valores dos cartões renderizam como `R$ 119,90` e `1` (avaliado via
  `querySelectorAll('.vx-dashboard__metric-value')` no DOM);
- seção Produtos (preços de variações): lista renderizada sem nenhuma ocorrência de
  `'"'` em células monetárias (`R$ 10,00`, `R$ 399,90`, `R$ 2999,90`, ...).

## Limitações

- A inspeção foi somente leitura e em 1280 px; 375/768 px não foram reconferidos para
  esta fix (a apresentação é idêntica em todas as larguras).
