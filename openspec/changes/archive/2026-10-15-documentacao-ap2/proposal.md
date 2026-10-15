## Why

A entrega da AP2 (21/10/2026) exige um conjunto documental de engenharia de requisitos (elicitação, user stories, backlog, priorização, visão de produto e SRS) que o projeto ainda não possui de forma consolidada. O Voltix já tem base forte e reaproveitável — `docs/project-overview.md`, `docs/domain-model.md` e as 8 specs consolidadas em `openspec/specs/` — mas faltam os artefatos formais da AP2 e há um defeito de encoding em `openspec/specs/internal-access/spec.md` que prejudica a leitura/entrega.

## What Changes

- Criar o conjunto de documentos da AP2 em `docs/ap2/`, reaproveitando o conteúdo já existente e evitando duplicação:
  - `01-elicitacao-requisitos.md`: técnicas de elicitação efetivamente utilizadas e suas evidências reais no repositório (sem inventar entrevistas, questionários ou resultados).
  - `02-user-stories.md`: user stories no formato "Como <papel>, quero <ação>, para <benefício>", com critérios de aceitação derivados do comportamento já especificado.
  - `03-product-backlog.md`: Product Backlog consolidado a partir das specs e changes do OpenSpec, com status real.
  - `04-priorizacao-moscow.md`: matriz de priorização MoSCoW considerando valor de negócio, esforço e risco.
  - `05-product-vision-board.md`: Product Vision Board com os cinco elementos (Visão, Grupo-alvo, Necessidades, Produto, Objetivos de negócio).
  - `06-srs.md`: SRS consolidado com requisitos funcionais, requisitos não funcionais e casos de uso.
  - `README.md`: capa/índice da entrega com campos de identificação acadêmica **a preencher** (sem dados pessoais ou acadêmicos inventados) e a lista de referências internas citadas.
- Aplicar as correções apontadas na revisão acadêmica dos seis documentos: identificação da entrega, justificativa formal da elicitação documental, reconciliação das classificações de esforço do MoSCoW com os critérios declarados, correção de informações sobre changes ativas/arquivadas e contagem, tratamento de US-F2 como funcionalidade pendente, formalização dos casos de uso (pré-condições, fluxo numerado, alternativas e pós-condições), e ajustes de rastreabilidade, formatação e consistência. Nenhum requisito, comportamento ou dado real é inventado.
- Corrigir o encoding (mojibake `Ã`) de `openspec/specs/internal-access/spec.md` para UTF-8, preservando integralmente o conteúdo e os requisitos existentes.
- Não alterar código funcional, backend/Xano, rotas, State do Reflex, testes, dependências, `.env` ou regras de negócio.

Fica fora do escopo: implementar funcionalidades, alterar specs de comportamento, criar novos requisitos, alterar o Domain Model, criar dados fictícios, ou realizar commit/push/archive.

## Capabilities

### New Capabilities

Nenhuma. Esta mudança é exclusivamente de documentação (docs/tooling) e não altera o comportamento do sistema descrito pelas specs.

### Modified Capabilities

Nenhuma. A correção de encoding em `openspec/specs/internal-access/spec.md` é preservação de conteúdo, sem alteração de requisito comportamental. Por isso, a Change declara `skip_specs: true` em `.openspec.yaml`.

## Impact

- Novos arquivos em `docs/ap2/` (6 documentos numerados + `README.md` de capa/índice).
- `openspec/specs/internal-access/spec.md`: correção de encoding, sem mudança de conteúdo/recomportamento.
- Sem impacto em `voltix/voltix.py`, `tests/`, `xano/`, `rxconfig.py`, `.env` ou dependências.
- Verificação: leitura integral dos documentos, checagem de que cada afirmação tem evidência em `docs/`/`openspec/`, e `openspec validate documentacao-ap2`.
