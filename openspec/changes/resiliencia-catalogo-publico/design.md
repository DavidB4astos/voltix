## Context

Ver `proposal.md` — Why. Pontos de código relevantes no estado atual:

- `_request_xano_json` (`voltix/voltix.py:747-779`) usa `urllib.request.urlopen(..., timeout=10)` e lança `HTTPError` em respostas não-2xx; `_server_side_xano_request` (`:782-795`) o executa via `asyncio.to_thread`. Não há tratamento específico de 429 nem registro de erro.
- `load_public_catalog` (`:1489-1516`) faz 1 GET de categorias, depois `_fetch_public_products` (`:1471-1487`), que faz 1 GET de produtos e `asyncio.gather` de 1 GET de imagem por produto. Toda a exceção é capturada e convertida na mensagem genérica, sem log.
- `load_public_catalog` é `on_load` de `/` (`:6365`) e `/catalogo` (`:6371`).
- Restrição externa confirmada: plano gratuito do Xano = **10 requisições / 20 s**; em 429 o Xano envia `Retry-After: 20`.
- State do Reflex é por sessão; o processo backend (granian, 1 worker em dev) importa o módulo uma vez, permitindo estruturas de cache no nível do módulo.

## Goals / Non-Goals

**Goals:**

- Eliminar a falha intermitente do catálogo causada por HTTP 429, mantendo o plano gratuito e os contratos do Xano.
- Reaproveitar dados entre Home e Catálogo por curto período e colapsar cargas simultâneas em uma só.
- Tratar 429 com `Retry-After` e tentativas limitadas; registrar falhas de forma observável e segura.
- Cobrir os cenários com testes automatizados.

**Non-Goals:**

- Alterar XanoScripts, contratos/rotas de endpoints ou dados no Xano.
- Mudar plano do Xano, interface visual, rotas, autenticação ou regras de negócio.
- Introduzir dependências novas ou cache distribuído/persistente.

## Decisions

- **Cache em memória no nível do módulo (não no State).** Estrutura compartilhada no processo backend, com chave por filtro de categoria (`""` para todas). Alternativa considerada: cache no State (por sessão) — rejeitada porque ainda reemite requisições para cada nova sessão e não colapsa chamadas entre sessões. O dado é público e somente-leitura, então compartilhar é seguro.
- **Cache cobre apenas a listagem (categorias + produtos + imagens resolvidas).** Detalhes de produto permanecem sob demanda (`load_public_product_details`), mas também se beneficiam do retry de 429. Mantém a mudança mínima e não altera o fluxo de detalhes.
- **TTL curto, constante no módulo (padrão 30 s).** Escolhido por ser maior que a janela de 20 s do Xano e suficiente para abranger navegação interativa Home↔Catálogo, mantendo frescor aceitável. Alternativa: TTL muito longo — rejeitado por risco de dados desatualizados. Constante permitirá ajuste sem alterar contratos.
- **Single-flight com `asyncio.Future` compartilhado por chave.** Enquanto uma carga está em andamento, chamadas concorrentes aguardam o mesmo `Future` (o resultado em progresso) em vez de disparar novas requisições. Alternativa: usar apenas o flag `public_catalog_loading` do State — rejeitada por ser por sessão e não cobrir chamadas concorrentes antes do flag ser marcado. Alternativa descartada: `asyncio.Lock` no nível do módulo — um `Lock` de módulo fica vinculado ao primeiro event loop que o usa e levantaria `RuntimeError` ao ser reutilizado em outro loop (o backend e a suíte de testes executam múltiplos `asyncio.run`/loops). O `Future` é criado dentro do loop em execução e removido ao final da carga.
- **Retry de 429 no `_request_xano_json` (executado em thread).** Ler `Retry-After` dos cabeçalhos do `HTTPError`, aguardar por um limite máximo, e repetir até um número fixo de tentativas (padrão 3). O sono ocorre na thread de `asyncio.to_thread`, sem bloquear o loop. Somente GETs (todos os do catálogo público são idempotentes). Ao esgotar, relançar o erro original para manter o comportamento de falha observável existente. Alternativa: retry no wrapper assíncrono — rejeitada por duplicar a captura de `HTTPError` já existente na camada síncrona.
- **Logging com `logging.getLogger` dedicado, sem dados sensíveis.** Registrar nível `warning` com o nome lógico do endpoint (mapeado a partir da constante de ambiente) e o status HTTP; nunca registrar a URL completa, query, token ou o caminho privado da imagem.
- **Preservação de UI/contratos.** Mantém-se a mensagem `public_catalog_message`, o flag `public_catalog_loading` e o botão "Tentar novamente" existentes; nenhuma forma de requisição ao Xano é alterada.
- **Testabilidade.** Tornar o TTL/limite de tentativas constantes de módulo para permitir testes de expiração/backoff via `patch`/`assertLogs`, seguindo o estilo atual (`unittest`, `AsyncMock`, patch de `_server_side_xano_request` e `urllib.request.urlopen`).

## Risks / Trade-offs

- **Dados desatualizados até o TTL** → TTL curto (30 s) e expiração explícita; aceitável para catálogo público somente-leitura.
- **Espera por `Retry-After` pode atrasar a primeira resposta** → limitar tentativas e teto de espera; o cache evita repetição nas navegações seguintes.
- **Cache por processo (não distribuído)** → em múltiplos workers cada um tem seu cache; o limite do Xano é global, mas o single-flight por worker + TTL ainda reduzem a carga. Em dev há 1 worker. Aceitável; registrado como limitação conhecida.
- **Log excessivo em falhas repetidas** → logar apenas uma vez por falha final, com endpoint lógico e status.
- **Regressão no comportamento de erro** → manter a mensagem e o fluxo atuais; coberto por testes de 429 persistente.

## Testing Strategy (evidências AP2)

Objetivo: produzir evidências verificáveis **antes e depois** da correção, registrando resultados e eventuais erros.

- **Baseline (antes da correção):** script somente-leitura que dispara rajada contra os endpoints públicos para induzir HTTP 429 (limite 10/20 s) e registra status, `Retry-After` e horários; reprodução da navegação repetida Home↔Catálogo registrando a mensagem genérica atual. Nenhuma alteração de código de produção.
- **Simulação de 429 nos testes:** no nível unitário, mockar `urllib.request.urlopen` para lançar `HTTPError` com status 429 e cabeçalho `Retry-After`; no nível funcional, rajada controlada contra o Xano para provocar 429 real.
- **Testes automatizados (após a correção):** cache (reuso e expiração), single-flight (concorrência), 429 (sucesso após retry, `Retry-After` respeitado, 429 persistente) e logging (sem dados sensíveis) — no estilo `unittest`/`AsyncMock` de `tests/test_public_catalog.py`.
- **Testes funcionais:** navegação repetida Home↔Catálogo no app em execução confirmando ausência de 429 e reuso do cache (via log); verificação do tratamento de 429 real e simulado.
- **Registro de evidências:** documentar os casos (passo, resultado esperado, resultado observado, status, evidência/log) em `docs/ap2/07-evidencias-catalogo-429.md`, incluindo os erros encontrados e como foram resolvidos.
- **Ferramentas:** `python -m unittest discover -s tests`; `reflex compile --dry`; servidor dev para verificação visual.

## Migration Plan

- Sem migração de dados. Aplicar com reinício do backend (o cache é em memória e se aquece na primeira carga).
- Rollback: reverter o commit da mudança; nenhum estado persistente é criado.
