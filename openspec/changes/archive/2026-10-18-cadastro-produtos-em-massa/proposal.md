## Why

O cadastro administrativo de Produtos aceita apenas um produto por vez, com uma variação inicial por formulário (Change `gestao-produtos`). Operações reais de catálogo exigem cadastrar dezenas de produtos e variações de uma só vez; sem importação em massa, o custo operacional é alto e sujeito a erros manuais de digitação. O Domain Model já define regras rígidas para Produto e VariacaoProduto (categoria e marca obrigatórias, SKU obrigatório e globalmente único, preço maior que zero, quantidade não negativa, ao menos uma variação), que precisam valer também na entrada em lote.

## What Changes

- Adicionar à área interna, visível somente para `ADMINISTRADOR`, um fluxo de **importação em massa de Produtos e de suas variações** a partir de arquivos **CSV** e **XLSX**.
- **Modelo de planilha:** uma linha por variação, com colunas de Produto (nome, descrição, especificações técnicas), classificação (nome da Categoria e nome da Marca) e Variação (nome, SKU, preço, quantidade disponível). Linhas com o mesmo nome de Produto formam um único Produto com múltiplas variações.
- **Validação completa antes de qualquer gravação:** campos obrigatórios, formato de preço e quantidade, existência e status `ATIVO` da Categoria e da Marca referenciadas, unicidade de SKU (inclusive contra variações inativas, conforme `product-management`) e conflitos de agrupamento dentro do arquivo.
- **Pré-visualização obrigatória** com o resultado linha a linha (válida, erro com motivo, duplicada) antes da confirmação; nada é persistido antes da confirmação explícita do administrador.
- **Política de duplicidade sem sobrescrita:** Produto já existente (mesmo nome) ou SKU já existente é **pulado, nunca sobrescrito ou atualizado**; o relatório final identifica cada registro pulado.
- **Importação confirmada processada produto a produto**, reutilizando os endpoints `POST` de Produto já publicados pela Change `gestao-produtos`, com respeito ao limite do plano Xano Free (10 req / 20 s), progresso visível, cancelamento e retomada segura por reexecução do mesmo arquivo.
- **Autorização:** controles apresentados somente para `ADMINISTRADOR`; toda gravação continua sendo autorizada no backend (sessão válida, usuário `ATIVO`, perfil `ADMINISTRADOR`), sem depender da interface.

Ficam fora desta Change: imagens de produto (upload ou galeria), edição ou sobrescrita de Produtos existentes, exclusão de registros, coluna de status na planilha, criação de Categorias ou Marcas novas pela planilha (somente referência às existentes), pedidos, carrinho, estoque, CRM, novos endpoints Xano e novas dependências de biblioteca sem aprovação prévia. A Change não altera as regras de domínio documentadas.

## Capabilities

### New Capabilities

- `product-bulk-import`: Importação administrativa em massa de Produtos e variações a partir de CSV/XLSX, com validação, pré-visualização, política de duplicidade e importação em lotes compatível com o plano Xano Free.

### Modified Capabilities

Nenhuma. A importação obedece às regras já especificadas em `product-management` (delta da Change `gestao-produtos`) e em `catalog-management` sem alterá-las.

## Impact

- Adiciona lógica no State Reflex para leitura, parse, validação de arquivos e orquestração da importação; **nenhum endpoint Xano novo** (reutiliza `POST products` e as listagens administrativas de Categoria, Marca e Produto existentes).
- Adiciona interface administrativa na seção de Produtos de `/interno`, restrita a `ADMINISTRADOR`.
- Adiciona testes novos de parse, validação, duplicidade e orquestração com HTTP simulado.
- **Dependências:** Change `gestao-produtos` **concluída e arquivada** (2026-10-18); endpoints publicados e sincronizados no `.env`; capability `product-management` **consolidada** em `openspec/specs/product-management/spec.md`. O pré-requisito de sequência está satisfeito, permitindo iniciar as tarefas de implementação desta Change (regra do roadmap de uma Change por vez).
- Não introduce novas dependências de biblioteca; CSV e XLSX são processados com a biblioteca padrão do Python.
