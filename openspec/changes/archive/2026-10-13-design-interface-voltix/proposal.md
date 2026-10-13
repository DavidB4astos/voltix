## Why

As funcionalidades principais do Voltix já estão disponíveis, mas as páginas Reflex ainda usam padrões visuais básicos e inconsistentes. Uma identidade visual coesa e responsiva tornará a loja e a área interna mais profissionais sem mudar o comportamento de negócio.

## What Changes

- Definir uma identidade visual única de tecnologia premium com azul-marinho, ciano elétrico e superfícies claras, aplicada de modo coerente em desktop e mobile.
- Padronizar header/navegação, footer, tipografia, espaçamentos, cores, botões, formulários, cards, tabelas, mensagens, estados vazios e carregamento.
- Atualizar Home/acesso interno, catálogo e detalhes de produto, conta/login/cadastro do Cliente, carrinho, checkout, pedidos e gestão administrativa.
- Reutilizar componentes Reflex simples para elementos compartilhados e manter conteúdo, ações, rotas, permissões, dados e mensagens funcionais existentes.

Ficam fora do escopo mudanças em regras de negócio, APIs Xano, autenticação, persistência, Domain Model, criação de funcionalidades novas, serviços/frameworks visuais adicionais ou alterações ao fluxo comercial.

## Capabilities

### New Capabilities

- `visual-interface`: identidade visual compartilhada e comportamento de apresentação responsivo das interfaces existentes do Voltix.

### Modified Capabilities

Nenhuma. A mudança altera apresentação e consistência de UI, sem modificar contratos funcionais das capacidades de negócio.

## Impact

- Refatora componentes de apresentação nas páginas existentes de `voltix/voltix.py` e configura estilos/tema Reflex quando necessário.
- Reutiliza Reflex, Tailwind v4 e Radix Themes já configurados; não requer dependências novas nem alterações em Xano, autenticação, schemas, dados ou Domain Model.
- Abrange estados funcionais já existentes: carregamento, erro, sucesso, vazio, indisponível e controles desabilitados.
