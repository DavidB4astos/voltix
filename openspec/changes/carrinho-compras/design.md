## Context

Consulte [proposal.md](./proposal.md) e [specs/shopping-cart/spec.md](./specs/shopping-cart/spec.md). A tabela Xano `variacao_produto` já armazena `produto_id`, preço decimal, quantidade disponível decimal e status; a tabela `produto` armazena o status. Embora o domínio diga que quantidade de Carrinho é inteira, o estoque disponível no modelo atual é decimal, portanto a operação deve comparar a quantidade inteira solicitada com o estoque numérico atual sem mudar o schema comercial existente.

O Cliente já possui autenticação própria na tabela `CLIENTE`, endpoints de identidade, token separado de `UsuarioInterno` e uma página Reflex em `/cliente`; as chamadas HTTP a Xano são mediadas por State/Python. O catálogo público retorna produtos e variações ativos, mas não possui ação de Carrinho. A documentação define Carrinho sem snapshot de preço e explicita que ele não reserva estoque.

## Goals / Non-Goals

**Goals:**

- Persistir o Carrinho e suas linhas sob a identidade autenticada de Cliente.
- Aplicar validação de estoque/status e propriedade no backend, independente da interface.
- Reutilizar preços persistidos das VariaçõesProduto para exibir totais atuais.
- Acrescentar a ação de adicionar ao carrinho no catálogo e uma visão/edição de Carrinho integrada à conta de Cliente.
- Preservar itens confirmados quando dados comerciais mudarem; não remover silenciosamente itens indisponíveis.

**Non-Goals:**

- Reservar, baixar ou ajustar estoque.
- Criar Pedido ou implementar checkout, pagamento, frete, descontos, taxas ou CRM.
- Alterar Produto, VariaçãoProduto, autenticação Cliente ou operações administrativas existentes.
- Guardar snapshot de preço, estoque ou dados de catálogo em ItemCarrinho.

## Decisions

### Persistir um Carrinho reutilizável e itens únicos por variação

Criar tabelas `carrinho` e `item_carrinho`. O Carrinho referencia `CLIENTE`; cada item referencia um Carrinho e uma `variacao_produto`, guarda somente quantidade e timestamps, em conformidade com os atributos do Domain Model. O Carrinho é criado de forma preguiçosa na primeira inclusão; uma leitura sem registro retorna estado vazio sem criar persistência. Uma restrição única por Cliente mantém um único Carrinho reutilizável, inclusive depois de esvaziado. Uma restrição composta por Carrinho e variação evita itens duplicados; uma tentativa repetida substitui a quantidade total solicitada, como definido pelo Domain Model, e não soma implicitamente. Quantidade zero remove a linha e mantém o Carrinho.

### Aplicar propriedade e validação comercial em endpoints Xano

Criar endpoints autenticados por `CLIENTE` para leitura, inclusão, atualização e remoção. Cada endpoint revalida o Cliente `ATIVO` a partir de `$auth.id`; não recebe proprietário do payload nem confia em IDs de Carrinho fornecidos pela interface. As mutações verificam a propriedade do Carrinho/Item, o status `ATIVO` do Produto e da VariaçãoProduto, quantidade inteira e estoque atual antes da escrita. O backend trata simultaneidade de operações de uma mesma linha com escrita consistente e usa o índice único como última barreira contra duplicação.

Uma inclusão ou alteração positiva exige Produto e VariaçãoProduto ativos e quantidade não superior ao estoque observado no momento da mutação. Não se reserva estoque, nem se altera a VariaçãoProduto. Quantidade zero remove o item; quantidade negativa ou fracionária é rejeitada. Se o estoque cair depois da inclusão, preservar o item, permitir reduzir a quantidade ao limite atual quando Produto/Variação ainda estiverem ativos, e permitir remover. Se Produto ou Variação ficar inativo, manter a linha visível como indisponível e permitir sua remoção, mas rejeitar novas inclusões/alterações positivas. Isso evita apagar intenção do Cliente ou tratar disponibilidade antiga como atual.

### Calcular subtotais usando preços atuais

As respostas de leitura retornam preço atual e status da VariaçãoProduto, status do Produto, quantidade persistida, subtotal e total. O backend calcula subtotal como preço decimal corrente multiplicado pela quantidade inteira e soma os subtotais sem arredondamento ou regra comercial adicional. A interface não envia preço; a resposta do backend é a fonte dos valores. Como ItemCarrinho não possui preço histórico no Domain Model, uma alteração administrativa de preço atualiza os valores exibidos na próxima leitura, sem mudar a quantidade.

### Integrar catálogo público e conta Cliente sem misturar sessões

Adicionar ação de inclusão junto das variações no catálogo público. Visitante não autenticado recebe caminho para autenticar-se como Cliente antes de incluir; a operação de dados só ocorre após a sessão Cliente estar confirmada. A página `/carrinho` exige essa sessão para exibir e alterar dados; a página de Cliente recebe navegação para o Carrinho. State utiliza o token de Cliente existente, um endpoint/URL de ambiente dedicado e o helper HTTP server-side; não usa nem substitui o token de `UsuarioInterno`. Erros de rede, validação e respostas incompatíveis permanecem visíveis e preservam o último estado confirmado.

## Risks / Trade-offs

- [Produto, Variação ou estoque podem mudar entre leitura e operação] -> Revalidar status e estoque no Xano em toda mutação, nunca confiar no catálogo previamente carregado e preservar/identificar linhas que ficaram indisponíveis.
- [Duas inclusões simultâneas da mesma variação podem competir] -> Aplicar unicidade persistente `(carrinho_id, variacao_produto_id)` e tratar conflito relendo/atualizando a linha própria de forma consistente.
- [Preço pode mudar enquanto o Carrinho está aberto] -> Calcular em cada resposta com o preço atual persistido; não comunicar preço garantido nem criar snapshot de preço.
- [A Change de cadastro de Cliente ainda tem validação E2E remota pendente por bloqueio externo do Xano] -> Não presumir endpoints publicados; confirmar no ambiente autorizado que dependências de Cliente e Produto estão disponíveis antes de publicar. Se o ambiente bloquear publicação, manter código local e documentar a limitação, sem contornar permissões nem alegar E2E.
- [Itens podem tornar-se inativos ou exceder estoque após inclusão] -> Preservar as linhas existentes, marcar indisponibilidade com dados atuais, permitir remover e permitir reduzir quantidade apenas enquanto Produto e Variação estiverem ativos.

## Migration Plan

1. Confirmar no Xano autorizado as tabelas e APIs de Cliente, Produto e VariaçãoProduto usadas por esta Change, sem alterar esses recursos.
2. Adicionar as tabelas de Carrinho e ItemCarrinho com referências e índices de unicidade necessários; não migrar dados de outras Changes nem criar registros de Cliente/Produto para teste.
3. Criar endpoints autenticados e testar autorização, integridade, estoque, valores decimais, repetição de variação e falhas sem mexer no estoque.
4. Configurar localmente a URL de Carrinho, integrar State/Python, catálogo e página Cliente/Carrinho e executar testes locais.
5. Validar E2E somente no Xano autorizado. Em rollback, desabilitar a interface/endpoints da Change sem apagar carrinhos ou itens persistidos; não alterar dados de Produto, VariaçãoProduto ou Cliente.

## Open Questions

Nenhuma decisão funcional bloqueante permanece. O comportamento de uma nova inclusão da mesma variação como substituição da quantidade atual e o uso do preço atual foram definidos pelo modelo de ItemCarrinho, que não prevê incremento implícito nem snapshot de preço.
