# Home desktop — referência Apple

Implementado em 27/10/2026 a pedido do usuário.

- Referência observada: https://www.apple.com/br/ (estrutura e captura no navegador).
- Hero centralizado com tipografia grande, CTA arredondado e fotografia panorâmica local; identidade navy/cyan preservada.
- Barra desktop reduzida de 88 para 64px; categorias compactadas; destaques e editorial em superfícies neutras.
- Categorias abrem o catálogo filtrado; produtos abrem os detalhes existentes antes da grade. Voltar à Home limpa o filtro.
- Parâmetros inválidos não abrem detalhes; identificadores de categoria continuam validados contra a lista pública existente.

Verificação: 149 testes passaram (incluindo 4 novos cenários de entrada contextual), Reflex compile concluído e OpenSpec strict válido. Navegador: Monitores selecionado, mouse com detalhes abertos, retorno com 5 categorias e 3 destaques, parâmetros inválidos com Todas as categorias e sem detalhes. Layout desktop conferido em 1024 e 1440px, sem overflow horizontal; controle a 390px confirmou estilos desktop desativados.

Limites: fotos atuais permanecem, incluindo repetição do mouse na seção editorial; uma nova seleção de fotos autorizadas ainda é necessária para melhorar a apresentação. Não foi feita auditoria de acessibilidade completa nem compra/autenticação. O DOM inclui o rótulo Connection Error já observado antes; a navegação e os dados descritos acima foram renderizados e conferidos. Nenhum commit, push ou arquivamento.
