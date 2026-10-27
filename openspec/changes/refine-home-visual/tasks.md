## 1. Escopo e implementação
- [x] Registrar escopo inicial e extensões aprovadas de cabeçalho/desktop/contexto.
- [x] Implementar hero sem eyebrow, fotografia com proveniência e fallback próprio.
- [x] Implementar benefícios em faixa e categorias tipográficas com numeração.
- [x] Implementar seleção verificável de até quatro produtos e créditos visíveis.
- [x] Distinguir skeleton, erro/retry, catálogo vazio e ausência de elegíveis.
- [x] Implementar editorial com foto aprovada, crédito e omissão sem asset.
- [x] Implementar navegação desktop pública, página atual e logo para Home.
- [x] Preservar variante legada abaixo de 1024px e na área interna.
- [x] Aplicar referência Apple no desktop sem copiar assets ou marca.
- [x] Corrigir links de categorias e produtos; validar parâmetros; limpar filtros na Home.
- [x] Apresentar detalhes selecionados antes da grade do catálogo.

## 2. Verificações concluídas
- [x] Sintaxe Python e compilação Reflex.
- [x] Suíte de 149 testes, incluindo quatro cenários de entrada contextual.
- [x] Validação OpenSpec strict.
- [x] Navegação real: Monitores abre filtro; mouse abre detalhes; retorno restaura Home completa.
- [x] Parâmetros inválidos abrem catálogo sem detalhe indevido.
- [x] Verificação desktop 1024/1440px sem overflow; controle 390px sem estilo desktop.
- [x] Destinos de cabeçalho e CTA Explorar produtos conferidos na extensão anterior.
- [x] Hierarquia de títulos da Home e foco no CTA conferidos anteriormente.
- [x] Estados e assets ausentes verificados em contexto de teste controlado (evidência histórica).
- [x] Registrar captura desktop atual separada das capturas históricas.

## 3. Pendências — não arquivar como concluída
- [ ] Percorrer toda a Home por teclado e registrar foco de todos os controles.
- [ ] Conferir o CTA editorial no fluxo atual e registrar resultado.
- [ ] Exercitar erro real e retry do servidor em ambiente isolado, sem alterar dados remotos.
- [ ] Revisar e confirmar os textos comerciais de prazo/garantia com o responsável pelo projeto.
- [ ] Concluir revisão final e arquivar/sincronizar a change somente após resolver as pendências.

## 4. Versionamento
- [x] Revisar staged diff limitado à Home e navegação pública aprovada; criar commit local (esta revisão).

As capturas anteriores documentam fases anteriores; não comprovam o layout atual. Ver evidence/README.md. Novas fotos, busca e rodapé pertencem a uma proposta futura e não fazem parte das tarefas concluídas.
