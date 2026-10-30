# Reconciliação verificada — 30/10/2026

- Novo snapshot com 98 documentos, perfil voltix/workspace 147981, sem registros/variáveis/drafts e fora do repositório.
- Product Management: canonical local alterado de voltix-product-management para umWTO5yo; GUID igual ao grupo existente.
- Public Catalog: canonical local alterado de voltix-public-catalog para cVn4Vybh; GUID igual ao grupo existente.
- Somente os campos canonical e guid dos dois arquivos foram ajustados. Descrições e tags locais preservadas; não foram copiadas configurações Swagger nem segredos do snapshot.
- As seis URLs configuradas desses grupos já usam as bases publicadas: Products, Variations, Public categories, Products, Details e Image. Hash de .env antes/depois idêntico; seus valores não estão nesta evidência.
- URLs example.invalid de testes continuam fictícias e não foram substituídas. Nenhuma query, State, handler, regra, registro ou dependência alterada.
- Dry-run de diretório contendo somente dois descritores: API Groups ~2 updated, UPDATE Product Management e UPDATE Public Catalog. Nenhuma criação, exclusão, query ou tabela prevista.
- NÃO foi executado push real. O dry-run identifica as mesmas entidades; ainda prevê duas atualizações porque as descrições/tags locais não coincidem integralmente com as remotas. Isso é uma diferença editorial explícita, não motivo para enviar os grupos nesta change.
- Sem alteração de runtime, a suite da aplicação não foi repetida. Verificação por leitura do snapshot/configuração, diff e dry-run; não declarar um novo E2E remoto.
- Outras divergências de GET administrativos, ordenação pública, joins do carrinho/checkout, defaults de schema e upload permanecem fora do escopo. Não declarar sincronização total e não fazer push global.
