# Inventário de telas em execução — 20/11/2026

Servidor de produção local (`reflex run --env prod --single-port --frontend-port 3090`) contra a
instância Xano configurada no `.env`. Navegador em 1280x800, 768x1024 e 375x812 (DPR 1). Toda a
navegação foi **somente leitura**: nenhum pedido, upload, importação, inativação, exclusão, edição
ou cadastro foi executado.

## Rotas públicas (9)

| Rota | Cabeçalho | Carrega | Observações |
| --- | --- | --- | --- |
| `/` | Voltix — tecnologia premium | sim | Hero, categorias, rodapé; sem overflow em 375/768/1280 |
| `/catalogo` | Catálogo de produtos | sim | 23 produtos, 5 categorias, busca e filtro por categoria funcionando |
| `/catalogo` + detalhe | Detalhes do produto | sim | Painel com variações, SKU, estoque, preço e ação; preenchido ao clicar no card |
| `/cliente` | Minha conta | sim | Cadastro e login de Cliente; sem sessão |
| `/carrinho` | Seu carrinho | sim | Estado "entre como Cliente" correto |
| `/checkout` | Checkout | sim | Bloqueio de sessão correto |
| `/pedidos` | Meus pedidos | sim | Bloqueio de sessão correto |
| `/interno/recuperar-senha` | Recuperar senha | sim | Campo de e-mail e ação |
| `/interno/redefinir-senha` | Redefinir senha | sim | Lê `email`/`token` da URL e preenche o formulário |

Busca por "headset" retornou 2 produtos; categoria "Monitores" retornou 3; combinação vazia
retornou o estado "Nenhum produto encontrado". Nenhuma rota apresentou erro de carregamento.

## Seções internas (9, com sessão de ADMINISTRADOR)

| Seção | Cabeçalho | Carrega | Observações |
| --- | --- | --- | --- |
| Dashboard | Dashboard | sim | Métricas, série diária, filtros de período |
| CRM | CRM | sim | 7 clientes ativos, 2 pedidos, faturamento e ticket médio |
| Clientes | Clientes | sim | Consulta com 7 linhas; CPF/e-mail mascarados |
| Atendimentos | Atendimentos | sim | Formulário e lista (lista vazia: sem registros) |
| Pedidos | Pedidos | sim | 2 pedidos com total, status, paginação; detalhe abre |
| Produtos | Produtos | sim | 41 linhas |
| Categorias e marcas | Categorias e marcas | sim | 18 linhas |
| Importação | Importação | sim | Preparação, conferência e acompanhamento |
| Usuários | Usuários | sim | 4 usuários |

## Responsivo

- 375 px: rotas públicas sem overflow horizontal; grade do catálogo em 1 coluna; interno com
  navegação empilhada e conteúdo abaixo.
- 768 px: catálogo em 2 colunas (conforme a spec), sem overflow; interno sem overflow.
- 1280 px: catálogo em 3 colunas, painéis internos com densidade adequada.

## Bloqueado nesta auditoria

- Jornada autenticada de **Cliente** (carrinho → checkout → pedidos): as credenciais de teste
  registradas no `.env` foram rejeitadas (HTTP 403) no endpoint de login; o usuário auditou a
  área interna com sessão manual, mas não houve sessão de Cliente.
- Ações de escrita: compra, upload de imagem, importação, inativação e exclusão — por decisão de
  escopo (somente leitura).
- Entrega real de e-mail da recuperação de senha: não exercitada.
