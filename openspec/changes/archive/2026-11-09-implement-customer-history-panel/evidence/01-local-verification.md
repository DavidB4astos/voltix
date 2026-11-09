# 01 — Tela de histórico do Cliente: verificação local (09/11/2026)

## Escopo verificado

- Seção **Histórico de pedidos** no detalhe do Cliente, em largura total abaixo da
  lista/ficha.
- Carregamento automático ao abrir a ficha, consumindo
  `GET customers/{customer_id}/orders` (C6 já publicado).
- Filtros de status (`TODOS` por padrão) e período `from`/`to` (`YYYY-MM-DD`, UTC,
  inclusivos), com paginação de 20.
- Pedidos com resumo e itens sempre expandidos.
- Estados de carregamento, vazio, erro e sessão não autorizada.
- Nenhuma alteração de backend, schema ou endpoint Xano.

## Verificação local

| Item | Resultado |
|---|---|
| `python -m unittest discover -s tests -q` | **205 testes**, OK |
| `python -m unittest tests.test_internal_customers -q` | **33 testes**, OK |
| `openspec validate implement-customer-history-panel --strict` | válido |
| `python -c "from voltix.voltix import index; index()"` | componente construído sem erro |
| `reflex compile` | **App compiled successfully** |
| `git diff --check` | limpo |

## Contrato Python

- `history_parameters` valida status, datas `YYYY-MM-DD`, `from <= to`, página e
  `per_page` (1–50).
- `order_record` valida chaves exatas, status, valores monetários, data e itens.
- `order_history_page` valida `cliente_id`, página, tamanho da página, totais e
  duplicidade de Pedidos.
- SKU/descrição nulos são normalizados para vazio e exibidos como "Indisponível".
- Valores monetários são preservados como texto, sem recálculo.

## Segurança

- Requisição server-side com token interno (`Bearer`), sem token de Cliente.
- Nenhuma credencial ou URL privada é registrada nesta evidência.
- 401/403 limpam lista, ficha, histórico e contadores.
- Respostas obsoletas são descartadas por geração, token, usuário, Cliente e detalhe.

## Configuração

- Nova variável: `XANO_INTERNAL_CUSTOMER_ORDERS_URL`.
- Valor esperado: URL do endpoint C6 com o placeholder `{customer_id}`. O valor não é
  reproduzido nesta evidência.

## Limites

- Não houve publicação no Xano: a tela reutiliza o endpoint da C6.
- Não houve teste visual autenticado porque o ambiente não disponibilizou credencial de
  FUNCIONARIO/ADMINISTRADOR nesta execução. A validação ficou limitada a contrato,
  handlers, renderização do componente e compile.
- `reflex.lock/bun.lock` e `reflex.lock/package.json` foram alterados pelo compile local
  e restaurados; não entram no commit.
