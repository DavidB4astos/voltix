## 1. Preparação

- [x] 1.1 Conferir a spec de `product-management`, a tabela `variacao_produto`, o PATCH
      existente e o painel de produtos — verificação: leitura dos arquivos sem alteração
- [x] 1.2 Confirmar que `docs/domain-model.md` §9 e o design da C1 permanecem válidos sem
      entidade de movimentação — verificação: nenhuma mudança de decisão documentada

## 2. Backend Xano

- [x] 2.1 Criar `xano/api/product_management/variation/variation_id_stock_adjustments_POST.xs`
      com `auth = "user"` e `ADMINISTRADOR` ativo verificado antes de ler a variação —
      verificação: precondições no topo do `stack`
- [x] 2.2 Validar `delta` não nulo, variação existente e estoque suficiente com
      `db.increment` guardado — verificação: guarda
      `quantidade_disponivel >= $required_quantity` e `return = {type: "count"}`
- [x] 2.3 Responder a variação atualizada com allowlist de campos — verificação: somente
      `id`, `produto_id`, `nome_ou_descricao`, `sku`, `preco`, `quantidade_disponivel`,
      `status`, `created_at`, `updated_at`
- [x] 2.4 Rejeitar delta zero, variação inexistente e estoque insuficiente sem escrita —
      verificação: erros `inputerror`, `notfound` e `badrequest`
- [x] 2.5 Validar o arquivo com o dry-run/importação do Xano — verificação: dry-run
      restrito e publicação aceitaram a query após trocar `-$input.delta` por
      `0 - $input.delta`

## 3. Frontend

- [x] 3.1 Adicionar sufixo opcional de caminho em `_catalog_request` para reutilizar
      `XANO_VARIATIONS_URL` — verificação: requisição
      `variations/{id}/stock-adjustments` montada server-side
- [x] 3.2 Adicionar Estado e handlers `begin_stock_adjustment`, `cancel_stock_adjustment`,
      setters e `save_stock_adjustment` — verificação: sessão `ADMINISTRADOR` exigida pelo
      `_catalog_request`
- [x] 3.3 Renderizar a ação "Ajustar estoque" e o formulário dedicado com rótulos,
      quantidade atual, direção e quantidade positiva — verificação: controles desabilitados
      durante a operação
- [x] 3.4 Validar quantidade maior que zero e mapear falhas para mensagens observáveis —
      verificação: sem sucesso inventado; valores do formulário preservados em caso de erro
- [x] 3.5 Recarregar a lista após sucesso e exibir a quantidade confirmada pelo backend —
      verificação: mensagem de falha quando a recarga não confirmar

## 4. Testes

- [x] 4.1 Cobrir payload/validação, chamada `POST`, sucesso com recarga e falhas
      `400`/`403`/`404`/rede em `tests/test_product_management.py` — verificação: 26 testes
      focados aprovados
- [x] 4.2 Cobrir o XanoScript: autorização antes do negócio, `db.increment`, delta não nulo,
      sem campo de motivo e allowlist de resposta — verificação: asserções de conteúdo
- [x] 4.3 Executar a suíte completa — verificação: `python -m unittest discover -s tests -q`
      com 356 testes aprovados

## 5. Verificação e publicação

- [x] 5.1 `openspec validate implement-variation-stock-adjustment --strict` — verificação:
      válido
- [x] 5.2 `reflex compile` e restauração de `reflex.lock/*` não relacionado — verificação:
      `git status` sem migração acidental de dependências
- [x] 5.3 `git diff --check` — verificação: sem whitespace/conflito
- [x] 5.4 Dry-run de `variation_id_stock_adjustments_POST.xs` — verificação: preview com
      apenas `CREATE query variations/{variation_id}/stock-adjustments POST`
- [x] 5.5 **GATE** — autorização explícita antes de publicar no Xano — verificação:
      aprovação registrada do usuário em 10/11/2026
- [x] 5.6 Pull independente pós-publicação — verificação: guarda, allowlist e GUID
      `NiRGIMH9OHa57klOkcqHNkk0tOc` preservados
- [x] 5.7 Verificação remota somente leitura da rota publicada — verificação: `401` sem
      sessão; nenhuma escrita real em estoque executada

## 6. Encerramento

- [x] 6.1 Sincronizar a delta com `openspec/specs/product-management/spec.md` e confirmar
      `openspec validate --all --strict` — verificação: validação global
- [x] 6.2 Atualizar `docs/roadmap-changes.md` e `docs/AI_AGENT_HANDOFF.md` — verificação:
      consistente com a evidência
- [x] 6.3 Arquivar a change — verificação: diretório em `openspec/changes/archive/`
- [ ] 6.4 Commit/push somente com autorização explícita — verificação:
      `git status --short --branch` limpo e sincronizado
