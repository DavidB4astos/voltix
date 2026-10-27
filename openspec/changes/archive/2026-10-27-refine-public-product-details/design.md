## Decisions
Usar seção semântica com título H2 e H3 para variações/especificações. CSS .vx-product-detail, carregado apenas no catálogo. Desktop >=1024px com colunas minmax e imagens object-fit contain. Manter rx.foreach das variações ativas e evento add_to_cart(variation.id), quantidade fixa atual de um. Botões desabilitados com cart_loading ou estoque zero. Formatação de preço exclusivamente de apresentação com NumberVar .2f e separador decimal brasileiro; nenhum cálculo comercial alterado. Reutilizar mapeamento seguro de créditos aprovado já utilizado pelos cards.

## Verification
Comparar AST dos handlers/State e demais páginas antes/depois. Suíte existente e compilação. Navegador em desktop: abrir/fechar, foto/crédito e placeholder, preço, variações, acesso por teclado e aviso de login sem sessão. Não efetuar compra ou criar dados Xano. Cenários de estoque zero/sem variações: verificar composição e parsers com fixtures caso não existam nos dados reais. Conferir 1024 e 1440px e controle estreito sem redesenho mobile.

## Risks
API pode limitar requisições; evitar recargas excessivas. Não confundir placeholders com fotografias reais. Testes de carrinho autenticado não fazem parte desta revisão visual; autoridade sobre preço e estoque permanece no Xano.
