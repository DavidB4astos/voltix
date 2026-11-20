# Evidência 05 — Prontidão da demonstração (20/11/2026)

## Objetivo

Consolidar achados, classificá-los por impacto e definir o roteiro de ensaio das quatro jornadas
aprovadas.

## 1. Matriz achado → jornada → classificação → próxima ação

| Achado | Jornada | Classificação | Próxima ação |
| --- | --- | --- | --- |
| Nenhum bloqueador de demo identificado nas rotas e fluxos executáveis nesta rodada | Todas | falso positivo de risco | Seguir com o ensaio; manter as limitações explícitas |
| Catálogo com 20 produtos, preços `a partir de R$`, painel de detalhe e estados sem sessão coerentes | Catálogo → detalhe → carrinho | coerente | Nenhuma; não acionar "Adicionar ao carrinho" no ensaio sem sessão |
| `Connection Error:` vazio no DOM (div `title` sem texto) | Todas | falso positivo | Nenhuma; já classificado como D7 na auditoria anterior |
| Avisos de `autocomplete` e `id/name` em formulários | Cliente, ADMIN, recuperação | pós-entrega | Change própria de acessibilidade, após 23/11 |
| `docs/AI_AGENT_HANDOFF.md:631` registra 435 testes (versão corrente: 445) | Não afeta a demo | pós-entrega | Corrigir na tarefa 6.5, com aprovação desta change |
| Aviso de versão do Reflex 0.9.12 desatualizada | Não afeta a demo | informativo | Avaliar migração em change própria |
| `ResourceWarning` de HTTPError simulados no stderr da suíte | Não afeta a demo | falso positivo | Nenhuma; veredito do `unittest` foi `OK` |
| Sessão ADMINISTRADOR indisponível após o restart do Chrome | ADMIN | limitação documentada | No ensaio, fazer login com conta autorizada pelo apresentador; sem gravação |
| Login de Cliente retornou 403 na auditoria anterior | Cliente, checkout | limitação documentada | Não resetar senha; se necessário, autorizar credencial de teste em change própria |
| Sem compra E2E: E6 exige ambiente Xano isolado e autorizado | Checkout/pedido | limitação documentada | Manter simulação; não submeter pedido nem pagamento |
| Joins de carrinho/checkout, defaults de schema, upload 403 e tabela `tmp_rollback_test` | Checkout, ADMIN | limitação documentada | Manter adiados; ver `03-xano-readonly.md` |
| Negação anônima confirmada com HTTP 401 em cinco endpoints | ADMIN, Cliente | coerente | Nenhuma |
| Matriz papel × rota/ação conferida por código, XanoScript e specs | ADMIN, Cliente | coerente | Nenhuma correção identificada nesta auditoria; detalhes em `04-security.md` |
| Superfície legada `DB_XANO_BASTOS/status_cliente_*` sem `auth` no código local | ADMIN | pós-entrega | Mantida; substituída por endpoint autenticado novo em change arquivada, sem revalidação remota aqui |
| `role == "admin"` em templates Xano e limpeza de sessão só em `403` em duas transições | ADMIN | falso positivo | Nenhuma; ambos intencionais e cobertos por código/testes |
| Conclusões de autorização são estáticas; provas autenticadas positivas não repetidas | ADMIN, Cliente | limitação documentada | Se necessário, change própria com sessões e ambiente autorizado |

**Veredito:** a demonstração está pronta para as quatro jornadas aprovadas, condicionada às
limitações acima. Não há defeito classificado como bloqueador de demo no escopo executável desta
auditoria. A jornada de Cliente autenticado depende de credencial válida no momento da apresentação;
a de checkout permanece estritamente simulada.

## 2. Roteiro de ensaio

### Jornada 1 — Catálogo → detalhe → carrinho

1. Abrir `/` em 1280 px: hero, navegação e rodapé sem badge do framework.
2. Ir a `/catalogo`: conferir "Catálogo · 20 produtos", busca, filtro e preços `a partir de R$ …`.
3. Clicar em `Ver detalhes` do primeiro card: conferir SKU, preço, estoque, variações e especificações.
4. **Não** clicar em `Adicionar ao carrinho`.
5. Abrir `/carrinho`: mostrar o estado "Seu carrinho começa na sua conta".
6. Repetir os passos 2–5 em 768 px e 375 px; conferir ausência de rolagem horizontal.

### Jornada 2 — Área interna ADMIN

1. Abrir `/interno` e autenticar com conta ADMINISTRADOR ativa fornecida pelo apresentador.
2. Mostrar Dashboard, CRM e Pedidos; em Pedidos, conferir os valores em uma linha (ex.: `R$ 119,90`).
3. Mostrar Produtos com a tabela de variações e as ações disponíveis para ADMINISTRADOR.
4. **Não** inativar, excluir, importar, ajustar estoque nem avançar status de pedido.
5. **Não** exibir CPF, e-mail completo, telefone, senha, hash ou token; máscaras devem permanecer.

### Jornada 3 — Login de Cliente

1. Abrir `/cliente`: mostrar cadastro e login separados.
2. Se houver credencial de Cliente válida e autorizada, autenticar apenas para exibir a conta; caso
   contrário, mostrar o estado de bloqueio conhecido (403 histórico).
3. **Não** resetar senha, **não** reenviar credenciais e **não** expor o erro com dados pessoais.
4. Registrar o desfecho como coerente ou limitação documentada.

### Jornada 4 — Checkout/pedido simulado

1. Sem sessão: abrir `/checkout` e `/pedidos` e mostrar os blocos "Entre como Cliente para
   finalizar/consultar".
2. Com sessão de Cliente válida (somente se disponível): navegar até checkout e conferir entrega,
   endereço e valores existentes, sem confirmação.
3. **Não** submeter pedido, pagamento simulado ou qualquer `POST` de checkout.
4. **Não** gerar e-mail real nem consumir estoque.

## 3. O que não deve ser executado no vídeo

- Compra E2E, pagamento, baixa de estoque ou criação de Pedido (E6).
- Inativação, exclusão, importação, upload de imagem, ajuste de estoque, avanço de status.
- Reset de senha de Cliente ou de usuário interno; reenvio de e-mail real.
- Publicação Xano, `push`, `PATCH`, `POST`, `DELETE`, ou varredura que provoque HTTP 429.
- Exibição de CPF, e-mail, telefone, senha, hash, token, `.env` ou credenciais.
- Capturas com dados reais de clientes; usar somente estados sintéticos/mascarados.

## Limitações

- O roteiro depende de sessão ADMINISTRADOR e, opcionalmente, de sessão de Cliente válida no momento
  do ensaio; nenhuma credencial foi fornecida ou armazenada por esta auditoria.
- A Jornada 4 é uma simulação de navegação/estados, não uma prova de compra ponta a ponta.
- A classificação final não substitui revisão humana das evidências antes do arquivamento.
