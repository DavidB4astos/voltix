## Context

See proposal.md - Why. Current state: single module `voltix/voltix.py`, rota `/` ocupada pelo acesso interno (`index()`), catálogo público em `/catalogo`. Já existem componentes compartilhados (`site_header`, `site_footer`, `page_shell`, `surface_card`, `feedback_text`, `empty_state`, `loading_text`, `section_heading`) e dados públicos do Xano carregados por `State.load_public_catalog` (produtos + categorias públicas). Identidade atual: navy `#102A43` / ciano `#00B8D9` / superfície `#F5F8FC`; a referência nova traz navy `#071525`, azul `#0866D9`, ciano `#00B8D9`, branco e fundo `#F5F7FB`.

## Goals / Non-Goals

**Goals**
- Home pública premium em `/`, reutilizando helpers e dados Xano existentes.
- Relocar acesso interno para `/interno` sem mudança de comportamento (mesmo login, sessão, permissões).
- Atualizar links "Acesso interno" dos cabeçalhos públicos.
- Responsivo 375/768/1280 sem overflow.

**Non-Goals**
- Não alterar Xano/XanoScript, regras de negócio, autenticação, persistência, Domain Model.
- Não reestilizar o restante do storefront além do mínimo exigido para a Home.
- Não adicionar dependências visuais novas.

## Decisions

- **Rota `/` = Home pública; acesso interno em `/interno`.** Necessário para a Home ocupar a raiz. Alternativa considerada: Home em `/home` com raiz preservada — descartada por não produzir a página inicial pública desejada. Decisão registrada como risco dependente de aprovação.
- **Reuso de dados Xano sem backend novo.** A Home usa `State.load_public_catalog` (produtos ativos + categorias públicas) e vars públicas existentes. Alternativa considerada: eventos próprios chamando o mesmo endpoint Xano com filtro "destaques" — descartada por exigir contrato novo/limite sem ganho nesta etapa.
- **Herói e imagens sem ativos novos.** Imagem do herói usa a primeira imagem de produto público disponível; sem imagem, fallback em gradiente navy→ciano com o nome do produto. Cards de categoria mostram nome sobre bloco gradiente (as categorias não possuem campo de imagem no modelo atual — suposição registrada).
- **Componentes locais da Home** (`home_header_nav`/`hero`/`benefits_strip`/`category_card`/`product_tile`) compostos sobre os helpers existentes; nenhum helper compartilhado é quebrado, apenas o link interno passa a apontar para `/interno`.
- **Ajuste de tom da identidade**: atualizar os tokens de cor da Home (navy/azul) para a referência `#071525`/`#0866D9`, mantendo ciano e fundo claros; não alterar os demais pages nesta Change.

## Risks / Trade-offs

- [Relocação de rota pode quebrar asserts da suíte (ex.: acesso interno esperado em `/`)] → rodar `python -m unittest discover -s tests` após o ajuste e corrigir apenas asserts de rota/link, sem mudar comportamento.
- [Suporte a serviços/links externos do herói] → hero sem fontes/icons externos; tipografia já configurada no App style.
- [Categorias sem imagem no Xano] → placeholder gradiente consistente, sem depender de schema novo.
- [Home depende de produto com imagem para o hero] → fallback gradiente garante renderização sempre.

## Migration Plan

- `index()` passa a ser registrada em `/interno` (mesma função, rota nova); `home_page()` nova registrada em `/`.
- Atualizar links "Acesso interno" em `site_header` dos pages públicos.
- Executar `reflex compile --dry` e a suíte automatizada; validar Home em modo dev manualmente pelo usuário.
- Rollback: reverter `add_page` de Home para o estado anterior e restaurar `index` em `/` — nenhuma mudança de dados ou backend envolvida.

## Open Questions

- Nenhuma que altere specs, abordagem ou tarefas; a aprovação do movimento de rota é condição para o apply (ver Risco acima).