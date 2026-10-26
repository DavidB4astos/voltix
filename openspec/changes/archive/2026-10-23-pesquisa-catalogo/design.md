## Context

Ver `openspec/changes/pesquisa-catalogo/proposal.md` - Why. 
Limites Xano Free já foram tratados no projeto (429, limite de requisições). 
Código atual: `xano/api/public_catalog/products_GET.xs` só aceita `category_id`; `voltix/voltix.py` já possui estados `public_catalog_loading`, `public_catalog_loaded`, `public_catalog_message`, filtro por categoria e cache/retry existentes.

## Goals / Non-Goals

**Goals:**
- Permitir busca por nome do produto via parâmetro opcional `q` no endpoint público de listagem.
- Combinar `q` com `category_id` (quando ambos fornecidos).
- Buscar por correspondência parcial, case-insensitive, apenas em `nome`.
- Integrar no cliente Reflex mantendo estados, cache e tratamento de 429 existentes.
- Atualizar testes.

**Non-Goals:**
- Buscar em `descricao`, `especificacoes_tecnicas`, SKU ou marca.
- Busca full-text avançada, fuzzy, autocomplete ou sugestões.
- Alterar detalhe do produto, carrinho, checkout, autenticação ou admin.
- Criar/alterar tabelas, índices, dependências ou lockfiles.
- Alterar comportamento de imagens já corrigido.

## Decisions

### 1) Parâmetro e semântica
- Input: `q` (text?, opcional). Se vazio/whitespace, ignorar filtro.
- Escopo: apenas `nome` do produto (`produto.nome`). Decisão justificada para manter escopo mínimo e evitar ambiguidade com outros campos.
- Combinação: AND com `category_id` quando ambos presentes; manter regras de categoria ativa.

**Alternativas:** incluir descrição/SKU - rejeitadas por escopo e sem confirmação; usar POST - rejeitada pois endpoint é GET e contrato atual é leitura.

### 2) Operador XanoScript para busca parcial case-insensitive
- Consultas XanoScript em `db.query` permitem operadores como `includes`/`LIKE`/`ilike` conforme contexto. Pelo que vimos no código existente e docs consultadas, `includes` é flexível e case-insensitive para strings. Também pode-se normalizar com lower/upper, mas operador nativo é preferido.
- Abordagem: aplicar filtro `($input.q != null && $input.q != "") && ($db.produto.nome includes $input.q)` combinado com as condições existentes. Se necessário normalizar, usar funções disponíveis, mas priorizar operador nativo.
- Importante: validar sintaxe exata ao implementar no Xano (não apenas teoria). Esta mudança adiciona apenas o filtro, sem alterar estrutura.

**Alternativas:** `regex` - mais complexo e menos necessário; `LIKE` case-sensitive indesejado.

### 3) Fluxo no endpoint
- Manter dois ramos condicionais existentes (com/sem `category_id`) ou unificar com condições compostas.
- Aplicar filtro `q` em ambos os ramos mantendo `sort = {nome: "asc"}` e mesmo `output` (incluir `imagem_principal` já presente).
- Não alterar assinatura de resposta.

### 4) Cliente Reflex
- Adicionar campo de busca no catálogo (`rx.input` ou equivalente) vinculado a estado (ex: `public_catalog_search`).
- Enviar `q` em `_fetch_public_products` apenas se não vazio (trim).
- Debounce simples? Não obrigatório; manter padrão existente. Cache por (categoria, q)? Considerar chave de cache incluindo `q` para evitar reutilizar resultado de busca diferente. O requisito "Reuse respects the selected category" já existe - estender para (categoria, termo).
- Estados loading/empty/loaded já cobrem busca sem resultados.

**Alternativas:** filtrar no cliente - rejeitado pois iria buscar tudo e não escala; não usar cache por busca - possível mas pode gerar mais requisições; incluir q na chave é correto.

### 5) Testes
- Ampliar `tests/test_public_catalog.py` com casos: busca por nome retorna resultados, busca case-insensitive, busca com categoria combinada, busca sem resultados, busca vazia ignora filtro.

## Risks / Trade-offs

- [Risco] Sintaxe XanoScript para `includes` em `where` pode variar → Mitigação: consultar referência interna se necessário e testar lógica; manter fallback documentado no design se incerto.
- [Risco] Cache atual não considera `q` → Mitigação: incluir `q` normalizado na chave de cache/reuso.
- [Risco] Buscar em muitos produtos sem índice → Mitigação: escopo apenas nome, sem alteração de índice proposta (fora do escopo). Em contexto acadêmico/Xano Free aceitável.
- [Risco] Combinação com 429/retry existente → Mitigação: não alterar lógica de retry, apenas adicionar parâmetro.

## Migration Plan

Não aplicável (mudança aditiva, backward compatible).

## Open Questions

Nenhuma - escopo definido como "nome de produto" apenas.
