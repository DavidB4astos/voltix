## Context

Ver `proposal.md` — Why. A C10 já publicou `GET reports/sales` no grupo `Voltix Internal
Orders`, com `auth = "user"` e precondições de FUNCIONARIO/ADMINISTRADOR `ATIVO`. A resposta
real é:

```
{
  periodo: {inicio, fim, timezone},
  faturamento, pedidos, ticket_medio,
  status_incluidos: [PAGAMENTO_CONFIRMADO, EM_PREPARACAO, ENVIADO, ENTREGUE],
  serie_diaria: [{data, faturamento, pedidos}]
}
```

A tela não altera o Xano. O painel interno é renderizado em `voltix/voltix.py` por
`internal_workspace_shell`, com seções controladas por `State.internal_section`. As telas de
Atendimentos e Pedidos já estabeleceram o padrão de contrato estrito em módulo próprio,
handlers server-side com token interno, descarte por geração e composição de seção.
`internal_customers.positive_int` e `_cart_money_text` são reutilizáveis.

Restrições:

- Sessão interna privada no servidor; nenhum token no navegador.
- A resposta contém apenas agregados; nenhum identificador de Cliente ou dado pessoal.
- Sem backend novo, schema, migração ou escrita.

## Goals / Non-Goals

**Goals**

- Reutilizar o padrão de seção e contrato das telas de Atendimentos/Pedidos.
- Validar a resposta antes do navegador e apresentar valores monetários sem recálculo.
- Manter o backend como autoridade de período, status e arredondamento.

**Non-Goals**

- Gráficos avançados, exportação, previsões/metas ou comparativos.
- Paginação da série diária, cache local ou persistência de filtros entre sessões.
- Alterar `reports/sales` ou qualquer rota Xano.

## Decisions

### 1. Módulo próprio `voltix/internal_sales.py`

- `dashboard_filters(from_value, to_value)` valida strings opcionais `YYYY-MM-DD`, datas
  reais, ordem ascendente e limite de 366 dias inclusivos. Retorna apenas as chaves
  informadas (`from`/`to`), deixando o backend completar a janela.
- `sales_dashboard(value)` valida a resposta e devolve `SalesDashboard` ou `ValueError`.
- Dataclasses achatadas para o Estado: `SalesDashboard` carrega período, totais e
  `serie_diaria: list[DailySales]`; `DailySales` carrega `data`, `data_display`,
  `faturamento` e `pedidos`. Listas de dataclasses já são suportadas pelo `rx.foreach`
  (usado nos itens de Pedido).

Alternativa considerada: reaproveitar o contrato de `sales-dashboard` do backend. Rejeitada
porque o frontend precisa de campos de apresentação e de validação estrita próprios.

### 2. Valores monetários canônicos em `str`

A resposta JSON traz números. O contrato converte cada valor para `Decimal`, quantiza em duas
casas (`ROUND_HALF_UP`) e expõe `str` canônico. A UI usa `_cart_money_text`, que já formata
`R$ 1.234,56` a partir de texto decimal, sem aritmética no navegador.

Alternativa considerada: manter `float` e formatar no cliente. Rejeitada por risco de
artefatos binários e de recálculo divergente do backend.

### 3. Validação da resposta

- Chaves exatas em todos os níveis; `periodo.timezone == "UTC"`; `inicio`/`fim` em
  `YYYY-MM-DD`, `inicio <= fim` e dentro do padrão do backend.
- `status_incluidos` exatamente `["PAGAMENTO_CONFIRMADO", "EM_PREPARACAO", "ENVIADO",
  "ENTREGUE"]`.
- `pedidos` inteiro não negativo; `faturamento` e `ticket_medio` numéricos finitos e não
  negativos.
- `pedidos == 0` exige `faturamento == 0`, `ticket_medio == 0` e `serie_diaria` vazia.
- Com `pedidos > 0`: série não vazia, datas estritamente crescentes e dentro do período,
  cada dia com `pedidos >= 1`, soma dos `pedidos` da série igual a `pedidos`, e
  `ticket_medio` dentro de um centavo de `faturamento / pedidos`.
- A comparação do ticket usa tolerância de `0.01` para absorver diferença de convenção de
  arredondamento entre Xano e Python; os demais totais são comparados em `Decimal`.

### 4. Handlers server-side e descarte

- `load_internal_dashboard` valida filtros, incrementa `_internal_dashboard_generation`,
  captura token/usuário e só grava se geração, token e usuário continuarem atuais.
- `apply_internal_dashboard_filters` normaliza `from`/`to` do formulário e recarrega;
  `clear_internal_dashboard_filters` volta ao período padrão do backend.
- `401`/`403` limpam sessão e Dashboard; `400` informa período inválido mantendo a sessão;
  outras falhas usam mensagem genérica.
- `_clear_internal_dashboard` é chamado nos mesmos pontos de logout/troca de identidade que
  limpam Clientes, Atendimentos e Pedidos.

### 5. Navegação e composição

- `select_internal_section` aceita `dashboard` para FUNCIONARIO e ADMINISTRADOR e dispara
  `load_internal_dashboard` ao trocar para a seção.
- Dashboard entra como primeira seção, com ícone `layout-dashboard`; título "Dashboard" e
  descrição sobre faturamento e volume de vendas.
- A seção renderiza cartões de faturamento, Pedidos e ticket médio, o período aplicado, os
  status incluídos e a tabela da série diária. Sem paginação: a série é limitada a 366 dias.
- Estados de carregamento, vazio, erro e mensagens em `role=status`.

### 6. Configuração

Nova variável `XANO_INTERNAL_SALES_URL` (GET, já inclui a rota `reports/sales`) documentada
em `.env.example` sem valor.

## Risks / Trade-offs

- [Arredondamento divergente entre Xano e Python] → comparar ticket médio com tolerância de
  um centavo e manter os valores canônicos em `Decimal`.
- [Série longa em períodos de até 366 dias] → tabela com rolagem vertical, sem paginação nem
  gráfico; o limite do backend restringe o volume.
- [Resposta fora do contrato derruba a tela] → validação estrita falha com mensagem e não
  renderiza dados parciais.
- [Diferença de fuso] → exibir o período retornado pelo backend e não calcular datas no
  navegador.

## Migration Plan

1. Adicionar `XANO_INTERNAL_SALES_URL` ao ambiente.
2. Publicar o frontend; nenhuma migração de dados ou rollback de backend é necessário.
3. Rollback: remover a seção e a variável; o endpoint C10 permanece inalterado.

## Open Questions

Nenhuma.
