## 1. Artefatos e validação

- [x] 1.1 Manter `proposal.md`, deltas de `public-catalog`/`visual-interface`, `design.md` e
      `tasks.md` coerentes com o escopo aprovado ("Todos os 6") — verificação: leitura cruzada
- [x] 1.2 `openspec validate fix-demo-blockers --strict` e `openspec validate --all --strict` —
      verificação: change válida; 29 itens válidos no total; sem erros de whitespace

## 2. Correções locais (D3, D5, D6, D4)

- [x] 2.1 D3: `show_built_with_reflex=False` em `rxconfig.py` — verificação: `reflex compile` e,
      no servidor 3091, nenhum badge "Built with Reflex" no DOM/HTML e rodapé legível em 1280 px
- [x] 2.2 D5: `.vx-nav__mobile-nav` com quebra de pílulas e sem máscara na borda direita —
      verificação: em 375 px, `Acesso interno` em `left=112, right=219` dentro da viewport de 375,
      sem overflow; teste existente de scroll do header atualizado
- [x] 2.3 D6: classe `vx-internal__money-cell` na célula de Total de `order_row` e regra CSS com
      `white-space: nowrap`/`tabular-nums` — verificação: `R$ 2999,90` com 1 linha (`Range`),
      `white-space: nowrap`, sem overflow horizontal na tabela de 2 pedidos
- [x] 2.4 D4: placeholder padronizado em card e detalhe, mantendo o texto `Imagem não disponível` —
      verificação: 8 cards com o mesmo bloco tracejado no DOM; nenhuma foto ou crédito inventado

## 3. Preço no catálogo (D2)

- [x] 3.1 Adicionar `preco_minimo` em `xano/api/public_catalog/products_GET.xs` — verificação:
      `db.query variacao_produto` ATIVO ordenado por preço crescente; endpoint publicado
- [x] 3.2 Estender `PublicProductEntry` com `min_price: str = ""` e validar `preco_minimo` em
      `_public_product_entry` via `Decimal`, preservando ausência como `""` — verificação: 10 testes
      novos, incluindo `119.9`, `119`, `null`, string inválida, booleano e negativo
- [x] 3.3 Exibir `a partir de R$ <valor>` no `product_card` somente quando houver preço real —
      verificação: 22 de 23 cards exibem `a partir de R$ 119,90` etc. na instância limpa 3092; o
      único sem preço é `TMP-VALIDB-…`, sem variação ativa (nenhum valor inventado)
- [x] 3.4 `xano workspace push -d xano --dry-run -i "api/public_catalog/products_GET.xs"` —
      verificação: preview de 1 endpoint mostrado; publicação `--force` autorizada em 20/11/2026
- [x] 3.5 Após publicação, chamada somente leitura ao endpoint público — verificação: 23 produtos
      com `preco_minimo`; conferência em 5 produtos contra o menor preço ativo do detalhe

## 4. Limpeza de dados (D1)

- [x] 4.1 Confirmar os três produtos na listagem administrativa — verificação: nomes exatos
      `TMP-VALIDB-20261015142856-A`, `Notebook Voltix Teste Hp`, `mouse`
- [x] 4.2 Inativar (`status = "INATIVO"`) os três produtos pela interface administrativa com sessão de
      ADMINISTRADOR — verificação: **autorização explícita de gravação obtida antes das ações**;
      badges alterados para `Inativo` e ações para `Reativar produto`
- [x] 4.3 Recarregar o catálogo público na instância limpa 3092 — verificação: `Catálogo · 20 produtos`,
      nenhum dos três nomes no DOM, 20 cards com preço e demais produtos preservados

## 5. Verificação e fechamento

- [x] 5.1 Suíte completa — verificação: `.venv-novo-pc\Scripts\python.exe -m unittest discover -s tests -q`
      → 445 testes OK
- [x] 5.2 `reflex compile` — verificação: sucesso (`Success: App compiled successfully in 2.106 seconds`)
- [x] 5.3 Inspeção visual em 1280/768/375 px nas rotas afetadas — verificação: sem overflow no
      documento, rodapé legível, `Acesso interno` visível (375 px: 112–219), 20 cards com preço e
      5 placeholders; Pedidos mantém valor em uma linha com rolagem interna da tabela em 375 px
- [x] 5.4 `git diff --check` — verificação: sem erros de whitespace; `reflex.lock/*` restaurado antes
- [x] 5.5 Arquivamento com consolidação de specs (`openspec archive fix-demo-blockers -y`) —
      verificação: `public-catalog` (+1) e `visual-interface` (+2, ~1) atualizadas; change em
      `archive/2026-11-20-fix-demo-blockers/`; `openspec validate --all --strict`: 28 itens válidos
- [x] 5.6 Atualizar `docs/AI_AGENT_HANDOFF.md` e `docs/roadmap-changes.md` — verificação: decisões,
      exceção de push Xano autorizado, limitações e estado final registrados
- [x] 5.7 Commit/push somente com autorização explícita — verificação: autorização registrada;
      commit e push executados em 20/11/2026
