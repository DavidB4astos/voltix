## Context

`.vx-internal__sidebar` usa `position: sticky; top: 0; height: 100vh;` em grid de duas colunas (`246px minmax(0, 1fr)`). Em telas de notebook (1366×768 com barra do Windows e abas/favoritos do navegador), a altura útil do viewport fica em torno de 600 px, menor que a soma dos espaçamentos atuais da sidebar.

## Goals / Non-Goals

- **Goals:**
  - Garantir que o conteúdo da sidebar nunca ultrapasse visualmente o fundo `#071525`.
  - Manter `Ver loja`, card do usuário e `Sair da conta` visíveis sem corte em viewports de ~600 px de altura.
  - Evitar quebra artificial no meio do TLD de e-mail no card `Identidade`.
- **Non-Goals:**
  - Alterar breakpoints mobile ou componentes Python em `voltix/`.

## Decisions

1. **Compactação vertical + `overflow-y: auto` em `.vx-internal__sidebar`:** reduz espaçamentos excessivos mantendo a hierarquia visual e adiciona `overflow-y: auto` como proteção definitiva contra vazamento.
2. **Grid de valores em `.vx-profile__values`:** aumenta a largura mínima da coluna para `180px` e usa `overflow-wrap: break-word`.
