## Context

Ver `openspec/changes/consulta-clientes-admin/proposal.md` - Why. 
Já existe tela administrativa em `/admin` para gestão de pedidos/atendimentos; endpoint `/api:voltix-admin/customers` ainda não criado. 
Limites Xano Free já tratados (429, limite 10 req/20s). 
Perfis: `ADMINISTRADOR` ativo tem acesso ampliado; `FUNCIONARIO` acesso operacional. 
Endpoint interno `/auth/me_GET` já expõe `role`/`status` para validação.

## Goals / Non-Goals

**Goals:**
- Tela administrativa de listagem e busca de clientes no painel interno.
- Máscara de e-mail (apenas primeiros 3 chars + "*****").
- Apenas `ADMINISTRADOR` ativo pode consultar; `FUNCIONARIO` negado.
- Endpoint GET /admin/customers com parâmetros opcionais `q` e `status`.
- Respeitar limites Xano Free (rate limit, cache 30s).

**Non-Goals:**
- Criar/alterar endpoint de cliente público (/products, /cliente).
- Expor senhas, tokens ou dados sensíveis.
- Alterar carrinho, checkout, pedidos, pagamentos.
- Fuzzy search, autocomplete, IA/ML.
- Novas tabelas/banco de dados; apenas leitura de dados existentes.
- Funcionário consultar clientes alheios ou sem perfil admin.

## Decisions

### 1) Endpoint e input
- `GET /admin/customers` com inputs opcionais: `text q?` (busca nome/e-mail), `status?` (`ATIVO`/`INATIVO`).
- Se ambos nulos, retorna todos os clientes ATIVOs.
- Máscara de e-mail aplicada no frontend; backend retorna e-mail completo (sem more).

**Alternativas:** endpoint POST - rejeitado por ser leitura; endpoint sem filtros - rejeitado por não atender necessidade admin.

### 2) Máscara de e-mail
- Aplicar no frontend apenas; backend não altera e-mail.
- Exibir `XXX@xx.xx` formatado a partir do e-mail completo recebido.

**Alternativas:** backend retorna máscara - rejeitado por violar princípio de responsabilidade única (apresentação vs dados).

### 3) Autorização
- Verificar `role == "ADMINISTRADOR" && status == "ATIVO"` no `_public_catalog_request` ou novo `_admin_catalog_request`.
- Usar middleware existente de profile validation do Reflex.

**Alternativas:** verificar no frontend apenas - rejeitado por segurança (não confiar apenas em validação frontend).

### 4) Cache e rate limit
- Cache TTL 30s para lista sem filtros.
- Rate limit existente do Xano Free aplicado; novo endpoint compartilha mesmos limites.

**Alternativas:** cache por query string - possível mas adiciona complexidade desnecessária para uso esporádico admin.

### 5) UI no painel admin
- Tabela responsiva com paginação simples (ou scroll infinito limitado).
- Colunas: ID, nome, e-mail (mascarado), telefone, data cadastro, status.
- Botão "Ver detalhes" → modal com e-mail completo, telefone, endereço, cadastro/atualização.
- Campo de busca `q` com debounce 300ms; clear button.

**Alternativas:** nenhuma - esta é a decisão adotada.

## Risks / Trade-offs

- [Risco] Exposição acidental de e-mail no frontend se máscara falhar → Mitigação: máscara testada unitariamente; backend não altera dado.
- [Risco] Admin cadastro de novo cliente não incluso → Mitigação: fora do escopo; nova change se necessário.
- [Risco] Rate limit admin impactar outras operações → Mitigação: endpoint compartilha limites Xano Free já existentes; uso esporádico.

## Migration Plan

Não aplicável (nova adição, sem remoção ou alteração de comportamentos existentes).

## Open Questions

Nenhuma - escopo e decisões definidas na proposal.