## Why

A C10 publicou `GET reports/sales`, mas o painel interno ainda não oferece a tela
correspondente. Funcionários e administradores conseguem consultar Pedidos, porém não têm uma
visão consolidada de faturamento, volume e ticket médio por período. A tela de Pedidos (C3)
validou o padrão de seção, contrato estrito e handlers server-side que será reutilizado, sem
novo backend.

## What Changes

- Nova seção **Dashboard** no painel interno, visível a FUNCIONARIO e ADMINISTRADOR ativos.
- Filtro de período por `from`/`to` (`YYYY-MM-DD`), inclusivo em UTC, com padrão de 30 dias
  fornecido pelo backend; validação local de formato, ordem e limite de 366 dias.
- Exibição de `faturamento`, `pedidos`, `ticket_medio`, período aplicado e
  `status_incluidos`, além da `serie_diaria` (dias com vendas) em tabela.
- Estados de carregamento, vazio, erro e sessão não autorizada; nenhum dado pessoal,
  identificador de Cliente, CPF, telefone, senha, hash ou token é exibido.
- Contrato Python próprio e estrito que valida a resposta antes do navegador, com descarte de
  respostas obsoletas por geração, token e usuário.
- **Fora do escopo**: alteração ou publicação Xano, mudança de schema, gráficos avançados,
  exportação, previsões/metas, relatórios contábeis, CRM e reembolso.

## Capabilities

### New Capabilities
- `sales-dashboard-panel`: seção desktop de métricas de vendas, com filtro de período,
  indicadores agregados, série diária, regras de acesso e ausência de dados sensíveis.

### Modified Capabilities
- `internal-workspace`: a navegação passa a oferecer a seção Dashboard a FUNCIONARIO e
  ADMINISTRADOR e o texto do shell SHALL deixar de vedar dashboards implementados.

## Impact

- **Frontend**: `voltix/internal_sales.py` (novo contrato), `voltix/voltix.py` (State,
  handlers, navegação e seção), `assets/voltix-internal.css` (bloco `vx-dashboard`) e
  `tests/test_internal_sales.py`.
- **Configuração**: nova variável `XANO_INTERNAL_SALES_URL` em `.env.example`.
- **Backend**: nenhum; a tela reutiliza `GET reports/sales` já publicado na C10.
- **Dados**: somente leitura de agregados; nenhuma escrita.
