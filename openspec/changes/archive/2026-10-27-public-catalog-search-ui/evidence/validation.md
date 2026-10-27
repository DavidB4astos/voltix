# Busca pública — verificação em 27/10/2026

## Implementação
Formulário explícito por nome, Enter/Buscar, rascunho separado do termo aplicado, combinação AND com categoria, limpeza dos dois filtros e dos detalhes. URL usa q/category_id codificados. Mesmo destino retorna o loader para evitar loading preso. Campo/URL/form limitados a 100 caracteres. Apenas o catálogo recebe a nova folha de estilo. Nenhum endpoint ou dado Xano alterado.

## Testes e compilação
163 testes aprovados: 153 anteriores, oito cenários do formulário/URL e dois de recuperação/recursos HTTP (um deles acrescentado à fixture existente). Cobrem digitação sem chamada ao loader, encoding, trim/limite, filtro combinado, limpeza, repetição de URL, entrada contextual e HTTP 503 local com retry preservando q/category_id. Resposta HTTPError é fechada antes de propagar a falha, sem alterar status, mensagem ou número de tentativas. Compilação Reflex e OpenSpec strict aprovados.

## Navegador com dados públicos reais
- Antes de enviar mouse: URL continua /catalogo e status continua com 23 produtos; digitação não aplica busca.
- Enter com mouse retorna 4 produtos; Buscar com MOUSE também retorna 4 (sem distinção de maiúsculas).
- MOUSE + Periféricos retorna 3; reabrir/recarregar a URL conserva campo, categoria e contagem.
- mouse + Monitores retorna zero e a mensagem específica, sem a grade anterior.
- Limpar filtros restaura /catalogo e 23 produtos. Também fecha detalhes que estavam abertos.
- Repetir a consulta da mesma URL conclui e reabilita Buscar. Uma nova busca teclado retorna 1 produto.
- Botão Buscar alcançado por Tab com foco sólido e 44px de altura; Enter ativa a busca. Rótulos do campo e categoria presentes.
- 1440/1024px sem overflow; controle 390px também sem overflow, com controles empilhados. Não é redesenho mobile.

## Limites
Busca é por nome conforme o contrato existente, não por um índice separado de marcas, autocomplete ou tolerância a erros. Falha/retry foram testados contra servidor HTTP local isolado; não se provocou indisponibilidade do Xano. A estabilidade contínua, leitor de tela e checkout completo não foram auditados. O rótulo Connection Error permanece no DOM como nas revisões anteriores, mas os dados e ações citados renderizaram normalmente. Sem login, compra, alterações remotas ou push. O visual dos cards do catálogo, inclusive produtos sem foto, é trabalho futuro.
