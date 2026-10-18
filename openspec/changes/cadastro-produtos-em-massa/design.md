## Context

A área interna já gestiona Produto e VariacaoProduto um a um (Change `gestao-produtos`, endpoints publicados no Xano e sincronizados no `.env`). O fluxo atual cria um Produto com uma ou mais variações por requisição `POST` ao endpoint de Produto, com autorização `ADMINISTRADOR` + `ATIVO` validada no backend. Categoria e Marca são referenciadas por id e já possuem listagens administrativas protegidas. O plano Xano Free limita a 10 requisições por 20 s (`ERROR_CODE_TOO_MANY_REQUESTS`), já registrado no roadmap (E5) e mitigado na leitura pública com cache e backoff. O State mantém o token apenas no servidor e faz as chamadas HTTP em Python.

## Goals / Non-Goals

**Goals:**

- Cadastrar em lote Produtos válidos com suas variações, reutilizando o agregado e as regras já estabelecidas por `product-management`.
- Detectar e relatar todos os problemas de dados **antes** de qualquer gravação, com pré-visualização linha a linha.
- Nunca sobrescrever dados já persistidos; permitir reexecução segura do mesmo arquivo após falhas parciais.
- Operar dentro do limite de 10 req / 20 s do Xano Free, com progresso e cancelamento observáveis.

**Non-Goals:**

- Imagem de Produto (upload, galeria ou associação) em qualquer etapa da importação.
- Atualização, edição ou sobrescrita de Produtos ou variações existentes; exclusão de registros.
- Criação de Categorias ou Marcas pela planilha; a planilha apenas referencia por nome registros já existentes.
- Novo endpoint Xano de importação em lote, autenticação própria da importação, agendamento automático ou importação por URL remota.

## Decisions

### Planilha com uma linha por variação e agrupamento por nome de Produto

Colunas, nesta ordem e com estes cabeçalhos exatos: `produto_nome`, `produto_descricao`, `produto_especificacoes_tecnicas`, `categoria_nome`, `marca_nome`, `variacao_nome`, `sku`, `preco`, `quantidade_disponivel`. Descrição e especificações são opcionais; os demais campos são obrigatórios por linha. Linhas com o mesmo `produto_nome` (após `strip`) formam um único Produto, cuja descrição e especificações devem ser idênticas em todas as linhas do grupo; divergência é erro de agrupamento. O mesmo vale para `categoria_nome`/`marca_nome` dentro do grupo. Agrupar por nome foi escolhido porque a planilha não tem como referenciar ids internos; o Domain Model não torna o nome de Produto único, então a unicidade por nome é uma **regra do arquivo, não do domínio**, e vale apenas para o conteúdo de uma importação. Como nova Categoria ou Marca não é permitida, a validação usa a semântica de "exatamente igual após `strip`" contra os registros existentes.

### CSV e XLSX sem novas dependências

CSV: UTF-8 com ou sem BOM, delimitador detectado entre `;` e `,` (`csv.Sniffer` com fallback determinístico), aspas conforme `csv` da biblioteca padrão. XLSX: leitor mínimo baseado em `zipfile` + `xml.etree` da biblioteca padrão, restrito à primeira planilha do arquivo, aceitando células de texto compartilhado (`sharedStrings`), texto inline e números; fórmulas, datas, estilos, macros e arquivos `.xls` (formato binário legado) são rejeitados com erro explícito. Números e preços aceitam notação com `.` ou `,` decimal, normalizados antes da validação. Aceitar `.xlsx` sem `openpyxl` evita uma dependência nova num projeto que hoje só usa biblioteca padrão; a alternativa `openpyxl` foi rejeitada por exigir aprovação prévia de dependência e por ser desnecessária para leitura de uma planilha simples. Extensões aceitas: `.csv` e `.xlsx`; qualquer outra é rejeitada antes do parse.

### Quantidade inteira e preço positivo

`quantidade_disponivel` deve ser um inteiro maior ou igual a zero e `preco` um número finito maior que zero, com no máximo duas casas decimais. Exigir inteiro para quantidade é mais estrito que o formulário individual atual (que usa leitura decimal), mas está alinhado à regra de estoque inteiro ≥ 0 registrada no roadmap (C1) e é a regra adotada por esta Change; o formulário individual permanece com leitura decimal. Valores negativos, fracionários ou não numéricos são erro de linha.

### Fluxo em duas fases: pré-visualização e depois confirmação

Fase 1 (sem gravação): o arquivo é enviado pela interface, lido no State, parseado e validado; o resultado é uma pré-visualização com todas as linhas e seu status (`VÁLIDA`, `ERRO` com motivo, `DUPLICADA`). A confirmação fica indisponível se não houver nenhuma linha válida. Fase 2 (gravação): somente após confirmação explícita o administrador inicia a importação, que percorre os grupos válidos. A validação prévia é usada para usabilidade; o backend continua sendo a autoridade final de todas as regras no momento da escrita.

### Importação reutiliza o `POST products` existente, um Produto por requisição

A importação confirmada executa um `POST` por grupo de Produto (agregado com suas variações), reutilizando o contrato já publicado pela Change `gestao-produtos` e o helper de requisição do State. Um endpoint novo de importação em lote no Xano foi rejeitado: duplicaria a validação de domínio já existente no backend, adicionaria superfície de XanoScript e dependeria do comportamento de transação no plano Free, o mesmo ponto bloqueante já registrado para a baixa de estoque (C1). O custo de uma requisição por Produto é aceitável porque a duplicidade detectada torna a reexecução idempotente.

### Lotes compatíveis com o limite de 10 req / 20 s

A importação é sequencial, com intervalo mínimo configurável entre requisições (padrão sugerido de 2,5 s, o que mantém o consumo abaixo de 8 POST por janela de 20 s) e retry diante de `429` com a mesma política já existente no projeto (`XANO_RATE_LIMIT_MAX_ATTEMPTS = 3` e `_rate_limit_wait_seconds`, com espera padrão de 20 s limitada a 30 s). Como o helper de requisição atual (`_request_xano_json`) só reexecuta `429` para `GET`, esta Change SHALL estender esse caminho para também reexecutar `429` nas gravações da importação; reutilizar as constantes e a espera não dispensa esse ajuste. As leituras de Categoria, Marca e Produto usadas na validação entram no mesmo orçamento e são feitas antes do início do loop. Limites por arquivo (confirmados): no máximo 200 linhas, 50 grupos de Produto e 2 MB; exceder qualquer limite rejeita o arquivo com mensagem clara. A interface exibe progresso (grupo atual, criados, pulados, falhas) e permite cancelar o processamento em andamento.

### Duplicidade pulada, nunca sobrescrita

Antes de criar um grupo, o nome já existente no catálogo (comparação após `strip`) marca o grupo como `DUPLICADA` e o pula; o mesmo vale para SKU já existente em qualquer variação, ativa ou inativa. Não existe modo de atualização na importação: atualizar dados de um Produto já cadastrado continua sendo responsabilidade do formulário individual existente. Como consequência, reexecutar o mesmo arquivo após uma falha parcial reprocessa apenas o que ainda não foi criado, o que viabiliza a retomada sem controle de estado persistido entre sessões.

### Autorização na interface e no backend

Os controles de importação são apresentados apenas quando o State indica sessão de `ADMINISTRADOR` ativo, no mesmo padrão da gestão de produtos atual. Todas as operações de gravação reutilizam endpoints que já exigem sessão válida, usuário `ATIVO` e perfil `ADMINISTRADOR` no backend; a leitura de Categorias, Marcas e Produtos usada na validação usa as mesmas listagens administrativas protegidas. O parse e a validação do arquivo acontecem na camada de State (lado do servidor Reflex) e não expõem credenciais ao navegador.

### Falhas parciais são reportadas e retomáveis

Falha de gravação de um grupo (validação do backend, rede, autorização ou limite de requisições) não interrompe os demais grupos: o processamento continua e o relatório final lista, por grupo, `CRIADO`, `PULADO (duplicado)` ou `FALHA` com a mensagem do backend. Se a sessão expirar ou a importação for cancelada, o relatório parcial é exibido e a orientação é reenviar o mesmo arquivo, aproveitando a detecção de duplicidade. Nenhuma falha é apresentada como sucesso.

## Risks / Trade-offs

- [Agrupar por nome de Produto pode colidir com o fato de o domínio não tornar o nome único] -> Regra restrita ao arquivo, conflito reportado como erro de agrupamento e Produto existente sempre pulado; se no futuro surgir identificador comercial de Produto, o modelo da planilha poderá evoluir em outra Change.
- [Uma requisição por Produto confronta o limite de 10 req / 20 s em arquivos grandes] -> Caps por arquivo, espaçamento entre requisições, backoff em `429` e retomada idempotente por reexecução.
- [Leitor XLSX próprio pode cobrir menos casos de arquivo do que uma biblioteca] -> Contrato de formato explícito e restrito (primeira planilha, sem fórmulas/datas), com erro claro para células não suportadas; `.xls` legado é rejeitado.
- [Um administrador pode editar um Produto manualmente durante a importação] -> O backend revalida no momento de cada escrita; a importação nunca edita o que já existe, então o pior caso é um Produto criado na importação ser logo em seguida editado pela UI individual.
- [Quantidade inteira na importação é mais estrita que o formulário individual atual] -> Decisão desta Change: exigir inteiro ≥ 0 no arquivo, alinhado à regra de estoque inteiro do roadmap (C1); o formulário individual permanece com leitura decimal.

## Migration Plan

1. Nenhuma alteração de schema ou endpoint no Xano; a Change é composta por State e interface no Reflex e por testes.
2. Adicionar parse, validação e pré-visualização sem disponibilizar a confirmação em produção até os testes de orquestração passarem.
3. Disponibilizar a importação na seção de Produtos para `ADMINISTRADOR` após verificação de autorização negativa e do relatório de falhas parciais.
4. Rollback pela remoção da seção de interface e dos handlers associados; Produtos já criados pela importação são dados de domínio e são preservados.

## Open Questions

1. Confirmar o espaçamento padrão de 2,5 s entre requisições de gravação.
