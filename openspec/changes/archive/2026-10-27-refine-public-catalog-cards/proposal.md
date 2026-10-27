## Why
Os cards atuais não reservam imagem quando ela falta, cortam fotos com object-fit cover, repetem H1 por produto e deixam os textos junto à borda. O usuário autorizou melhorar cards e apresentação dos produtos após a busca.

## What Changes
- Cards semânticos com nome em H2, marca/categoria secundárias e descrição real sem truncamento.
- Área visual com proporção estável, fotos contidas sem distorção e placeholder neutro quando não há URL.
- Botão Ver detalhes consistente e com nome acessível específico do produto, preservando o evento existente.
- Créditos das fotos locais aprovadas apresentados com autoria, fonte e licença; atribuição completa disponível no título da fonte e no manifesto.
- Estilos exclusivos do catálogo, preservando grade responsiva, busca, filtros, detalhes e regras de compra.

## Capabilities
### Modified Capabilities
- public-catalog: apresentação dos cards públicos e créditos das fotos aprovadas.

## Out of Scope
Novas fotos ou produtos, remoção de registros de teste, preços/estoque/avaliações nos cards, backend/Xano, autenticação, checkout, redesign do painel de detalhes, header, footer, Home e dependências. Não completar fotos ausentes com outros modelos. Foco em desktop; preservar funcionamento responsivo básico.
