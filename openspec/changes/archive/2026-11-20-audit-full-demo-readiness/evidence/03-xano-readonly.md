# Evidência 03 — Xano somente leitura (20/11/2026)

## Objetivo

Comparar contratos locais e publicados e registrar pendências históricas, sem escrita, publicação ou
exposição de dados sensíveis.

## Método (somente leitura)

- `xano workspace pull -d <diretório temporário fora do repositório>` → **126 documentos** baixados
  da instância configurada. Não foram usadas as opções `--env` ou `--records`, portanto nenhuma
  variável de ambiente nem registro de dados foi trazido para disco.
- Nenhum `xano push`, `PATCH`, `POST` ou `DELETE` foi executado. Nenhum arquivo versionado em `xano/`
  foi alterado; o diretório de comparação fica em área temporária fora do Git.
- Uma única chamada HTTP GET ao endpoint público de produtos, com resposta resumida (status, contagem
  e presença do campo), sem imprimir URL, token, corpo ou dados pessoais.
- Não foi repetida a varredura de 23 detalhes de produto que já resultou em
  `ERROR_CODE_TOO_MANY_REQUESTS` (limite de 10 requisições/20 s do plano Free). Não houve HTTP 429.

## Comparação local × publicado

- As listagens locais e publicadas não têm exatamente o mesmo caminho: o repositório usa nomes
  simplificados (`api/customer/...`, `api/public_catalog/...`) e o pull devolve os nomes canônicos
  dos grupos (`api/voltix_customer/...`, `api/product_management/...`). Isso é conhecido e documentado
  em `docs/auditorias/xano-sync-2026-10-30.md`; não é divergência de contrato.
- `api/public_catalog/products_GET.xs`: `preco_minimo` presente nos dois lados (linha 219 local,
  linha 221 publicado), com a mesma origem `$min_price`. O `git diff --no-index -w` mostra diferenças
  de **serialização** — aspas no nome da query, ordem de atributos (`return` antes/depois de `where`),
  vírgulas nos arrays de `output` e linhas em branco — sem alteração semântica observável no campo
  usado pela demo.
- `api/product_management/products_GET.xs`: 46 linhas nos dois lados; diferença apenas em linhas em
  branco.
- Foi encontrado no pull um documento sem contraparte local: `table/tmp_rollback_test.xs`. Trata-se de
  artefato de teste **já registrado como pendência histórica** em
  `docs/auditorias/xano-sync-2026-10-30.md` (linha 35). Não foi consultado, modificado nem excluído:
  ausência no Git não autoriza remoção.

## Leitura pública (4.2)

| Verificação | Resultado |
| --- | --- |
| GET ao endpoint público de produtos | HTTP **200** |
| Itens devolvidos | **20** |
| Itens com `preco_minimo` preenchido | **20/20** |
| HTTP 429 | nenhum |
| Dados pessoais ou credenciais na resposta | nenhum campo desse tipo identificado no resumo; corpo não foi impresso |

O resultado confirma a correção D2 de `fix-demo-blockers` no ambiente publicado: o catálogo tem 20
produtos ativos e todos expõem preço mínimo de variação ativa.

## Pendências históricas mantidas (4.3)

Registradas em `docs/auditorias/xano-sync-2026-10-30.md` e `docs/roadmap-changes.md`, sem nova
publicação nesta auditoria:

1. **Joins de carrinho/checkout:** diferenças preexistentes de `type inner` e simplificação booleana
   preservadas; prova no runtime exige ambiente Xano isolado e autorizado (E6). O plano
   [de retomada](../../../../docs/deferred-changes/2026-10-30-cart-join-runtime-tests/README.md)
   permanece adiado.
2. **Defaults de schema:** pendentes, sem alteração nesta change.
3. **Upload de imagem:** retorno HTTP 403 histórico (`ERROR_CODE_ACCESS_DENIED`, recurso não
   suportado no plano Free); não foi repetido.
4. **Tabela remota temporária:** `tmp_rollback_test`, apenas no remoto, sem exclusão autorizada.
5. **Sincronização integral:** não declarada; a comparação cobriu os contratos relevantes à demo, não
   uma equivalência semântica completa dos 126 documentos.

## Limitações

- O pull de metadados não incluiu `--env` nem `--records`, por decisão de não expor configuração ou
  dados. Isso impede afirmar algo sobre valores de variáveis remotas ou registros.
- Nomes canônicos e simplificados dificultam um diff 1:1 integral; a conferência foi focada nos
  contratos usados pelas jornadas da demo e nas pendências já documentadas.
- Nenhuma leitura autenticada de endpoints internos foi feita nesta frente (exigiria sessão e POSTs de
  login); a matriz de autorização é avaliada na frente 5 por código/specs e pelo comportamento de
  negação anônima já verificado no baseline.
