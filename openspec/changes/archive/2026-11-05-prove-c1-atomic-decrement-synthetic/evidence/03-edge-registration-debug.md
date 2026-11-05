# 03 — Depuração de publicação HTTP (C1 Proof Temp)

Data: 04/11/2026.

## Contexto

O push do pacote de prova foi executado em etapas. O primeiro push (criação do grupo)
publicou 4 documentos e ativou as rotas. Rotas criadas em pushes posteriores não aparecem
no roteador HTTP do edge, embora existam na Metadata API e sejam puxadas corretamente.

## Evidências

1. `xano workspace push` inicial: `+1 table (test_c1_estoque)`, `+1 api_group (C1 Proof
   Temp)`, `+2 queries (c1_prova/baixa POST, c1_prova/estado GET)` → **ambas as rotas
   funcionam** (validação do input da stack e resposta `{"itens":[]}`).
2. `xano workspace push` posterior de `c1_prova/seed` (push isolado): saída do CLI indicou
   `db.* → table "test_c1_estoque" does not exist`; a rota responde 404 no edge.
3. Re-push do seed/reset/preparar/preparar2, com e sem a tabela no mesmo pacote, incluindo
  mudança real de conteúdo e criação de documento 100% novo (sem GUID), **todos respondem
  HTTP 404** (`{"code":"ERROR_CODE_NOT_FOUND"}`) no edge.
4. `xano function run "C1 Proof / preparar"` retorna `ERROR_CODE_NOT_FOUND`;
   `xano function get "Getting Started Template/create_event_log"` (função pré-existente do
   workspace) também retorna 404 (`"Unable to locate request."`). A família `function` do
   CLI não responde para este profile/instância.
5. O runtime SQL do workspace **existe e funciona**: `baixa` executou `db.increment` com
   guarda `quantidade_disponivel >= quantidade` dentro de `db.transaction`; retornou
   `confirmado=false` com `erro.name="EstoqueInsuficiente"` (throw da própria stack), o que
   confirma que a tabela física `test_c1_estoque` é localizada e atualizada pelo runtime.
6. Pasta local do grupo: rotas `seed`, `reset`, `preparar` e `preparar2` (duplicadas,
   mesmas regras; `preparar2` sem GUID local antes do primeiro push).
7. O CLI não expõe outra forma de "deploy" além do push e de `release deploy`
   (releases não existem neste workspace; `branch` só tem `v1 (live)`). Deliberadamente
   **não** foi usado `--sync`/`--delete` para forçar re-registro.

## Conclusão parcial

O roteamento HTTP do edge parece ser registrado na criação do grupo/API; pushes posteriores
não republicam as rotas novas para o edge. É necessário um passo na interface do Xano
(botão de publicar/re-deploy ou recriação do grupo pelo usuário) ou orientação oficial.

## Decisão pendente do usuário

- Opção A: no editor do Xano, localizar o API group **C1 Proof Temp** e publicar/ativar as
  rotas novas (se houver botão ou toggle).
- Opção B: excluir o API group **C1 Proof Temp** no editor (contém apenas rotas de prova) e
  reautorizar um único push do pacote completo (grupo + tabela + todas as rotas), que foi o
  padrão que funcionou (push inicial).
- Opção C: cadastrar manualmente os 5 registros sintéticos (TEST-C1-*) na UI e prosseguir
  com a prova usando apenas as rotas HTTP já registradas (`baixa`, `estado`), sem rotas de
  seed/reset. Os testes C e D (rollback multi-item e concorrência) ainda são possíveis com
  baixa+estado; o caso E (deadlock) também pode ser tentado nessas mesmas rotas.

Nada foi publicado no fluxo cliente/produção; nenhum dado real foi tocado.
