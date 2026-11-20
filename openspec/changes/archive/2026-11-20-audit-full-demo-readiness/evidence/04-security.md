# Evidência 04 — Segurança e autorização (20/11/2026)

## Objetivo

Verificar papéis, guardas, negações de acesso e ausência de dados sensíveis no DOM e nas evidências.

## 1. Matriz papel × rota/ação

Revisão estática de `voltix/voltix.py`, dos XanoScripts locais e das specs consolidadas (E1/E2/E4).
Caminhos abreviados: `V` = `voltix/voltix.py`, `X` = `xano/api/`.

| Papel | Permitido | Negado | Evidência |
| --- | --- | --- | --- |
| Visitante | `/`, `/catalogo`, health, recuperação de senha, cadastro/login | `/interno` e grupos `Voltix Internal *` (401/403) | V:11441-11452; X:`public_catalog/products_GET.xs`, X:`integration/health_GET.xs:1-11` |
| Cliente (sessão própria) | `/cliente`, `/carrinho`, `/checkout`, `/pedidos`; próprios perfil/endereços/carrinho/pedidos; cancelar próprio pedido em `AGUARDANDO_PAGAMENTO` | `/interno`, endpoints internos, perfil/carrinho de terceiros, exclusão de Cliente, produtos/usuários | V:11453-11475, V:4256, V:4263, V:6052-6053; X:`customer/customer_me_GET.xs:3,15`, X:`customer/order_id_cancel_POST.xs:3,27` |
| FUNCIONARIO ativo | clientes, atendimentos, pedidos, dashboard, CRM e próprio perfil; leitura de clientes/pedidos/histórico; criar/editar atendimento; `ABERTO→EM_ATENDIMENTO`; finalizar/cancelar atendimentos próprios | produtos, catálogo, importação, usuários; editar/inativar cliente; avançar status de pedido; ajustar estoque; inativar/excluir produto | V:2167-2169, V:2233-2246, V:2520-2521, V:3388-3392; X:`internal_customers/customer_id_PATCH.xs:23`, X:`internal_orders/order_id_status_POST.xs:21`, X:`product_management/product/product_id_DELETE.xs:21` |
| ADMINISTRADOR ativo | tudo acima + produtos, catálogo, importação, usuários; editar/inativar cliente; avanço estrito `PAGAMENTO_CONFIRMADO→EM_PREPARACAO→ENVIADO→ENTREGUE`; cancelar pedido em `PAGAMENTO_CONFIRMADO`; finalizar qualquer atendimento; ajustar estoque; excluir produto sem histórico | alterar próprio `role`/`status`; excluir Cliente; excluir produto com `ItemPedido`/`ItemCarrinho`; cancelar em `EM_PREPARACAO`/`ENVIADO`/`ENTREGUE` | V:2168-2169, V:2245-2246, V:5393-5400; X:`internal_users/user/user_id_PATCH.xs:58-60,78-88`, X:`product_management/product/product_id_DELETE.xs:21,87`, X:`internal_orders/order_id_cancel_POST.xs:16` |
| INATIVO (interno ou Cliente) | nenhuma operação autenticada | login negado; token existente não autoriza; `/interno` e endpoints internos negados | X:`authentication/auth/login_POST.xs:38-42`, X:`authentication/auth/me_GET.xs:32-36`, X:`customer/customer_login_POST.xs:21`; V:6052-6054, V:6082-6093 |

Guardas: base comum `_internal_customer_allowed()` em V:2186-2188 (token + `is_authenticated` +
`session_status == "success"` + `ATIVO` + role aprovada), derivadas em V:2233-2246 e V:2520-2521.
Limpeza de sessão central em V:4429-4456, chamada em cerca de 20 handlers em 401/403; logout em
V:6107-6111. Tokens distintos para Cliente (`_customer_auth_token`, V:4263) e interno
(`_auth_token`, V:4250), com `auth = "user"` vs `auth = "CLIENTE"` no backend.

### Achados da revisão

- **Coerente:** Admin-only para inativar/excluir produto, avançar pedido, gerenciar usuários e editar
  cliente; FUNCIONARIO com leitura e atendimentos; Cliente barrado no interno; INATIVO barrado.
  Casos alinhados a `openspec/specs/internal-access/spec.md:47-92`, `product-management/spec.md:85-92,206-234`,
  `order-management/spec.md:44-70` e `internal-customers/spec.md:8-21,109-123`.
- **Coerente:** separação Cliente × UsuarioInterno em duas camadas; máscaras de e-mail preservadas no
  backend em X:`internal_customers/customer_id_PATCH.xs:117-218` (E4).
- **Falso positivo:** `role == "admin"` minúsculo em `event_logs/logs/admin/account_events_GET.xs:17`
  e grupos `members_accounts` são templates Xano fora do modelo Voltix, sem uso pela aplicação.
- **Falso positivo:** limpeza de sessão apenas em `401` (não `403`) em
  `change_internal_attendance_status` (V:3209-3218) e `advance_internal_order_status` (V:3426-3434)
  é intencional: `403` é negação de regra de negócio, coberta por `tests/test_internal_attendances.py:334`
  e `tests/test_internal_orders.py:332`.
- **Pós-entrega:** a superfície legada `DB_XANO_BASTOS/status_cliente_*` permanece sem `auth` nem
  `precondition` no código local (ex.: X:`db_xano_bastos/status_cliente_POST.xs:1-19`). O próprio
  arquivamento de `implement-internal-customer-edit` registra que o `PATCH` legado não autenticado foi
  substituído por endpoint novo; não é mudança de decisão. O estado publicado não foi revalidado.
- **Limitação:** as conclusões são estáticas do `.xs` local; provas autenticadas positivas, expiração
  de token e o mapeamento HTTP real de `accessdenied` (401 vs 403) não foram executados nesta rodada.

## 2. Varredura de dados sensíveis no DOM

Nas 9 rotas em 1280 px, o DOM renderizado foi varrido por padrões de CPF (`ddd.ddd.ddd-dd`), e-mail,
telefone, texto `Bearer`/`token`, nomes de variáveis `XANO_*`/chaves e campos `input[type=password]`.

| Rota | CPF | E-mail | Telefone | Campos de senha | Token/Bearer | Config no DOM |
| --- | --- | --- | --- | --- | --- | --- |
| `/` | 0 | 0 | 0 | 0 | não | não |
| `/catalogo` | 0 | 0 | 0 | 0 | não | não |
| `/cliente` | 0 | 0 | 0 | 2 (cadastro e login) | não | não |
| `/carrinho` | 0 | 0 | 0 | 0 | não | não |
| `/checkout` | 0 | 0 | 0 | 0 | não | não |
| `/pedidos` | 0 | 0 | 0 | 0 | não | não |
| `/interno` | 0 | 0 | 0 | 1 (login) | não | não |
| `/interno/recuperar-senha` | 0 | 0 | 0 | 0 | não | não |
| `/interno/redefinir-senha` | 0 | 0 | 0 | 3 (token e nova senha/confirmação) | não | não |

Campos de senha aparecem somente em formulários de autenticação/recuperação, como esperado. Nenhum
valor sensível foi preenchido, lido ou impresso. Os cinco arquivos de evidência desta change também
foram varridos: nenhum CPF, e-mail, telefone, senha, hash, token ou variável `XANO_*` presente.

## 3. Negação de acesso anônimo

Requisições GET anônimas, espaçadas em 4 s (5 no total, sem HTTP 429):

| Endpoint (referência por variável de ambiente) | Resultado |
| --- | --- |
| `XANO_INTERNAL_ACCESS_URL` | HTTP **401** |
| `XANO_INTERNAL_CUSTOMERS_URL` | HTTP **401** |
| `XANO_INTERNAL_ORDERS_URL` | HTTP **401** |
| `XANO_INTERNAL_USERS_URL` | HTTP **401** |
| `XANO_CUSTOMER_ME_URL` | HTTP **401** |

Nenhuma URL, token, corpo de resposta ou dado pessoal foi impresso. Nenhuma requisição de escrita foi
enviada. No frontend, `/interno` sem sessão exibe apenas o formulário de login e `/carrinho`,
`/checkout` e `/pedidos` exibem os estados de "entre como Cliente".

## 4. Usuário inativo

A negação para usuário `INATIVO` não foi reexecutada ao vivo nesta rodada: exigiria credencial de teste
e POSTs de login, fora do escopo de somente leitura. A regra é verificada estaticamente nas guardas de
backend e está registrada nas evidências arquivadas de `acesso-interno`, `gestao-produtos` e
`implement-internal-user-management`. Classificação: **limitação documentada**, não bloqueador.

## Limitações

- Nenhuma leitura autenticada positiva foi repetida (sem sessão ADMINISTRADOR/CLIENTE nesta execução).
- A varredura de DOM cobre o estado inicial das rotas; dados internos autenticados não estavam
  presentes para varredura. Máscaras de CPF/e-mail usadas em painéis internos foram verificadas em
  evidências arquivadas, não ao vivo.
- Nenhuma credencial, hash ou token foi lido de `.env`, impresso ou armazenado em arquivo versionado.
