## 0. Pré-requisito de sequência

- [x] 0.1 Confirmar que a Change `gestao-produtos` foi encerrada e arquivada antes de iniciar qualquer tarefa de implementação (regra do roadmap: uma Change por vez); registrar a confirmação nesta lista. — Confirmado: `gestao-produtos` foi concluída (15/15), arquivada em 2026-10-18 (`openspec/changes/archive/2026-10-18-gestao-produtos/`) e publicada em `origin/main` (commits `3421dc8`, `3b91921`).

## 1. Leitura e parse de arquivos

- [x] 1.1 Implementar o parse de CSV (UTF-8 com ou sem BOM, delimitador `;` ou `,` detectado, cabeçalhos exigidos na ordem definida) usando somente a biblioteca padrão; verificar aceitação e rejeição de arquivos com e sem BOM e delimitadores diferentes.
- [x] 1.2 Implementar o leitor mínimo de XLSX (primeira planilha, `sharedStrings`, texto inline e números; sem fórmulas, datas ou estilos) usando `zipfile` e `xml.etree`; verificar leitura correta e erro explícito para `.xls`, planilha vazia ou célula não suportada.
- [x] 1.3 Implementar a normalização de números (aceitar `.` e `,` decimal) e os limites de arquivo (extensão, tamanho e quantidade de linhas); verificar rejeição clara ao exceder qualquer limite.

## 2. Validação e pré-visualização

- [x] 2.1 Implementar a validação por linha (campos obrigatórios, preço finito maior que zero, quantidade inteira não negativa, agrupamento consistente do Produto) com motivo específico por rejeição; verificar cada regra com dados inválidos isolados.
- [x] 2.2 Implementar a validação contra o catálogo (Categoria e Marca existentes e `ATIVO`; SKU único inclusive com variações inativas; nome de Produto já existente) a partir das listagens administrativas; verificar os três casos de rejeição e o caso positivo.
- [x] 2.3 Implementar a pré-visualização com status por linha (`VÁLIDA`, `ERRO`, `DUPLICADA`) e a indisponibilidade da confirmação sem linhas válidas; verificar que nenhuma gravação ocorre antes da confirmação.

## 3. Orquestração da importação

- [x] 3.1 Implementar o processamento confirmado produto a produto reutilizando o `POST products` existente (agregado com suas variações), com espaçamento entre requisições e backoff na resposta de limite de requisições; verificar o consumo compatível com 10 req / 20 s e a nova tentativa em resposta de limite.
- [x] 3.2 Implementar o relatório final por grupo (`CRIADO`, `PULADO`, `FALHA` com mensagem), o cancelamento em andamento e a orientação de reexecução; verificar falha em um grupo sem interrupção dos demais e retomada por reenvio do mesmo arquivo.
- [x] 3.3 Verificar que toda gravação rejeitada pelo backend (sem sessão, sessão inválida, perfil `FUNCIONARIO`, usuário inativo) interrompe com falha observável e não cria registros.

## 4. Interface administrativa

- [x] 4.1 Adicionar a seção de importação na área de Produtos de `/interno`, visível somente para `ADMINISTRADOR`, com envio de arquivo, pré-visualização e ações de confirmar/cancelar; verificar ausência dos controles para `FUNCIONARIO`.
- [x] 4.2 Conectar as ações aos eventos do State (parse, pré-visualização, confirmação, cancelamento), exibindo progresso, mensagens de erro e o relatório final; verificar estados de carregamento e mensagens após recarregar a página.

## 5. Testes e verificação

- [x] 5.1 Criar testes unitários de parse (CSV com/sem BOM, delimitadores, XLSX montado em teste, limites) e de validação (cada regra de linha, agrupamento, SKU duplicado no arquivo e no catálogo, Produto existente pulado); verificar cobertura dos cenários da spec `product-bulk-import`.
- [x] 5.2 Criar testes de orquestração com HTTP simulado (sucesso, falha em grupo intermediário, resposta de limite de requisições com nova tentativa, cancelamento, rejeição de autorização); verificar relatório parcial e ausência de sucesso simulado.
- [x] 5.3 Executar `python -m unittest discover -s tests -p "test_*.py"`, `python -m py_compile voltix/voltix.py` e `python -m reflex compile --dry`; verificar suite completa verde e ausência de regressões. — Executado: 113 testes verdes, `py_compile` OK, `reflex compile --dry` OK.
- [x] 5.4 Validar com ADMINISTRADOR ativo o envio de um arquivo real pequeno, a pré-visualização, a criação e a reexecução do mesmo arquivo com registros já criados pulados; confirmar comportamento da lista de produtos após recarregar. — E2E executado em 2026-10-18 (Chrome DevTools MCP, sessão ADMINISTRADOR ativa, Xano real, servidor não reiniciado): todos os critérios comprovados, incluindo o cancelamento em andamento após a correção; registros temporários inativados. Evidências no §7.

## 6. Auditoria de escopo

- [x] 6.1 Auditar o diff final para confirmar ausência de tratamento de imagem, atualização/sobrescrita de Produtos existentes, novos endpoints Xano, novas dependências de biblioteca e alterações fora da área de importação; confirmar que nenhum segredo ou token foi versionado.

## 7. Evidências e achados da validação E2E (2026-10-18)

Executada com Chrome DevTools MCP em `http://localhost:3000/interno`, sessão `ADMINISTRADOR` ativo (`teste.moderador@gmail.com`), backend Xano real; servidor Reflex não reiniciado; nenhum produto comercial alterado; nenhum HTTP 429 provocado.

- **Envio + pré-visualização + criação**: `e2e_tmp_test_001.csv` (1 linha) → pré-visualização `1 linha(s), 1 válida(s), 1 produto(s) prontos`, confirmação habilitada → confirmar → `Importação concluída. Criados: 1, pulados: 0, falhas: 0` → produto `E2E_TMP_TEST_001` + variação `SKU-E2E-TMP-001` (ATIVO) presentes na lista.
- **Arquivo inválido**: CSV com linha inválida → status `ERRO` com motivo por linha, `0 válida(s)`, confirmação indisponível, nenhuma gravação.
- **Reexecução do mesmo arquivo (duplicidade pulada)**: reenvio idêntico de `e2e_tmp_test_001.csv` → `1 linha(s), 0 válida(s), 0 produto(s) prontos`, linha `DUPLICADA` — `Produto já existente (pulado).`, botão "Confirmar importação" ausente, zero persistência. Arquivo misto (nome já existente + `SKU-E2E-CANCEL-003` já existente) → ambas as linhas `DUPLICADA` (`Produto já existente (pulado).` / `SKU já existente no catálogo (pulado).`), `0 válida(s)`; após "Atualizar lista": nenhum registro novo (`E2E_DUP_TEST_001` inexistente; `E2E_TMP_TEST_001` permanece com 1 ocorrência).
- **Lista após recarga**: F5 na página → sessão `ADMINISTRADOR` preservada, seção de importação presente, pré-visualização persiste e lista inalterada (1× `E2E_TMP_TEST_001`, 0× `E2E_DUP_TEST_001`, variação `SKU-E2E-TMP-001` única).
- **Cancelamento em andamento — COMPROVADO após correção (2026-10-18)**: o bug registrado anteriormente (progresso/cancelamento só visíveis ao final) foi corrigido. `confirm_bulk_import` passou a `@rx.event(background=True)` com envio de progresso/cancelamento em blocos `async with self:` sequenciais, preservando os registros já criados e abortando apenas antes do próximo `POST` (nunca uma requisição em voo). E2E real com CSVs reais (`e2e_cancel_fix_e.csv`, linhas `E1`/`E2`, `SKU-E2E-CANCEL-FIX-E1/E2`): "Carregando catálogo..." 0,06 s → "Processando 1/2 ... (criados: 0)" 13,6 s → "Processando 2/2 ... (criados: 1)" 17,7 s → clique em "Cancelar importação" em 17,736 s → **"Importação cancelada. Criados: 1, pulados: 0, falhas: 0."** 18,8 s. Checagem por SKU após refresh: `E1` presente, `E2` ausente, `C1`/`C2` ausentes. Progresso limpo e UI desbloqueada ao final. Janela de cancelamento: intervalo entre requisições `BULK_IMPORT_REQUEST_INTERVAL_SECONDS = 3.0`; como o `POST` usa `throttle=False`, a janela útil depende da duração do `POST` anterior — cliques durante "Processando X/Y" são respeitados no próximo check pré-`POST` (a 1ª tentativa, com `POST` longo, concluiu "Criados: 2", o que é o comportamento correto de não abortar requisição em voo). Confirmado também que o `StateProxy` não é reentrante na mesma task (`ImmutableStateError`), por isso todo `sleep` ocorre fora do `async with self`. Cobertura de unidade em `tests/test_product_bulk_import.py` (cancelamento, progresso, concorrência).
- **429 real não provocado** (por instrução, para não gerar carga no Xano Free): retry com espera coberto por `test_ambiguous_429_on_post_is_not_reported_as_success`; precondição de SKU único no `POST products` (400 → `PULADO`) testada.
- **Observações menores**: (1) `_refresh_products` (4 GETs ao fim da importação e no "Atualizar lista") não passa pelo espaçamento `_bulk_import_wait` — apenas leituras, orçamento compartilhado; (2) duplicidades detectadas na pré-visualização não aparecem no relatório final (excluídas dos grupos válidos, conforme `design.md`); o caminho `PULADO` do relatório cobre a duplicidade detectada na confirmação (testado em unidade) e arquivo só com duplicatas não gera relatório porque a confirmação fica indisponível (cenário "Confirmation is unavailable without valid rows").
- **Suíte**: `python -m unittest discover -s tests -p "test_*.py"` (via `.venv`) → **120 testes OK** após a correção do cancelamento/progresso (37 no arquivo `tests/test_product_bulk_import.py`); `python -m py_compile voltix/voltix.py` OK; `reflex compile --dry` "App compiled successfully".
- **Arquivos temporários**: CSVs de teste removidos do repositório. Registros temporários criados pela validação foram **inativados** via UI (`toggle_product_status`, nunca comerciais) em 2026-10-18: `TMP-VALID-20261015142315-A`, `TMP-VALIDB-20261015142856-A`, `TMP-VALID-PLAY-EDITED`, `E2E_TMP_TEST_001`, `E2E_CANCEL_TEST_003`, `E2E_CANCEL_A/B/C`, `E2E_CANCEL_X1–X5`, `E2E_CANCEL_Y1–Y3`, `E2E_CANCEL_FIX_1/2`, `E2E_CANCEL_FIX_E1`. Exclusão definitiva permanece fora do escopo (Non-goal: exclusão de registros).
