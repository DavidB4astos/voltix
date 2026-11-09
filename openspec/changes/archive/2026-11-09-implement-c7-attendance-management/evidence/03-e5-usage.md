# 03 — E5: plano, requisições e 429 (09/11/2026)

## Plano

- Plano atual: **Free** (workspace `147981`, instância `x8ki-letl-twmt`).
- Confirmado no workspace ("Free Plan") e na página de Billing ("Free — Current Plan").
- Nenhum upgrade foi realizado.

## Requisições e erros

- Amostra carregada no Request History: **32 solicitações**, sendo **22 com sucesso (`2xx`)** e
  **10 não-`2xx`**.
- Error Logs das últimas 24h: **10 erros**, todos `ERROR_CODE_UNAUTHORIZED` (401).
  Os 401 correspondem a chamadas sem sessão usadas nas verificações.
- Busca por `429` e `TOO_MANY` no Error Logs: **nenhum resultado**.
- Conclusão: **0 erros 429 observados** no período consultado.

## Consumo de registros

O Xano **não exibiu** o consumo de registros em nenhuma das telas consultadas:

- workspace / Request History;
- Error Logs;
- Upgrade Plan / Billing;
- configurações do workspace;
- CLI (`profile me`, `workspace get`, `platform get`, `tenant list`).

A CLI confirma apenas o plano Free; não expõe contadores de registros, requisições ou 429.
Nenhum registro real foi baixado ou impresso.

## Impacto da C7

- `+1` tabela (`atendimento`) criada **vazia**.
- `+1` grupo de API e `+5` endpoints.
- A publicação **não insere registros** e **não gera tráfego**; o consumo só ocorre quando a
  futura tela ou integração chamar os endpoints.
- O dry-run confirmou exatamente esses 7 documentos, sem alterar objetos existentes.

## Avaliação

O risco imediato de limite de registros na publicação é desprezível, porque a tabela nova
começa vazia e nenhum dado é migrado. O histórico de 429 está limpo na amostra disponível.
A limitação restante é a **ausência de medição do total de registros usados**, que o Xano
não expôs; isso deve ser monitorado após a primeira carga real de atendimentos.

## Limitações

- O período exato do Request History não pôde ser ampliado para 30 dias; a amostra carregada
  é a disponível na tela.
- O total de registros usados permanece desconhecido.
- Nenhuma consulta autenticada, escrita de dados ou upgrade foi executado.
