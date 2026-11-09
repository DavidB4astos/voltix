# 01 — Dashboard de vendas: verificação local (09/11/2026)

## Escopo verificado

- Seção **Dashboard** no painel interno, acessível a FUNCIONARIO e ADMINISTRADOR ativos.
- Filtros opcionais `from`/`to` (`YYYY-MM-DD`), inclusivos em UTC, com período padrão de 30
  dias fornecido pelo backend e validação local de formato, ordem e limite de 366 dias.
- Cartões de faturamento, Pedidos e ticket médio, além do período aplicado, status incluídos
  e série diária em tabela crescente.
- Estados de carregamento, vazio, erro e sessão não autorizada.
- Nenhuma alteração de backend, schema, rota ou publicação Xano.

## Verificação local

| Item | Resultado |
|---|---|
| `python -m unittest discover -s tests -q` | **290 testes**, OK |
| `reflex compile` | **App compiled successfully** (3,7 s) |
| `openspec validate implement-sales-dashboard-panel --strict` | válido |
| `openspec validate --all --strict` | **25 passed**, 0 failed |
| `git diff --check` | limpo (apenas avisos de LF/CRLF) |
| `git status` após compile | sem alterações em `reflex.lock` |

## Contrato Python

`voltix/internal_sales.py`:

- `dashboard_filters` aceita `from`/`to` opcionais em `YYYY-MM-DD`, valida datas reais,
  ordem ascendente e no máximo 366 dias inclusivos; retorna apenas as chaves informadas para
  o backend completar a janela.
- `sales_dashboard` exige exatamente `{periodo, faturamento, pedidos, ticket_medio,
  status_incluidos, serie_diaria}` e `periodo {inicio, fim, timezone}` com `timezone="UTC"`.
- `status_incluidos` deve ser exatamente `PAGAMENTO_CONFIRMADO`, `EM_PREPARACAO`, `ENVIADO`,
  `ENTREGUE`, nessa ordem.
- Valores monetários são convertidos para `Decimal`, quantizados em duas casas e expostos
  como texto canônico; a UI reutiliza `_cart_money_text` sem recálculo.
- A série diária exige datas reais, crescentes e dentro do período, `pedidos >= 1` por dia e
  soma dos Pedidos igual a `pedidos`. O ticket médio é conferido com tolerância de um centavo.
- `pedidos=0` exige faturamento e ticket médio zerados e série vazia.

## Handlers e segurança

- Requisição server-side com token interno (`Bearer`); nenhum token ou URL privada chega ao
  navegador.
- `load_internal_dashboard` valida filtros antes de requisitar, descarta respostas obsoletas
  por geração, token e usuário e grava apenas o resultado atual.
- `apply_internal_dashboard_filters` normaliza os limites e recarrega;
  `clear_internal_dashboard_filters` volta ao período padrão do backend.
- `401`/`403` encerram a sessão e limpam o Dashboard; `400` informa período inválido mantendo
  a sessão; falhas de rede e respostas malformadas não renderizam dados parciais.
- `_clear_internal_dashboard` é chamado nos fluxos de logout e troca de identidade, junto de
  Clientes, Atendimentos e Pedidos.

## Configuração

Nova variável, documentada em `.env.example` sem valor:

- `XANO_INTERNAL_SALES_URL` — endpoint `GET reports/sales` já publicado na C10.

## Limites

- Não houve publicação ou verificação remota autenticada: a tela reutiliza o endpoint C10.
- Não houve QA visual autenticada por falta de credencial interna nesta execução; a validação
  ficou limitada a contrato, handlers, navegação, renderização e `reflex compile`.
- A série diária não é paginada; o limite de 366 dias do backend restringe o volume.
- `reflex.lock/bun.lock` e `reflex.lock/package.json` foram verificados e restaurados; não
  entram no commit.
