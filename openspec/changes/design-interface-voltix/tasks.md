## 1. Identidade visual e componentes compartilhados

- [x] 1.1 Definir tokens centrais de cor, tipografia, espaçamento, raios, bordas, elevação e foco conforme o design aprovado; verificar contraste e compilar Reflex.
- [x] 1.2 Criar componentes Reflex reutilizáveis para shell de página, header/navegação, footer, títulos de seção, superfícies/cards e feedback; confirmar que links apontam somente para rotas existentes e que handlers de State permanecem inalterados.

## 2. Loja e conta do Cliente

- [x] 2.1 Aplicar identidade responsiva ao catálogo, cards, detalhes e variações de produto; verificar que dados, disponibilidade e ação existente de adicionar ao carrinho não mudaram.
- [x] 2.2 Atualizar apresentação de login/cadastro, perfil e gerenciamento de Endereços com componentes compartilhados; verificar campos, mensagens, handlers e permissões existentes.
- [x] 2.3 Aplicar o padrão visual ao carrinho e checkout, preservando estados, quantidades, totais e ações; verificar os testes existentes de carrinho e checkout.

## 3. Pedidos e área interna

- [x] 3.1 Atualizar listagem/detalhes de Pedidos e confirmação de pagamento simulado; verificar estados/mensagens e que ação de pagamento continua exclusiva a Pedido próprio elegível.
- [x] 3.2 Atualizar acesso interno e telas administrativas existentes de Categoria, Marca, Produto e Variação; verificar que controles condicionais e permissões de Administrador permanecem intactos.

## 4. Verificação responsiva e regressão

- [x] 4.1 Inspecionar as rotas existentes em larguras mobile (375 px), tablet (768 px) e desktop (1280 px); corrigir overflow, conteúdo ilegível, navegação inutilizável, estados vazios/loading/erro pouco distinguíveis e foco de teclado ausente.
- [x] 4.2 Executar compilação Reflex e suíte automatizada existente; validar visualmente os fluxos sem alterar APIs Xano, regras, autenticação, dados, Domain Model ou dependências.

## 5. Refinamento visual adicional (capturas atuais)

- [x] 5.1 Catálogo (`/catalogo`): estado de erro/vazio/loading como componente compacto e centralizado (ícone, título, descrição e botão "Tentar novamente" com largura limitada) e filtros em barra horizontal responsiva; preservar catálogo real, filtros e mensagens, sem mascarar falha de integração com dados fictícios.
- [x] 5.2 Área do Cliente (`/cliente`): centralizar o conjunto cadastro/login em grid responsivo (duas colunas no desktop, empilhado no mobile), com larguras máximas adequadas, padding/espaçamento entre campos e diferenciação visual entre cadastro e login; manter labels acima dos campos, handlers, validações e dados enviados ao Xano.
- [x] 5.3 Acesso interno (`/interno`): centralizar o login em card de largura controlada, alinhando título, descrição, campos e botão com espaçamento consistente; preservar autenticação, permissões e mensagens existentes.
- [x] 5.4 Rodapé compartilhado (`site_footer`/`page_shell`): padronizar padding, contraste e hierarquia e posicionar o rodapé com altura mínima de página para não ficar colado aos formulários; preservar os textos institucionais aprovados.
- [x] 5.5 Reexecutar `python -m unittest discover -s tests -p "test_*.py"`, `reflex compile --dry` e `openspec validate design-interface-voltix`.

## 6. Correções pós-validação visual

- [x] 6.1 Centralizar horizontalmente o container da Área do Cliente (`/cliente`) com largura máxima e espaçamento consistentes, eliminando o espaço vazio à direita.
- [x] 6.2 Centralizar horizontalmente o card do Acesso interno (`/interno`), preservando sua largura compacta.
- [x] 6.3 Reexecutar `python -m unittest discover -s tests -p "test_*.py"`, `reflex compile --dry` e `openspec validate design-interface-voltix`.
