# Implementação local — 29/10/2026
- Nova change validada antes da implementação, limitada à apresentação e seleção interna.
- Shell navy/cyan escopado a vx-internal, sidebar, título/descrição, identidade compacta e saída. Sem links ou indicadores de funcionalidades futuras.
- Login separado do shell autenticado; seções reutilizam conteúdo e handlers existentes, com guards administrativos preservados.
- Seleção inicia/reset em clientes; valores desconhecidos, payloads de tipo incorreto e sessão/perfil não autorizado são rejeitados. Nenhuma chamada de API ou mutação adicionada à seleção.
- 185 testes passaram, incluindo três novos testes de seleção por perfil/guards/reset usando State real. Compilação Reflex 100%.
- Folha de estilo registrada no App e escopada por classe; condicionamento único de login/workspace simplifica transição de conteúdo.
- A prévia precisou reiniciar o processo de interface e habilitar escrita em arquivos temporários de tipos. Sem nova dependência versionada; não confundir essa recuperação local com alteração do produto.
- Pendente: capturas desktop e navegação autenticada dos dois perfis, teclado e logout. Não arquivar antes dessa verificação.

## Retomada em 30/10/2026
- Suite completa novamente: 185 testes, OK (2,086 s). Ajustado o teste legado da interface de importação para localizar o novo shell sem remover a verificação do guard administrativo nem dos handlers.
- Compilação Reflex 100%; change validada em modo strict. git diff --check sem erros.
- Administrador de teste autenticado: quatro seções disponíveis, seleção e título correspondentes; conteúdo de Clientes ausente em Produtos e formulário de produto ausente em Importação. Sem overflow horizontal a 1440px.
- Ativação de Categorias e marcas por Enter, com foco cyan de 3px e aria-current na seção selecionada. Logout removeu o workspace e mostrou somente login.
- Capturas admin-clientes, admin-produtos, admin-categorias e admin-importacao registradas sem carregar clientes ou executar operações de catálogo.
- Ajustado padding do cartão do conteúdo após inspeção; confirmar visual atualizado com o segundo perfil.
- Dependências geradas guardadas em .local-backup/2026-10-30-lockfiles-internal-workspace e arquivos versionados restaurados. Nenhuma migração de dependências nesta change.
- Pendente: conferência visual do Funcionário e encerramento. Atalho para conteúdo ainda sem confirmação de foco no destino; não registrar como aprovado.
