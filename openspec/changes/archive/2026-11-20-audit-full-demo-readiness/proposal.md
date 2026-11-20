## Why

Após a correção dos bloqueadores D1–D6, a demonstração precisa de uma conferência final ampla antes
da entrega prevista para 23/11/2026. A auditoria de runtime anterior cobriu telas, mas não avaliou
de forma coordenada código/specs/gates, contratos Xano e segurança/autorização, nem amarrou esses
achados às jornadas que serão exibidas. O usuário aprovou uma única change cobrindo as quatro frentes
e todas as jornadas da demo, com execução no Antigravity em worktree separado e escopo disjunto.

## What Changes

- Realizar auditoria somente leitura em quatro frentes, nesta ordem sequencial:
  1. **Runtime/telas:** reinspecionar as rotas públicas e seções internas em 1280/768/375 px,
     incluindo catálogo, detalhe, carrinho, checkout, pedidos e workspace administrativo.
  2. **Código, specs e gates:** conferir coerência entre `AGENTS.md`, docs, OpenSpec, testes,
     `reflex compile`, `git diff --check` e estado do Git.
  3. **Xano somente leitura:** comparar contratos locais e publicados, sem writes, sem publicação e
     respeitando o limite do plano Free (10 requisições/20 s).
  4. **Segurança/autorização:** verificar papéis, guardas de backend/frontend e exposição de CPF,
     e-mail, telefone, senha, hash, token ou `.env`.
- Mapear os achados para as quatro jornadas aprovadas da demonstração:
  - catálogo → detalhe → carrinho;
  - área interna ADMIN (login, produtos e pedidos, sem mutação);
  - login de Cliente (apenas verificar e documentar o 403 conhecido; **sem reset de senha**);
  - checkout/pedido simulado (navegação e estados existentes, **sem submeter compra**).
- Produzir evidências em `evidence/`, com classificação por impacto: bloqueador de demo,
  pós-entrega, limitação documentada ou falso positivo.
- Registrar o plano de ensaio da demonstração e as decisões que permanecem bloqueadas por E6.
- **Fora do escopo:** qualquer escrita em Xano, publicação de endpoint, compra E2E, e-mail real,
  reset de credencial, criação de novas imagens de produto, correção de código ou alteração de specs
  consolidadas. Defeitos encontrados exigirão change própria aprovada.

## Capabilities

### New Capabilities

- Nenhuma. Esta é uma change de auditoria e documentação; nenhum comportamento observável muda.

### Modified Capabilities

- Nenhuma. `skip_specs: true` está declarado em `.openspec.yaml`.

## Impact

- Artefatos OpenSpec: `proposal.md`, `design.md`, `tasks.md` e evidências em `evidence/`.
- Código, testes, specs consolidadas e configuração do app: **nenhuma alteração**.
- Runtime: leituras autenticadas e anônimas nas instâncias locais já usadas; sessão de Cliente pode
  não estar disponível (403 conhecido), o que será documentado como limitação.
- Xano: somente leitura; nenhum `push`, `PATCH`, `POST`, `DELETE` ou dado sensível exposto.
- Antigravity: execução em worktree separado, sem tocar em `main` enquanto a change está ativa;
  mesmos gates de validação, testes e revisão do projeto.
