# Voltix — E-commerce de Tecnologia com CRM Integrado

## 1. Apresentação

A **Voltix** é uma plataforma web de e-commerce especializada em produtos de tecnologia (computadores, componentes de hardware, periféricos e acessórios) integrada a um painel administrativo e a um **CRM (Customer Relationship Management)**.

### Problema que resolve
Em operações de comércio eletrônico convencionais, os dados de vendas (pedidos, itens e pagamentos) costumam ficar separados do relacionamento com o cliente. A Voltix centraliza a loja pública, a gestão operacional e o histórico de atendimentos em uma única plataforma, permitindo que a equipe interna acompanhe pedidos, histórico de compras e atendimentos com consistência.

### Público-alvo
- **Consumidores (Visitantes e Clientes):** interessados em pesquisar, comparar variações e adquirir produtos de tecnologia.
- **Equipe interna (Funcionários e Administradores):** responsáveis por acompanhar vendas, atender clientes no CRM e gerenciar o catálogo, pedidos e usuários.

---

## 2. Acesso ao aplicativo

- **Frontend:** desenvolvido em **Reflex** (Python).
- **Backend e persistência:** desenvolvidos em **Xano / XanoScript**.

### Principais rotas da aplicação
| Área | Rota | Finalidade |
|---|---|---|
| Loja pública | `/` | Página inicial da loja |
| Catálogo | `/catalogo` | Listagem, busca por nome, filtro por categoria e modal de detalhes |
| Conta do Cliente | `/cliente` | Cadastro, login, dados pessoais e endereços |
| Carrinho | `/carrinho` | Gerenciamento de itens selecionados (requer login de Cliente) |
| Checkout | `/checkout` | Seleção de endereço, método de pagamento simulado e confirmação |
| Meus pedidos | `/pedidos` | Histórico de compras, status, pagamento simulado e cancelamento |
| Área interna | `/interno` | Painel administrativo e CRM (requer login de Usuário Interno) |
| Recuperação de senha interna | `/interno/recuperar-senha` | Solicitação de código de recuperação |
| Redefinição de senha interna | `/interno/redefinir-senha` | Definição de nova senha com código recebido |

### Execução local
1. Crie e ative um ambiente virtual Python e instale as dependências de `requirements.txt`.
2. Copie `.env.example` para `.env` e preencha as URLs dos endpoints do workspace Xano configurado.
3. Execute `reflex run` na raiz do repositório e acesse `http://localhost:3000/` no navegador.

> **Nota:** por segurança, nunca versione o arquivo `.env` nem credenciais de acesso.

---

## 3. Perfis de usuários

| Perfil | Autenticação | Permissões principais |
|---|---|---|
| **Visitante** | Não autenticado | Navegar na página inicial, consultar o catálogo público, buscar por nome, filtrar por categoria e abrir detalhes/variações dos produtos. |
| **Cliente** | Conta de Cliente (`/cliente`) | Gerenciar seus endereços de entrega, adicionar/remover itens no carrinho, finalizar pedidos com pagamento simulado, consultar seus pedidos e cancelar pedido próprio em `AGUARDANDO_PAGAMENTO`. Não acessa `/interno`. |
| **Funcionário** | Usuário Interno (`/interno`) | Consultar Dashboard de vendas (leitura), Dashboard de CRM, consultar clientes (com CPF mascarado), consultar histórico de pedidos de clientes, listar/visualizar pedidos e criar/atualizar atendimentos de CRM (`ABERTO` / `EM_ATENDIMENTO`). |
| **Administrador** | Usuário Interno (`/interno`) | Todas as permissões de Funcionário, além de: cadastrar/editar/inativar/excluir produtos (sem histórico comercial), gerenciar categorias e marcas, importar catálogo em massa, avançar status de pedidos (`PAGAMENTO_CONFIRMADO` → `EM_PREPARACAO` → `ENVIADO` → `ENTREGUE`), cancelar pedidos em `AGUARDANDO_PAGAMENTO` ou `PAGAMENTO_CONFIRMADO`, editar/inativar clientes e gerenciar usuários internos. |

Todas as regras de autenticação e autorização são aplicadas no backend (XanoScript), além das proteções da interface.

---

## 4. Funcionalidades

### E-commerce (Loja pública e Cliente)
- Página inicial editorial e catálogo público com busca por nome e filtro por categoria.
- Modal de detalhes do produto com marca, categoria, descrição, especificações técnicas, variações (`SKU`), preço e disponibilidade de estoque.
- Cadastro e autenticação de Cliente, além de CRUD de endereços de entrega (com no máximo um endereço principal).
- Carrinho de compras persistido por Cliente (sem reserva prévia de estoque) e checkout com baixa atômica de estoque.
- Pagamento simulado (`PIX`, `CARTAO` ou `BOLETO`) e histórico de pedidos com cancelamento e devolução automática de estoque quando aplicável.

### Painel Administrativo e CRM (`/interno`)
- **Dashboard de vendas:** faturamento, quantidade de pedidos, ticket médio e série diária filtrável por período (UTC).
- **Dashboard de CRM e Atendimentos:** criação, consulta, filtragem e transição de status de atendimentos (`ABERTO` → `EM_ATENDIMENTO` → `FINALIZADO` / `CANCELADO`), com vinculação opcional a um Pedido do mesmo Cliente.
- **Clientes:** consulta com CPF mascarado por padrão, histórico de pedidos do cliente e edição/inativação exclusiva de Administrador.
- **Pedidos:** listagem, detalhe e avanço estrito de status pelo Administrador.
- **Catálogo interno:** gestão de Produtos, Variações, ajuste de estoque, Categorias, Marcas e Importação em massa (`CSV`/`XLSX`) com pré-visualização antes da confirmação.
- **Usuários e Meu perfil:** gestão de equipe (Administrador) e atualização de nome, e-mail e senha própria.

---

## 5. Manual de utilização

### Jornada 1 — Visitante e Cliente (Compra ponta a ponta)
1. **Explorar o catálogo:** acesse `/` ou `/catalogo`. Utilize o campo **Buscar no catálogo** ou selecione uma **Categoria** para filtrar os produtos.
   - *Resultado esperado:* exibição dos cards com imagem (ou `"Imagem não disponível"`), título, categoria e preço `a partir de R$ …`.
2. **Consultar detalhes:** clique em **Ver detalhes** em qualquer card.
   - *Resultado esperado:* abertura do modal centralizado com variações disponíveis, SKU, preço unitário, quantidade em estoque e especificações técnicas.
3. **Autenticar-se como Cliente:** acesse `/cliente` e faça login ou cadastre uma nova conta informando nome completo, CPF, e-mail, telefone e senha.
   - *Resultado esperado:* acesso liberado ao perfil do cliente, endereços, carrinho e pedidos.
4. **Gerenciar endereço e carrinho:** em `/cliente`, cadastre ao menos um endereço de entrega. No catálogo, abra o modal do produto e clique em **Adicionar ao carrinho**. Acesse `/carrinho` para ajustar quantidades ou remover itens.
   - *Resultado esperado:* itens e subtotal atualizados conforme o estoque disponível.
5. **Finalizar pedido e simular pagamento:** em `/checkout`, selecione o endereço de entrega e o método de pagamento (`PIX`, `CARTAO` ou `BOLETO`) e confirme o pedido. Em seguida, em `/pedidos`, acompanhe o pedido criado e execute a simulação de pagamento quando estiver em `AGUARDANDO_PAGAMENTO`.
   - *Resultado esperado:* criação do pedido com código único, pagamento associado e baixa automática do estoque das variações compradas.

### Jornada 2 — Funcionário (CRM e Atendimentos)
1. **Acessar área interna:** entre em `/interno` com um usuário interno ativo (`FUNCIONARIO`).
   - *Resultado esperado:* exibição das seções permitidas na barra lateral (sem abas exclusivas de administração).
2. **Consultar Cliente e histórico:** acesse **Clientes**, filtre e abra o detalhe de um cliente (CPF exibido mascarado). Consulte também o histórico de compras associado.
   - *Resultado esperado:* visualização segura dos dados cadastrais e pedidos do cliente.
3. **Registrar e acompanhar Atendimento:** acesse **Atendimentos**, preencha o formulário informando o ID do Cliente, ID do Pedido (opcional), assunto, descrição e data, e salve.
   - *Resultado esperado:* atendimento criado em `ABERTO`, podendo ser iniciado (`EM_ATENDIMENTO`) e finalizado (`FINALIZADO`) pelo responsável ou Administrador; registros encerrados tornam-se somente leitura.

### Jornada 3 — Administrador (Gestão de Pedidos, Catálogo e Equipe)
1. **Gerenciar Pedidos:** em `/interno` → **Pedidos**, filtre pedidos, abra os detalhes e avance o status seguindo a sequência `PAGAMENTO_CONFIRMADO` → `EM_PREPARACAO` → `ENVIADO` → `ENTREGUE` (ou cancele quando permitido, devolvendo o estoque).
2. **Gerenciar Catálogo:** em **Produtos** e **Categorias e marcas**, cadastre novos itens, ajuste estoque de variações ou inative produtos sem apagar histórico comercial.
3. **Importação e Equipe:** em **Importação**, envie um arquivo `CSV`/`XLSX` para pré-visualizar e validar linhas antes de confirmar; em **Usuários**, gerencie contas internas e permissões.

---

## 6. Exemplos de utilização

### Cenário ilustrativo completo (dados fictícios)
1. **Cliente fictício** (`Maria Silva`, e-mail `maria.exemplo@voltix.local`) acessa `/catalogo`, filtra por periféricos, abre **Ver detalhes** de um teclado (`SKU VTX-DEMO-003`) e adiciona 1 unidade ao carrinho.
2. Em `/checkout`, seleciona o endereço `"Casa"` e o método `PIX`, formalizando o pedido em `AGUARDANDO_PAGAMENTO`. Em `/pedidos`, aciona o pagamento simulado, alterando o pedido para `PAGAMENTO_CONFIRMADO`.
3. **Funcionário** entra em `/interno` → **Atendimentos**, registra um atendimento para o cliente vinculado ao código do pedido com o assunto `"Confirmação de prazo de separação"` e inicia o atendimento (`EM_ATENDIMENTO`).
4. **Administrador** acessa `/interno` → **Pedidos**, avança o pedido para `EM_PREPARACAO` e acompanha a atualização do faturamento no **Dashboard**.

---

## 7. Limitações conhecidas

- **Pagamento simulado:** não há integração real com gateways financeiros ou instituições bancárias; a aprovação/recusa é simulada para fins acadêmicos.
- **Sem emissão fiscal nem transportadora real:** não gera NF-e e não possui cálculo/rastreamento integrado com Correios ou transportadoras externas.
- **Upload de imagem de produto no plano Xano Free:** o upload direto para o backend apresentou restrição `HTTP 403` no plano gratuito utilizado; as imagens da vitrine de demonstração são servidas localmente a partir de `assets/demo/` com licenças registradas em `assets/demo/manifest.json`.
- **Rate limit do backend (Xano Free):** o plano gratuito limita a **10 requisições a cada 20 segundos**; consultas muito rápidas em sequência podem retornar `HTTP 429`.
- **Ambiente único:** não há ambiente separado de homologação/sandbox no plano gratuito utilizado, exigindo cautela ao testar mutações em dados existentes.
- **Responsividade mobile:** o foco principal de acabamento visual desta entrega é **desktop**; listas e tabelas administrativas densas podem exigir rolagem horizontal em telas estreitas.
