# Refinar os acessos e o rodapé no desktop

## Why

As referências visuais mostram três pontos de inconsistência no desktop: os cartões de cadastro/login de Cliente ficam altos demais, o rodapé público ocupa muito espaço vertical e a página de acesso interno usa navegação e cartão de login que destoam do cabeçalho da loja.

## What Changes

- Refinar os cartões de cadastro e login de Cliente, permitindo alturas adequadas ao conteúdo.
- Compactar o rodapé público sem remover links, avisos ou conteúdo.
- Usar no acesso interno o cabeçalho desktop compartilhado, marcar a rota atual e alinhar a apresentação do login à identidade Voltix.
- Aplicar uma composição de login interno centralizada entre cabeçalho e rodapé.

## Fora do escopo

- Alterar campos, textos, validações, handlers, autenticação, sessão, permissões, rotas ou chamadas ao Xano.
- Modificar layouts mobile/tablet, imagens, páginas autenticadas ou regras de negócio.
- Alterar dependências ou introduzir funcionalidades.

## Impacto

Mudanças visuais desktop a partir de 1024 px nos cartões `/cliente`, no shell público usado pelo rodapé e no acesso `/interno` sem sessão. Navegação e conteúdo existentes permanecem disponíveis.
