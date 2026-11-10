## Why

A consulta interna de Clientes (C4) permanece somente leitura: a ficha apresenta apenas
dados mascarados e orienta o usuário a não editar. O CRM, porém, exige corrigir nome,
e-mail, telefone e inativar um Cliente sem apagar seu histórico. Hoje não existe endpoint
interno de edição; o único `PATCH` legado de Cliente é autenticado pelo próprio Cliente e
o `PATCH status_cliente/{id}` não possui autenticação, portanto não pode ser reaproveitado
com segurança.

## What Changes

- Criar o endpoint Xano `PATCH internal_customers/{customer_id}` no grupo já publicado
  `Voltix Internal Customers`, com `auth = "user"` e autorização exclusiva de
  `ADMINISTRADOR` ativo.
- Aceitar somente `nome_completo`, `email`, `telefone` e `status`, todos opcionais; campos
  ausentes mantêm o valor atual. CPF, senha, `USER_ID` e vínculos não são editáveis.
- Validar nome, e-mail e telefone no backend, exigir e-mail único entre Clientes e manter
  a resposta sanitizada idêntica ao detalhe (máscaras, sem credenciais).
- Permitir inativação e reativação idempotentes; o Cliente inativo continua existindo e
  perde apenas novos logins, preservando pedidos, atendimentos e endereços.
- Adicionar à ficha do Cliente, apenas para `ADMINISTRADOR`, um formulário de edição com
  nome pré-preenchido e e-mail/telefone em branco ("deixe em branco para manter"), além
  de ação de status com confirmação explícita para inativar.
- Reutilizar o contrato sanitizado existente, adicionar o construtor de payload ao módulo
  `internal_customers` e tratar `400`, `403`, `404` e sessão expirada na interface.

## Capabilities

### New Capabilities

Nenhuma capability nova.

### Modified Capabilities

- `internal-customers`: a consulta deixa de ser estritamente somente leitura; passa a
  permitir que administradores atualizem dados cadastrais e status, mantendo leitura
  mascarada para os dois papéis internos.

## Impact

- Xano: novo arquivo `xano/api/internal_customers/customer_id_PATCH.xs`; publicação
  restrita ao endpoint e ao grupo, pendente de autorização explícita.
- Código: `voltix/internal_customers.py` (payloads), `voltix/voltix.py` (Estado, handlers
  e ficha do Cliente), `assets/voltix-internal.css` (bloco de edição).
- Configuração: nova variável server-side `XANO_INTERNAL_CUSTOMER_UPDATE_URL`.
- Testes: contrato e handlers em `tests/test_internal_customers.py`.
- Specs: `internal-customers` com requisitos de autorização, máscaras, interface e edição.
- Fora do escopo: revelar dados, excluir Cliente, editar CPF, alterar endereços, pedidos,
  atendimentos ou credenciais, e qualquer alteração de schema ou tabela.
