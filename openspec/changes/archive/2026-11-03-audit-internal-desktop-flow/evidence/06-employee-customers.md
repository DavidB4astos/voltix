Etapa 6 — Clientes (Funcionário), conferência integrada em 03/11/2026.

Perfil visível: Usuario Funcionario Teste / Funcionário. A navegação interna mostra somente Clientes; Produtos, Categorias e marcas e Importação não aparecem. A tela aberta permaneceu em Clientes, sem uma lista carregada. A área de consulta informa que a consulta começa vazia e oferece ações explícitas de busca/carregamento; nenhuma foi acionada nesta auditoria, portanto não houve solicitação da lista nem mutação de dados.

Teclado: Tab percorreu o link “Ir para o conteúdo”, a marca que leva à loja pública e o botão Clientes. O botão Clientes recebeu foco visível. A navegação foi possível sem usar o mouse.

Conferência do código local: `State.select_internal_section` aceita `clientes` para perfil interno autenticado ativo e acrescenta `produtos`, `catalogo` e `importacao` apenas para ADMINISTRADOR. A navegação renderiza essas três opções somente para ADMINISTRADOR, e o painel protegido também condiciona essas seções ao papel de Administrador. Isso confirma a guarda do frontend local; não substitui uma verificação independente de autorização no Xano.

Limites registrados por decisão do usuário: não será produzida nem salva captura PNG do perfil Funcionário. A tentativa de acesso por links/rotas diretas às seções administrativas não foi feita. Não foram carregados clientes, testadas consultas, nem verificadas permissões remotas do Xano. A guarda observada é do frontend local e não comprova autorização independente no Xano. Não declarar conformidade WCAG com esta conferência.
