## Why
A Home precisava cumprir os requisitos de fotografia, créditos e seção editorial, além de melhorar a hierarquia visual e a navegação. O usuário aprovou o refinamento inicial, a barra desktop e, depois, o uso de apple.com/br como referência de composição.

## What Changes
- Hero sem eyebrow, fotografia local aprovada com proveniência e fallback gráfico.
- Benefícios em faixa, categorias tipográficas numeradas, vitrine de até quatro produtos com correspondência verificável de nome e imagem aprovada.
- Skeleton, erro com retry, catálogo vazio e ausência de produtos elegíveis como estados distintos.
- Editorial com foto aprovada, crédito e descrição fiel; omissão se faltar a imagem.
- Desktop (>=1024px): hero centralizado, CTA arredondado, categorias compactas e superfícies neutras. Navy/cyan e assets próprios preservados, sem copiar marca ou imagens Apple.
- Barra desktop pública com Início/Produtos, conta/carrinho e acesso interno secundário; logo retorna à Home. Faixa secundária de categorias omitida somente no desktop. Cabeçalho legado preservado em telas menores e área interna.
- Categorias levam a /catalogo?category_id=<id>; produtos a /catalogo?product_id=<id>. A entrada valida os parâmetros e usa os fluxos existentes de filtro/detalhes. Detalhes aparecem antes da grade. A Home limpa filtros anteriores.

## Capabilities
### New Capabilities
Nenhuma nova área de negócio.
### Modified Capabilities
- public-home: apresentação, navegação pública desktop e entrada contextual no catálogo.

## Impact
Arquivos: voltix/voltix.py (Home, cabeçalho público, dois eventos de entrada e posição do painel de detalhes), assets/voltix-home.css, assets/voltix-navigation.css e testes relacionados. A change contém especificação, tarefas e evidências.

## Out of Scope
Backend, APIs Xano, dados, autenticação, autorização, regras de compra, dependências e lockfiles. Nenhuma publicação ou push. Novas fotos, busca, mudança do rodapé e demais sugestões da revisão continuam propostas futuras, não implementadas. Mobile não recebe novo redesenho na extensão desktop; seus links compartilham a correção funcional.

## Authorization
A extensão desktop e a navegação contextual substituem as restrições dos rascunhos anteriores sobre não modificar site_header, State e destinos, exclusivamente para os elementos descritos acima. A mudança inicial também implementou o layout responsivo já previsto; não se iniciou outro redesenho mobile.
