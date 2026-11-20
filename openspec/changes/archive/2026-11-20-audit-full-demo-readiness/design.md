## Context

O repositório está limpo em `main` no commit `79f57a5`, sem changes ativas, com D1–D6 concluídos e
publicados. A auditoria anterior (`2026-11-20-audit-runtime-screens-and-flows`) estabeleceu o
inventário de rotas e o padrão de evidências; esta change reutiliza esse padrão e amplia a cobertura.
A execução será feita no Antigravity, mas o projeto não possui integração específica com essa IDE:
ela será tratada como outro agente obedecendo `AGENTS.md`, OpenSpec e os mesmos gates.

## Goals / Non-Goals

**Goals:**

- Produzir evidências verificáveis para as quatro frentes de auditoria em uma única change.
- Classificar cada achado por impacto na demonstração e separar claramente falso positivo.
- Definir o roteiro ensaiável das quatro jornadas aprovadas sem violar E6.
- Manter `main` intocável durante a execução, usando worktree com escopo disjunto.

**Non-Goals:**

- Corrigir defeitos, publicar Xano, escrever dados ou criar novas imagens.
- Resetar senha de Cliente ou exercitar e-mail real.
- Alterar specs consolidadas: `skip_specs: true` permanece válido.
- Repetir a varredura de 23 detalhes que estourou o limite do plano Free.

## Decisions

- **Uma change, quatro frentes sequenciais.** Alternativa considerada: quatro changes separadas.
  Optou-se pela change única porque o usuário aprovou "tudo" e porque a classificação final depende
  da correlação entre telas, código, contratos e segurança. A sequência interna mantém o princípio
  de uma tarefa por vez.
- **Worktree separado no Antigravity.** Alternativa: trabalhar diretamente em `main`. Rejeitada
  porque hazards de concurrent edits e porque o histórico recente deve permanecer limpo até a
  revisão final. O worktree será criado a partir de `79f57a5` e receberá somente artefatos desta
  change.
- **Somente leitura por padrão.** Login é permitido quando necessário para observar áreas
  autenticadas; toda ação de gravação fica registrada como bloqueada, não executada. Isso preserva
  E6 e evita poluir o workspace compartilhado.
- **Evidências em `evidence/`.** Arquivos separados por frente, mais um resumo final com matriz
  achado → jornada → classificação → próxima ação. Nenhuma evidência conterá CPF, e-mail, telefone,
  senha, hash, token, `.env` ou credenciais.
- **Demo sem mutação.** Catálogo/detalhe/carrinho e área interna serão navegados normalmente; o
  checkout será mostrado em estados existentes, sem submeter pedido. O login de Cliente será
  verificado e documentado; se o 403 persistir, a jornada fica marcada como limitação, sem reset.
- **Gates inalterados.** Antes do arquivamento: suíte completa, `reflex compile`,
  `git diff --check` com `reflex.lock/*` restaurado, `openspec validate --all --strict` e revisão
  humana das evidências.

## Risks / Trade-offs

- [Sessões por porta/navegador] → usar as instâncias locais já conhecidas; se o Antigravity não
  compartilhar a sessão, o login será feito pelo usuário, sem compartilhar token.
- [Rate limit Xano: 10 requisições/20 s] → espaçar leituras, limitar amostras e não repetir a
  varredura de detalhes; registrar 429 como limitação, não como defeito funcional.
- [Achado classificado como bloqueador depois da auditoria] → não corrigir nesta change; abrir
  proposta separada com escopo e aprovação próprios.
- [Tempo até 23/11] → manter as quatro frentes em profundidade proporcional; priorizar o que
  aparece nas jornadas da demo e documentar o restante como pós-entrega.
- [Ferramenta diferente] → tratar Antigravity como executor, não como autoridade de decisão;
  todas as mudanças passam pelo mesmo fluxo OpenSpec.

## Migration Plan

Não aplicável: a change não altera runtime, schema, contrato publicado nem dados. Se a auditoria
recomendar correções, cada uma será migrada para uma change nova, aprovada e arquivada
independentemente.

## Open Questions

Nenhuma. As decisões de escopo, login de Cliente e checkout simulado foram respondidas pelo usuário
antes da criação desta change.
