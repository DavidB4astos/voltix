## Context

As melhorias propostas são estritamente de apresentação (atributos HTML/Reflex e polimento visual) sobre componentes já existentes em `voltix/voltix.py` e `voltix/internal_attendances.py`.

## Goals / Non-Goals

- **Goals:**
  - Eliminar avisos de acessibilidade de `id`/`name`/`autocomplete` nos formulários públicos e internos.
  - Tornar o placeholder `"Imagem não disponível"` visualmente mais equilibrado sem alterar seu texto.
  - Tornar o estado vazio de Atendimentos mais informativo para o operador.
- **Non-Goals:**
  - Alterar lógica de `State`, chamadas HTTP ou contratos Xano.
  - Alterar fotos de produtos, tokens principais de marca ou layout mobile de tabelas internas.

## Decisions

1. **Preservação de contratos:** manter todos os `id`, `name`, `on_change`, `on_submit` e textos exigidos por testes e specs (`"Imagem não disponível"`, rótulos de formulário, mensagens de erro).
2. **Escopo mínimo em Reflex:** usar `rx.input(..., auto_complete=...)` e `rx.icon(...)` nativos do Reflex já utilizados no projeto, sem dependências novas.
