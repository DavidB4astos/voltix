# Corrigir hierarquia dos títulos no login interno

## Why

A auditoria registrou três elementos `h1` no DOM do login interno: a marca Voltix repetida no cabeçalho e rodapé legado, além do título da página. A tela deve ter um único título principal claro.

## What Changes

- Manter “Acesso interno” como o único título de nível principal.
- Renderizar as marcas reutilizadas do cabeçalho/rodapé como títulos de nível secundário, preservando texto e aparência.

## Fora do escopo

- Alterar os textos, o visual ou a navegação do cabeçalho/rodapé.
- Corrigir rótulos de formulário, preços, contraste ou outras telas.
- Alterar login, autorização, Xano ou dados.

## Impacto

Somente a semântica do componente reutilizável de marca e a especificação `internal-access`. Nenhuma mudança de backend ou dados.
