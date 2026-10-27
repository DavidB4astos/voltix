## Context
Frontend Reflex, dados públicos no Xano e desenvolvimento incremental com OpenSpec. A mudança existente foi ampliada por autorização do usuário para cabeçalho desktop e referência Apple. Não há novo framework ou serviço.

## Decisions
1. Home composta por hero, benefícios, categorias, destaques e editorial; classes sob .vx-home. A folha da Home só é carregada na Home.
2. Hero usa assets/demo/vtx-editorial-setup.jpg com proveniência visível. Se indisponível, mostra painel gráfico próprio. Desktop centraliza título/CTA e usa recorte panorâmico; mobile mantém conteúdo/CTA antes da imagem.
3. Destaques filtrados na apresentação por nome e URL local aprovada no manifesto, no máximo quatro; sem preço ou disponibilidade. Nunca preencher posições com imagens de outro SKU. Créditos de autor, fonte e licença permanecem visíveis.
4. Editorial usa vtx-demo-004.jpg (vista inferior do MX Master 3S), heading Precisão em cada detalhe e descrição fiel. A repetição da fotografia é uma limitação conhecida do acervo, não uma correção concluída.
5. Erro fora de retry tem precedência sobre loading, seguido de vazio e produtos. Skeleton sem animação. Respeitar prefers-reduced-motion e foco visível.
6. Cabeçalho público tem variante desktop >=1024px, altura 64px, logo/Home, Início/Produtos, conta/carrinho e acesso interno secundário; legado preservado em telas menores e páginas internas. CSS sob .vx-navigation e seletor específico da faixa de categorias.
7. Links contextuais usam query parameters. enter_public_catalog valida identificadores ASCII numéricos curtos, a categoria continua validada contra a lista pública pelo loader existente; ID de produto deve ser positivo. Erros de item inexistente usam o tratamento existente. Não há acesso privilegiado.
8. enter_public_home limpa categoria, busca e detalhe selecionado antes de carregar dados públicos. O cache existente continua em uso. O painel de detalhes do catálogo precede a grade para tornar o item escolhido visível.
9. Referência observada: https://www.apple.com/br/ em 27/10/2026. Adotar hierarquia clara, uma mensagem por seção, CTA simples e superfícies neutras; manter identidade e assets Voltix.

## Scope and Risks
Sem alterações em APIs, autenticação, estoque, dados, dependências ou lockfiles. Outras mudanças locais do repositório não pertencem a esta entrega. Fotos atuais possuem enquadramento e resolução limitados; substituição depende de novos assets adequados e autorizados. Promessas de prazo, garantia e suporte foram substituídas por funcionalidades comprovadas, após aprovação do usuário.

## Verification
149 testes aprovados, compilação Reflex e OpenSpec strict válidos na última implementação. Navegação real conferida: categoria Monitores, produto MX Master 3S, retorno à Home e parâmetros inválidos. Evidências anteriores de estados simulados são históricas e identificadas como tal. A revisão final percorreu os links por teclado e comprovou recuperação do loader após HTTP 503 em servidor local isolado, sem alterar Xano. Ver evidence/final-review.md.

## Rollback
Reverter o commit desta change restaura código e estilos versionados anteriores. Não há migração de dados ou alteração remota a desfazer. Não reverter outras mudanças locais para desfazer esta entrega.


## Revisão de conteúdo aprovada — 27/10/2026
O usuário aprovou substituir prazo de envio, garantia estendida e suporte não documentados por funcionalidades comprovadas: categorias, detalhes/variações e conta com histórico de pedidos. Remover também entrega rápida da frase do hero. Não introduzir novas regras de negócio.
