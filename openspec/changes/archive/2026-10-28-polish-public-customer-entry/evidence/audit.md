# Auditoria desktop — Voltix — 28/10/2026

## Escopo e objetivo
Revisão do aplicativo real em 1440px, com navegação pública e estados sem sessão. Objetivo: descobrir produtos e encontrar o acesso à conta para seguir a compra. Conferência adicional da conta em 1024px sem overflow. Mobile fora do escopo.

## Etapas e evidências
1. **Home:** [captura](01-home.png). Hero legível, CTA claro e procedência da imagem informada. O destaque do MX Master abre o produto correto.
2. **Catálogo:** [captura](03-catalogo.png). Total confirmado de 23 produtos. Vinte cartões exibem Imagem não disponível; o início da grade tem três espaços sem foto. Produto de teste e registro temporário também estão publicados.
3. **Busca e detalhes:** [resultado](04-busca.png), [produto](02-produto.png). MX Master retornou um produto. Detalhes mostram variação, SKU, valor e estoque; tentativa de adicionar sem sessão apresentou orientação de login. Nenhum item foi persistido.
4. **Carrinho sem sessão:** [captura](05-carrinho-sem-sessao.png). Orientação clara e ação azul de acesso; navegação chegou à conta.
5. **Minha conta pública:** [antes](06-conta-publica.png), [depois](10-conta-depois.png). Cadastro e login estavam disponíveis, mas faltava H1 visível. Corrigido com Minha conta e orientação curta, mantendo campos e envios.
6. **Checkout sem sessão:** [antes](08-checkout-sem-sessao.png), [depois](09-checkout-depois.png). Acesso corretamente exige conta, mas o link tinha pouca ênfase. Agora segue o CTA azul do carrinho; clique chegou a /cliente.
7. **Pedidos sem sessão:** [antes](07-pedidos-sem-sessao.png), [depois](11-pedidos-depois.png). Histórico protegido e sem exposição de pedidos. Ação de acesso agora segue o mesmo padrão e chegou a /cliente.

## Pontos fortes
- Cabeçalho, navegação e rodapé consistentes nas rotas visitadas.
- Home leva ao produto real correto; busca devolveu o resultado esperado.
- Fotos disponíveis têm atribuição e links de licença.
- Carrinho, checkout e pedidos orientam autenticação; não exibem sucesso fictício.

## Achados e prioridade
| Prioridade | Achado observado | Encaminhamento |
|---|---|---|
| Alta | 20/23 cartões mostram ausência de imagem | Próxima change: cobertura de imagens por produto, com correspondência de modelo, origem e licença verificáveis. Não substituir por imagem genérica nem inferir que o backend perdeu os arquivos. |
| Alta | Registros Notebook Voltix Teste Hp, TMP-VALIDB-20261015142856-A e mouse aparecem no catálogo público | Revisar curadoria/status e possíveis referências antes de qualquer inativação. Nenhuma remoção ou alteração de dados nesta auditoria. |
| Média | Conta pública não possuía H1 visível | Corrigido nesta change. |
| Média | Checkout/pedidos usavam link simples enquanto carrinho usava CTA azul | Corrigido nesta change, mantendo /cliente e guardas. |

## Acessibilidade observada
- Conta pública final: um H1 visível; títulos dos formulários preservados.
- CTA checkout/pedidos: 48px medidos, fundo #0866d9 e texto branco, nome acessível preservado.
- Teclado: Tab do retorno ao carrinho alcançou CTA de acesso com outline sólido.
- Sem overflow observado em conta a 1024px.
- Isto não é certificação WCAG: leitor de tela, zoom ampliado, todos os contrastes e validação completa de formulários não foram auditados.

## Verificação técnica da correção
- 165 testes existentes passaram em 1,585s.
- Compilação do aplicativo real chegou a 100% e o backend/frontend iniciaram; rotas finais renderizadas no navegador.
- Comparação AST: apenas customer_account_page, customer_checkout_page e customer_orders_page alteradas. State idêntico. Eventos, destinos navegáveis, nomes, tipos, required e disabled preservados.
- Estilos de entrada restritos a checkout/pedidos; título/intro restritos à conta.

## Limites e próximo incremento
Não houve login, criação de conta/endereço/pedido, alteração de carrinho autenticado ou simulação de pagamento. Os estados autenticados não foram revalidados nesta execução; evidências isoladas anteriores continuam sendo testes distintos, não prova de compra de ponta a ponta. Não foram usados screenshots antigos como evidência desta auditoria. Todos os PNGs são capturas desta execução, vistas e salvas sem substituição.

Próximo incremento recomendado: curadoria das imagens e dos produtos publicados, com plano e revisão antes de mudar dados Xano. Depois, teste integrado autenticado com conta de teste autorizada, separado da conferência visual.
