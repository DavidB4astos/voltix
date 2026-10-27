# Cabeçalho desktop — Voltix

Data: 27/10/2026. Escopo autorizado: melhorar a barra superior desktop e testar seus acessos. Mobile e área interna preservados.

## Decisão sobre Catálogo público
O acesso ao catálogo é útil e permanece. No desktop, o rótulo passou a Produtos, com link para /catalogo. A distinção público/interno continua na entrada Acesso interno, que agora tem menor destaque visual. A faixa branca de categorias foi ocultada somente no desktop porque seus links repetiam /catalogo sem filtro; a lista no corpo da Home continua presente.

## Alterações
- Barra navy única, alinhada ao grid de 72rem, fixa durante a rolagem desktop.
- Início e Produtos como navegação textual; conta/carrinho como ações identificadas.
- Indicação de página atual por sublinhado e aria-current.
- Logo desktop para a Home nas páginas públicas.
- Variante anterior integralmente preservada abaixo de 1024px e na área interna.
- CSS exclusivo em assets/voltix-navigation.css; sem alteração de State, autenticação, APIs ou regras de negócio.

## Verificações
1. Antes da edição: catálogo, conta, carrinho e acesso interno abriram suas telas.
2. Depois da edição: Produtos abriu Catálogo de produtos; Minha conta abriu o formulário de cliente; Carrinho abriu a mensagem de acesso para visitante; Acesso interno abriu seu login. Nenhum formulário enviado.
3. Logo e Início retornaram à Home; Explorar produtos continuou abrindo o catálogo.
4. Produtos indicou aria-current=page no catálogo e Início na Home. Tab de Início moveu foco para Produtos com outline sólido de 2px.
5. Em 1024/1280/1440px, nenhuma sobreposição ou overflow; links com altura mínima de 48px. Versão antiga escondida no desktop.
6. Controle 390px: versão nova display:none, antiga display:block, faixa de categorias presente e sem overflow global. Não houve redesenho mobile.
7. py_compile OK; 145 testes OK; Reflex 0.9.12 compilou em 35,232 segundos; OpenSpec strict válido.
8. Auditoria AST confirma que somente site_header e o wrapper da faixa da Home mudaram. O componente legado foi preservado. Lockfiles anteriores à compilação foram restaurados.

## Limites
Teste de navegação sem autenticação ou compras. Não testa sessões de clientes autenticados nem acessibilidade completa. Há um elemento Connection Error no estado acessível do navegador, mas as páginas e destinos testados renderizaram; esta mudança não diagnostica a conexão do backend. Não houve commit, publicação ou arquivamento.

## Evidência visual
