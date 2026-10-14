# AP2 — Documentação de Engenharia de Requisitos — Voltix

> Capa e índice da entrega da AP2. Documento de apoio aos seis artefatos numerados deste diretório.
> **Entrega:** 21/10/2026.

## Identificação acadêmica

> Os campos abaixo devem ser **preenchidos pela equipe**. Nenhum dado pessoal ou acadêmico foi criado automaticamente; os campos entre `< >` estão em branco de propósito.

| Campo | Valor |
|-------|-------|
| Instituição | `<a preencher>` |
| Curso | `<a preencher>` |
| Disciplina | `<a preencher>` |
| Professor(a) | `<a preencher>` |
| Turma | `<a preencher>` |
| Integrantes (nome e matrícula) | `<a preencher>` |
| Data de entrega | 21/10/2026 |
| Versão do documento | `<a preencher>` (ex.: 1.0) |

## Índice dos artefatos

| # | Documento | Conteúdo |
|---|-----------|----------|
| 01 | [01-elicitacao-requisitos.md](01-elicitacao-requisitos.md) | Técnicas de elicitação efetivamente utilizadas, com evidências reais, e técnicas não aplicadas. |
| 02 | [02-user-stories.md](02-user-stories.md) | User stories com critérios de aceitação (Dado/Quando/Então) e rastreabilidade às specs. |
| 03 | [03-product-backlog.md](03-product-backlog.md) | Product Backlog consolidado (épicos e itens) com status real do repositório. |
| 04 | [04-priorizacao-moscow.md](04-priorizacao-moscow.md) | Matriz de priorização MoSCoW (valor, esforço e risco) e itens fora de escopo. |
| 05 | [05-product-vision-board.md](05-product-vision-board.md) | Product Vision Board (Visão, Grupo-alvo, Necessidades, Produto, Objetivos). |
| 06 | [06-srs.md](06-srs.md) | SRS com requisitos funcionais, requisitos não funcionais e casos de uso. |

## Nota metodológica

Esta entrega é **documental**: consolida e referencia a documentação já existente do Voltix (`docs/` e `openspec/`) sem alterar código, comportamento ou regras de negócio. Onde não há dado real disponível, o campo é marcado como **"a definir"** ou **"pendente"** — nenhuma métrica, requisito, entrevista ou dado pessoal foi inventado.

- Elicitação: apenas técnicas observáveis no repositório; entrevistas e validação com usuários **não** foram realizadas (ver `01-elicitacao-requisitos.md` §4 e §7).
- Priorização: produzida pela própria equipe, sem priorização formal com stakeholders externos (ver `04-priorizacao-moscow.md`).

## Referências (fontes internas do projeto)

Arquivos do próprio repositório usados como fonte desta documentação. Não há bibliografia externa.

- Governança e processo: `AGENTS.md`; `openspec/config.yaml`.
- Visão e escopo: `docs/project-overview.md`.
- Domínio: `docs/domain-model.md`.
- Comportamento especificado: `openspec/specs/*/spec.md` (8 capabilities, 43 requisitos).
- Mudanças incrementais: `openspec/changes/` (changes ativas e arquivadas).
- Contratos e persistência: `xano/api/`, `xano/table/`.
- Configuração por ambiente: `.env.example`.
- Verificação automatizada: `tests/`.
- Referências visuais: `docs/referencias/`.
