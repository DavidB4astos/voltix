## Context

Ver `proposal.md` (Why). Contexto técnico mínimo:

- Reflex 0.9.12: handler coroutine emite um único delta ao final (`chain_updates` após `await fn(...)`); deltas intermediários só existem em handlers generator (`yield`).
- Defaults de estado no primeiro render da sessão: `public_products = []`, `public_catalog_loading = False`, `public_catalog_message = ""` (enviados pela hidratação).
- Condições atuais: Home (voltix.py ~6406-6435) e `/catalogo` (voltix.py ~6761-6799) tratam `loading`, `message` e `length() == 0`, sem noção de "primeira carga concluída".
- Handlers compartilhados: `load_public_catalog` é usado por `on_load` da Home e de `/catalogo` e por `filter_public_catalog`.

## Goals / Non-Goals

**Goals:**
- Distinção observável dos três estados no primeiro carregamento da sessão: carregando, vazio (carga concluída sem produtos), com produtos — na Home e em `/catalogo`.
- Compatibilidade estrita com Reflex 0.9.12, usando apenas `rx.cond` e operadores de Var já existentes no código.

**Non-Goals:**
- Página de detalhes do produto (`public_product_loading`/`public_product_message`) — mantida como está.
- Alterar retry 429, cache TTL, contratos Xano, filtro por categoria ou qualquer fluxo de dados.
- Alterar textos, tratamentos visuais ou primitivas existentes (`loading_text`, `empty_state`, `status_panel`).
- Tornar o `loading` visível em recarregamentos subsequentes (refiltro) — somente o estado inicial da sessão.

## Decisions

**D1 — Flag `public_catalog_loaded: bool = False` setada no `finally` do `load_public_catalog`.**
- Rationale: é a única alteração que reflete exatamente o evento observável "a primeira consulta da sessão terminou" (sucesso ou falha), independente de quem dispara o load (`on_load` ou filtro).
- Alternativas descartadas:
  - *Inicializar `public_catalog_loading = True`* (1 linha): funciona para a primeira carga, mas `loading` é rebaixado no mesmo delta em que os produtos chegam; em F5 com dados já no estado, "Carregando..." poderia coincidir com a grade. Mais frágil semanticamente (loading diz respeito à operação, não à sessão).
  - *Handler generator com `yield`* para emitir delta intermediário: exige reescrever `load_public_catalog` como async generator e redesenhar `filter_public_catalog` (que faz `await` direto) — escopo maior, risco de regressão, e desnecessário para o estado inicial.

**D2 — O loading exibido na Home e no catálogo durante a primeira carga usa a condição `public_catalog_loading | !public_catalog_loaded`.**
- Rationale: no primeiro render `public_catalog_loading` é `False` (o delta com `True` só chega ao final, junto do `False`), então `!public_catalog_loaded` é o que garante o estado correto; manter `public_catalog_loading` na condição preserva o comportamento atual caso o estado seja reutilizado/alterado por outro evento.
- `rx.cond(State.public_catalog_loading | (State.public_catalog_loaded == False), ...)` — operadores já usados no projeto (`&` em 6782).

**D3 — Empty state condicionado a `public_catalog_loaded == True` (além das condições atuais).**
- Rationale: única forma de impedir o empty prematuro sem esconder o empty legítimo. Falha continua caindo no ramo de `public_catalog_message` (ramo anterior na cascata), preservando "Tentar novamente".

**D4 — Um único var compartilhado entre Home e catálogo, pois ambos os `on_load` usam o mesmo handler e os dados são os mesmos (`public_products`).**
- Alternativa descartada: dois flags (um por página) — duplicaria estado sem ganho, pois a sessão e os dados são compartilhados.

**D5 — Testes mínimos no harness existente (`_FakePublicState` em `tests/test_public_catalog.py`), três casos:**
1. Antes da primeira carga: `public_catalog_loaded` é `False` (estado inicial).
2. `load_public_catalog` com sucesso conclui com `public_catalog_loaded = True` e `public_products` preenchido.
3. `load_public_catalog` em falha conclui com `public_catalog_loaded = True` e mensagem de erro (não fica preso em "não concluído").
- A distinção render (condições da UI) é coberta pela inspeção manual descrita na task de verificação; testes de UI não fazem parte da suíte atual do projeto.

## Risks / Trade-offs

- [Flag nunca setada se `load_public_catalog` não for disparado (ex.: JS desabilitado)] → `on_load` é registrado nas duas páginas (voltix.py:7844, 7850); sem JS a aplicação já não funciona. Mesmo comportamento do loading atual.
- [`finally` seta `loaded = True` mesmo em falha] → intencional: falha tem ramo próprio (`public_catalog_message`) que prevalece sobre o empty; garantia de que "não concluído" não vira estado permanente.
- [Estado retido entre navegações Home↔Catálogo dentro do TTL] → `loaded = True` persiste na sessão; navegação subsequente não mostra loading desnecessário, coerente com o requisito de reuso de cache já existente.
- [Refiltro por categoria com catálogo genuinamente vazio pode exibir empty durante o refetch] → limitação pré-existente, fora do escopo (o estado inicial é o alvo da mudança).

## Migration Plan

Sem migração: var novo com default `False` não exige mudança de dados, backend ou dependências. Rollback = reverter o commit (nenhum estado persistido é afetado).

## Open Questions

_(nenhuma — escopo e comportamento aprovados pelo usuário.)_
