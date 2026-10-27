# Home Voltix — implementação e validação

Data: 27/10/2026. Mudança: refine-home-visual. Não arquivada e sem commit.

## Entregue
- Hero navy de largura completa, fotografia local com proveniência, CTA único e fallback quando o asset falta.
- Conteúdo e CTA antes da imagem no mobile.
- Benefícios em faixa linear, categorias numeradas e responsivas, mantendo os destinos existentes.
- Vitrine com até quatro correspondências verificadas por nome e URL aprovada no manifesto. Três produtos elegíveis no snapshot atual, com atribuição e links de fonte/licença.
- Skeleton inicial, erro com retry, catálogo vazio e omissão sem elegíveis tratados separadamente.
- Seção editorial com fotografia aprovada, crédito legível e omissão se faltar o asset.
- CSS carregado somente na Home, totalmente sob .vx-home. Instâncias do logo nesta página usam h2 para preservar um único h1; implementação compartilhada não alterada.

## Verificações aprovadas
- py_compile e 145 testes da suíte existente (0,416 s na última execução).
- Compilação Reflex 0.9.12 concluída (12,858 s na última compilação funcional).
- OpenSpec strict: Change 'refine-home-visual' is valid.
- Navegador em 360, 390, 768, 1024 e 1440 px: sem overflow horizontal ou imagens quebradas.
- H1 único, foco visível no CTA, alvo principal >=44 px, zoom 200% e movimento reduzido.
- Cenários controlados no navegador: carga inicial, erro antes da primeira carga (sem skeleton ocultando-o), vazio, foto de produto incompatível, zero elegíveis e limite de quatro.
- Construção dos componentes com foto do hero ausente e com todos os assets ausentes: fallback/omissão sem exceção.
- Smoke em /catalogo, /carrinho, /cliente e /interno. Três capturas iguais pixel a pixel ao baseline; catálogo difere apenas em 128 pixels na área 16x16 do indicador de carregamento.
- Comparação de fonte: bytes anteriores e posteriores a home_page() preservados. Nenhuma alteração no State, backend, rotas ou componentes compartilhados. Arquivos de reflex.lock restaurados ao snapshot anterior à compilação.

## Limites e próximo passo
A API pública foi consultada em leitura e respondeu com 5 categorias e 23 produtos. As capturas e cenários usam esse snapshot aplicado ao contexto do navegador de teste, sem alterar a aplicação ou dados remotos. A conexão persistente do servidor local existente não respondeu; carga contínua, retry real e navegação com dados após reinício permanecem pendentes. Não foram realizados login, compra, publicação ou alteração no Xano.

Reinicie o servidor Voltix no terminal do VS Code (Ctrl+C e o comando abaixo, em CMD na raiz do projeto):

    set REFLEX_USE_NPM=true
    .venv-windows\Scripts\python.exe -m reflex run

Depois confira http://localhost:3000/. As tarefas pendentes continuam abertas; não arquivar antes dessa confirmação.
