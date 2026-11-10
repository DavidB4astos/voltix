## 1. Backend Xano

- [x] 1.1 Criar `xano/api/internal_customers/customer_id_PATCH.xs` no grupo publicado `Voltix Internal Customers`, com `auth = "user"` e `precondition` de UsuarioInterno `ATIVO` e `ADMINISTRADOR` — verificação: revisão do arquivo e dry-run restrito
- [x] 1.2 Aceitar somente `nome_completo?`, `email?`, `telefone?` e `status?`, exigir ao menos um campo, aplicar `trim`/`lower` e validar 1–300 caracteres para nome, e-mail válido até 254, telefone até 30 e status `ATIVO`/`INATIVO` — verificação: revisão estática dos `precondition` e casos de erro previstos
- [x] 1.3 Confirmar o Cliente por `id` positivo, validar e-mail único ignorando o próprio registro e manter CPF, senha e vínculos fora da entrada — verificação: revisão do fluxo e do schema `CLIENTE`
- [x] 1.4 Aplicar `db.patch CLIENTE` em `db.transaction`, atualizar `updated_at` e responder no mesmo contrato sanitizado do detalhe (`id`, `nome_completo`, `email_masked`, `telefone_masked`, `status`, `created_at`, `cpf_masked`) — verificação: inspeção da resposta e ausência de campos privados
- [x] 1.5 Executar `xano workspace push -d xano --dry-run -i "api/internal_customers/customer_id_PATCH.xs" -i "api/internal_customers/api_group.xs"` e revisar o plano — verificação: somente o grupo e o novo endpoint aparecem no dry-run (requer autorização)
- [x] 1.6 Publicar o endpoint com autorização explícita e confirmar por pull/verificação somente leitura que as referências e o contrato foram preservados — verificação: evidência de publicação com GUIDs e resposta sanitizada

## 2. Contrato Python

- [x] 2.1 Adicionar `customer_update_payload(nome_completo, email, telefone, current_name)` em `voltix/internal_customers.py`, retornando apenas campos alterados e válidos (`nome_completo`, `email`, `telefone`) — verificação: testes unitários do módulo passam
- [x] 2.2 Adicionar `customer_status_payload(status)` aceitando apenas `ATIVO`/`INATIVO` — verificação: testes rejeitam outros valores
- [x] 2.3 Reutilizar `customer_record(..., detail=True)` para validar a resposta do `PATCH`, sem novo formato — verificação: teste confirma máscaras e rejeição de campos crus ou extras
- [x] 2.4 Documentar `XANO_INTERNAL_CUSTOMER_UPDATE_URL` em `.env.example` sem valor — verificação: nome presente e nenhum segredo exposto

## 3. Estado e handlers

- [x] 3.1 Adicionar ao `State` os campos de edição (`nome`, `email`, `telefone`), confirmação de status, salvamento e feedback; limpá-los em `_clear_internal_customers` e no fechamento da ficha — verificação: testes de limpeza e `reflex compile`
- [x] 3.2 Refatorar `load_internal_customers` para permitir recarga preservando o detalhe (`_load_internal_customers(preserve_detail=True)`), mantendo o comportamento atual nos demais fluxos — verificação: testes existentes continuam aprovados
- [x] 3.3 Preencher `internal_customer_edit_nome` ao abrir o detalhe e limpar e-mail/telefone, confirmação e feedback — verificação: teste de `show_internal_customer` confirma os campos
- [x] 3.4 Implementar `save_internal_customer` restrito a `ADMINISTRADOR`, validando localmente, enviando somente campos preenchidos e recusando payload vazio sem requisição — verificação: testes cobrem FUNCIONARIO sem requisição, payload vazio e envio correto
- [x] 3.5 Implementar confirmação em dois passos para inativação (`request`/`confirm`/`cancel`) e reativação direta, ambos via `PATCH` de status — verificação: testes cobrem inativação confirmada, cancelamento e reativação idempotente
- [x] 3.6 Tratar `400` (dados inválidos ou e-mail duplicado), `404` (Cliente ausente), `401`/`403` (encerrar sessão) e falha genérica; descartar resposta quando token/usuário mudarem — verificação: testes de erro e de logout durante a atualização
- [x] 3.7 Atualizar a ficha e a linha correspondente após sucesso e recarregar a lista preservando o detalhe, com feedback persistente — verificação: teste confirma detalhe atualizado e recarga chamada

## 4. Interface

- [x] 4.1 Exibir o formulário e as ações de status apenas quando `user_role == "ADMINISTRADOR"`, mantendo a ficha somente leitura para `FUNCIONARIO` — verificação: inspeção de código e teste de handler
- [x] 4.2 Renderizar nome pré-preenchido e e-mail/telefone vazios com a instrução "deixe em branco para manter"; impedir envio durante salvamento — verificação: `reflex compile` e revisão de rótulos/`aria_label`
- [x] 4.3 Exibir a confirmação de inativação com texto sobre preservação do histórico e bloqueio de novos acessos, além de feedback `role=status` de sucesso/erro — verificação: revisão dos fluxos e `reflex compile`
- [x] 4.4 Adicionar estilos de edição de Cliente em `assets/voltix-internal.css` reutilizando a linguagem de `vx-attendance`, com quebra em tela estreita — verificação: revisão de CSS e `reflex compile`

## 5. Verificação e encerramento

- [x] 5.1 Rodar `python -m unittest discover -s tests -q` — verificação: suíte completa aprovada
- [x] 5.2 Rodar `reflex compile` restaurando `reflex.lock` — verificação: `git status` sem alterações em `reflex.lock`
- [x] 5.3 Rodar `openspec validate implement-internal-customer-edit --strict`, `openspec validate --all --strict` e `git diff --check` — verificação: tudo válido e diff limpo
- [x] 5.4 Registrar evidência local e de publicação em `evidence/`, atualizar `docs/roadmap-changes.md` e `docs/AI_AGENT_HANDOFF.md` — verificação: documentação consistente
- [x] 5.5 Arquivar a change e sincronizar a spec principal, ajustando o propósito de `internal-customers` para refletir a edição administrativa — verificação: `openspec validate --all --strict`
- [ ] 5.6 Commit e push somente com autorização explícita — verificação: `git status --short --branch` e `git log --oneline -1`
