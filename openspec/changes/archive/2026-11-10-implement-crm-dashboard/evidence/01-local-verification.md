# Verificação local — CRM dashboard

Data: 10/11/2026

## Escopo verificado

- Nova seção **CRM** na navegação interna, disponível a `FUNCIONARIO` e `ADMINISTRADOR` ativos.
- Painel somente leitura com blocos Relacionamento, Vendas no período, Últimos atendimentos e atalhos.
- Sete leituras sequenciais, exclusivamente de endpoints publicados:
  - `GET internal_customers` (`status=ATIVO`, `per_page=1`).
  - `GET atendimentos` (`status` em `ABERTO`, `EM_ATENDIMENTO` e `FINALIZADO`, `per_page=1`).
  - `GET internal_orders` (`status=TODOS`, `per_page=1`).
  - `GET atendimentos` (`status=TODOS`, `per_page=10`).
  - `GET reports/sales` sem filtro de período.
- Contrato estrito `voltix/internal_crm.py` sobre modelos já validados.
- Sessão encerrada e dados limpos em `401`/`403`; tudo ou nada em falha de qualquer leitura.

## Resultados

| Verificação | Resultado |
|---|---|
| `python -m unittest tests.test_internal_crm -v` | 15 testes aprovados |
| `python -m unittest discover -s tests -q` | 337 testes aprovados |
| `python -m reflex compile` | compilado com sucesso |
| `openspec validate implement-crm-dashboard --strict` | válido |
| `git diff --check` | sem erros |

## Limites

- Nenhuma publicação, tabela, função, permissão ou registro do Xano foi criado ou alterado.
- A carga real contra o Xano não foi executada nesta verificação; os handlers foram exercitados com respostas sintéticas dos contratos existentes.
- A conferência visual em navegador (375, 768 e 1280 px) permanece pendente.
- O painel identifica Cliente por `cliente_id` nos Atendimentos, conforme a spec de privacidade vigente.
