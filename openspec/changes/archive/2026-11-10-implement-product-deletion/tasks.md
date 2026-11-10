## 1. Preparação

- [x] 1.1 Conferir a spec de `product-management`, as tabelas `produto`, `variacao_produto`,
      `item_pedido` e `item_carrinho` e o endpoint PATCH existente — verificação: leitura
      dos arquivos sem alteração
- [x] 1.2 Confirmar a regra de domínio §8.4 e o conjunto fechado de `error_type` do
      XanoScript — verificação: referências comerciais usam `badrequest` (HTTP 400), não
      `409`

## 2. Backend Xano

- [x] 2.1 Criar `xano/api/product_management/product/product_id_DELETE.xs` com
      `auth = "user"` e `ADMINISTRADOR` ativo verificado antes de ler o produto —
      verificação: precondições no topo do `stack`
- [x] 2.2 Responder `404` para produto inexistente e `403` para sessão sem autorização —
      verificação: precondições com `notfound` e `accessdenied`
- [x] 2.3 Verificar referências em `item_pedido` e `item_carrinho` a qualquer variação do
      produto e recusar com `400` orientando a inativação — verificação: nenhuma exclusão
      quando houver referência
- [x] 2.4 Excluir as variações e o produto em uma única `db.transaction` quando não houver
      referência — verificação: `db.del variacao_produto` por `produto_id` seguido de
      `db.del produto` por `id`
- [x] 2.5 Responder `{id, deleted: true}` sem expor dados internos — verificação: resposta
      limitada ao identificador e ao resultado
- [x] 2.6 Validar o arquivo com o dry-run/importação do Xano — verificação: dry-run
      restrito e publicação aceitarem a query

## 3. Frontend

- [x] 3.1 Adicionar Estado `product_deletion_id` e `product_deletion_name` e os handlers
      `begin_delete_product`, `cancel_delete_product` e `confirm_delete_product` —
      verificação: sessão `ADMINISTRADOR` exigida pelo `_catalog_request`
- [x] 3.2 Renderizar a ação "Excluir produto" e a confirmação em dois passos com nome do
      produto e aviso de exclusão definitiva — verificação: controles desabilitados durante
      a operação
- [x] 3.3 Enviar `DELETE products/{id}`, recarregar a lista e limpar o formulário quando o
      produto excluído estava em edição — verificação: sem sucesso inventado
- [x] 3.4 Mapear falhas `400` de histórico, `401`, `403`, `404` e rede para mensagens
      observáveis — verificação: `400` de histórico distingue a orientação de inativação

## 4. Testes

- [x] 4.1 Cobrir `DELETE` com `record_id`, sucesso com recarga, limpeza da edição e falhas
      `400`/`404` em `tests/test_product_management.py` — verificação: testes focados
      aprovados
- [x] 4.2 Cobrir o XanoScript: autorização antes do negócio, verificação das duas tabelas de
      itens, transação, `db.del` das variações e do produto e resposta limitada —
      verificação: asserções de conteúdo
- [x] 4.3 Ajustar a expectativa de endpoints publicados de 8 para 9 e a asserção da ação de
      exclusão — verificação: testes atualizados ao novo contrato
- [x] 4.4 Executar a suíte completa — verificação: `python -m unittest discover -s tests -q`

## 5. Verificação e publicação

- [x] 5.1 `openspec validate implement-product-deletion --strict` — verificação: válido
- [x] 5.2 `reflex compile` e restauração de `reflex.lock/*` não relacionado — verificação:
      `git status` sem migração acidental de dependências
- [x] 5.3 `git diff --check` — verificação: sem whitespace/conflito
- [x] 5.4 Dry-run de `product_id_DELETE.xs` — verificação: preview com apenas o `CREATE`
      esperado
- [x] 5.5 **GATE** — autorização explícita antes de publicar no Xano — verificação:
      aprovação registrada do usuário
- [x] 5.6 Pull independente pós-publicação — verificação: autorização, checagens,
      transação e GUID preservados
- [x] 5.7 Verificação remota somente leitura da rota publicada — verificação: `401` sem
      sessão; nenhuma exclusão real executada

## 6. Encerramento

- [x] 6.1 Sincronizar a delta com `openspec/specs/product-management/spec.md` e confirmar
      `openspec validate --all --strict` — verificação: validação global
- [x] 6.2 Atualizar `docs/roadmap-changes.md` e `docs/AI_AGENT_HANDOFF.md` — verificação:
      consistente com a evidência
- [x] 6.3 Arquivar a change — verificação: diretório em `openspec/changes/archive/`
- [ ] 6.4 Commit/push somente com autorização explícita — verificação:
      `git status --short --branch` limpo e sincronizado
