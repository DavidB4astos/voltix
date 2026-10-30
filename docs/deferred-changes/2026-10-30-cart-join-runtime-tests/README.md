# Prova de runtime dos joins — ADIADA

Não é uma change ativa nem funcionalidade concluída. A avaliação documental evaluate-isolated-cart-join-tests registrou indisponibilidade de ambiente separado, mantendo gratuito o projeto. Nenhum teste Xano foi executado e nenhuma falha funcional foi demonstrada.

## Condições de retomada
1. Ambiente Xano separado, gratuito e autorizado, sem dados reais. Reconfirmar condições vigentes; não prometer disponibilidade por documentação de outro plano.
2. Perfil e destino inequivocamente diferentes do workspace do Voltix. Uma branch ou tabelas temporárias no banco atual não comprovam isolamento.
3. Escopo e pacote aprovados antes de criar schemas ou publicar queries. Sem promoção automática para o Voltix, cobrança, alteração de licença ou limpeza de dados existentes.

## Casos sintéticos a executar
Criar apenas tabelas mínimas de produtos, variações e itens nesse ambiente. Usar prefixo de teste e identificadores sintéticos; nunca importar registros, contas ou segredos do Voltix. Duas consultas idênticas em table/where/eval/output/sort, diferindo somente pela presença de type inner nos dois joins.

| Caso | Condição | O que medir |
|---|---|---|
| Vínculos completos | Item → variação → produto existentes | Mesmos IDs, valores e uma linha por item nas duas formas |
| Variação ausente | Item sem correspondência na variação | Retorno omitido, campos nulos ou erro; comparar com inner explícito |
| Produto ausente | Variação sem correspondência no produto | Retorno omitido, campos nulos ou erro; comparar com inner explícito |
| Produto/variação inativos | Registros existem, status INATIVO | Separar seleção do join da disponibilidade comercial; não adicionar filtro ATIVO |
| Estoque zero | Vínculos válidos e estoque 0 | Quantidade/preço intactos; indisponibilidade não muda vínculo |
| Vários itens e outro carrinho | IDs inseridos fora de ordem e proprietário distinto | sort id asc e where carrinho_id preservados; nada do outro carrinho |

## Evidência exigida
Registrar versão/plano do runtime de teste, código enviado e retornado por pull, aceitações/erros de sintaxe, resultados sanitizados por caso e diferenças entre as duas formas. Se o serializador remover type, isso isoladamente não prova o default do executor. Se ambas falharem, a comparação não é conclusiva.

Para equivalência, todos os casos devem coincidir e o resultado com inner deve respeitar sua semântica esperada (somente vínculos completos). Um mock ou implementação SQL local demonstra apenas o modelo do teste; não substitui a prova no Xano. Não executar checkout/confirm para testar joins.

## Decisão após a prova
Se houver equivalência comprovada, propor alinhar a representação local à aceita pelo runtime, com testes e publicação somente se necessária. Se houver diferença, avaliar impacto antes de qualquer correção. Se faltar isolamento, manter adiado e seguir outras entregas independentes. Não alterar estoque, histórico, autenticação ou comportamento por suposição.
