# Design — refinamento do workspace interno

## Context

O workspace interno usa um shell próprio: sidebar navy `.vx-internal` com itens
`.vx-internal__nav-item` (hover/selected), header de seção com overline/título/descrição
e uma pill de canto superior `.vx-internal__status` ("Acesso interno"). A auditoria
ao vivo (12/11/2026, conta funcionalista, somente leitura) confirmou hierarquia boa,
mas encontrou inconsistência de ações (links de texto "Carregar / atualizar …" ao lado
do botão primário de busca), estados de erro/vazio com altura excessiva e tabelas sem
tratamento explícito de densidade.

## Goals / Non-Goals

**Goals:**

- Ações de leitura/refresh do workspace viram botões sólidos consistentes com os
  botões primários já existentes; mesma autorização e mesmos handlers.
- Sidebar mais compacta, seleção com contraste reforçado, pílula redundante removida
  no header de seção.
- Painéis de erro/aviso/empty states compactos sem remover mensagens/ações.
- Tabelas legíveis em desktop/tablet sem overflow; CSS responsivo preservado/empilhado
  em 375/768 px.
- Verificação: suíte, `reflex compile`, capturas onde possível e CSS estático para
  mobile.

**Non-Goals:**

- Backend, Xano, rotas, State de negócio, permissões, novas capacidades ou imagens.
- Redesenho da identidade, da sidebar (cores/estrutura) ou da ordem das seções.
- Login interno e recuperação de senha (já refinados).
- Live audit mobile completa (a troca de viewport encerra a sessão do teste);
  a verificação mobile é estática.

## Decisions

- **Reaproveitar `primary_button` para ações de refresh.** Hoje as seções usam
  `"Carregar / atualizar X"` como links de texto; a decisão é trocá-los pelo mesmo
  componente de botão primário, preservando `on_click`, `disabled` e o texto. Isso
  uniformiza hierarquia sem custo de State/handlers. Alternativa rejeitada: criar um
  botão "tertiary" novo — duplicaria variantes sem ganho.
- **Densidade via CSS, não via restruturação.** Painéis de erro e empty states
  recebem redução de `padding`/`min-height`/espaçamentos internos com a mesma marcação;
  tabelas recebem `font-size` e `padding` consistentes via CSS existente
  (`.vx-internal__content table`). Alternativa rejeitada: reescrever markup — mais
  arriscada para handlers e testes estruturais.
- **Pill "Acesso interno" substituída por indicador de sessão discreto.** O canto
  superior direito do header de seção mostrava redundância factual (o usuário já vê o
  brand na sidebar); a decisão é exibir "Sessão ativa" com o mesmo dot verde-teal — ou
  remover a pill caso se prefira espaço limpo; a opção escolhida mantém a ancoragem
  visual sem ruído e não muda autorização. Alternativa rejeitada: manter como está —
  viola a meta de densidade.
- **Apenas CSS + mudança de componente nas ações.** Nenhum estilo novo de estrutura,
  nenhum novo design token; `assets/voltix-internal.css` recebe os ajustes e as
  classes existentes são reutilizadas.
- **Verificação responsiva estática.** Em 375/768 px o workspace já empilha
  (`@media (max-width: 800px)`); a mudança valida legibilidade e ausência de overflow
  por inspeção de CSS e capturas em desktop; mobile confere com login manual se o
  usuário desejar nova rodada de auditoria.

## Risks / Trade-offs

- [Risco] Botões extras podem mudar a leitura de testes estruturais existentes que
  procuram links de texto "Carregar / atualizar" → Mitigação: localizar ocorrências
  nos testes e ajustar assertions junto com a troca para botões.
- [Risco] Espaços mais compactos vaziam demais painéis grandes → Mitigação: manter
  mensagens, funções e nada de remover texto; ajustar apenas dimensões.
- [Risco] Usuário perde o indicador de saída → Mitigação: o logout permanece no rodapé
  da sidebar; o header passa a indicar sessão ativa.
- [Risco] Tablet 768 px sobrecarrega login (já verificado) e workspace (CSS novo) →
  Mitigação: media queries existentes preservadas; verificar colunas/empilhamento.

## Migration Plan

1. Trocar ações de atualização/refresh de links de texto para `primary_button` nas
   seções do workspace (clientes, dashboard, CRM, atendimentos, pedidos, usuários).
2. Ajustar densidade no `assets/voltix-internal.css` (painéis de erro/vazio, tabelas).
3. Compactar `.vx-internal__nav-item` e reforçar `.is-selected` no CSS.
4. Substituir a pill "Acesso interno" por "Sessão ativa" no `internal_workspace_shell`.
5. Atualizar testes estruturais que referenciam os links antigos; rodar suíte.
6. `reflex compile`, `git diff --check`, capturas em 375/768/1280 (estático/manual
   quando aplicável), `openspec validate --all --strict`.
7. Restaurar `reflex.lock/*`; commit/push somente com autorização.

## Open Questions

Nenhuma: escopo, restrições (identidade mantida, sem novas imagens, sem backend) e
sequenciamento foram aprovados pelo usuário em 12/11/2026; a configuração local do
`.env` para as seções de dados foi adicionada e documentada no proposal.
