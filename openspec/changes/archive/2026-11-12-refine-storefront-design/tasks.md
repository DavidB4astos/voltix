## 1. Preparação e auditoria

- [x] 1.1 Confirmar a captura da auditoria visual (375/768/1280) nas páginas
      `/`, `/catalogo`, `/cliente`, `/carrinho`, `/checkout`, `/pedidos` e registrar
      os pontos de partida — verificação: auditoria executada em 375/768/1280 (header
      mobile volumoso, categoria recortada, grade de 1 coluna em 768 px, créditos densos)
- [x] 1.2 Confirmar que backend, Xano, rotas e State de negócio ficam fora do escopo —
      verificação: escopo aprovado conferido no proposal
- [x] 1.3 Subir o servidor de produção local e restaurar `reflex.lock/*` após o uso —
      verificação: `git status` sem migração acidental

## 2. Navegação pública compacta abaixo de 1024 px

- [x] 2.1 Criar o tratamento mobile do cabeçalho público em `assets/voltix-navigation.css`
      (barra de altura fixa, identidade à esquerda, Início/Produtos ao centro e ações
      de conta/carrinho à direita, rótulos curtos com ícones) — verificação: todos os
      destinos atuais permanecem, sem novos destinos
- [x] 2.2 Atualizar `site_header()` em `voltix/voltix.py` para renderizar o cabeçalho
      compacto abaixo de 1024 px e o desktop a partir de 1024 px, preservando
      `aria_current`, `aria_label` e destinos — verificação: `aria-current` na rota atual e links das mesmas rotas
- [x] 2.3 Recolher o "cabeçalho legado" para uso não-público (ou removê-lo do fluxo
      público) sem alterar páginas internas — verificação: legado removido do fluxo público; páginas internas inalteradas
- [x] 2.4 Ajustar `site_header`/`site_footer` para o comportamento de `aria-current` e
      ativo por rota nas páginas públicas compactas — verificação: 375 px inspecionado

## 3. Barra de categorias da Home

- [x] 3.1 Adicionar `scroll-snap`, trilho com rolagem suave e fade/affordance nas bordas
      da `.vx-home-category-bar` em `assets/voltix-home.css` — verificação: rótulos não
      recortados em 375 px e cue visual visível
- [x] 3.2 Garantir rolagem via teclado/toque sem perder os itens nem a ordem —
      verificação: inspecionado em 375 px e 768 px

## 4. Catálogo responsivo e créditos compactos

- [x] 4.1 Ajustar faixas de colunas em `assets/voltix-catalog-cards.css`: 1 coluna
      abaixo de 768 px, 2 colunas entre 768 e 1023 px, 3 colunas a partir de 1280 px —
      verificação: grade renderizada nas duas faixas sem overflow
- [x] 4.2 Fixar `aspect-ratio`/altura estável da área de mídia dos cards — verificação:
      altura igual por linha em 768 px e 1280 px
- [x] 4.3 Compactar `compact_credit` no catálogo: tipografia menor, uma linha quando
      possível, mesmo autor/fonte/licença/aviso e links acessíveis por teclado —
      verificação: licença visível e contrastada
- [x] 4.4 Revisar densidade do grid em 375 px (stacking de CTA e mídia) — verificação:
      sem overflow nem texto cortado

## 5. Testes

- [x] 5.1 Adicionar testes estruturais: cabeçalho mobile compacto com destinos e
      `aria-current`, grade de cards por faixa e presença de `scroll-snap`/fade —
      verificação: `python -m unittest tests.test_storefront_design`
- [x] 5.2 Preservar e ajustar testes existentes de navegação/rodapé/home — verificação:
      suíte existente verde (422 testes)
- [x] 5.3 `openspec validate refine-storefront-design --strict` — verificação: válido

## 6. Verificação visual e encerramento

- [x] 6.1 `reflex compile` — verificação: sucesso (`compile --dry` OK)
- [x] 6.2 Servidor local e capturas em 375/768/1280 px das páginas públicas — verificação:
      `/`, `/catalogo`, `/cliente`, `/carrinho`, `/checkout`, `/pedidos` sem overflow e
      sem cabeçalho dominante
- [x] 6.3 `git diff --check` — verificação: sem problemas (apenas aviso LF/CRLF)
- [x] 6.4 `openspec validate --all --strict` — verificação: todas as specs válidas (29 itens)
- [x] 6.5 Restaurar `reflex.lock/*` — verificação: `git status` limpo
- [x] 6.6 Sincronizar specs, arquivar a change e atualizar docs — verificação: diretório
      em `openspec/changes/archive/` (`2026-11-12-refine-storefront-design`)
- [x] 6.7 Commit/push somente com autorização explícita — verificação: autorização
      registrada; `5ad2d36` em `main`
