## Why

A auditoria ao vivo do workspace interno em 12/11/2026 (conta funcionalista, somente
leitura) mostrou um shell visual já sólido — sidebar navy, hierarquia clara, foco
visível — com inconsistências de hierarquia de ações e densidade: ações primárias como
"Carregar / atualizar" são links de texto em vez de botões, painéis de erro e empty
states consomem altura excessiva e a pill de canto superior "Acesso interno" é redundante
em toda tela. A refinamento completa a sequência de design iniciada com a storefront.

## What Changes

- Unificar a hierarquia de ações do workspace: toda ação de leitura/atualização de dados
  vira botão sólido consistente com as ações primárias existentes (mantendo handlers e
  papéis); ações destrutivas permanecem com o tratamento destrutivo.
- Reduzir a densidade de painéis de erro/aviso/empty states e aumentar a legibilidade
  das tabelas e formulários (mais respiro útil, menos altura vazia).
- Sidebar mais compacta, estado ativo com mais contraste e remoção da pill "Acesso
  interno" redundante no canto superior (a identidade já vive na sidebar).
- Validação responsiva estática em 375, 768 e 1280 px no CSS do workspace (empilhamento
  da sidebar, formulários e tabelas sem overflow, tipografia fluida preservada).
- Preservar comportamento, permissões, rotas e State — somente apresentação.

Sem **BREAKING** changes.

## Capabilities

### New Capabilities

<!-- Nenhuma capability nova. -->

### Modified Capabilities

- `internal-workspace`: requisito de hierarquia desktop ganha hierarquia de ações
  consistente (ações primárias como botões, destrutivas no tratamento existente),
  densidade e affordance explícitas; indicador superior redundante removido em favor
  de um indicador de sessão discreto.

## Impact

- Frontend: `voltix/voltix.py` (workspace shell, painéis e handlers de clique só para
  reexpor os mesmos handlers como botões onde hoje são links de texto),
  `assets/voltix-internal.css` e eventuais ajustes de tokens/variáveis locais.
- Testes: novos testes estruturais (ações como botões, ausência da pill redundante,
  regras de densidade); suíte existente preservada.
- Verificação: suíte completa, `reflex compile`, `openspec validate --all --strict`,
  inspeção visual estática 375/768/1280 px e sessão funcional ao vivo quando a sessão
  permitir (login manual do usuário; sem mutações).
- Observação registrada: o `.env` local faltava as URLs internas (`XANO_INTERNAL_*` e
  `XANO_INTERNAL_SALES_URL`); adicionadas nos caminhos canônicos em 12/11/2026 para que
  os painéis carreguem dados localmente — os painéis de dados só exibem conteúdo com
  essas variáveis configuradas.
- Fora do escopo: backend (Xano), rotas, State de negócio, permissões, novas imagens,
  login interno/recuperação (já refinados) e o storefront público (change anterior).
