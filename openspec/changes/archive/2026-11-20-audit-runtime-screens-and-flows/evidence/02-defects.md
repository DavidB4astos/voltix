# Defeitos encontrados em execução — 20/11/2026

Classificação: **bloqueador de demo** (impede uma jornada que a entrega precisa mostrar),
**correção imediata** (visível e barato de corrigir), **pós-entrega** (incomoda, não impede),
**limitação** (causa externa) ou **falso positivo**.

## D1 — Catálogo público exibe produtos de teste (bloqueador de demo)

- Rota: `/catalogo` (visitante).
- Obtido: 23 produtos, dos quais **1 tem nome de teste explícito**
  (`TMP-VALIDB-20261015142856-A`) e 2 têm nomes de rascunho (`Notebook Voltix Teste Hp`, `mouse`).
- Esperado: catálogo público sem resíduos de testes/banco de validação.
- Evidência: inventário (contagem e nomes extraídos do DOM em 1280 px).
- Impacto: na demonstração, o visitante vê lixo de teste antes de ver o catálogo.

## D2 — Cards do catálogo não exibem preço (correção imediata)

- Rota: `/catalogo` (visitante).
- Obtido: cada card mostra marca, nome, categoria, descrição, crédito de imagem e ação; **não
  exibe preço**. O preço só aparece no painel de detalhes.
- Esperado: a capability `visual-interface` exige alinhamento de "imagem, preço e ação" nos cards
  do catálogo (requisito consolidado e cenário "cards alinham imagem, preço e ação").
- Evidência: `product_card` em `voltix/voltix.py` não renderiza preço; varredura do DOM não
  encontrou valor monetário nos cards.
- Impacto: loja sem preço na vitrine, contrariando o requisito visual consolidado.

## D3 — Selo "Built with Reflex" sobrepõe o rodapé (correção imediata)

- Rotas: todas (públicas e internas).
- Obtido: o selo fixo no canto inferior direito cobre o texto do rodapé ("Preços e pagamentos…"
  fica cortado) e, no painel Pedidos, cobre a ação do canto.
- Esperado: conteúdo do rodapé legível.
- Evidência: capturas em 1280 px; selo renderizado pelo runtime do Reflex.
- Nota: existe opção de configuração `show_built_with_reflex` (documentada; em algumas versões
  restrita a planos pagos). Verificar viabilidade antes de prometer a correção.

## D4 — Oito de 23 produtos sem imagem (correção imediata)

- Rota: `/catalogo` (visitante).
- Obtido: 8 cards com o placeholder "Imagem não disponível": Mouse Logitech G203 LIGHTSYNC,
  Mouse Logitech M90, Notebook Voltix Teste Hp, Processador AMD Ryzen 5 5600, Roteador TP-Link
  Archer C6, SSD WD Blue SN580 1TB, `TMP-VALIDB-…` e `mouse`.
- Esperado: catálogo com imagens ou com tratamento visual intencional para itens sem foto.
- Impacto: na demo, metade dos cards com placeholder enfraquece a vitrine. Cinco desses itens já
  estavam registrados como pendentes (G203, M90, SN580, Ryzen 5 5600, Archer C6).

## D5 — Cabeçalho mobile esconde "Acesso interno" (pós-entrega)

- Rota: `/` e demais públicas em 375 px.
- Obtido: a fileira de pílulas tem rolagem horizontal; "Acesso interno" fica fora da viewport
  (posição 349–456 px em viewport de 375 px) e depende de rolagem para ser alcançado.
- Esperado: destino da equipe alcançável sem depender de gesto de rolagem.
- Impacto: equipe precisa rolar o cabeçalho para achar a entrada interna; não impede o uso.

## D6 — Total quebra de linha no painel Pedidos (pós-entrega)

- Rota: `/interno` → Pedidos (1280 px).
- Obtido: valores altos como `R$ 2999,90` quebram em duas linhas na coluna "Total".
- Esperado: valor em uma linha na coluna.
- Impacto: leitura prejudicada em valores grandes.

## D7 — "Connection Error:" na árvore de acessibilidade (falso positivo)

- Rota: `/catalogo`.
- Obtido: o snapshot de acessibilidade trouxe `generic description="Connection Error:"`, mas a
  busca no DOM por esse rótulo não encontrou elemento, não houve mensagens de erro no console e o
  detalhe do produto carregou normalmente.
- Veredito: não confirmado como defeito visível. Registrado para nova checagem em uma sessão
  limpa, sem risco de marcar falso positivo.

## Limitações (causa externa, não defeito de código)

- Sessão de **Cliente** indisponível: credenciais de teste rejeitadas com HTTP 403; as jornadas
  autenticadas de carrinho/checkout/pedidos não foram exercitadas nesta auditoria.
- **Atendimentos** lista vazia (sem registros na base) — estado legítimo, não distingue "vazio" de
  "falha"; o formulário carrega.
- Upload de imagem de produto: HTTP 403 histórico no plano Free, não validado.
- Entrega de e-mail de recuperação: não exercitada (limite do plano Free).
- 5 imagens de produto pendentes: dependem de fonte de imagem/direitos; decisão do usuário
  congelou novas imagens de produto.

## Escopo fechado proposto para a change de correção

1. **Limpeza do catálogo** (D1): remover/inativar os resíduos de teste que aparecem no catálogo
   público (critério: nenhum produto com nome de teste visível ao visitante).
2. **Preço nos cards** (D2): exibir preço no card do catálogo, respeitando o requisito de
   alinhamento e mantendo o detalhe inalterado (critério: card com imagem, preço e ação).
3. **Selo do Reflex** (D3): avaliar e, se viável, ocultar sem comprometer o layout (critério: texto
   do rodapé integralmente legível).
4. **Imagens ausentes** (D4): definir tratamento para os 8 itens sem foto (critério: vitrine sem
   placeholders soltos ou com placeholder padronizado).
5. **Cabeçalho mobile** (D5) e **quebra de Total** (D6): incluir se o prazo permitir.

D7 e as limitações ficam registradas, fora do escopo de correção.
