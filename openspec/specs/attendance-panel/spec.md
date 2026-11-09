# attendance-panel Specification

## Purpose
Definir a seção desktop de Atendimentos do painel interno, que permite a usuários internos
ativos listar, criar, consultar, editar e transicionar Atendimentos, respeitando os vínculos,
os estados e a autorização publicados na capability `attendance-management`, sem expor dados
pessoais do Cliente.

## Requirements

### Requirement: Attendance panel is restricted to active internal users

A seção Atendimentos SHALL ser apresentada somente dentro de uma sessão interna validada de
UsuarioInterno `ATIVO` com papel `FUNCIONARIO` ou `ADMINISTRADOR`. Visitantes, Clientes e
usuários internos `INATIVO` SHALL NOT visualizar ou operar a seção. A autorização do backend
SHALL permanecer autoritativa, e uma resposta `401` SHALL encerrar a apresentação da seção,
limpar os dados carregados e devolver a superfície de acesso interno. Uma resposta `403` em
leitura, criação ou edição SHALL ter o mesmo efeito; em transição de status, `403` representa
operação negada e SHALL manter a sessão e o registro, apenas informando a negativa.

#### Scenario: Active employee opens the panel

- **WHEN** um FUNCIONARIO ativo seleciona a seção Atendimentos
- **THEN** a seção é apresentada com a listagem pronta para consulta, sem outras seções internas

#### Scenario: Unauthorized session loses the panel

- **WHEN** o backend responde `401` a qualquer operação de Atendimento, ou `403` a uma leitura, criação ou edição
- **THEN** a tela limpa listagem, detalhe, filtros e mensagens e retorna à superfície de acesso interno

#### Scenario: Status operation denied keeps the session

- **WHEN** o backend responde `403` a uma transição de status
- **THEN** a tela mantém a sessão, o status anterior e mostra que a operação não é permitida

### Requirement: Attendance listing supports filters and pagination

A seção SHALL listar Atendimentos com filtros opcionais por `cliente_id` (inteiro positivo) e
`status` (`TODOS`, `ABERTO`, `EM_ATENDIMENTO`, `FINALIZADO` ou `CANCELADO`), com 20 itens por
página e navegação anterior/próxima. A resposta SHALL conter exatamente `items`, `page`,
`per_page`, `total_items` e `total_pages`, e cada item SHALL conter exatamente `id`,
`cliente_id`, `usuario_interno_id`, `pedido_id`, `assunto`, `descricao`, `status`,
`data_atendimento`, `created_at` e `updated_at`. A tela SHALL exibir o total e a página atual,
aplicar filtros válidos reiniciando na página 1 e rejeitar filtros inválidos com mensagem
local, sem enviar requisição. Respostas com campos extras, tipos inválidos, status
desconhecido ou totais inconsistentes SHALL ser rejeitadas com mensagem de erro.

#### Scenario: Filter by customer and status

- **WHEN** o usuário informa um `cliente_id` válido e `status=EM_ATENDIMENTO` e aplica os filtros
- **THEN** a tela carrega a primeira página apenas com os Atendimentos correspondentes e atualiza o total

#### Scenario: Invalid filter is not sent

- **WHEN** o usuário informa um `cliente_id` menor que 1 ou um status fora do conjunto aceito
- **THEN** a tela mostra uma mensagem de filtros inválidos e não executa a consulta

#### Scenario: Empty listing

- **WHEN** a consulta retorna `items=[]` e `total_items=0`
- **THEN** a tela mostra um estado vazio com a opção de ajustar os filtros, sem erro genérico

#### Scenario: Pagination metadata

- **WHEN** a resposta indica `page=2` e `total_pages=3`
- **THEN** a tela mostra "Página 2 de 3" e habilita apenas a navegação permitida

### Requirement: Creation uses the authenticated internal user as responsible

A seção SHALL oferecer criação de Atendimento com `cliente_id` obrigatório, `pedido_id`
opcional, `assunto` de 1 a 200 caracteres, `descricao` de 1 a 2000 caracteres e
`data_atendimento` opcional. A tela SHALL NOT enviar `usuario_interno_id` nem `status`; o
backend cria o registro como `ABERTO` e responsável igual ao interno autenticado. Em sucesso,
a tela SHALL limpar o formulário, atualizar a listagem e apresentar o Atendimento criado. Em
`notfound`, `badrequest` ou `inputerror`, a tela SHALL mostrar mensagem específica e preservar
os valores digitados.

#### Scenario: Create a general attendance

- **WHEN** o usuário informa um `cliente_id` existente, assunto e descrição e envia o formulário
- **THEN** a tela cria o Atendimento `ABERTO`, limpa o formulário e mostra o registro na listagem

#### Scenario: Reject order from another customer

- **WHEN** o `pedido_id` informado pertence a outro Cliente
- **THEN** a tela mostra que o Pedido não pertence ao Cliente e mantém os valores do formulário

#### Scenario: Invalid local input

- **WHEN** o assunto ou a descrição estão vazios ou excedem o limite permitido
- **THEN** a tela impede o envio e indica o campo inválido, sem chamar o backend

### Requirement: Attendance detail and editing respect status and links

A seção SHALL abrir o detalhe de um Atendimento consultando o endpoint publicado e exibir
`id`, `cliente_id`, `usuario_interno_id`, `pedido_id`, `assunto`, `descricao`, `status`,
`data_atendimento`, `created_at` e `updated_at`. A edição SHALL permitir alterar somente
`assunto`, `descricao` e `data_atendimento` e SHALL estar disponível apenas para Atendimentos
em `ABERTO` ou `EM_ATENDIMENTO`. Os vínculos `cliente_id`, `usuario_interno_id` e `pedido_id`
SHALL ser apresentados como imutáveis e SHALL NOT ser enviados em edição. Em sucesso, a tela
SHALL atualizar o detalhe e a listagem. Em `notfound`, a tela SHALL remover o detalhe e
mostrar que o Atendimento não existe; em `badrequest` para registro encerrado, a tela SHALL
manter o detalhe somente leitura e informar a imutabilidade.

#### Scenario: Edit an open attendance

- **WHEN** o usuário altera assunto ou descrição de um Atendimento `ABERTO` e salva
- **THEN** a tela envia apenas os campos editáveis e mostra os valores atualizados

#### Scenario: Closed attendance is read-only

- **WHEN** o detalhe pertence a um Atendimento `FINALIZADO` ou `CANCELADO`
- **THEN** a tela não oferece controles de edição e informa que o registro é histórico

#### Scenario: Missing attendance

- **WHEN** o detalhe responde `notfound`
- **THEN** a tela fecha o detalhe e mostra a mensagem de Atendimento não encontrado

### Requirement: Status controls reflect the published transition rules

A seção SHALL oferecer `EM_ATENDIMENTO` somente para Atendimentos `ABERTO`, e `FINALIZADO`
ou `CANCELADO` somente para Atendimentos `ABERTO` ou `EM_ATENDIMENTO`. Os controles de
finalizar e cancelar SHALL ser apresentados apenas ao UsuarioInterno responsável ou a um
`ADMINISTRADOR`, usando a identidade e o papel da sessão atual como indicação visual; o
backend SHALL permanecer a autoridade final. Repetir o status atual SHALL ser apresentado
como operação idempotente sem escrita. Em sucesso, a tela SHALL atualizar o detalhe e a
listagem; em `accessdenied` ou `badrequest`, SHALL manter o estado anterior e mostrar a
mensagem correspondente.

#### Scenario: Any employee starts an attendance

- **WHEN** um funcionário autorizado aciona "Iniciar atendimento" em um registro `ABERTO`
- **THEN** a tela envia `EM_ATENDIMENTO` e atualiza o status apresentado

#### Scenario: Responsible finishes an attendance

- **WHEN** o responsável aciona "Finalizar" em um registro `ABERTO` ou `EM_ATENDIMENTO`
- **THEN** a tela envia `FINALIZADO` e passa a apresentar o registro como imutável

#### Scenario: Non-responsible employee has no finish control

- **WHEN** um FUNCIONARIO que não é o responsável abre um Atendimento
- **THEN** a tela não oferece finalizar ou cancelar e mantém as demais ações permitidas

#### Scenario: Administrator cancels an attendance

- **WHEN** um ADMINISTRADOR aciona "Cancelar" em um registro `ABERTO` ou `EM_ATENDIMENTO`
- **THEN** a tela envia `CANCELADO` e atualiza o detalhe

#### Scenario: Invalid transition is rejected

- **WHEN** o backend responde `badrequest` a uma transição
- **THEN** a tela mantém o status anterior e informa que a transição não é permitida

### Requirement: Panel handles loading, stale responses and errors safely

A seção SHALL apresentar estados distintos de carregamento, vazio, erro e sessão não
autorizada, com mensagens em português e sem expor payload bruto, tokens ou credenciais ao
navegador. Requisições SHALL ocorrer no servidor com o token interno. A tela SHALL descartar
respostas cuja sessão, filtros, página ou Atendimento selecionado não sejam mais os atuais.
Falhas de rede, `429`, `500` ou respostas inválidas SHALL mostrar mensagem genérica e
permitir nova tentativa, mantendo o backend como fonte de verdade.

#### Scenario: Stale response is discarded

- **WHEN** uma resposta de listagem chega após o usuário trocar o filtro ou a página
- **THEN** a tela ignora a resposta obsoleta e mantém o estado do filtro atual

#### Scenario: Session expires

- **WHEN** uma requisição responde `401`, ou `403` em leitura/criação/edição
- **THEN** a tela limpa os dados do Atendimento e retorna ao acesso interno

### Requirement: Panel is accessible and exposes no personal customer data

A seção SHALL usar rótulos associados aos campos, nome acessível nos controles, foco visível,
status comunicado programaticamente e mensagens em `role=status`. O Cliente SHALL ser
identificado apenas por `cliente_id`; nome, e-mail, CPF, telefone, endereço, senha ou token
SHALL NOT ser exibidos ou inventados pela tela.

#### Scenario: Keyboard and assistive access

- **WHEN** o usuário navega por teclado ou leitor de tela pela seção
- **THEN** campos, botões, estados de carregamento e mensagens são anunciados corretamente

#### Scenario: No personal customer data

- **WHEN** qualquer Atendimento é listado ou detalhado
- **THEN** o Cliente aparece somente como `cliente_id`, sem dados pessoais
