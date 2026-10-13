## Why

O Voltix não possui uma página inicial pública: a rota `/` hoje abre direto o acesso interno. Um e-commerce de tecnologia premium precisa de uma vitrine pública com identidade visual forte (home com hero, benefícios, categorias e vitrine de produtos) que conduza o visitante ao catálogo, usando a mesma arquitetura Reflex + Xano já existente.

## What Changes

- Criar uma Home pública premium na raiz `/`, com: barra superior azul-marinho (logo, menu horizontal, conta e carrinho), hero claro com título à esquerda, imagem de eletrônicos à direita e botão "Explorar produtos", faixa de benefícios, grid de categorias, vitrine de produtos em grid responsivo e rodapé institucional.
- Reutilizar dados reais do Xano já expostos pelo State (categorias e produtos públicos), sem novas APIs ou alterações de backend.
- Mover o acesso interno existente da rota `/` para `/interno`, preservando login, autenticação e permissões intactos (apenas relocação de rota + atualização de links internos).
- Atualizar os links "Acesso interno" dos cabeçalhos das páginas públicas para `/interno`.
- Aplicar a identidade Voltix (azul-marinho `#071525`, azul `#0866D9`, ciano `#00B8D9`, branco, fundo `#F5F7FB`), com componentes responsivos (375 / 768 / 1280 px).
- Manter as mesmas regras de negócio, autenticação, regras de domínio e integrações Xano.

Fica fora do escopo: alterações em regras de negócio, APIs Xano, autenticação, persistência, Domain Model, criação de funcionalidades comerciais novas (checkout, pedidos, contas), dependências visuais novas e mudanças nos fluxos existentes do catálogo/carrinho/cliente.

## Capabilities

### New Capabilities

- `public-home`: homepage pública premium do Voltix — layout, navegação pública, hero, benefícios, categorias, vitrine de produtos e responsividade, alimentada por dados públicos do Xano.

### Modified Capabilities

Nenhuma. A relocação do acesso interno de `/` para `/interno` é detalhe de implementação (rota), sem mudança de requisito comportamental da capability `internal-access`.

## Impact

- `voltix/voltix.py`: novo `home_page()`, possíveis extensões em helpers compartilhados (`site_header`, `site_footer`, `page_shell`), `app.add_page` para `/` e `/interno`, atualização do link interno nos cabeçalhos públicos, e adições pontuais de State para a vitrine da Home (reutilizando chamadas Xano existentes).
- Testes: a suíte automatizada pode conter asserts sobre a rota `/` ou sobre o módulo de acesso interno; a relocação de rota deve ser validada por `python -m unittest` e `reflex compile --dry`.
- Sem dependências novas, sem alterações em Xano/XanoScript, sem mudanças em schemas ou dados.