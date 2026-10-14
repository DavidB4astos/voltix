# 04 — Matriz de Priorização MoSCoW

> Documento da AP2 — Voltix. Entrega: 21/10/2026.
> Fontes: itens de `03-product-backlog.md`; evidências em `openspec/specs/`, `openspec/changes/` e `docs/`.
> **Nota metodológica:** a priorização foi produzida pela própria equipe com base no estado documentado do projeto. Não houve priorização formal com stakeholders externos (ver `01-elicitacao-requisitos.md` §4). Nenhuma métrica de valor/retorno é inventada.

## 1. Critérios de avaliação

Como não há dados de negócio quantitativos (receita, número de usuários), os eixos são avaliados de forma **qualitativa e ancorada em evidências do repositório**.

### 1.1 Valor de negócio
Contribuição para a proposta central da Voltix (e-commerce de tecnologia com CRM integrado) e dependência entre capacidades.

- **Alto** — indispensável ao fluxo comercial ou à proposta central.
- **Médio** — melhora a experiência/proposta, mas não bloqueia o fluxo principal.
- **Baixo** — desejável, sem impacto direto no fluxo principal.

### 1.2 Esforço
Ancorado em evidência observável: número de requisitos consolidados, número de tarefas na change e existência de persistência nova.

- **Baixo** — ≤ 4 requisitos e/ou change pequena.
- **Médio** — 5–12 tarefas/requisitos.
- **Alto** — > 12 tarefas, ou persistência/integração substancial.

### 1.3 Risco
Incerteza técnica ou de requisitos.

- **Baixo** — comportamento já especificado e verificado (spec consolidada).
- **Médio** — change ativa em andamento, escopo claro.
- **Alto** — ausência de spec, dados legados ou dependência não resolvida.

## 2. Matriz de priorização por épico

| Épico | Valor | Esforço | Risco | MoSCoW | Justificativa (evidência) |
|-------|-------|---------|-------|--------|---------------------------|
| EP-12 Integração Reflex↔Xano | Alto | Baixo | Baixo | **Must** | Habilitador técnico de toda a plataforma; 4 requisitos; spec consolidada. (`reflex-xano-integration/spec.md`) |
| EP-04 Acesso interno | Alto | Médio | Baixo | **Must** | Porta de entrada da operação e base de autorização; 5 requisitos; spec consolidada. (`internal-access/spec.md`) |
| EP-05 Gestão de catálogo | Alto | Médio | Baixo | **Must** | Sem categorias/marcas não há produto; 5 requisitos; spec consolidada. (`catalog-management/spec.md`) |
| EP-06 Gestão de produtos | Alto | Alto | Médio | **Must** | Núcleo do catálogo; change `gestao-produtos` (15 tarefas → > 12). (`product-management`) |
| EP-01 Catálogo público | Alto | Médio | Médio | **Must** | Vitrine de vendas; 5 requisitos; risco da imagem assinada; spec consolidada + `conectar-catalogo-publico-xano`. (`public-catalog/spec.md`) |
| EP-07 Acesso/Endereços Cliente | Alto | Médio | Alto | **Must** | Pré-requisito de carrinho/pedidos; risco por tabela legada `CLIENTE`; change `cadastro-cliente-enderecos` (12 tarefas). |
| EP-08 Carrinho | Alto | Médio | Médio | **Must** | Etapa central da compra; 5 requisitos; spec consolidada. (`shopping-cart/spec.md`) |
| EP-09 Checkout/Pedidos | Alto | Médio | Alto | **Must** | Concretiza a venda; atomicidade Pedido+itens+Pagamento; change `checkout-pedidos` (9 tarefas). |
| EP-10 Pagamento simulado | Alto | Baixo | Baixo | **Must** | Fecha o fluxo de compra no escopo acadêmico; 4 requisitos; spec consolidada. (`order-payment/spec.md`) |
| EP-02 Home pública | Médio | Médio | Baixo | **Should** | Fortalece a vitrine/identidade, mas o fluxo de compra não depende dela; spec consolidada. (`public-home/spec.md`) |
| EP-03 Interface visual | Médio | Médio | Baixo | **Should** | Qualidade percebida e responsividade; 7 requisitos; não bloqueia funcionalidades; spec consolidada. (`visual-interface/spec.md`) |
| EP-11 CRM / Atendimento | Alto | Não estimado | Alto | **Should** | Diferencial da proposta, porém **sem spec** e com fluxo não definido — risco de requisitos. Sem spec, não há contagem para ancorar o esforço. (`project-overview.md` §6.3; `domain-model.md` §6.1) |

## 3. Itens explicitamente fora do escopo atual (Won't — este ciclo)

Fonte: `docs/project-overview.md` §5.2 e `docs/domain-model.md` §9.

- Marketplace com vendedores externos.
- Integração fiscal real.
- Integração real com transportadoras / rastreamento logístico.
- Recomendação com IA e chatbot automatizado.
- Aplicativo móvel nativo.
- Estoque como entidade independente e `MovimentacaoEstoque`.
- Galeria de imagens, avaliações, lista de desejos, cupons e descontos avançados.
- Histórico individual de tentativas de pagamento / `InteracaoAtendimento`.

## 4. Legenda de classificação MoSCoW

- **Must** — obrigatório para o funcionamento do fluxo comercial da entrega.
- **Should** — importante, mas contornável nesta entrega.
- **Could** — desejável, sem impacto no fluxo principal.
- **Won't (este ciclo)** — deliberadamente fora do escopo atual.

**Observação sobre "Could":** nesta entrega nenhum épico foi classificado como **Could** — os itens desejáveis sem impacto no fluxo principal estão cobertos por **Should** (EP-02, EP-03) ou correspondem a decisões de escopo já registradas como **Won't**. A categoria é mantida para uso futuro.

**Observação sobre "Won't":** os itens de §3 provêm de `docs/project-overview.md` §5.2 e `docs/domain-model.md` §9 (decisões de escopo documentadas) e **não** são itens do Product Backlog (`03-product-backlog.md`); portanto não são itens de backlog "rejeitados".

## 5. Observações

- Os épicos **Must** correspondem às capabilities já consolidadas ou em changes ativas com escopo definido.
- EP-11 (CRM) é o único épico de valor alto classificado como **Should** por ausência de especificação — recomenda-se tratá-lo como a principal lacuna a especificar.
- EP-06, EP-07 e EP-09 estão simultaneamente em **Must** e "Em andamento", o que concentra o maior esforço/risco da entrega.
- O esforço foi aplicado literalmente pela regra de §1.2 (nº de requisitos consolidados ou tarefas da change); itens sem contagem de evidência (EP-11) ficam como **não estimado**. A prioridade MoSCoW (Must/Should/Could) deriva de valor e risco, não de esforço.
