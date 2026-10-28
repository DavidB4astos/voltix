# Verificação do carrinho desktop — 28/10/2026

## Código e controle de regressão
- A implementação estava em andamento desde 27/10 e foi retomada antes do encerramento. Apenas customer_cart_page e três componentes puros de apresentação foram adicionados/alterados. Comparação AST confirma State, handlers de quantidade/remoção, payloads, parsers e demais páginas preservados.
- 165 testes existentes passaram novamente em 2,188 s em 28/10. Incluem carrinho vazio, preservação de confirmação após erro, sessão de Cliente, quantidade zero/remover, quantidade fracionária rejeitada e regras comerciais/autorização. Não equivalem a teste end-to-end autenticado real.
- A página real mantém o guard customer_authenticated. Em 27/10, a conferência do site existente sem sessão mostrou apenas Acesso ao carrinho e convite para entrar, sem dados autenticados.

## Prévia isolada autorizada pelo usuário
- O usuário escolheu explicitamente dados de teste isolados. Usou-se projeto separado no diretório de trabalho, frontend localhost:3012 e backend de transporte Reflex local em 127.0.0.1:8012. Nenhuma dependência foi instalada/atualizada no ambiente virtual do Voltix; os pacotes frontend gerados pertencem à prévia de trabalho.
- A prévia final extrai via AST somente CartItemEntry e as três funções puras do arquivo real. Não importa o App/State do Voltix, não lê sua .env e não oferece rota de bypass na aplicação real. Callbacks de refresh/update/remove apenas escrevem uma mensagem de prévia no console. O checkout local da prévia é inerte. Nenhum login, compra ou mutação Xano efetuado.
- A moldura (header e main) da prévia é simplificada. As verificações visuais se referem ao conteúdo compartilhado do carrinho; não são uma auditoria integral do shell autenticado em produção.

## Resultados observados no navegador
- Preenchido: duas linhas fictícias, nomes H2, variações, SKU, disponibilidade, preço unitário, subtotal, resumo e total R$ 1089,70, sem botão aninhado em link.
- Edição: digitar 3 manteve Quantidade confirmada: 2; o rascunho não altera a confirmação. Tab alcançou Atualizar quantidade de [produto/SKU], com outline solid. Valor devolvido a 2 antes da captura. Não se afirma persistência por callback inerte.
- Vazio: mensagem Seu carrinho está vazio e navegação para catálogo; sem resumo/checkout.
- Erro inicial: mensagem de falha visível e Atualizar carrinho habilitado; zero regiões de carrinho vazio, sem falsa confirmação.
- Carregamento: os seis botões de refresh/update/remove/continuação ficaram desabilitados, assim como os dois inputs. Nenhum link de checkout. Total confirmado continuou R$ 1089,70 e aviso de atualização permaneceu visível.
- Indisponível: linha fictícia com estoque zero e quantidade confirmada 2 permaneceu visível, com correção e remoção preservadas. Valores R$ 24,70 e subtotal R$ 49,40. Não houve escrita para produzir este estado.
- Precisão textual: 0 -> R$ 0,00; 12 -> R$ 12,00; 12.3 -> R$ 12,30; 12.35 -> R$ 12,35; 9007199254740993.12 -> R$ 9007199254740993,12; 0.0010 -> R$ 0,0010. Sem conversão para float ou perda de precisão extra.
- 1440px: duas colunas, dois itens, zero overflow horizontal e zero controles interativos aninhados. 1024px: duas colunas sem overflow; label associado ao input, min=0, step=1. Controle 390px: uma coluna, sem overflow. Não constitui redesenho/revisão completa mobile.

## Limites e arquivos locais
- Mutações autenticadas e checkout real não foram executados. As regras são preservadas por AST e testes existentes; a prévia não substitui um teste com conta de Cliente.
- O servidor de prévia usa Granian embedded apenas como transporte local de teste, sem alterar o iniciador padrão/configuração do produto.
- O rótulo genérico Connection Error faz parte do DOM Reflex; os cenários estáticos acima renderizaram e as navegações da prévia funcionaram. Não se afirma estabilidade prolongada ou conformidade WCAG integral.
- Lockfiles regenerados pelo Reflex são alterações locais anteriores, excluídas deste commit. Nenhuma alteração Xano, autenticação, frete, descontos, reserva de estoque ou imagem inventada.

Compilação final do aplicativo real em 28/10: concluída em 11,192 s, com saída de frontend isolada no diretório de trabalho. AST novamente conferido contra HEAD.
