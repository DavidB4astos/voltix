# Observações administrativas — 30/10/2026

Capturas novas da aplicação real, conta de Administrador de teste, largura de viewport 1252 px após o usuário ampliar a prévia. Nenhuma lista de clientes carregada, upload ou operação de gravação acionada. Não usar a captura preliminar de login feita durante interação do usuário como evidência aceita; somente as capturas numeradas conferidas após estabilização entram no relatório.

## Etapas observadas
1. Clientes: orientação inicial, zero linhas de clientes, apenas módulo Clientes e nenhum formulário de login. aria-current acompanha a seleção. Página sem overflow horizontal (scrollWidth 1252).
2. Produtos: heading Produtos, formulários rotulados e lista de 41 cards no DOM, incluindo inativos/cadastros antigos de teste. Somente o módulo Produtos renderizado; scrollWidth 1239. A lista inteira e cada ação de escrita não foram auditadas.
3. Categorias/marcas: quatro labels associados a IDs únicos; duas seções, status textual, scrollWidth 1239. Navegação persiste ao rolar até Marcas: sidebar sticky top 0 e nav top 141. Uma captura inicial da rolagem foi rejeitada por não mostrar a barra lateral estabilizada; a substituta foi inspecionada.
4. Importação: somente módulo correspondente, nenhum arquivo selecionado, zero tabelas/confirmar no estado inicial. Explicação de que prévia não grava. Não foi executado upload, prévia ou confirmação reais.
5. Teclado/saída: Tab de Clientes para Produtos tem outline solid; Enter seleciona Produtos com aria-current page. Ir para o conteúdo coloca foco em internal-workspace-main. Sair da conta remove o workspace e apresenta campos vazios.

## Achados confirmados
- Login: inputs email/password têm labels.length 0, aria-label e aria-labelledby ausentes. A presença de texto próximo ou placeholder não equivale à associação persistente de um label. Recomendar IDs/labels explícitos em change própria, preservando eventos e payload.
- Login: três H1 no DOM (Voltix, Acesso interno, Voltix). Recomendar hierarquia de título da página e marcas sem H1 duplicado; não foi feita validação completa por leitor de tela.
- Produtos: primeiro preço aparece 119.9 na coluna Preço (R$). Recomendar apresentação pt-BR com duas casas, sem arredondar/mudar o valor armazenado. É clareza visual, não prova de erro contábil.
- Registros de teste antigos aparecem no catálogo administrativo. Não são removidos por esta auditoria; inativos são legitimamente preservados para relações históricas. Avaliar futuramente separação de ambiente/dados de demonstração sem exclusão automática.

## Limites e riscos visuais
Texto auxiliar é pequeno e claro em várias telas; contraste, zoom a 200%, leitor de tela e navegação completa por todos os controles precisam de prova própria. Não afirmar conformidade WCAG nem falha de contraste a partir das capturas. Não testados gravação, cancelamento de importação, expiração de sessão, compra, rollback ou permissões remotas negativas nesta auditoria. A passagem para Funcionário aguarda login do usuário.
