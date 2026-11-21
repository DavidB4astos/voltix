## Context

O `README.md` deve ser claro, autoexplicativo, alinhado a `docs/project-overview.md`, `docs/domain-model.md` e às rotas reais implementadas em `voltix/voltix.py` (`/`, `/catalogo`, `/cliente`, `/carrinho`, `/checkout`, `/pedidos`, `/interno`, `/interno/recuperar-senha`, `/interno/redefinir-senha`).

## Goals / Non-Goals

- **Goals:**
  - Atender integralmente aos 7 tópicos solicitados para o manual de uso no GitHub.
  - Garantir zero exposição de credenciais, tokens, URLs privadas ou dados reais de clientes.
- **Non-Goals:**
  - Alterar código de aplicação ou criar capturas contendo registros reais.

## Decisions

1. **Fonte de verdade:** usar apenas comportamentos, rotas, status e regras verificadas em `docs/` e `voltix/voltix.py`.
2. **Dados fictícios:** todos os exemplos de utilização usam dados claramente ilustrativos (ex.: `Maria Silva`, `cliente.exemplo@voltix.local`, `VTX-DEMO-...`).
