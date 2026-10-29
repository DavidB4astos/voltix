# Publicação restrita — 29/10/2026

- Usuário aprovou publicação do grupo e dos dois GETs. Nenhuma nova operação fora desse escopo.
- Dry-run indicou CREATE de Voltix Internal Customers e customers GET / customers/{customer_id} GET.
- Dois retornos HTTP 400 apontaram sintaxe: precondition com múltiplas atribuições em uma linha e else na mesma linha. Blocos normalizados; terceira tentativa publicada com sucesso, três GUIDs sincronizados.
- Comparação de metadados antes/depois: 95 → 98 documentos, apenas três novos no grupo; nenhum existente modificado/removido. Pulls sem registros e sem variáveis de ambiente. Evidência sanitizada em publication-scope.json.
- Testes HTTP reais: lista e detalhe retornaram 401 para requisições anônimas e token inválido. Nenhum corpo de resposta de cliente foi lido ou impresso.
- URLs locais configuradas nos dois nomes aprovados, preservando os demais valores do .env. Nenhum segredo/URL privada persistido em evidências.
- Código publicado recuperado do Xano e promovido para xano/api/internal_customers; candidatos removidos para evitar duplicação.
- **Pendente:** validar Cliente autenticado negado, interno inativo negado e funcionário/administrador ativos permitidos; filtros combinados, máscaras, paginação e fluxo real em contas de teste autorizadas. Não foram inventados resultados positivos.
- 180 testes Python e prévia desktop com fixtures passaram na etapa local anterior. Isso não substitui a validação autenticada no Xano. Change permanece aberta.

## Revalidação local
- OpenSpec strict aprovado novamente e 180 testes Python passaram (TEMP/TMP apontados para pasta de trabalho gravável).
- Sessão real de Funcionário confirmou acesso ao painel; diagnóstico local confirmou execução de search_internal_customers e load_internal_customers, com guarda de autorização positiva.
- Busca sem correspondência exibiu Consulta indisponível. Portanto o fluxo autenticado de consulta ainda não foi aprovado; investigação em andamento, sem registrar token, senha ou corpo de clientes.
- Diagnóstico executado fora do repositório, sem mudar comportamento de negócio; nenhuma evidência de erro foi tratada como sucesso.

## Correção e primeira validação autenticada
- Diagnóstico sanitizado identificou HTTP 500 ERROR_FATAL: Unable to locate var: page.items.
- Causa: output da db.query paginada selecionava campos no nível raiz; ajustado para items.id/items.nome_completo/items.email/items.telefone/items.status/items.created_at, preservando itemsTotal e pageTotal.
- Dry-run limitado a customers_GET.xs mostrou somente um UPDATE; publicação do único documento concluída com sucesso.
- Funcionário ATIVO: busca por termo sintético sem correspondência retornou objeto com os cinco campos do contrato e a UI exibiu estado vazio, sem erro. Repetido com status ATIVO, TODOS e INATIVO.
- Evidência recortada somente no painel, sem identidade da conta, senha, token ou clientes. Essa busca vazia não comprova máscaras de registros, paginação com resultados, detalhe nem permissão de Administrador/Cliente/inativo; continuam pendentes.
