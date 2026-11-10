## Context

O painel interno já possui quatro leituras autenticadas e validadas: Clientes (`GET internal_customers`), Atendimentos (`GET atendimentos`), Pedidos (`GET internal_orders`) e Vendas (`GET reports/sales`). Cada uma retorna paginação com `total_items` e registros estritos. O CRM não tem endpoint próprio, e o projeto decidiu não publicar backend novo nesta change.

O dashboard de vendas existente permanece: ele responde "quanto vendi" e tem filtro de período. O CRM responde "como está o relacionamento" e não deve duplicá-lo nem absorvê-lo.

## Goals / Non-Goals

**Goals:**

- Entregar uma seção CRM com indicadores reais de relacionamento e vendas.
- Reutilizar os contratos e o token interno existentes, sem backend novo.
- Manter a seção somente leitura, com estados seguros e sem dados pessoais.
- Fechar a lacuna de navegação para os dois papéis internos.

**Non-Goals:**

- Criar capability de escrita, edição ou exclusão.
- Exibir nome de Cliente nos Atendimentos; a identificação continua por `cliente_id`.
- Traduzir ou agregar dados no navegador.
- Substituir o Dashboard de vendas.

## Decisions

- **Uma leitura por indicador exato.** Os endpoints de lista aceitam `status` e `per_page`. Para obter totais exatos por situação, a seção faz uma leitura com `per_page=1` por status e usa `total_items`, em vez de contar itens de uma página. Alternativa descartada: contar a primeira página, que produz números errados acima de 50 registros.
- **Sete leituras sequenciais.** Clientes ativos (1), Atendimentos por situação (3), Pedidos registrados (1), Atendimentos recentes (1) e Vendas (1). A execução é sequencial para reduzir risco de `429` no plano Free; cada leitura usa o tratamento de rate limit já existente. Alternativa descartada: `gather` concorrente, que multiplica requisições simultâneas no mesmo workspace.
- **Tudo ou nada.** Se qualquer leitura falhar, a seção não renderiza números parciais: apresenta erro e permite nova tentativa. Alternativa descartada: mostrar parcialmente, que produz um painel enganoso.
- **Contrato derivado, não novo contrato de rede.** `CrmDashboard` é montado a partir dos modelos já validados (`InternalCustomer` page, `Attendance` page, `OrderSummary` page, `SalesDashboard`). Não há parsing novo de JSON bruto.
- **Período de vendas padrão.** A leitura de vendas não envia `from`/`to`; o backend aplica sua janela padrão e a seção exibe o período retornado, sem calcular datas no navegador.
- **Somente leitura.** Nenhum handler de escrita é chamado; os atalhos apenas trocam `internal_section`.

## Risks / Trade-offs

- **Sete requisições por carga** → sequencial e sob demanda; o botão de atualização é explícito e o carregamento é bloqueado durante a execução.
- **Rate limit `429`** → reaproveita o retry limitado existente; falha persistente vira mensagem de erro, não número inventado.
- **Atendimentos identificados por `Cliente #id`** → decisão de privacidade já consolidada; a ficha do Cliente continua sendo o lugar com nome.
- **Vendas e CRM com períodos diferentes** → o bloco de vendas exibe o período retornado pelo backend para não sugerir que os demais números usam a mesma janela.
- **Painel parecido com o Dashboard de vendas** → separação explícita por blocos "Relacionamento" e "Vendas no período"; o CRM não repete a série diária.

## Migration Plan

Não há migração de dados. A seção nasce vazia e carrega sob demanda. Reverter consiste em remover o item de navegação, o painel, o módulo, os campos de estado e os testes, mantendo o Dashboard de vendas intacto.
