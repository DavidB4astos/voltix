## Why

A identidade visual do Voltix já foi consolidada (change arquivada `design-interface-voltix`), mas restam inconsistências pontuais de apresentação: mensagens de feedback, badges de status e botões são definidos caso a caso; carrinho, checkout e pedidos não têm um padrão uniforme de alinhamento e resumo; e há pequenos problemas de responsividade. Esta Change eleva a consistência visual e a legibilidade sem alterar comportamento.

## What Changes

- Padronizar primitivas de apresentação reutilizáveis — alerta de feedback com tom semântico, badge de status e botões padronizados (primário, secundário, destrutivo) — e aplicá-las às páginas existentes.
- Melhorar a apresentação de carrinho, checkout e pedidos (alinhamento de itens, resumo, totais e status), sem remover campos, ações ou mensagens.
- Alinhar cards do catálogo (imagem, preço e ações) de forma consistente em 375, 768 e 1280 px.
- Corrigir problemas de responsividade nesses três pontos de quebra.
- No painel administrativo, realizar apenas ajustes visuais simples (espaçamento, agrupamento e uso das primitivas compartilhadas), sem reestruturar a navegação.

Ficam fora desta Change: backend, banco, endpoints Xano, autenticação, regras de negócio, rotas, State, handlers, textos funcionais, reestruturação de navegação e quaisquer dependências pagas.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `visual-interface`: adiciona requisitos de apresentação (primitivas compartilhadas, alinhamento responsivo das superfícies de loja/compra e ajustes visuais simples do painel), preservando o comportamento existente.

## Impact

- Refatora apenas componentes de apresentação em `voltix/voltix.py`; reutiliza Reflex, Tailwind v4 e Radix Themes já configurados.
- Não altera State, handlers, rotas, permissões, Xano, dados ou Domain Model.
- Estende os testes Playwright já existentes em `e2e/` com verificações responsivas.
