## ADDED Requirements

### Requirement: Public catalog reuses recently loaded data

O carregamento do catálogo público SHALL reutilizar, por um curto período de expiração, os dados já obtidos (categorias e produtos com a respectiva imagem resolvida). Dentro desse período, navegar entre a Home e o Catálogo SHALL NOT emitir novas requisições ao Xano. Após a expiração, o próximo carregamento SHALL consultar o Xano novamente. A reutilização SHALL respeitar a seleção de categoria vigente e SHALL NOT alterar o formato das requisições nem os contratos dos endpoints públicos.

#### Scenario: Navigation within the reuse period reuses data
- **WHEN** o visitante carrega a Home ou o Catálogo e, dentro do período de expiração, navega para a outra página
- **THEN** o catálogo apresenta os mesmos dados sem emitir novas requisições ao Xano

#### Scenario: Data is refreshed after expiration
- **WHEN** o período de expiração termina e o catálogo é carregado novamente
- **THEN** o sistema consulta o Xano novamente e apresenta os dados atualizados

#### Scenario: Reuse respects the selected category
- **WHEN** o visitante seleciona uma categoria diferente da anterior
- **THEN** o sistema obtém os produtos correspondentes à categoria selecionada, sem reutilizar dados de uma seleção diferente

### Requirement: Public catalog prevents concurrent duplicate loads

Enquanto um carregamento do catálogo público estiver em andamento, novas solicitações de carregamento SHALL NOT disparar consultas duplicadas ao Xano; as solicitações concorrentes SHALL aguardar ou reutilizar o resultado do carregamento em andamento.

#### Scenario: Concurrent loads issue a single set of requests
- **WHEN** dois carregamentos do catálogo público são solicitados simultaneamente
- **THEN** apenas um conjunto de requisições é enviado ao Xano e ambos os carregamentos recebem o mesmo resultado

### Requirement: Public catalog respects Xano rate limiting

Ao receber HTTP 429 do Xano, o sistema SHALL aguardar conforme o cabeçalho `Retry-After` (ou um intervalo padrão quando ausente) e SHALL repetir a requisição por um número limitado de tentativas. Esgotadas as tentativas, a falha SHALL permanecer observável e nova tentativa SHALL ser possível. O sistema SHALL respeitar o limite do plano gratuito do Xano sem exigir mudança de plano e SHALL NOT simular sucesso.

#### Scenario: Transient rate limit is retried and succeeds
- **WHEN** o Xano responde HTTP 429 com `Retry-After` e uma tentativa seguinte retorna sucesso
- **THEN** o catálogo carrega os dados normalmente, sem apresentar falha ao visitante

#### Scenario: Retry-After interval is respected
- **WHEN** o Xano responde HTTP 429 informando um intervalo em `Retry-After`
- **THEN** o sistema aguarda aproximadamente esse intervalo antes de repetir a requisição

#### Scenario: Persistent rate limit remains observable
- **WHEN** o Xano continua respondendo HTTP 429 após o número máximo de tentativas
- **THEN** a interface informa que o catálogo não pôde ser carregado e permite nova tentativa

### Requirement: Public catalog failures are logged without exposing sensitive data

Falhas de carregamento do catálogo público SHALL ser registradas no backend com informação suficiente para diagnóstico (por exemplo, o endpoint lógico e o status HTTP). Os registros SHALL NOT conter credenciais, tokens, URLs completas com parâmetros sensíveis nem o caminho privado de armazenamento da imagem.

#### Scenario: Failure is recorded for diagnosis
- **WHEN** uma consulta do catálogo público falha após o tratamento de erros
- **THEN** o backend produz um registro de log identificando a causa/status e o endpoint lógico da falha

#### Scenario: Sensitive data is not logged
- **WHEN** um registro de falha é produzido
- **THEN** ele não contém credenciais, tokens, o caminho privado da imagem nem URLs completas com parâmetros sensíveis

## MODIFIED Requirements

### Requirement: Public catalog failures remain observable
Uma falha de rede, erro HTTP ou resposta inválida SHALL ser apresentada como falha de carregamento, sem dados ou sucesso simulados, e SHALL permitir nova tentativa quando aplicável. Falhas transitórias de limite de taxa (HTTP 429) SHALL ser tratadas com nova tentativa limitada, respeitando `Retry-After`, antes de reportar a falha ao visitante.

#### Scenario: Catalog request fails
- **WHEN** a consulta pública falha por indisponibilidade, erro HTTP ou resposta inválida
- **THEN** a interface informa que o catálogo não pôde ser carregado e não apresenta os dados da tentativa como resultado confirmado

#### Scenario: Transient rate limit is retried before reporting failure
- **WHEN** o Xano responde HTTP 429 de forma transitória
- **THEN** o sistema repete a requisição respeitando `Retry-After` e só reporta a falha se as tentativas se esgotarem
