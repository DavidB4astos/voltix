## Context

Os dois endpoints de escrita de senha do grupo `Voltix Internal Users` declaram
`minAlpha:1|minDigit:1` em inputs `text`. Esses filtros só existem para inputs do
tipo `password`; em `text`, o XanoScript não os oferece, e o `confirm_POST.xs` da
change `implement-internal-password-recovery` já estabeleceu o padrão aprovado para
contornar a limitação: `filters=min:8` no input e a regra de letra e dígito aplicada
na stack com `regex_test`.

O contrato de negócio não muda: `openspec/specs/internal-users/spec.md` já exige 8+
caracteres com letra e dígito, e o frontend (`voltix/internal_users.py`,
`_password`) já valida a mesma regra antes de enviar. Ver `proposal.md` para a
motivação.

## Goals / Non-Goals

**Goals:**

- Os dois endpoints publicáveis aplicam a regra de senha existente usando
  construções válidas do XanoScript.
- Verificação estática nos testes (asserções sobre o conteúdo dos `.xs`), sem
  escrita em dados reais nem publicação automática.
- Publicação restrita aos dois endpoints, somente após dry-run e autorização
  explícita, com verificação remota somente leitura.

**Non-Goals:**

- Alterar a coluna `password` da tabela `user` (tipo `password` aceita
  `minAlpha`/`minDigit`; permanece como está).
- Alterar o contrato HTTP, as mensagens de outras operações, o frontend, a
  autenticação, os tokens ou qualquer dado real.
- Criar rate limiting, revogação global de tokens ou política de senha nova.

## Decisions

1. **`text filters=min:8` + precondition `regex_test` na stack**, em vez de trocar o
   tipo do input para `password`.
   Alternativa considerada: `text password filters=...` com tipo `password`.
   Rejeitada porque alteraria o tipo de dado do input (e a forma como o Xano trata
   o valor, inclusive em logs/metadados) para além do necessário, enquanto o
   `confirm_POST.xs` publicado já valida o padrão de regex na stack. Manter `text`
   preserva a assinatura do endpoint e o raio mínimo da mudança.

2. **Ordem das preconditions: autorização → validação de formato → unicidade/regra
   de negócio → escrita.** A regra de senha entra junto das demais validações de
   entrada, antes de qualquer `db.add`/`db.edit` e depois do guard de sessão,
   preservando o padrão já testado em `test_authorization_precedes_business_reads_and_writes`.

3. **Mensagem de erro específica para senha fraca** ("The password must contain at
   least 8 characters, a letter and a digit."), diferente do `confirm_POST.xs`.
   Motivo: o endpoint é autenticado e não tem por que apaziguar enumeração; o
   frontend já exibe validação equivalente, e uma mensagem clara ajuda o
   administrador e o próprio usuário. Nenhuma das duas mensagens revela credenciais.

4. **`skip_specs: true`**: nenhuma requirement da spec `internal-users` muda; o
   delta seria uma reescrita idêntica do comportamento já especificado.
5. **Testes estáticos** sobre os `.xs` (ausência dos filtros inválidos, presença do
   `regex_test`, ordem das preconditions, ausência de segredo na resposta),
   seguindo `InternalRecoveryScriptTests` e `InternalUserScriptTests` já
   existentes. Sem teste remoto de escrita.

## Risks / Trade-offs

- [Senha curta demais passa a ser rejeitada no backend mesmo se o frontend for
  contornado] → É exatamente o comportamento exigido pela spec; o risco é de
  expectativa de clientes antigos, mitigado pela mensagem clara e por o contrato já
  ser o mesmo desde a publicação original.
- [`regex_test` com ranges ASCII não cobre letras acentuadas] → Aceitável e
  intencional: a regra exige ao menos uma letra `A-Za-z` e um dígito, idêntica à do
  frontend e do `confirm_POST.xs`.
- [Publicação Xano sem a change] → Bloqueada por gate explícito: dry-run mostrando
  apenas os dois `query` alterados, pull posterior para conferência e verificação
  remota somente leitura (400 esperado para senha fraca quando autenticado; 401 sem
  sessão). Nenhuma escrita em dados reais.
- [Falha de importação no Xano por sintaxe] → Os arquivos são canônicos em relação
  ao `confirm_POST.xs` já publicado; `git diff --check` e os testes estáticos
  antecipam problemas.

## Migration Plan

1. Implementar os dois `.xs` e os testes estáticos; rodar a suíte completa.
2. `openspec validate fix-internal-users-password-filters --strict`.
3. Dry-run restrito dos dois endpoints; mostrar o preview ao usuário.
4. **GATE**: autorização explícita antes de publicar.
5. Publicar somente os dois endpoints; pull independente e comparação.
6. Verificação remota somente leitura (401 sem sessão; 400/422 de validação com
   senha fraca se houver sessão descartável, senão limitar-se a 401 e registrar a
   limitação).
7. Atualizar evidências, `docs/roadmap-changes.md`, `docs/AI_AGENT_HANDOFF.md`,
   arquivar e validar globalmente.

Rollback: republicar a versão anterior dos dois arquivos (presentes no histórico do
Git) com o mesmo fluxo de dry-run + autorização.
