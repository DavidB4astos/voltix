# Implementação local — 29/10/2026

O usuário aprovou o contrato e confirmou que “moderador” significa o ADMINISTRADOR existente. Não criar terceiro perfil. A consulta é a primeira parte do CRM; a organização completa do painel por perfil, histórico interno de compras e atendimentos permanecem para escopos posteriores, sem iniciar outra change em paralelo.

## Evidência de schema

Executado pull de metadados do workspace pelo perfil já existente, em pasta de apoio fora do repositório, sem `--records` e sem `--env`. CLIENTE confirma nome_completo, email, telefone, cpf, status e created_at; user confirma role/status e os dois perfis internos. Nenhum registro de cliente foi solicitado. Não versionar a cópia bruta do workspace.

## Implementado localmente

- Contrato estrito em internal_customers.py, whitelist, validação de máscaras, paginação e limites; payload extra/sensível é rejeitado antes de chegar ao State público.
- Sessão interna privada em GET server-side, sem usar token Cliente. Guarda de perfil/status, invalidação de geração/token/id, limpeza em logout/troca de identidade e 401/403.
- Filtros submetidos, paginação, detalhe, estados vazio/erro/carregamento; retry 429 no máximo uma vez com Retry-After numérico entre 0 e 30 segundos. Sem alterar a política global de outros endpoints.
- Clientes em /interno; gestão de produtos continua com seus guards ADMINISTRADOR existentes. Rótulos de campos associados e hierarquia de títulos conferidos no navegador.
- Candidatos Xano isolados no diretório backend da change, sem publicação. Preview retornou CREATE de um grupo e dois endpoints, sem atualização/exclusão de objetos existentes.
- Configuração de exemplo sem segredos, sem alteração do .env real ou inclusão de URLs privadas.

## Verificação e limites

- 180 testes passaram em 1,910s, com fixtures isoladas. Cobrem normalização, campos extras, contato bruto, limites, paginação vazia, perfis, token interno, respostas obsoletas, logout, fechamento de detalhe e retry limitado.
- App principal compilou a 100%; componente final recompilado na prévia isolada. Navegador 1440×1100, tabela e detalhe com clientes fictícios. Captura anexa. Prévia sem importar App/State do Voltix e sem requisições Xano; controles inertes para conferência visual, não E2E do backend.
- A primeira execução de testes usou pasta temporária do Windows sem permissão e falhou em testes de arquivos; após direcionar TEMP/TMP à pasta de apoio permitida, a suíte passou. Avisos ResourceWarning em fixtures HTTPError não foram falhas da suíte.
- Publicação, execução de sintaxe/máscaras/filtros e autorização real nos dois endpoints ainda pendentes. Não declarar a capability funcional no Xano e não arquivar esta change.
- A consulta permanece indisponível no app sem URLs de configuração válidas; a UI não inventa sucesso nem dados. Sem compras, escrita de registros ou leitura de clientes reais nesta etapa.

OpenSpec: 14 specs e esta change passaram (15 itens, zero falhas). Rascunho adiado preservado com hashes idênticos. Lockfiles regenerados guardados em cópia local ignorada e restaurados para a versão Git. A change segue aberta, sem arquivamento de feature incompleta.
