## 1. Baseline e evidências pré-correção (AP2)

- [x] 1.1 Executar um script somente-leitura de rajada contra os endpoints públicos para induzir HTTP 429 e registrar evidências (status, `Retry-After`, contagem e horários), sem alterar código de produção.
- [x] 1.2 Reproduzir a navegação repetida Home↔Catálogo no app em execução e registrar a mensagem genérica atual e os erros observados.
- [x] 1.3 Criar o documento de evidências `docs/ap2/07-evidencias-catalogo-429.md` com os casos de teste, resultado esperado, resultado observado e evidência/log do baseline.

## 2. Cache de curto TTL

- [x] 2.1 Adicionar em `voltix/voltix.py` constantes de módulo para TTL (padrão 30 s) e número máximo de tentativas (padrão 3); verificar que o módulo importa sem erro (`python -c "import voltix.voltix"`).
- [x] 2.2 Implementar estrutura de cache em memória no nível do módulo, com chave por filtro de categoria e registro de data/hora de validade, reutilizando os objetos já parseados (categorias e produtos com `image_url`); verificar com teste unitário de leitura dentro do TTL.
- [x] 2.3 Integrar leitura/escrita do cache em `load_public_catalog`/`_fetch_public_products`, sem alterar o formato das requisições ao Xano; verificar que os testes atuais de `tests/test_public_catalog.py` continuam passando.
- [x] 2.4 Garantir que a reutilização respeita a categoria selecionada (chave por `category_id`); verificar com teste de seleção de categoria diferente.

## 3. Prevenção de carregamentos simultâneos duplicados

- [x] 3.1 Adicionar mecanismo single-flight baseado em `asyncio.Future` por chave (no lugar de um `asyncio.Lock` de módulo, que ficaria vinculado a um único event loop), de modo que chamadas concorrentes reutilizem a carga em andamento; verificar com teste que N cargas concorrentes geram um único conjunto de requisições.

## 4. Tratamento de HTTP 429

- [x] 4.1 Implementar retry limitado em `_request_xano_json`, reconhecendo HTTP 429, lendo `Retry-After` (com teto máximo) e aguardando antes de repetir; verificar com testes de 429→sucesso e de `Retry-After` respeitado.
- [x] 4.2 Garantir que, esgotadas as tentativas, o erro original é propagado e o comportamento existente (mensagem de falha e "Tentar novamente") é preservado; verificar com teste de 429 persistente.

## 5. Registro de erros sem dados sensíveis

- [x] 5.1 Adicionar logger dedicado e registrar falhas finais do catálogo público com o endpoint lógico e o status HTTP, sem URL completa, query, token ou caminho privado; verificar com teste usando `assertLogs`.

## 6. Testes automatizados (estilo `unittest`/`AsyncMock` atual)

- [x] 6.1 Testar navegação repetida Home↔Catálogo dentro do TTL sem novas requisições ao Xano.
- [x] 6.2 Testar expiração do TTL disparando nova consulta ao Xano.
- [x] 6.3 Testar cargas simultâneas gerando um único conjunto de requisições.
- [x] 6.4 Testar HTTP 429 com `Retry-After` (sucesso após retry) e 429 persistente (falha observável).
- [x] 6.5 Testar que o log de falha não contém credenciais, token, URL completa nem caminho privado de imagem.
- [x] 6.6 Executar a suíte completa (`python -m unittest discover -s tests`) e confirmar que todos os testes passam.

## 7. Testes funcionais e evidências pós-correção (AP2)

- [x] 7.1 Verificar no app em execução a navegação repetida Home↔Catálogo, confirmando ausência de 429 e reuso do cache (evidenciado no log do backend).
- [x] 7.2 Verificar o comportamento sob HTTP 429 simulado (mock) e real (rajada controlada), registrando o retry e o respeito ao `Retry-After`.
- [x] 7.3 Atualizar `docs/ap2/07-evidencias-catalogo-429.md` com os resultados pós-correção, eventuais erros encontrados e como foram resolvidos.

## 8. Verificação final

- [x] 8.1 Executar `reflex compile --dry` e confirmar que compila sem erros.
- [x] 8.2 Executar `openspec validate resiliencia-catalogo-publico --strict` e confirmar que a mudança é válida.
- [x] 8.3 Verificação visual manual: navegar repetidamente entre Home e Catálogo e confirmar que "Não foi possível carregar o catálogo" não reaparece. Confirmado pelo usuário em 14/10/2026 (verificação visual realizada pelo próprio usuário; esta sessão não executou testes visuais adicionais).

## 9. Entrega (somente após aprovação e verificação visual)

- [x] 9.1 Fazer commit das alterações de código, testes e documento de evidências com mensagem descritiva.
- [x] 9.2 Fazer push para o remoto `main`.
- [x] 9.3 Arquivar a change `resiliencia-catalogo-publico` e sincronizar as specs consolidadas.
