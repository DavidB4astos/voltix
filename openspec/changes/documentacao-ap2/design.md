## Context

Ver `proposal.md` — Why. Restrições que moldam a abordagem:

- Fonte de verdade já existente: `docs/project-overview.md` (visão, escopo, funcionalidades, restrições), `docs/domain-model.md` (13 conceitos e regras) e `openspec/specs/` (8 specs, 43 requisitos, com cenários WHEN/THEN).
- Regra do projeto (AGENTS.md): reutilizar conteúdo, evitar duplicação, não inventar dados/evidências, não alterar código funcional nesta etapa.
- Ferramental disponível: apenas arquivos Markdown em `docs/` e `openspec/`; sem novas dependências.
- Defeito conhecido: `openspec/specs/internal-access/spec.md` contém mojibake (`Ã`) em vários trechos.

## Goals / Non-Goals

**Goals:**

- Produzir 6 documentos da AP2 coerentes entre si e rastreáveis à documentação existente.
- Derivar user stories, backlog, MoSCoW, Vision Board e SRS do conteúdo já validado, sem criar requisitos novos.
- Documentar elicitação apenas com evidências reais observáveis no repositório.
- Corrigir o encoding de `internal-access/spec.md` preservando bytes de conteúdo semântico.

**Non-Goals:**

- Não alterar regras de negócio, specs de comportamento, código, testes, Xano ou `.env`.
- Não criar entrevistas, questionários, personas fictícias ou resultados inventados.
- Não construir ferramentas, diagramas executáveis ou automações.

## Decisions

### D1. Localização dos documentos: `docs/ap2/` com prefixo numérico

Agrupar os 6 documentos em `docs/ap2/` (`01-elicitacao-requisitos.md` … `06-srs.md`), numerados na ordem dos entregáveis da AP2.

- Por quê: mantém a documentação entregável coesa, separada de `docs/` (visão/domínio) e de `openspec/` (comportamento), e dá ordem de leitura.
- Alternativas: arquivos soltos em `docs/` (mistura com documentos-fonte) ou dentro de `openspec/changes/` (mistura planejamento com entrega acadêmica). Descartadas.

### D2. Rastreabilidade a partir das specs, sem duplicar requisitos

Cada documento referencia as specs/arquivos de origem por caminho, em vez de recopiar integralmente o texto.

- User stories: derivadas de `docs/project-overview.md` §4/§6 e das capabilities em `openspec/specs/`.
- Critérios de aceitação: reaproveitados/adaptados dos `#### Scenario:` existentes, apontando a spec de origem.
- SRS (RF): consolidado das specs, com referência a cada capability.
- Por quê: evita divergência e retrabalho; respeita AGENTS.md §3.

### D3. User stories no formato padrão com ID e vínculo

Formato: `US-xx: Como <papel>, quero <ação>, para <benefício>`, seguido de critérios de aceitação em Gherkin (Dado/Quando/Então) e referência à spec/arquivo de origem. Papéis restritos a Cliente, Funcionário, Administrador (conforme `docs/project-overview.md` §4).

### D4. Backlog consolidado derivado das specs + changes

Estrutura: épicos por capability, itens com status real (implementado = spec consolidada; em andamento = changes com tarefas pendentes; pendente = capacidades ainda não especificadas, ex. CRM/atendimentos e cancelamento de pedido). Status reflete o estado do repositório, não estimativas inventadas.

### D5. MoSCoW com valor, esforço e risco

Classificar cada item do backlog em Must/Should/Could/Won't, justificando com três eixos (valor de negócio, esforço, risco) e ancorando "esforço" no tamanho observável (nº de specs/tarefas já existentes), não em horas inventadas.

### D6. Product Vision Board (5 elementos de Roman Pichler)

Seções: Visão, Grupo-alvo, Necessidades, Produto, Objetivos de negócio — preenchidas a partir de `docs/project-overview.md` §1–4, §6 e metas de escopo. Sem métricas de negócio inexistentes: onde não houver dado, registrar como "a definir" em vez de inventar números.

### D7. SRS consolidado com RF, RNF e casos de uso

- RF: consolidados por capability, referenciando specs.
- RNF: reunir os já implícitos (segurança/autorização backend, observabilidade de falhas, responsividade/acessibilidade, configuração por ambiente, consistência de dados) em `project-overview.md` §7/§10, `internal-access`, `visual-interface`, `reflex-xano-integration`, `public-catalog`; marcar explicitamente o que está ausente (desempenho, disponibilidade, escalabilidade, portabilidade, manutenibilidade, interoperabilidade, localização) como lacuna/"a definir".
- Casos de uso: derivar atores/fluxo principal/fluxos alternativos dos cenários existentes, sem introduzir comportamento novo.

### D8. Elicitação somente com evidências reais

Documentar as técnicas efetivamente observáveis: análise de documentação de referência, análise do Domain Model, modelagem orientada a especificações (OpenSpec), e validação incremental por changes/cenários. Cada técnica aponta artefatos concretos do repositório como evidência. Técnicas não aplicadas (entrevistas, questionários, observação) são listadas como não utilizadas, sem resultados fabricados.

### D9. Correção de encoding preservando conteúdo

Reescrever `openspec/specs/internal-access/spec.md` em UTF-8, corrigindo os caracteres corrompidos (`Ã`/`Â` etc.) para os acentos corretos em português, mantendo textos, requisitos, IDs de cenário e estrutura intactos.

### D10. Reconciliação das classificações de esforço do MoSCoW (C3)

Aplicar a **regra já declarada** em `04-priorizacao-moscow.md` §1.2 (Baixo ≤ 4; Médio 5–12; Alto > 12, contando requisitos consolidados **ou** tarefas da change), sem alterar as faixas e sem horas inventadas. Ajustar as classificações que contradizem a própria regra: EP-03 (7 requisitos) → **Médio**; EP-07 (12 tarefas) → **Médio**; EP-09 (9 tarefas) → **Médio**; EP-11 (sem spec, sem contagem) → **"não estimado (sem âncora)"**. A prioridade MoSCoW (Must/Should) permanece inalterada, pois deriva de valor/risco, não de esforço.

- Descartada a alternativa de redefinir as faixas de esforço: seria arbitrária e poderia mascarar a inconsistência em vez de corrigi-la.

### D11. Capa/índice e Referências (C1)

Criar `docs/ap2/README.md` como capa e índice da entrega, com duas partes: (a) campos de **identificação acadêmica a preencher** (instituição, curso, disciplina, professor(a), integrantes, turma, data de entrega, versão) — sem inventar nomes, matrículas ou quaisquer dados pessoais/acadêmicos; (b) **Referências** — lista dos arquivos-fonte internos citados (docs, specs e changes), sem bibliografia externa fabricada. O README também liga os seis documentos numerados.

### D12. Casos de uso formalizados (I4)

Reescrever a seção `06-srs.md` §4 com template explícito por caso de uso: **ID**, **atores**, **pré-condições**, **fluxo principal com passos numerados**, **fluxos alternativos/exceções numerados**, **pós-condições** e **referência à spec de origem**. O conteúdo deriva apenas dos cenários existentes; nenhum passo novo de comportamento é introduzido.

### D13. Elicitação documental justificada e lacunas explícitas (C2/I3/I6)

Em `01-elicitacao-requisitos.md`, adicionar a justificativa metodológica formal de por que a elicitação documental/spec-driven é a técnica adequada ao contexto (projeto acadêmico, sem acesso a stakeholders, com fontes canônicas no repositório) e registrar explicitamente a ausência de entrevistas e de validação com usuários. Tratar como **lacuna/"a definir"** — sem inventar dados — tudo que não possui evidência real: US-F2/CRM (funcionalidade pendente, não user story com critérios), métricas de negócio e RNF quantitativos.

## Risks / Trade-offs

- [Derivar user stories/casos de uso pode introduzir comportamento não especificado] → Manter cada item rastreável a um `#### Scenario:`/requisito existente; sinalizar lacunas em vez de inventar.
- [Backlog/MoSCoW parecerem arbitrários] → Ancorar valor/esforço/risco em evidências (specs existentes, nº de tarefas, status real) e registrar a justificativa.
- [Correção de encoding alterar conteúdo por engano] → Revisar requisito por requisito antes/depois; validar com `openspec validate` e leitura integral.
- [Divergência entre docs AP2 e specs] → Referenciar specs por caminho e não recopiar regras; conferência final de consistência.

## Migration Plan

Não aplicável — mudança apenas documental, sem deploy nem rollback de runtime. Rollback = reverter os arquivos adicionados/editados via Git, se necessário.
