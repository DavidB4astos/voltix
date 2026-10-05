## Context

A aplicação Reflex já autentica `UsuarioInterno` pelo State e usa chamadas HTTP server-side para Xano. A área interna geral permite os dois perfis ativos, enquanto os recursos Xano atuais não incluem tabelas ou operações para Categoria e Marca. Esta Change precisa aplicar autorização mais restrita sem alterar o contrato de acesso interno existente.

## Goals / Non-Goals

**Goals:**

- Reutilizar a sessão interna existente e autorizar cada operação de gestão no Xano.
- Manter listas e formulários no Reflex, com o State como único intermediário HTTP entre interface e backend.
- Garantir unicidade no backend e preservar registros inativos.

**Non-Goals:**

- Criar ou relacionar Produtos e VariacoesProduto.
- Alterar a autorização da área interna geral ou implementar permissões administrativas além de categorias e marcas.
- Criar um dashboard, catálogo público, pesquisa ou exclusão definitiva.

## Decisions

### Persistir Categoria e Marca separadamente no Xano

Criar uma estrutura Xano para cada entidade, contendo nome obrigatório, descrição opcional, status `ATIVO`/`INATIVO` e os campos de auditoria gerenciados pelo Xano. Novos registros começam ativos. A unicidade do nome será protegida pelo backend e pela persistência, abrangendo também registros inativos; ao editar, o próprio registro não será tratado como duplicata.

Uma entidade genérica compartilhada foi descartada porque Categoria e Marca são conceitos separados no Domain Model e podem evoluir independentemente. Relações com Produto não serão criadas nesta Change, pois Produto está fora do escopo.

### Aplicar autorização específica nos endpoints de gestão

Cada operação Xano exigirá autenticação e consultará o usuário associado à sessão, autorizando somente `role = ADMINISTRADOR` e `status = ATIVO`. Essa verificação será aplicada também em listagem, além de criação, edição e mudança de status. O endpoint geral de acesso interno não será ampliado nem modificado para essa permissão; `FUNCIONARIO` continuará podendo acessar a área interna geral, mas não os dados ou operações desta gestão.

Esconder os controles na interface para outros perfis melhora a experiência, mas não constitui controle de segurança. Uma alternativa baseada somente em condições do Reflex foi descartada por permitir chamadas diretas aos endpoints sem autorização.

### Mediar as chamadas Xano pelo State Reflex

A interface acionará eventos do State; o State fará as requisições HTTP server-side aos endpoints Xano e enviará o token de sessão em `Authorization`. O token permanece em `_auth_token` backend-only e não fará parte de valores públicos da interface. Dados de formulários e respostas incluirão somente os campos necessários para Categoria ou Marca.

Não serão adicionadas bibliotecas ou chamadas HTTP executadas diretamente no navegador. O tratamento de falhas distinguirá validação, autorização e indisponibilidade, sem representar falha como sucesso.

### Integrar a gestão à área interna sem criar dashboard

Os controles de categorias e marcas serão apresentados dentro da área interna existente somente quando o usuário autenticado tiver perfil `ADMINISTRADOR`. Cada seção permitirá listar os dois status, criar, editar e alternar o status, incluindo reativação. Não haverá ação de exclusão definitiva; erro de persistência deve preservar a lista e o registro anterior até nova consulta confirmada.

## Risks / Trade-offs

- [O endpoint de autenticação atual aceita ambos os perfis para a área interna geral] -> Aplicar a verificação de `ADMINISTRADOR` em cada endpoint de gestão e testar chamadas diretas autenticadas como `FUNCIONARIO`.
- [Um token pode continuar válido após a inativação do usuário] -> Revalidar role e status no backend em toda operação de gestão.
- [Uma validação apenas na interface pode deixar dados acessíveis] -> Não retornar dados nem alterar registros antes da autorização Xano.
- [Nomes duplicados podem surgir em operações concorrentes] -> Aplicar unicidade na persistência e tratar conflitos no backend como falha observável.
- [Categoria e Marca pertencem a um domínio que futuramente se relacionará a Produto] -> Manter as entidades sem relações de produto nesta Change; uma mudança futura definirá a associação e o tratamento de registros já utilizados.
- [As alterações nos arquivos de lock já presentes no working tree são alheias a esta Change] -> Preservá-las sem incluí-las ou modificá-las durante implementação futura desta Change.

## Migration Plan

1. Criar as estruturas Xano de Categoria e Marca sem alterar tabelas existentes de usuário ou cliente.
2. Criar as operações Xano protegidas por sessão e perfil, com validação de campos, status e unicidade.
3. Implementar no State as chamadas server-side e conectar a interface administrativa mínima.
4. Validar autorização negativa/positiva, operações de dados e cenários de erro antes de considerar a Change concluída.
5. Em rollback, desabilitar os endpoints e remover a interface associada; preservar quaisquer registros de Categoria ou Marca já criados, sem exclusão automática de dados.

## Open Questions

Nenhuma.
