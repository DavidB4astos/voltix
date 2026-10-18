# product-bulk-import Specification

## Purpose
Define o comportamento da importação administrativa em massa de Produtos e variações a partir de arquivos CSV/XLSX, incluindo validação, pré-visualização, política de duplicidade e processamento em lotes, sem alterar as regras de `product-management`.

## Requirements

### Requirement: Administrators can validate and preview a bulk import file

O sistema SHALL permitir que um `UsuarioInterno` autenticado, ativo e com perfil `ADMINISTRADOR` envie um arquivo `.csv` ou `.xlsx` e obtenha uma pré-visualização com o resultado de cada linha antes de qualquer gravação. A pré-visualização SHALL identificar, no mínimo, linhas válidas, linhas com erro e seu motivo, e linhas duplicadas. Nenhum Produto ou variação SHALL ser persistido antes da confirmação explícita do administrador.

#### Scenario: Administrator previews a valid file
- **WHEN** um administrador envia um arquivo com todas as linhas válidas
- **THEN** o sistema exibe a pré-visualização com cada linha marcada como válida e habilita a confirmação

#### Scenario: Nothing is persisted before confirmation
- **WHEN** um administrador envia um arquivo e apenas visualiza o resultado
- **THEN** o sistema não cria nem altera nenhum Produto ou variação

#### Scenario: Unsupported file is rejected
- **WHEN** um administrador envia um arquivo com extensão diferente de `.csv` ou `.xlsx`, ou um arquivo que não pode ser parseado
- **THEN** o sistema informa a falha e não apresenta pré-visualização

#### Scenario: Confirmation is unavailable without valid rows
- **WHEN** a pré-visualização não contém nenhuma linha válida
- **THEN** o sistema mantém a confirmação indisponível

### Requirement: Bulk import rows satisfy catalog and domain rules before confirmation

O sistema SHALL validar cada linha antes da confirmação conforme as regras existentes do domínio: campos obrigatórios (`produto_nome`, `categoria_nome`, `marca_nome`, `variacao_nome`, `sku`, `preco`, `quantidade_disponivel`), preço finito maior que zero, quantidade inteira maior ou igual a zero, Categoria e Marca existentes e com status `ATIVO`, SKU obrigatório e único inclusive contra variações inativas, e agrupamento consistente das linhas do mesmo Produto. Cada linha rejeitada SHALL receber um motivo específico na pré-visualização.

#### Scenario: Missing required field is reported per line
- **WHEN** uma linha não possui um campo obrigatório preenchido
- **THEN** o sistema marca a linha como erro na pré-visualização indicando o campo e não a inclui no processamento

#### Scenario: Invalid price or quantity is reported per line
- **WHEN** uma linha informa preço menor ou igual a zero, preço não numérico ou quantidade negativa, fracionária ou não numérica
- **THEN** o sistema marca a linha como erro e não a inclui no processamento

#### Scenario: Unknown or inactive category or brand is reported per line
- **WHEN** uma linha referencia uma Categoria ou Marca inexistente no catálogo ou com status `INATIVO`
- **THEN** o sistema marca a linha como erro e não a cria

#### Scenario: SKU duplicated in the file is reported
- **WHEN** duas linhas do mesmo arquivo informam o mesmo SKU
- **THEN** o sistema mantém apenas a primeira ocorrência como válida e marca as demais como erro de SKU duplicado

#### Scenario: Inconsistent grouping of the same product is reported
- **WHEN** linhas com o mesmo `produto_nome` divergem em descrição, especificações, Categoria ou Marca
- **THEN** o sistema marca as linhas conflitantes como erro de agrupamento

### Requirement: Existing products are never overwritten by an import

O sistema SHALL tratar como duplicidade, sem sobrescrever, atualizar ou reativar dados, todo Produto já existente com o mesmo nome (após remoção de espaços) e toda variação cujo SKU já exista em qualquer status. Registros duplicados SHALL aparecer na pré-visualização e no relatório final como pulados, e a reexecução do mesmo arquivo SHALL processar apenas o que ainda não foi criado.

#### Scenario: Existing product name is skipped
- **WHEN** o arquivo contém um Produto cujo nome já existe no catálogo
- **THEN** o sistema marca o grupo como duplicado, não altera o Produto existente e não cria suas variações

#### Scenario: Existing SKU is rejected
- **WHEN** o arquivo contém um SKU já utilizado por qualquer variação existente, inclusive inativa
- **THEN** o sistema marca a linha como erro de duplicidade e não a cria

#### Scenario: Re-running the same file resumes the import
- **WHEN** uma importação falha parcialmente e o mesmo arquivo é enviado novamente após as correções
- **THEN** o sistema pula os registros já criados e processa apenas os que faltam

### Requirement: Confirmed imports create products through authorized backend operations in rate-limit-compatible batches

O sistema SHALL processar a importação confirmada produto a produto, reutilizando as operações de criação existentes, respeitando o limite de requisições do ambiente (10 req / 20 s) com espaçamento entre requisições e nova tentativa com espera diante de resposta de limite de requisições. Todo Produto e variação criados pela importação SHALL iniciar com status `ATIVO`. A autorização de toda gravação SHALL continuar sendo validada no backend (sessão válida, usuário `ATIVO`, perfil `ADMINISTRADOR`).

#### Scenario: Confirmed import creates products with variations
- **WHEN** um administrador confirma um arquivo com linhas válidas
- **THEN** o sistema cria cada Produto com suas variações, todos ativos, e informa o progresso

#### Scenario: Rate limit responses are retried with wait
- **WHEN** uma requisição de gravação é rejeitada por limite de requisições
- **THEN** o sistema espera o intervalo de nova tentativa e retoma, sem reportar sucesso

#### Scenario: Unauthorized caller cannot import
- **WHEN** um `FUNCIONARIO`, usuário inativo ou chamador sem sessão tenta confirmar uma importação
- **THEN** o backend rejeita as gravações e nenhum Produto ou variação é criado

#### Scenario: Import controls are shown only to administrators
- **WHEN** um usuário interno sem perfil `ADMINISTRADOR` acessa a área interna
- **THEN** a interface não apresenta os controles de importação

### Requirement: Partial import failures remain observable and resumable

O sistema SHALL processar os grupos válidos mesmo diante de falhas individuais e SHALL apresentar, ao final, um relatório por grupo com o resultado `CRIADO`, `PULADO` ou `FALHA` e a mensagem de erro quando aplicável. O administrador SHALL poder cancelar o processamento em andamento. Nenhuma falha SHALL ser reportada como sucesso, e falhas parciais não podem deixar um Produto persistido sem variação.

#### Scenario: One group fails while others are processed
- **WHEN** a gravação de um grupo falha por validação do backend, rede ou limite de requisições
- **THEN** o sistema registra a falha daquele grupo, continua os demais e inclui a falha no relatório final

#### Scenario: Administrator cancels an import in progress
- **WHEN** um administrador cancela a importação durante o processamento
- **THEN** o sistema interrompe novas gravações e exibe o relatório parcial com o que já foi criado

#### Scenario: Session loss during import is observable
- **WHEN** a sessão expira durante o processamento
- **THEN** o sistema interrompe as gravações, informa a falha de autorização e não apresenta sucesso
