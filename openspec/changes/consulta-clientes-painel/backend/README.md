# Backend publicado — 29/10/2026

O grupo Voltix Internal Customers e seus dois GETs foram publicados após aprovação específica do usuário. Fontes canônicas, com GUIDs e formatação retornados pelo Xano: `xano/api/internal_customers/` (na raiz do projeto). Os candidatos foram retirados deste diretório para evitar cópias executáveis duplicadas.

Prévia e publicação restritas a três documentos, com confirmação interativa e transação padrão. Não foram usados force, sync, delete, records, env ou truncate. A comparação dos pulls antes/depois confirma três arquivos novos, nenhum arquivo existente alterado/removido. Nenhum registro ou variável de ambiente foi importado.

Primeiras tentativas foram rejeitadas por sintaxe; corrigidas preconditions compactas e posição de else em blocos multiline. O push posterior confirmou sucesso. Rejeições anteriores não mudaram os documentos existentes, conforme auditoria.

Ambos os endpoints retornam 401 para anônimo e token inválido. Isso não comprova autorização por perfil com tokens reais, filtros, máscaras ou paginação em execução autenticada. Essas verificações continuam pendentes e impedem arquivar a change como concluída.

As duas URLs estão configuradas somente no .env local; não versionar credenciais ou lista de clientes. Antes de qualquer futura alteração/publicação, executar dry-run restrito ao grupo e revisar a prévia.
