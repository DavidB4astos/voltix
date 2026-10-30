## Why
O painel interno acumula login e todas as áreas em uma página longa, com identificação repetida e pouca orientação. Após concluir C4, o usuário autorizou começar pelo acabamento premium do painel interno desktop.

## What Changes
- Separar visualmente acesso não autenticado e área de trabalho autenticada.
- Criar navegação lateral navy/cyan e cabeçalho discreto, com uma seção de trabalho por vez.
- Clientes disponível para Funcionário e Administrador; Produtos, Categorias e marcas e Importação apenas para Administrador, reutilizando componentes e handlers existentes.
- Manter identidade, saída e acesso à loja claros, sem expor e-mail em um cartão de destaque.

## Capabilities
### New Capabilities
- internal-workspace: organização visual e navegação interna por perfil.
### Modified Capabilities
Nenhuma regra de negócio alterada.

## Impact
Frontend Reflex e CSS local escopado; estado de seleção e testes de navegação. Sem mudança Xano, rotas públicas ou dependências. Fora de escopo: telas novas de pedidos/histórico/atendimentos, métricas inventadas, redesenho detalhado de formulários/tabelas administrativos e mobile como foco de aprovação. Preservar uso básico em telas estreitas.
