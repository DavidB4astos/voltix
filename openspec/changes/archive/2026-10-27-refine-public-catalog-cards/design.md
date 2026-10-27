## Decisions
- Alterar apenas product_card dentro de public_catalog_page; o painel de detalhes e seus eventos permanecem.
- article com frame 4:3, img object-fit contain, marca, H2, categoria e descrição. A ausência de URL usa ícone decorativo e Imagem não disponível, sem sugerir foto de outro modelo.
- Conteúdo em flex column, descrição flexível e ação final alinhada. Não esconder nomes/descrições por line-clamp.
- Reutilizar o cache de créditos do manifesto por uma função pública que retorna cópias apenas de metadados completos, arquivos existentes e nomes de arquivo seguros. O matcher da imagem usa a própria URL, sem atribuição a produto diferente.
- Crédito compacto visível com autor, fonte e licença; title/aria-label da fonte expõe a atribuição completa original. Não fabricar crédito para URL sem registro.
- Nova folha voltix-catalog-cards.css apenas no catálogo, seletores sob vx-catalog-card. Não alterar estilos globais ou shared surface_card.

## Validation
Testar filtragem/cópia dos créditos, suíte e compilação. Conferir no navegador resultados com foto/sem foto, cabeçalhos, layout, foco e abertura de detalhes; busca/filtros devem continuar. Não provocar indisponibilidade remota. URLs remotas expiradas continuam no fluxo existente; o placeholder desta etapa cobre URL ausente.
