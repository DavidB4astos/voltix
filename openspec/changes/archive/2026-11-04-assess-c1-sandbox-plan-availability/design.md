## Método

1. Consultar apenas a ajuda local do Xano CLI para `sandbox get` e `sandbox push`; não executar comandos que provisionem ou enviem documentos.
2. Consultar a página oficial de preços e o repositório oficial do CLI.
3. Separar disponibilidade geral do comando, elegibilidade do plano e situação específica da conta.
4. Atualizar o README do adiamento C1 com a condição de retomada e a decisão de não provisionar.

## Constatações

- O CLI local é v1.2.0 e informa que `sandbox get` cria um ambiente se não existir.
- O CLI não oferece filtros include/exclude para `sandbox push`; ele exige preview (`--dry-run`) antes de qualquer envio.
- A página oficial de preços consultada em 04/11/2026 lista `CLI sandbox environments` como benefício do plano Essential, exibido a US$85/mês com cobrança anual. O plano Free não lista esse benefício.
- A elegibilidade e o plano atuais da conta não foram consultados. O README do projeto informa que o plano conhecido é Free, mas esse dado é histórico e não prova o estado atual.

## Decisão

Não executar `xano sandbox get`, `sandbox push`, testes de escrita, upgrade ou publicação. C1 só pode avançar após confirmação do usuário de uma opção isolada sem custo adicional, ou autorização explícita para usar um plano pago já existente. Depois, abrir change própria para provisionamento e teste, com pacote de Xano mínimo e preview antes de qualquer push.
