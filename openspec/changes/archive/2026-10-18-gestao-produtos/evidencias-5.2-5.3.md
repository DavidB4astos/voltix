# Evidências — Validação 5.2 / 5.3 (gestao-produtos)

Data: 2026-10-17
Ambiente: Xano instância `x8ki-letl-twmt.n7.xano.io`, workspace `147981` (Free Plan)
Método: requisições autenticadas automatizadas via Chrome DevTools MCP (fetch no contexto do painel Xano).
Credenciais: sem senha; tokens internos de usuários de teste gerados via `POST /api:mvp-admin/workspace/147981/dbo/748950/auth` (sessão do painel). Tokens mantidos apenas em memória do navegador, nunca impressos.
Usuários de teste: #7 `Usuario Administrador Teste` (ADMINISTRADOR/ATIVO), #5 `Usuario Funcionario Teste` (FUNCIONARIO/ATIVO), #8 `Usuario Inativo Teste` (FUNCIONARIO/INATIVO).

Bases: Product Management `api:umWTO5yo`; Catalog Management `api:voltix-catalog-management`; Authentication `api:WFVDlCKn`.

---

## 5.2 — Validar (ADMINISTRADOR ativo)

Texto: "Validar com ADMINISTRADOR ativo listagem, criação de Produto com variação, edição, upload de imagem opcional, status de Produto/variações e persistência após reload; confirmar SKU único e rejeição de referências inativas novas".

| Critério | Resultado | Evidência |
|---|---|---|
| Listagem | OK | GET /products → 200 (4 produtos); GET /variations → 200 (4 variações) |
| Criação de Produto com variação | OK | POST /products → 200, id=5, status=ATIVO; variação id=5 criada (produto_id=5) |
| Persistência após reload | OK | GET /products e /variations após criação/edit/status confirmam os dados |
| Edição | OK | PATCH /products/5 {nome,categoria_id,marca_id} → 200, nome persistido |
| SKU único | OK | POST /products com SKU existente → 400 "A variation with this SKU already exists." |
| Rejeição de referência inativa nova | OK | cat 2 inativada → POST /products {categoria_id:2} → 400 "An active category is required."; cat 2 restaurada ATIVO |
| Upload de imagem (opcional) | NÃO VALIDADO (limitação de ambiente) | POST /products/5/image → 403 `{"code":"ERROR_CODE_ACCESS_DENIED","message":"Not supported. Please upgrade your Xano instance."}` (storage.create_image indisponível no plano/instância) |
| Status de Produto/variações | OK (corrigido) | DEFEITO F1 corrigido no backend e revalidado: `PATCH /products/5` só `{"status":...}` → 200; `PATCH /variations/5` só `{"status":...}` → 200 (ver "Correção F1") |

**Veredito 5.2: ATENDE os critérios executáveis** — a alternância de status (produto/variação) foi corrigida e revalidada (DEFEITO F1 resolvido). Permanece **1 pendência de ambiente**: upload de imagem não validável na instância Xano Free (HTTP 403, bloqueio confirmado da instância; não é falha de implementação).

---

## DEFEITO F1 — Alternância de status (produto e variação) — RESOLVIDO (correção publicada e revalidada em 2026-10-18)

Descrição do defeito: as telas usam payload somente `{"status": ...}`:

- `voltix/voltix.py:1924` — `_change_product_status`: `PATCH /products/{id}` body `{"status": status}`
- `voltix/voltix.py:2065` — `toggle_variation_status`: `PATCH /variations/{id}` body `{"status": status}`

Comportamento antes da correção:
- `PATCH /products/5 {"status":"INATIVO"}` → 400 `{"code":"ERROR_CODE_INPUT_ERROR","message":"Value is less than the minimum value of 1","payload":{"param":"categoria_id"}}`
- `PATCH /variations/3 {"status":"INATIVO"}` → 400 `{... "payload":{"param":"produto_id"}}`
- `PATCH /products/5 {"categoria_id":3,"marca_id":1,"status":"INATIVO"}` → 200 (funcionava quando os campos eram enviados)

Causa raiz: campos id opcionais `categoria_id?`/`marca_id?` (products PATCH) e `produto_id?` (variations PATCH) com `default:"0"` + filtro `min:1`; ao omitir, o default 0 era validado e o filtro falhava (400).

### Correção aplicada (XanoScript)
- `xano/api/product_management/product/product_id_PATCH.xs` (GUID `YJOD1IemBD5iLEfVD1EIPRpi5Vc`): removido `filters=min:1` de `categoria_id?`/`marca_id?`; pré-condições passam a tratar id ausente/não positivo como "não informado" (`!= null && > 0`).
- `xano/api/product_management/variation/variation_id_PATCH.xs` (GUID `MQCNgUmw-9fx-AScrC5HGOTBO2Y`): removido `filters=min:1` de `produto_id?`; pré-condição de reatribuição trata `<= 0` como ausente.
- Preservados: validação de referência (db.get + precondition de categoria/marca ATIVA) e autorização ADMINISTRADOR + ATIVO.
- Sem alteração no frontend (sem workaround).

### Publicação (Xano Free, workspace 147981)
- Pré-publicação: `workspace push --dry-run -i <2 arquivos>` → "Matched: 2 of 95 files"; preview **~2 updated** apenas (`products/{product_id} PATCH`, `variations/{variation_id} PATCH`). Nenhum outro artefato.
- Publicação escopada dos 2 endpoints (partial/`-i`). A CLI alertou "Unresolved References" (tabelas não incluídas no push parcial); verificado por `pull` que os `db.*` permaneceram íntegros.
- Verificação pós-push: `workspace pull` → ambos os endpoints exibem a correção e todas as referências `db.get`/`db.patch`/`db.query` intactas.

### Reteste ao vivo (apenas cenários afetados; dados temporários produto 5 / variação 5)
| Teste | Esperado | Obtido |
|---|---|---|
| `PATCH /products/5 {"status":"ATIVO"}` | 200 | 200 (ATIVO) |
| `PATCH /products/5 {"status":"INATIVO"}` (restaura) | 200 | 200 (INATIVO) |
| `PATCH /variations/5 {"status":"ATIVO"}` | 200 | 200 (ATIVO) |
| `PATCH /variations/5 {"status":"INATIVO"}` (restaura) | 200 | 200 (INATIVO) |
| `PATCH /products/5 {"categoria_id":99999}` | 400 | 400 "An active category is required for a new association." |
| `PATCH /variations/5 {"produto_id":1}` | 400 | 400 "A variation cannot be reassigned to another product." |
| `PATCH /products/5` sem token | 401 | 401 "Unauthorized - Authentication Required" |

Conclusão: F1 corrigido, alternância de status funciona com payload somente `{"status":...}`; validação de referências e autorização preservadas; estado dos dados restaurado (produto 5 e variação 5 = INATIVO).

---

## 5.3 — Validar autorização negativa e entradas inválidas

Texto: "Validar autorização backend negativa para FUNCIONARIO, sessão ausente/inválida e usuário inativo, e validar entradas inválidas de SKU, preço, quantidade e produto sem variação; confirmar ausência de persistência parcial".

| Critério | Resultado | Evidência |
|---|---|---|
| Sessão ausente | OK | GET /products e /variations sem token → 401 "Unauthorized - Authentication Required" |
| Sessão inválida | OK | GET /products token inválido → 401 "Invalid token." |
| FUNCIONARIO (perfil) | OK | POST /products com #5 (FUNC/ATIVO) → 403 "Administrator access is required." (status ATIVO ⇒ bloqueio é o perfil) |
| Usuário inativo (status) | OK | GET /auth/me com #8 (FUNC/INATIVO) → 403 "Internal access is not available." (role passou ⇒ bloqueio é o status). Controle: /auth/me #5 → 200 {FUNCIONARIO,ATIVO}; /auth/me #7 → 200 |
| SKU inválido (vazio) | OK | POST /products SKU "   " → 400 "Each variation requires a unique SKU, positive price, and non-negative quantity." |
| Preço inválido (=0) | OK | 400 mesma mensagem |
| Quantidade inválida (-1) | OK | 400 mesma mensagem |
| Produto sem variação ([]) | OK | 400 "At least one product variation is required." |
| Produto sem parâmetro variacoes | OK | 400 "Missing param: variacoes" |
| Ausência de persistência parcial | OK | Após todas as rejeições: GET /variations=5 e GET /products=5 (somente o registro válido de teste) |

**Veredito 5.3: ATENDE.**

Observação de isolamento: o usuário inativo (#8) é FUNCIONARIO+INATIVO, portanto no endpoint de produtos a rejeição seria ambígua (perfil ou status). O isolamento do status foi feito via `auth/me`, cujo encadeamento de preconditions (role antes de status) retorna "Internal access is not available." apenas quando o perfil é válido e o status não — provando que a causa é o status.

---

## Estado dos dados (restaurado)

- Produto temporário criado: id=5 `TMP-VALID-PLAY-EDITED`, inativado ao final (não há endpoint DELETE).
- Variação temporária: id=5 (sku `TMP-VALID-PLAY-1792200488241`), inativada.
- Categoria 2 (QA): inativada apenas durante o teste e restaurada para ATIVO.
- Produtos 1-4 e variações 1-4: inalterados.
- Reteste F1 (2026-10-18): produto 5 alternado ATIVO↔INATIVO e variação 5 alternada ATIVO↔INATIVO, ambos restaurados para INATIVO; contagem final GET /products=5 e GET /variations=5. Nenhum resíduo.
- Tokens: gerados em memória no contexto do painel e limpos ao final; nenhum token/senha impresso ou persistido em arquivo.
