# Design — hierarquia do login interno

## Decisão

Definir `as_="h2"` no `rx.heading` dentro de `brand_logo`. A tela de login `/interno` usa as marcas do cabeçalho e rodapé legados e mantém “Acesso interno” como o título principal de nível 1. A alteração preserva o texto e os atributos visuais do componente; o componente é compartilhado por cabeçalho e rodapé.

## Restrições

- Não mudar o título “Acesso interno”, os textos da marca ou estilos.
- Não modificar autenticação, navegação, chamadas ao Xano ou dados.
- Não incluir correções dos outros achados da auditoria.

## Verificação

Inspecionar o diff para confirmar que `brand_logo` continua com os mesmos estilos e texto, agora com nível 2, e que o título da tela permanece intacto. Validar a change com OpenSpec estrito e executar `git diff --check`. Sem login ou mutação remota.
