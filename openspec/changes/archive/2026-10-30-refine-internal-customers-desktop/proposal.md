## Why
A consulta de clientes já está segura e funcional, mas filtros, comandos, resultados e detalhe têm pouca hierarquia visual. O usuário autorizou seguir com esta etapa após o encerramento do shell interno.

## What Changes
- Dar aos filtros uma barra coerente, com busca explícita, limpar e atualizar identificáveis.
- Refinar tabela, status e paginação sem alterar consulta, ordenação ou limites.
- Organizar detalhe somente leitura em região nomeada, com campos protegidos e fechamento acessível.
- Distinguir estado inicial, carregamento, vazio e erro usando o estado existente, sem dados ou indicadores inventados.

## Capabilities
### Modified Capabilities
- internal-customers: apresentação desktop da consulta existente.

## Impact
Somente componente Reflex e CSS local. Preservar handlers, contratos, máscaras e permissões de Funcionário/Administrador. Fora de escopo: Xano, histórico, atendimentos, edição/exportação, novos dados, métricas e redesign mobile. QA visual pode usar fixtures fictícias isoladas, identificadas como tais; não equivalem a teste remoto.
