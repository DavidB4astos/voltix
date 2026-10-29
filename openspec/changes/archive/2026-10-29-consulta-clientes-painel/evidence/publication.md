# Publicação restrita — 29/10/2026

- Usuário aprovou publicação do grupo e dos dois GETs. Nenhuma nova operação fora desse escopo.
- Dry-run indicou CREATE de Voltix Internal Customers e customers GET / customers/{customer_id} GET.
- Dois retornos HTTP 400 apontaram sintaxe: precondition com múltiplas atribuições em uma linha e else na mesma linha. Blocos normalizados; terceira tentativa publicada com sucesso, três GUIDs sincronizados.
- Comparação de metadados antes/depois: 95 → 98 documentos, apenas três novos no grupo; nenhum existente modificado/removido. Pulls sem registros e sem variáveis de ambiente. Evidência sanitizada em publication-scope.json.
- Testes HTTP reais: lista e detalhe retornaram 401 para requisições anônimas e token inválido. Nenhum corpo de resposta de cliente foi lido ou impresso.
- URLs locais configuradas nos dois nomes aprovados, preservando os demais valores do .env. Nenhum segredo/URL privada persistido em evidências.
- Código publicado recuperado do Xano e promovido para xano/api/internal_customers; candidatos removidos para evitar duplicação.
- **Pendente:** validar Cliente autenticado negado, interno inativo negado e funcionário/administrador ativos permitidos; filtros combinados, máscaras, paginação e fluxo real em contas de teste autorizadas. Não foram inventados resultados positivos.
- 180 testes Python e prévia desktop com fixtures passaram na etapa local anterior. Isso não substitui a validação autenticada no Xano. Change permanece aberta.

## Revalidação local
- OpenSpec strict aprovado novamente e 180 testes Python passaram (TEMP/TMP apontados para pasta de trabalho gravável).
- Sessão real de Funcionário confirmou acesso ao painel; diagnóstico local confirmou execução de search_internal_customers e load_internal_customers, com guarda de autorização positiva.
- Busca sem correspondência exibiu Consulta indisponível. Portanto o fluxo autenticado de consulta ainda não foi aprovado; investigação em andamento, sem registrar token, senha ou corpo de clientes.
- Diagnóstico executado fora do repositório, sem mudar comportamento de negócio; nenhuma evidência de erro foi tratada como sucesso.

## Correção e primeira validação autenticada
- Diagnóstico sanitizado identificou HTTP 500 ERROR_FATAL: Unable to locate var: page.items.
- Causa: output da db.query paginada selecionava campos no nível raiz; ajustado para items.id/items.nome_completo/items.email/items.telefone/items.status/items.created_at, preservando itemsTotal e pageTotal.
- Dry-run limitado a customers_GET.xs mostrou somente um UPDATE; publicação do único documento concluída com sucesso.
- Funcionário ATIVO: busca por termo sintético sem correspondência retornou objeto com os cinco campos do contrato e a UI exibiu estado vazio, sem erro. Repetido com status ATIVO, TODOS e INATIVO.
- Evidência recortada somente no painel, sem identidade da conta, senha, token ou clientes. Essa busca vazia não comprova máscaras de registros, paginação com resultados, detalhe nem permissão de Administrador/Cliente/inativo; continuam pendentes.

## Administrador
- Usuário realizou logout de Funcionário e login com Administrador de teste. A UI confirmou ADMINISTRADOR; painel iniciou sem estado vazio herdado da conta anterior.
- Busca pelo mesmo termo sintético sem correspondência retornou estado vazio correto, sem Consulta indisponível.
- Evidência administrador-busca-vazia.png contém somente o painel de consulta. Permissões positivas de lista confirmadas para os dois perfis; testes com registros fictícios/detalhe e permissões negativas autenticadas continuam pendentes.

## Cliente fictício confirmado pelo usuário
- Usuário confirmou explicitamente David como cadastro fictício autorizado para a validação.
- Na sessão ADMINISTRADOR, busca david já apresentava dois resultados; seleção do registro correspondente a David abriu detalhe com sucesso.
- E-mail tes***** e telefone ***** apresentados protegidos; CPF sem valor. Não houve exposição de contatos completos, token ou credenciais no painel.
- Fechar detalhes funcionou. Busca DAVID manteve dois resultados, verificando insensibilidade a maiúsculas para esse termo.
- Limite: telefone longo e CPF válido não foram comprovados nesse cadastro; paginação com mais de uma página e permissões negativas autenticadas continuam pendentes.
- Pendências visuais identificadas no detalhe: CPF ausente fica em branco; created_at é exibido como timestamp numérico, sem formatação amigável. Não tratar a change como encerrada antes de revisar esses pontos.

## Refinamento do detalhe concluído
- Campos de contato ausentes agora mostram Não informado; máscaras de valores presentes foram preservadas.
- Cadastro formatado a partir do timestamp Xano em milissegundos, com fuso UTC explícito; datas ISO com offset também são normalizadas. Valor bruto preservado no DTO, apresentação em campo separado.
- 182 testes Python passaram, incluindo equivalência entre timestamp/ISO e fallback de datas inutilizáveis. Aplicação compilou 100%.
- Verificação na sessão de Administrador com David fictício confirmou CPF: Não informado e Cadastro: 15/10/2026 às 12:33 (UTC).
- Mantidas as pendências de permissões negativas autenticadas, paginação multipágina e máscaras com telefone longo/CPF válido; não arquivar prematuramente.

## Paginação real e limites de autorização
- Sessão Administrador ativa confirmada pelo usuário e pela UI. Verificação temporária local, fora do repositório, enviou GETs ao Xano com a sessão server-side existente, sem registrar credenciais nem payloads.
- Busca david, status ATIVO, per_page=1, páginas 1/2/3/1: tamanhos 1/1/0/1, total_items=2 e total_pages=2 em todas. Primeiras duas páginas com IDs distintos e primeira página repetida estável. Contrato estrito validado em cada retorno. Evidência sanitizada pagination-runtime.json, sem IDs/contatos.
- Na interface padrão de 20 itens, os dois resultados aparecem sem erro, detalhe anterior limpo e botões anterior/próxima desabilitados corretamente por haver apenas uma página. A navegação visual multipágina com mais de 20 registros não foi exercitada.
- Observados retornos 403 no login interno na tentativa que o usuário identificou como conta inativa; não houve token para validar autorização dos dois GETs nesse contexto. Não confundir recusa no login com comprovação do bloqueio em endpoint.
- Login interno ativo subsequente: GET de lista 200 e detalhe de ID inexistente 404. Nenhum registro alterado.
- Usuário informou que a conta de Cliente está indisponível agora; suas tentativas de login deram 403 e não produziram sessão para o teste de token de Cliente. Permanecem pendentes Cliente autenticado/ID coincidente e sessão interna inativa nos dois endpoints. Change continua aberta.

## Cliente autenticado negado — confirmado
- Usuário informou login de Cliente concluído. O verificador temporário recebeu a resposta de login com authToken em memória e usou essa sessão somente nos dois GETs internos aprovados.
- GET lista: 401. GET detalhe de ID inexistente: 401, sem revelar existência de registro. Nenhum token, senha, identificador de sessão ou corpo de cliente foi persistido na evidência.
- Evidência sanitizada customer-session-denied.json. Esse teste comprova a rejeição da sessão de Cliente utilizada; não foi verificada coincidência de ID com usuário interno nem foi criada/alterada conta para produzir essa condição.
- Não houve alteração de código, backend ou registros nesta etapa. Continua pendente a validação com sessão interna inativa e o cenário específico de ID coincidente; change permanece aberta.

## Sessão interna inativa — teste automático aprovado
- Usuário confirmou autenticação da conta fictícia autorizada. Sessão inicialmente ativa: lista sem correspondência 200 e detalhe de ID inexistente 404.
- Atualização parcial limitada ao status de user registro 5, Usuario Funcionario Teste; INATIVO confirmado por releitura.
- A mesma sessão já emitida recebeu 403 na lista e 403 no detalhe. Isso verifica o bloqueio no endpoint após inativação, independentemente do login.
- Bloco finally restaurou ATIVO; releitura e impressão dos demais campos confirmaram restauração e ausência de outras alterações. Diário local marcou needs_restore=false. Proteção independente de restauração também estava preparada.
- Evidência inactive-session-denied.json contém apenas códigos de status e confirmações; nenhum token, senha ou conteúdo privado.
- Pendência específica de autorização ainda não comprovada: Cliente com ID coincidente ao de usuário interno. A rejeição da sessão de Cliente disponível já foi comprovada, mas a coincidência dos IDs não foi medida. Não marcar 2.3 como integralmente concluída nem arquivar por inferência.

## Cenário de ID coincidente — aprovado
- Sessão existente de Cliente revalidada pelo endpoint de identidade, sem novo cadastro ou mudança de status.
- O ID retornado foi comparado em memória com o registro de mesmo número na tabela interna user via Metadata API somente leitura. Confirmada existência e perfil interno válido; somente booleanos persistidos.
- A mesma sessão de Cliente recebeu 401 nos GETs de lista e detalhe. Nenhum token ou ID foi persistido nessa evidência.
- customer-id-collision.json encerra a pendência específica dos relatórios anteriores.
- Revisão final: 182 testes passaram em 29/10/2026; conta temporariamente inativada está restaurada ATIVO e sem outros campos alterados. A execução temporária de alterações de status foi desativada no verificador após aprovação do teste, evitando repetição em novo login.
