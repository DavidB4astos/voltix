## Context
C4 e shell interno estão arquivados. Refinar uma área por vez sem reabrir regras de acesso.

## Decisions
- Manter submit para busca e handlers existentes; sem busca por tecla nem novas chamadas automáticas.
- CSS vx-customers escopado dentro do workspace. Faixa de filtros, tabela com cabeçalho claro, badges de status e paginação com contexto real.
- Lista e detalhe em duas colunas no desktop amplo; empilhar em larguras menores. Nenhum drawer modal que bloqueie a lista.
- Mostrar dados sanitizados já presentes; valores ausentes aparecem como Não informado. Nunca tentar recuperar valor original.
- Estado inicial convida a carregar clientes; loading identificado; mensagem vazia existente diferencia nenhum resultado; mensagens de falha continuam visíveis, com atualização manual. Não inventar conclusão antes de consultar.
- Manter dados e eventos de seleção/reset como estão; layout não deve mudar a segurança nem o ciclo das requisições.

## Verification
Suite existente, compilação e strict OpenSpec. Prévia isolada com dados fictícios: inicial, loading, vazio, erro, lista e detalhe; verificar contraste, foco, nomes dos controles, largura desktop e ausência de exposição de campos adicionais. Verificação com componentes reais e fixtures não comprova APIs remotas. Arquivar somente após resultados e limites documentados.
