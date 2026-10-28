## Context
Navegação pública revisada no aplicativo real em desktop. Carrinho já oferece CTA azul e claro. Checkout/pedidos exibem links simples. Minha conta pública inicia em dois H2, sem H1 visível.
## Decisions
Adicionar um H1 somente ao ramo público da conta; ramo autenticado já tem seu próprio H1. Reutilizar estilo do CTA existente em folha pequena compartilhada, com seletores restritos aos dois estados e foco visível. Sem troca de handlers ou URLs.
## Verification
Capturas antes/depois, inspeção de H1 e links acessíveis, foco por teclado, destino da navegação, comparação AST, suíte e compilação. Não criar pedidos, pagamentos, contas ou endereços reais.
