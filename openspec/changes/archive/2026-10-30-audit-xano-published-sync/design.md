## Method
Obter snapshot pelo workspace pull em diretório externo ao repositório, perfil voltix/workspace 147981, sem flags env/records/draft/verbose. Comparar por identidade lógica de grupo/rota/verbo em vez de nome do arquivo. Normalizar comentários, espaços, GUID gerado, aspas opcionais de identificador/default enum, separadores e fences de expressão. Não afirmar equivalência semântica plena a partir desta normalização.
## Safety and limits
Não versionar snapshot bruto, .env, credenciais ou configurações Swagger. Probes somente GET: saúde, categorias públicas, negativas de autenticação e cliente com ID inexistente. Não consultar lista antiga de clientes nem executar PATCH/DELETE/POST. Nenhum teste autenticado de mutação nesta auditoria. Diferenças não corrigidas automaticamente.
## Verification
Registrar totais, rotas divergentes e status HTTP sem corpos privados. Validar documentação OpenSpec e conferir escopo do commit. Suite da aplicação não precisa ser repetida para documentos sem alteração de código.
