## 1. Backend - XanoScript

- [x] 1.1 Adicionar endpoint `GET /admin/customers` em `xano/api/admin/customers_GET.xs`. Verificar que o endpoint continua aceitando apenas leitura anônima.
- [x] 1.2 Aplicar filtro por status quando fornecido: apenas clientes com `status == "ATIVO"` ou `status == "INATIVO"`. Clientes sem status definido também inclusos quando não informado.
- [x] 1.3 Aplicar filtro por busca parcial case-insensitive em `nome` e `e-mail` quando `q` não estiver vazio/em branco, usando operador `includes` do XanoScript. Combinar com filtro `status` (AND) quando ambos forem fornecidos.
- [x] 1.4 Montar resposta sem campos sensíveis: exibir `id`, `nome`, `e-mail` (máscara: primeiros 3 caracteres + "*****"), `telefone`, `data_cadastro`, `status`. **NUNCA** incluir `senha`, `token`, `chaves privadas` ou campos completos de e-mail.
- [x] 1.5 Garantir que o endpoint retorne no máximo 50 clientes por página. Verificar que o endpoint respeita limites de requisições do Xano Free (429/Retry-After) e que a validação de perfil no Reflex ( `role == "ADMINISTRADOR" && status == "ATIVO" `) ocorre no backend, não apenas no frontend.
- [x] 1.6 Verificar que o endpoint não requer auth user e é somente leitura. Confirmar que a validação de perfil no Reflex (se houver) seja consistente com a validação no próprio endpoint XanoScript.

## 2. Frontend - Reflex

- [x] 2.1 Adicionar campo de busca no painel administrativo existente vinculado ao `State`. Verificar que a UI permite digitar termo e acionar busca.
- [x] 2.2 Atualizar `admin_customers` (lista) quando busca for acionada. Verificar que os parâmetros são passados corretamente.
- [x] 2.3 Incorporar `q` na chave de cache/reutilização quando aplicável para respeitar "respeitar a seleção de categoria" e evitar reutilizar resultados de busca diferentes. Verificar comportamento.
- [x] 2.4 Integrar com estados existentes (loading/empty/error). Verificar que busca sem resultados exibe estado vazio.

## 3. Testes

- [ ] 3.1 Validar endpoint `GET /admin/customers` sem parâmetros retorna apenas clientes ATIVO (contagem esperada).
- [ ] 3.2 Validar filtro `status=ATIVO` reduz resultados apenas aos ativos.
- [ ] 3.3 Validar filtro `status=INATIVO` resultados apenas inativos.
- [ ] 3.4 Validar busca `q=Maria` retorna clientes com nome ou e-mail contendo "Maria" (case-insensitive).
- [ ] 3.6 Validar acesso negado quando perfil não for `ADMINISTRADOR` ativo (retornar 403 ou mensagem de erro apropriada).
- [x] 3.7 Verificar que `py_compile voltix/voltix.py` e `openspec validate consulta-clientes-admin --strict` passam.

## 4. Documentação e validação

- [x] 4.1 Atualizar `docs/roadmap-changes.md` para refletir `consulta-clientes-admin` como change ativa/proposta. Verificar alteração registrada.
- [x] 4.2 Executar `cmd /c "openspec validate consulta-clientes-admin --strict"`. Verificar saída sem erros.
- [x] 4.3 Revisar artefatos (proposal/design/specs/tasks) quanto à aderência ao escopo (apenas consulta administrativa, sem alteração de endpoints públicos, sem SKU/preço/estoque). Verificar conformidade.