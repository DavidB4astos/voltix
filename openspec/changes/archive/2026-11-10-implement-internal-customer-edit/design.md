## Context

Ver `proposal.md`. A ficha do Cliente hoje consome `GET customers/{customer_id}` e exibe
apenas nome, e-mail, telefone e CPF mascarados. O domínio (`docs/domain-model.md`, §4.1)
define CPF obrigatório e imutável, e-mail obrigatório e único, um único telefone e status
`ATIVO`/`INATIVO`, com o Cliente inativo preservado para manter o histórico.

Restrições:

- O frontend nunca é fonte de autorização; o backend reavalia papel e status a cada chamada.
- A única sessão aceita é a de UsuarioInterno (`auth = "user"`), nunca a de Cliente.
- Respostas continuam sem credenciais, hash, token, `USER_ID` ou dados não aprovados.
- Nenhuma alteração de schema, tabela, endereço ou credencial.
- A publicação do endpoint depende de autorização explícita do usuário.

## Goals / Non-Goals

**Goals:**

- `PATCH customers/{customer_id}` no grupo `Voltix Internal Customers`.
- Autorização exclusiva de `ADMINISTRADOR` ativo; `FUNCIONARIO` continua somente leitura.
- Edição parcial de nome, e-mail, telefone e status, com validação e unicidade de e-mail.
- Inativação/reativação idempotente, sem apagar histórico.
- Resposta sanitizada equivalente ao detalhe de leitura.
- Formulário e ação de status na ficha do Cliente, com confirmação para inativar.

**Non-Goals:**

- Editar CPF, senha, `USER_ID`, endereços, pedidos, atendimentos ou vínculos.
- Excluir Cliente ou criar lixeira/restauração além do status.
- Revelar e-mail, telefone ou CPF completos.
- Edição por `FUNCIONARIO` ou por sessão de Cliente.
- Alterar a listagem, os filtros ou o contrato de leitura.
- Criar histórico de auditoria de alterações nesta change.

## Decisions

1. **Endpoint e grupo**: reutilizar o grupo publicado `Voltix Internal Customers` e criar
   `xano/api/internal_customers/customer_id_PATCH.xs` com `query "customers/{customer_id}"
   verb=PATCH`. A rota fica no mesmo recurso do detalhe, evitando grupo ou caminho novo.
   - Alternativa considerada: reutilizar `PATCH status_cliente/{id}`. Rejeitada porque o
     endpoint legado não tem autenticação e expõe escrita irrestrita.
   - Alternativa considerada: reutilizar `PATCH cliente/{cliente_id}`. Rejeitada porque é
     autenticado pelo Cliente e só permite editar o próprio perfil.

2. **Autorização**: `auth = "user"`, `db.get user` restrito a `id`, `role` e `status`, com
   `precondition` de `status == "ATIVO"` e `role == "ADMINISTRADOR"`. A checagem ocorre
   antes de ler ou alterar o Cliente.
   - Alternativa considerada: permitir que `FUNCIONARIO` editasse contato. Rejeitada por
     alterar dados sensíveis fora do escopo aprovado.

3. **Campos editáveis**: entradas opcionais `nome_completo`, `email`, `telefone` e `status`.
   O backend exige ao menos um campo e rejeita os demais. CPF é imutável e não existe
   entrada correspondente.
   - Alternativa considerada: `PUT` com substituição completa. Rejeitada por exigir todos
     os campos, inclusive mascarados, e aumentar o risco de apagar dados.

4. **Semântica parcial**: campo ausente (`null`) mantém o valor atual. Nome recebe `trim`
   e exige 1 a 300 caracteres quando informado; e-mail recebe `trim|lower`, precisa ser
   válido e ter até 254 caracteres; telefone recebe `trim` e até 30 caracteres; status
   aceita apenas `ATIVO` ou `INATIVO`. Texto vazio é rejeitado no backend; a interface
   trata campo em branco como "manter", não enviando a chave.

5. **Unicidade de e-mail**: quando o e-mail informado difere do atual, o backend consulta
   `CLIENTE` por `email` e rejeita com `badrequest` se pertencer a outro Cliente. O mesmo
   e-mail do próprio registro é aceito sem conflito. A restrição única da tabela permanece
   como última barreira.

6. **Status**: a transição `ATIVO → INATIVO` e `INATIVO → ATIVO` é permitida e idempotente.
   Inativar não apaga o registro; o login de Cliente já exige `status == "ATIVO"`, então
   novos acessos ficam bloqueados sem afetar pedidos, atendimentos ou endereços existentes.

7. **Resposta**: após `db.transaction` com `db.patch CLIENTE`, a resposta replica o detalhe
   sanitizado: `id`, `nome_completo`, `email_masked`, `telefone_masked`, `status`,
   `created_at` e `cpf_masked`. As máscaras são recalculadas a partir do registro
   atualizado. `updated_at` recebe `now`, mas permanece privado e fora da resposta.

8. **Contrato Python**: adicionar `customer_update_payload(nome_completo, email, telefone,
   current_name)` e `customer_status_payload(status)` a `voltix/internal_customers.py`. A
   resposta usa `customer_record(..., detail=True)`, preservando a validação de campos e
   máscaras já testada.

9. **Interface**: a ficha continua idêntica para `FUNCIONARIO`. Para `ADMINISTRADOR`,
   exibe formulário com nome pré-preenchido e e-mail/telefone vazios com a instrução de
   deixar em branco para manter. A inativação exige uma confirmação em dois passos;
   reativação é direta. Após sucesso, a ficha e a linha da lista são atualizadas e a lista
   é recarregada preservando o detalhe, como em Atendimentos.

10. **Erros**: `400` informa dados inválidos ou e-mail já cadastrado; `404` informa Cliente
    não encontrado; `401`/`403` encerram a sessão interna; demais falhas exibem mensagem
    genérica sem inventar sucesso. `FUNCIONARIO` não envia requisição (defesa em
    profundidade), mas o backend continua sendo a autoridade.

## Risks / Trade-offs

- **Duplicação das máscaras no Xano**: o `PATCH` recalcula e-mail, telefone e CPF
  mascarados; qualquer mudança futura no detalhe precisa ser replicada. Mitigação: manter
  o bloco idêntico ao `customer_id_GET.xs` e validar a resposta pelo mesmo contrato.
- **E-mail mascarado no formulário**: como o detalhe não revela o e-mail atual, o campo
  começa vazio e só é enviado quando preenchido. Mitigação: instrução explícita na UI e
  ausência de alteração quando vazio.
- **Inativação imediata**: o Cliente perde novos logins. Mitigação: confirmação em dois
  passos e mensagem sobre preservação do histórico.
- **Publicação parcial**: o push do Xano emite avisos heurísticos de referências não
  resolvidas. Mitigação: dry-run restrito, publicação somente com autorização e pull de
  verificação.
