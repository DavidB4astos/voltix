# Validação da change de imagens — 27/10/2026

- 153 testes aprovados (150 anteriores + 3 verificações de asset ausente/crédito incompleto/fallback). Compilação Reflex concluída em 11,005 s. OpenSpec strict válido.
- Navegador em 1440px e 1024px: sem imagens quebradas, sem overflow horizontal; hero preserva proporção panorâmica 3:1 com object-fit contain. Um H1 na Home.
- Controle em 390px: sem imagens quebradas/overflow; nova variante de header desktop permanece oculta. Nenhum redesenho mobile; apenas assets compartilhados.
- Fotografia da vitrine: MX Master 3S e receptor, HS05; fotografia editorial distinta: lateral HS17. As duas têm crédito Hayden Schiff, fonte Commons e licença CC BY 4.0 visíveis.
- Navegação preservada: clicar no mouse abre /catalogo?product_id=25 e o painel de detalhes existente; retorno para Home funciona.
- Hero WebP gerado tem 2172×724 e 94.658 bytes. Identificado como cenário ilustrativo gerado por IA, sem representar SKUs. Nenhuma fotografia real de produto foi fabricada.
- Foto K120 original e CPU CC0 mantidas. Alternativa de teclado rejeitada por layout QWERTZ distinto, conforme assets.md. A uniformização completa das fotos depende de uma foto autorizada da variante correta; não é apresentada como concluída.
- Captura home-desktop.png conferida visualmente na versão atual. Sem login, compra, alteração de registros Xano ou push.
- O DOM inclui o rótulo Connection Error já observado anteriormente; os dados e a navegação acima renderizaram normalmente. Não constitui teste de estabilidade contínua do backend nem auditoria completa de acessibilidade.
