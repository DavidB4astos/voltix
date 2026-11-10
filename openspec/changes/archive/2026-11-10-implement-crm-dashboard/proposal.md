## Why

O escopo de CRM está implementado em três seções isoladas — Clientes, Atendimentos e Pedidos — sem nenhuma superfície que apresente o relacionamento com os Clientes de forma consolidada. O Dashboard existente mede vendas (faturamento, Pedidos, ticket médio), não a operação de CRM. O objetivo declarado do projeto é ter o CRM e uma tela de dashboard; hoje só existe a metade de vendas.

## What Changes

- Adicionar a seção **CRM** à navegação interna, disponível para `FUNCIONARIO` e `ADMINISTRADOR` ativos, entre Dashboard e Clientes.
- Criar o painel de CRM com um retrato somente leitura do relacionamento:
  - Clientes ativos.
  - Atendimentos por situação: abertos, em atendimento e finalizados.
  - Pedidos registrados.
  - Vendas do período padrão do backend: faturamento, Pedidos faturados e ticket médio.
  - Últimos atendimentos, em ordem decrescente de data.
  - Atalhos para as seções Clientes, Atendimentos e Pedidos.
- Reutilizar exclusivamente endpoints já publicados: `GET internal_customers`, `GET atendimentos`, `GET internal_orders` e `GET reports/sales`.
- Validar cada resposta com os contratos estritos já existentes e carregar a seção sob demanda, com estados de carregamento, vazio, erro e sessão encerrada.

## Capabilities

- Nova capability `crm-dashboard`: painel consolidado de relacionamento, somente leitura.
- Delta em `internal-workspace`: a navegação passa a oferecer a seção CRM aos dois papéis internos.

## Fora do escopo

- Criar ou alterar endpoints, tabelas, funções, permissões ou registros no Xano.
- Editar, inativar ou excluir Cliente, Produto ou Atendimento.
- Alterar status de Atendimento ou de Pedido.
- Exibir nome, e-mail, CPF, telefone, endereço, senha, hash ou token.
- Adicionar Atendimentos à ficha do Cliente ou pré-preencher o formulário de Atendimento a partir dela (change seguinte).
- Alterar a seção Dashboard de vendas existente.

## Impact

- Código: novo módulo `voltix/internal_crm.py`, campos e handler no `State`, painel e item de navegação em `voltix/voltix.py`, estilos em `assets/voltix-internal.css`.
- Specs: nova `crm-dashboard`; requisito de navegação de `internal-workspace` modificado.
- Xano: nenhuma publicação ou alteração.
- Dados: somente leitura; nenhuma escrita é emitida.
- Testes: novo arquivo de contrato e handlers, além dos testes de navegação existentes.
