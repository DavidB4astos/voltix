# Design — correção da exibição monetária

## Context

`_cart_money_text(value)` em `voltix/voltix.py` formata valores monetários vindos do
backend. A implementação atual faz `rx.Var.create(texto).to_string()`, que o Reflex
baixa para `JSON.stringify("119.90")` como parte da expressão, produzindo as aspas
literais no texto renderizado (`R$ "119,90"`). A correção ocorre na camada de
apresentação apenas; nenhum dado do backend é recalculado.

## Goals / Non-Goals

**Goals:** mesmos valores, exibidos como `R$ inteiro,fração` com exatamente duas casas
decimais e sem caracteres de escape/aspas; comportamento idêntico para `119`, `119.5` e
`119.90` e para todos os call sites.

**Non-Goals:** formatação alternativa (milhar/outra moeda/locale), qualquer mudança em
handlers, rotas, State, Xano ou nos dados.

## Decisions

- **Função pura em Python, sem `rx.Var`.** Todos os call sites passam strings Python
  vindas de dataclasses validadas (`_money` em `internal_sales.py`,
  `_cart_decimal_text`/`Decimal` em carrinho/checkout/pedidos), nunca `rx.Var`.
  Formata-se em Python: separa no primeiro `.`, normaliza a fração para duas casas,
  concatena `R$ <int>,<fra>`. Alternativas consideradas: manter `rx.Var` e escapar a
  string (mantém o JS com `JSON.stringify` sem benefício), `locale.format_string`
  (lokale/float inadequados a dinheiro), reescrever a cadeia com `|0`/substr em JS
  (mesma complexidade, mais opaca).
- **Tipo de retorno muda de `rx.Var[str]` para `str`.** Todos os call sites aceitam
  texto plano (`rx.text`, `rx.el.td`, `rx.el.dd`...), e o helper deixa de ser um
  construtor de Vars. Nenhum consumidor depende de `_js_expr`.
- **Preservar sementes decimais.** Sem `.quantize`/`int()`/`float`; apenas string +
  pad da fração, alinhado à filosofia existente (valores exibidos como recebidos).

## Risks / Trade-offs

- [Risco] Alguma superfície exibe `R$ "119,90"` hoje e algum teste/print depende disso →
  Mitigação: não há testes nem documentos com o formato com aspas; suíte deve confirmar.
- [Trade-off] Vírgula/milhar não agrupados — aceito, mantém o comportamento anterior.

## Migration Plan

Uma edição local + nova suíte `tests/test_money_display.py` + `reflex compile` +
`openspec validate` + inspeção visual no Dashboard/Pedidos. Sem Xano e sem deploy;
rollback por `git revert`.

## Open Questions

Nenhuma.
