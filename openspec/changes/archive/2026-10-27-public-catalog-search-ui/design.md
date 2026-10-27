## Decisions
- Reutilizar public_catalog_search e o cache com chave categoria/termo. Adicionar public_catalog_search_input apenas para o rascunho.
- Submeter busca e trocar categoria atualizam o estado e navegam para URL codificada com urlencode. enter_public_catalog lê q e categoria e usa o loader público existente. Se a URL já for a mesma, executar o loader diretamente, inclusive para refazer uma consulta após erro.
- Mudar categoria preserva o termo aplicado; rascunho não submetido é descartado ao aplicar categoria. Limpar filtros volta para /catalogo sem q/category_id. Toda mudança de filtros fecha o detalhe anterior.
- Marcar loading antes da navegação; desabilitar controles durante a carga. Não mostrar a grade anterior nem contagem como resultado confirmado durante loading/erro.
- A busca faz parte de um form sem reset no submit, acessível por rótulo e Enter. Categoria tem rótulo acessível. Status de resultados é anunciado sem mover foco à força.
- CSS restrito às classes vx-catalog-tools e vx-catalog-results, carregado apenas no catálogo. Sem novos frameworks, sem pesquisa a cada tecla.
- Contrato de q por nome já existe no XanoScript. Não fazer push no Xano. Buscar marcas só encontra nomes que já contêm a marca; não é filtro novo de marca.

## Validation
Testes de normalização, URL/encoding, combinação/limpeza, ausência de consulta na digitação, recarga da mesma URL e preservação de detalhes/contexto. Conferir no navegador busca, Enter, filtro combinado, vazio e limpeza com GETs reais, sem login/compra. Compilar e validar OpenSpec.


## Recursos de rede em falha
O teste HTTP isolado evidenciou resposta HTTPError aberta após falha pública. O cliente fecha o objeto de resposta antes de propagar a mesma exceção; mensagem, logging sanitizado, status e retry permanecem. Um teste garante que o corpo HTTP seja fechado. Não altera o endpoint nem o número de tentativas.
