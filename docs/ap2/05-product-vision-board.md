# 05 — Product Vision Board

> Documento da AP2 — Voltix. Entrega: 21/10/2026.
> Estrutura: Product Vision Board de Roman Pichler, com os cinco elementos — **Visão**, **Grupo-alvo**, **Necessidades**, **Produto** e **Objetivos de negócio**.
> Fontes: `docs/project-overview.md` §1–§4 e §6; `docs/domain-model.md`. Onde não há dado documentado, o campo é marcado como **a definir** (nenhuma métrica é inventada).

---

## Visão

> **Integrar, em uma única plataforma, o e-commerce de produtos de tecnologia e o relacionamento com os clientes, centralizando informações de vendas, clientes e atendimentos.**

*Evidência:* `docs/project-overview.md` §1 ("A proposta da Voltix é integrar a operação de vendas e o relacionamento com os clientes em uma única plataforma") e §3 (objetivo geral).

---

## Grupo-alvo

| Segmento | Descrição | Evidência |
|----------|-----------|-----------|
| **Cliente** | Consumidor que pesquisa e adquire produtos de tecnologia (computadores, componentes, periféricos, acessórios). | `project-overview.md` §4.1 |
| **Funcionário** | Usuário interno responsável por acompanhar a operação e o relacionamento com os clientes (CRM). | `project-overview.md` §4.2 |
| **Administrador** | Usuário interno com permissões administrativas (gestão de produtos, categorias e pedidos). | `project-overview.md` §4.3 |

---

## Necessidades

**Dos clientes** *(evidência: §4.1)*
- Pesquisar e navegar por produtos de tecnologia e categorias.
- Comprar com carrinho e acompanhar pedidos.
- Consultar seu histórico de compras.

**Dos usuários internos** *(evidência: §2 e §4.2/§4.3)*
- Acompanhar a jornada do cliente, seu histórico de compras e pedidos.
- Manter um registro organizado dos atendimentos realizados.
- Gerenciar produtos, categorias e pedidos.

**Problema central que as necessidades endereçam** *(evidência: §2)*
- Quando informações comerciais e de relacionamento **não estão integradas**, torna-se difícil acompanhar a jornada do cliente, consultar seu histórico e manter atendimentos organizados.

---

## Produto

Plataforma de e-commerce de tecnologia com CRM integrado *(evidência: §6)*.

| Área | Recursos previstos |
|------|--------------------|
| **E-commerce** | Cadastro/autenticação de clientes; catálogo e navegação por categorias; carrinho; criação e acompanhamento de pedidos; histórico de compras. |
| **Área administrativa** | Gestão de produtos e categorias; consulta e gestão de pedidos; consulta de clientes; acesso conforme permissões. |
| **CRM** | Consulta de clientes e histórico de compras; pedidos associados; registro e consulta de atendimentos; informações de relacionamento. |

**Tecnologia** *(evidência: §8)*: frontend em **Reflex**, backend e dados em **Xano/XanoScript**, versionamento em Git/GitHub, desenvolvimento incremental orientado por **OpenSpec**.

**Escopo inicial (resumo)** *(evidência: §5.1)*: cadastro/autenticação de clientes, catálogo, pesquisa, categorias, carrinho, pedidos, histórico, painel administrativo, gestão de produtos/categorias/pedidos, CRM de clientes e atendimentos.

---

## Objetivos de negócio

*Derivados dos objetivos específicos de `docs/project-overview.md` §3 e das restrições §7/§10.*

| Objetivo qualitativo | Evidência |
|----------------------|-----------|
| Centralizar informações comerciais e de relacionamento em uma plataforma. | §1, §2, §3 |
| Viabilizar o fluxo completo de compra (catálogo → carrinho → pedido → pagamento simulado). | §3, §6.1 |
| Instrumentar a equipe interna para acompanhar vendas, clientes e atendimentos. | §3, §6.2/§6.3 |
| Separar com segurança clientes e usuários internos, aplicando autorização no backend. | §7, §10 |
| Manter a consistência e a integridade das informações entre e-commerce e CRM. | §7, §10 |

**Metas quantitativas** (ex.: nº de clientes, volume de vendas, tempo de atendimento): **a definir** — não há dados ou métricas documentadas no projeto. Não foram inventadas.

---

## Resumo visual

```text
+---------------------------------------------------------------+
| VISÃO                                                          |
| Integrar e-commerce de tecnologia e relacionamento com         |
| clientes em uma única plataforma.                              |
+----------------------+----------------------------------------+
| GRUPO-ALVO           | NECESSIDADES                           |
| Cliente              | Pesquisar/comprar,                     |
| Funcionário          | acompanhar pedidos, consultar          |
| Administrador        | histórico; CRM e atendimentos          |
+----------------------+----------------------------------------+
| PRODUTO                                                        |
| E-commerce + Área administrativa + CRM (Reflex + Xano)         |
+----------------------------------------------------------------+
| OBJETIVOS DE NEGÓCIO                                           |
| Centralizar informações; viabilizar compra; instrumentar a     |
| operação; segurança e integridade dos dados. (métricas: a def.)|
+----------------------------------------------------------------+
```
