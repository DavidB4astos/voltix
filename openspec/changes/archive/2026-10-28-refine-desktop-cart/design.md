## Decisions
Extrair componentes puros de item e conteúdo autenticado com callbacks recebidos. A página real continua ligando State.load_cart, State.update_cart_item(item.id), State.remove_cart_item(item.id), State.cart_total e o guard customer_authenticated. Nenhuma entrada do usuário pode substituir valores comerciais. CSS .vx-cart apenas nessa página. Resumo e continuação existem quando há itens; durante cart_loading, as ações ficam desabilitadas e um aviso identifica os valores como os últimos confirmados. Sem itens, carregamento ou feedback prevalecem sobre afirmação prematura de vazio. Formulário mantém min=0 e step=1; zero continua remoção pelo evento existente. Mostrar quantidade confirmada separada do rascunho digitado.

## Verification
Suíte de carrinho e suíte geral, compilação, comparação AST para preservar State/handlers e outras páginas. Prévia separada usa os mesmos componentes de apresentação com fixtures de itens, indisponível, vazio, loading e erro; callbacks inertes. Nenhum token, dado real, endpoint ou bypass na aplicação. Navegador para layout/foco/labels em 1440/1024 e controle estreito. Funcionalidade de mutações é coberta pelos testes existentes com fake HTTP; a prévia visual não comprova integração autenticada.

## Risks
Não há sessão cliente autorizada para testar mutações reais; registrar limite. Não usar status visual genérico como confirmação de persistência. Não restaurar/commitar lockfiles gerados pelo servidor durante esta change.
