## Decisions
Snapshot de 98 documentos fora do Git, sem records/env/drafts. Usar os GUIDs das duas queries publicadas; pacote sem descritor de grupo, schemas ou registros.
Adicionar sort name asc à consulta de categorias ATIVO e sort sku asc às variações ATIVO do produto solicitado. Preservar listas de campos, preço, estoque zero, categoria/marca inativa omitidas e notfound de produto inativo. Não adicionar desempate, paginação ou afirmar ordem estável entre chaves iguais.
Partir da serialização publicada e adicionar somente sort; espelhar essa representação nos arquivos locais após revisão. O return list explícito já existe no publicado e será preservado.
Listagem products: comparar por tokens, permitindo somente formatação, vírgulas, delimitadores de expressão, GUID e ordem das propriedades de consulta return/where/sort. Isso não prova toda a semântica; leitura anônima deve verificar forma/status/ordem sem versionar corpos ou URLs assinadas.
## Verification
Validar OpenSpec; testes existentes de catálogo/parser e prova de contrato focada nas duas consultas. Dry-run deve atualizar exatamente duas queries. Antes de publicar, apresentar pacote concreto para revisão. Após autorização: pull independente, comparação de todas as identidades e probes GET anônimos de categorias/lista/detalhe e ID inexistente. Não mutar catálogo para fabricar cenários.
## Risks and limits
Leituras públicas dependem do conteúdo existente; dados iguais não demonstram casos de inatividade ou empate. Snapshots brutos permanecem externos por conter metadados privados. Não arquivar ou marcar publicação como feita enquanto não verificada.
