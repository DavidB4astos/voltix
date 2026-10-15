# Tasks

> Esta Change é apenas documental (`.openspec.yaml` com `skip_specs: true`). Nenhuma tarefa altera código funcional, testes, Xano, rotas, State ou `.env`.

## 1. Preparação e inventário das fontes

- [x] 1.1 Inventariar as fontes reutilizáveis (`docs/project-overview.md`, `docs/domain-model.md`, as 8 specs de `openspec/specs/` e as changes ativas/arquivadas) e registrar seus caminhos; verificação: cada documento AP2 abre citando suas fontes e todas resolvem para arquivos existentes.
- [x] 1.2 Confirmar que a Change declara `skip_specs: true` e não introduz requisito de comportamento; verificação: `openspec validate documentacao-ap2` sem erros e `.openspec.yaml` com `skip_specs: true`.

## 2. Documento de elicitação de requisitos (`docs/ap2/01-elicitacao-requisitos.md`)

- [x] 2.1 Descrever apenas as técnicas efetivamente observáveis no projeto (análise da documentação de referência, análise do Domain Model, especificação orientada por OpenSpec, validação incremental por changes e cenários), cada uma com evidência por caminho; listar explicitamente as técnicas NÃO utilizadas (entrevistas, questionários, observação, prototipação com usuários); verificação: toda técnica aponta artefato real e nenhuma entrevista/questionário/resultado é inventado.

## 3. User stories e critérios de aceitação (`docs/ap2/02-user-stories.md`)

- [x] 3.1 Escrever user stories do Cliente (cadastro, autenticação, catálogo/pesquisa, produto/variação, carrinho, checkout/pedido, histórico) referenciando `docs/project-overview.md` §4/§6 e as specs correspondentes; verificação: cada US tem ID, papel (Cliente), ação e benefício e aponta a origem.
- [x] 3.2 Escrever user stories internas (Administrador para catálogo/marcas/produtos/pedidos; Funcionário para CRM/atendimento) referenciando as specs; verificação: cada US aponta a capability/spec de origem.
- [x] 3.3 Anexar a cada US critérios de aceitação em Dado/Quando/Então derivados dos `#### Scenario:` das specs, com referência à spec de origem; verificação: nenhum critério descreve comportamento ausente das specs (sem invenção).

## 4. Product Backlog consolidado (`docs/ap2/03-product-backlog.md`)

- [x] 4.1 Consolidar o backlog em épicos por capability (catálogo, carrinho, pedidos/pagamento, acesso interno, área interna/cliente, catálogo público, home pública, interface visual, CRM/atendimento) com itens e status real; verificação: o status de cada épico confere com `openspec list --specs` e `openspec list`.
- [x] 4.2 Marcar separadamente o que está implementado (spec consolidada), em andamento (change com tarefas pendentes) e pendente (sem spec, ex. CRM/atendimento e cancelamento de pedido); verificação: nenhum status contradiz o repositório.

## 5. Matriz de priorização MoSCoW (`docs/ap2/04-priorizacao-moscow.md`)

- [x] 5.1 Definir critérios objetivos de valor de negócio, esforço (ancorado em nº de specs/tarefas existentes) e risco; verificação: critérios descritos antes da matriz.
- [x] 5.2 Classificar cada item do backlog em Must/Should/Could/Won't com justificativa nos três eixos; verificação: todo item do backlog aparece classificado exatamente uma vez, com justificativa rastreável.

## 6. Product Vision Board (`docs/ap2/05-product-vision-board.md`)

- [x] 6.1 Preencher os cinco elementos (Visão, Grupo-alvo, Necessidades, Produto, Objetivos de negócio) a partir de `docs/project-overview.md` §1–4/§6; onde não houver dado, registrar "a definir" em vez de inventar métricas; verificação: cinco seções presentes e nenhum número/meta sem fonte.

## 7. SRS consolidado (`docs/ap2/06-srs.md`)

- [x] 7.1 Consolidar os requisitos funcionais por capability, referenciando cada spec; verificação: todo RF rastreia a uma spec existente e nenhum comportamento novo é descrito.
- [x] 7.2 Consolidar os requisitos não funcionais já implícitos (segurança/autorização backend, observabilidade de falhas, responsividade/acessibilidade, configuração por ambiente, consistência de dados) e registrar como lacuna/"a definir" os ausentes (desempenho, disponibilidade, escalabilidade, portabilidade, manutenibilidade, interoperabilidade, localização); verificação: cada RNF aponta a seção/spec que o sustenta.
- [x] 7.3 Escrever os casos de uso (ator, pré-condições, fluxo principal, fluxos alternativos/exceções) derivados dos cenários das specs; verificação: cada caso de uso aponta a spec de origem.

## 8. Correção de encoding de `openspec/specs/internal-access/spec.md`

- [x] 8.1 Converter o arquivo para UTF-8 corrigindo o mojibake (`Ã`/`Â` etc.) para os acentos corretos, preservando integralmente requisitos, textos e IDs de cenário; verificação: leitura integral confirma conteúdo idêntico ao original (sem perda/adição de requisito).
- [x] 8.2 Revalidar a spec; verificação: `openspec validate internal-access --type spec` (ou equivalente) sem erros.

## 9. Consistência e verificação final

- [x] 9.1 Conferir coerência e ausência de duplicação/contradição entre os 6 documentos e as fontes; verificação: revisão cruzada de termos, status e classificações.
- [x] 9.2 Validar a Change; verificação: `openspec validate documentacao-ap2 --strict` sem erros.
- [x] 9.3 Confirmar ausência de impacto em código; verificação: `git status` mostra apenas arquivos de `docs/ap2/` e `openspec/specs/internal-access/spec.md` (sem `voltix/`, `tests/`, `xano/`, `.env`).

## 10. Correções da revisão acadêmica

> Correções apontadas no relatório de revisão dos seis documentos. Continuam estritamente documentais: nenhum requisito, comportamento ou dado real é inventado; lacunas permanecem explícitas. Decisões em `design.md` D10–D13.

- [x] 10.1 (C1/M5/M7) Criar `docs/ap2/README.md` como capa/índice, com campos de identificação acadêmica **a preencher** (instituição, curso, disciplina, professor(a), integrantes, turma, data de entrega, versão) e seção **Referências** com os arquivos-fonte internos citados; verificação: nenhum dado pessoal/acadêmico ou referência externa inventada e os seis documentos estão ligados.
- [x] 10.2 (C2) Em `01-elicitacao-requisitos.md`, adicionar a justificativa metodológica formal da elicitação documental/spec-driven e explicitar a ausência de entrevistas e de validação com usuários; verificação: a justificativa cita apenas fontes reais e a lacuna continua registrada.
- [x] 10.3 (C3) Em `04-priorizacao-moscow.md`, reconciliar esforço e classificações com a regra declarada (§1.2): EP-03, EP-07 e EP-09 → **Médio**; EP-11 → **não estimado (sem âncora)**; verificação: nenhuma classificação contradiz a regra e a prioridade MoSCoW permanece inalterada.
- [x] 10.4 (I1) Em `03-product-backlog.md`, corrigir a origem de EP-01: `conectar-catalogo-publico-xano` é change **ativa/concluída**, não arquivada; verificação: coerente com `openspec list`.
- [x] 10.5 (I2) Em `01-elicitacao-requisitos.md` e `03-product-backlog.md`, atualizar a contagem para **5** changes ativas (incluindo `documentacao-ap2`) ou explicitar "4 changes funcionais ativas"; verificação: contagem confere com `openspec list`.
- [x] 10.6 (I3) Em `02-user-stories.md`, reclassificar **US-F2** como funcionalidade **pendente**, fora do formato de user story com critérios, sem inventar critérios de aceitação; verificação: a pendência permanece explícita e rastreável.
- [x] 10.7 (I4) Em `06-srs.md` §4, formalizar os casos de uso (ID, atores, pré-condições, fluxo principal numerado, alternativos numerados, pós-condições, referência); verificação: cada passo deriva de cenário existente, sem comportamento novo.
- [x] 10.8 (I5) Em `06-srs.md`, registrar a nota de escopo de que os RF são enunciados resumidos que referenciam as specs consolidadas (decisão de não duplicar); verificação: a nota está visível antes da lista de RF.
- [x] 10.9 (I6) Em `06-srs.md`, manter os RNF sem métrica como lacunas explícitas ("a definir"), sem inventar metas; verificação: nenhuma métrica numérica de RNF sem fonte.
- [x] 10.10 (I7) Em `06-srs.md`, ajustar **RF-ORD-05** para registrar a baixa de estoque como **decisão pendente**, referenciando `docs/domain-model.md` §5.3, evitando contradição; verificação: o RF não afirma regra conflitante com o Domain Model.
- [x] 10.11 (I8) Em `02-user-stories.md`, substituir o nome da capability pelo **caminho completo do delta spec** nas user stories "Em andamento"; verificação: os caminhos resolvem para arquivos existentes.
- [x] 10.12 (M1) Em `02-user-stories.md` e `06-srs.md`, justificar **Visitante** como público do catálogo público e tratar **US-T1** como habilitador técnico (não persona); verificação: atores coerentes com `docs/project-overview.md` §4 ou com justificativa registrada.
- [x] 10.13 (M2) Corrigir forma/typos: "comparecer" em `05-product-vision-board.md`; "autenticação/ autorização" em `06-srs.md`; critérios de user story sem "Quando" em `02-user-stories.md`; verificação: busca de termos confirma as correções.
- [x] 10.14 (M3) Em `04-priorizacao-moscow.md`, justificar a categoria **Could** (ou registrar sua ausência) e explicitar que os itens "Won't" vêm de `project-overview.md` §5.2 / `domain-model.md` §9, não do backlog; verificação: nota presente na seção correspondente.
- [x] 10.15 (M4) Em `03-product-backlog.md`, registrar referência cruzada ao ordenamento por prioridade do `04-priorizacao-moscow.md`; verificação: cabeçalho/convenções citam a ordenação.
- [x] 10.16 (M6) Em `01-elicitacao-requisitos.md`, alinhar o inventário de fontes: ancorar `tests/` e `xano/table/` na técnica T6 ou removê-los do inventário; verificação: toda fonte listada é usada por alguma técnica ou tem papel explicitado.
- [x] 10.17 (M8) Em `01-elicitacao-requisitos.md`, descrever textualmente o que cada referência visual orientou, sem depender da leitura da imagem; verificação: a técnica T5 tem descrição textual própria.
- [x] 10.18 Revalidar e conferir impacto; verificação: `openspec validate documentacao-ap2 --strict` sem erros e `git status` restrito a `docs/ap2/`, `openspec/specs/internal-access/spec.md` e aos artefatos da change (sem `voltix/`, `tests/`, `xano/`, `.env`).
