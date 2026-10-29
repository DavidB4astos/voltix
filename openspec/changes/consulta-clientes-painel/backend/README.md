# Candidatos de backend — ainda não publicados

O diretório `api/` contém somente um grupo novo e dois endpoints GET. Fica fora de `xano/api/` para não entrar em um push geral acidental. Não copiar nem executar o draft antigo adiado.

A prévia `xano workspace push -p voltix -d openspec/changes/consulta-clientes-painel/backend --dry-run` indicou:

- CREATE API group: Voltix Internal Customers.
- CREATE customers GET.
- CREATE customers/{customer_id} GET.

Nenhuma tabela, registro, variável de ambiente, endpoint existente ou operação de escrita é incluída. Não usar `--sync`, `--delete`, `--records`, `--env`, `--truncate` ou `--force`.

O dry-run é uma prévia de importação, **não prova execução de filtros, máscaras, paginação ou autorização no Xano**. Após revisão específica da publicação, usar push restrito a este diretório, preservando confirmação interativa e transação padrão. Registrar erros sem dados pessoais. Após publicação, obter URLs reais e configurar apenas localmente `XANO_INTERNAL_CUSTOMERS_URL` e `XANO_INTERNAL_CUSTOMER_DETAILS_URL` (esta com `{customer_id}`).

Validar rejeição de anônimo, Cliente e interno inativo e aceitação de FUNCIONARIO/ADMINISTRADOR em contexto autorizado, sem expor registros reais em relatórios. A conferência visual com fixtures e os testes Python não substituem esse gate. Não arquivar como feature concluída antes disso.
