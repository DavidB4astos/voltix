## Context

See [proposal.md](./proposal.md) and [specs/visual-interface/spec.md](./specs/visual-interface/spec.md). A aplicação é um módulo Reflex único, `voltix/voltix.py`, com as rotas `/interno`, `/`, `/catalogo`, `/cliente`, `/carrinho`, `/checkout` e `/pedidos`. Já existem tokens centrais (`COLOR_*`, `RADIUS`, `CARD_SHADOW`, `FOCUS_STYLE`, `_TONE_COLORS`) e helpers compartilhados (`page_shell`, `site_header`, `site_footer`, `surface_card`, `section_heading`, `brand_logo`, `form_field`, `feedback_text`, `status_panel`, `empty_state`, `loading_text`). Todas as páginas usam `page_shell` + `site_header`. Os testes Playwright já estão configurados em `e2e/`.

## Goals / Non-Goals

**Goals:**

- Padronizar primitivas de feedback, badge de status e botões, aplicando-as uniformemente.
- Melhorar alinhamento e legibilidade de catálogo, carrinho, checkout e pedidos; corrigir responsividade em 375/768/1280 px.
- Realizar apenas ajustes visuais simples no painel administrativo.
- Preservar handlers, State, rotas, textos funcionais e integrações Xano.

**Non-Goals:**

- Reestruturar navegação do painel, rotas, páginas ou conteúdo funcional.
- Introduzir dependências pagas, novos frameworks visuais ou tabelas complexas.
- Alterar backend, banco, autenticação, permissões, dados ou regras de negócio.

## Decisions

### Estender os helpers existentes em vez de criar um novo design system

Adicionar `feedback_alert`, `status_badge` e helpers de botão que reutilizam os tokens e helpers já existentes; manter compatibilidade com `feedback_text` e migrar os pontos de uso em pequenos lotes.

Alternativa considerada: introduzir um pacote de design ou uma hierarquia profunda de componentes. Rejeitada por complexidade desnecessária e risco de regressão.

### Edições somente de apresentação, preservando contratos de comportamento

Tratar expressões de State, handlers, parâmetros de rota e textos funcionais como contratos: envolver/reorganizar apenas a apresentação. Manter rótulos e `type="submit"` exatos usados pelos testes Python e Playwright.

Alternativa considerada: simplificar telas removendo/reposicionando ações. Rejeitada por ser uma Change de apresentação.

### Alinhamento responsivo por layout intrínseco

Usar grid/flex responsivos e larguras máximas; evitar larguras fixas e overflow horizontal. Verificar em 375, 768 e 1280 px.

Alternativa considerada: implementações separadas para desktop e mobile. Rejeitada por duplicação e divergência visual.

### Painel administrativo: apenas visual

Limitar o painel a espaçamento, agrupamento em cards e uso das primitivas; não alterar navegação, estrutura das páginas, controles condicionais nem permissões.

Alternativa considerada: reorganizar o painel em abas/rotas. Rejeitada por estar fora do escopo aprovado.

## Risks / Trade-offs

- [Alterar rótulos ou `type="submit"` pode quebrar testes Python/Playwright] -> Manter textos e tipos exatos; validar com as suítes.
- [Refatorar apresentação pode mexer em handlers/State] -> Edições pequenas por grupo de páginas; revisar diffs de `diff`.
- [Overflow em telas estreitas com rótulos longos] -> Testar 375/768/1280 e ajustar `wrap`/larguras.
- [Escopo do painel crescer além do visual] -> Limitar a ajustes simples e não reestruturar navegação.

## Migration Plan

1. Adicionar as primitivas e aplicá-las transversalmente.
2. Ajustar carrinho, checkout e pedidos.
3. Ajustar catálogo e cards.
4. Ajustes visuais simples no painel administrativo.
5. Validar: Playwright (375/768/1280), suíte Python (`python -m unittest discover -s tests`), `reflex compile` e `openspec validate melhorar-ux-ui-ap2 --strict`.

Rollback por grupo de páginas se algum ajuste afetar navegação, ações ou autorização; não há migração de dados.
