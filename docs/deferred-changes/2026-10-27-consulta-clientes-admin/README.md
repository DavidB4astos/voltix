# Consulta administrativa de clientes — rascunho adiado

Status em 27/10/2026: **ADIADA, NÃO IMPLEMENTADA/VALIDADA COMO FUNCIONALIDADE COMPLETA**.

Esta revisão prevalece sobre marcações antigas de conclusão em tasks.md. Os cinco artefatos e o endpoint em draft/customers_GET.xs foram preservados com bytes idênticos aos arquivos locais encontrados. O endpoint foi retirado de xano/api/admin para não integrar acidentalmente um push de workspace. Não executar/publicar o rascunho. Nenhuma chamada de escrita foi feita ao Xano nesta organização; o estado remoto desse endpoint não foi auditado.

## Revisão estática
- tasks.md solicita leitura anônima, enquanto proposal/spec e o código exigem ADMINISTRADOR ativo. A consulta deve exigir autenticação e autorização no Xano.
- design.md alterna entre e-mail completo e máscara apenas na interface; proposal/spec exigem máscara. Definir contrato único com minimização no backend.
- O código consulta nome, e-mail e data_cadastro, mas a tabela local CLIENTE define nome_completo, email e created_at. Validar o schema real antes de implementar.
- foreach ($cliente) usa a variável antes de defini-la, em vez de percorrer $customers.
- O filtro status apenas verifica a existência de um registro; não restringe a listagem. A busca e o status não são combinados corretamente.
- Não há paginação/limite de 50 implementado; a máscara usa três asteriscos em vez dos cinco especificados.
- Não foi localizada integração de listagem/busca de clientes no frontend atual por inspeção dos símbolos e rotas; não considerar as tarefas de frontend concluídas.
- Há cinco testes de endpoint/permissões ainda desmarcados nos artefatos. A suíte geral existente não valida este endpoint novo.
- O delta contém texto com caracteres inválidos e cenário chamado Anonymous admin; revisar a codificação e os cenários de autorização.

## Condições de retomada
1. Aprovar escopo e contrato coerentes com a tabela real, incluindo máscara, filtros, paginação e detalhe.
2. Corrigir artefatos e reabrir a change no OpenSpec, restaurando apenas um rascunho revisado ao diretório publicável.
3. Validar sintaxe no Xano e testar acesso anônimo negado, cliente/funcionário negados, administrador inativo negado e administrador ativo permitido.
4. Verificar filtros combinados, máscara, paginação, vazio, erro e 429; integrar a interface e registrar evidências sem dados pessoais reais.
5. Publicar somente após revisão específica; não tratar o arquivamento desta organização como aprovação desse endpoint.
