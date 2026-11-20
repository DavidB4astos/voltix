## Context

O repositório Voltix usa Reflex no frontend, Xano/XanoScript no backend e OpenSpec para desenvolvimento incremental. A auditoria deve operar estritamente em modo somente leitura, preservando `main` intacta em worktree separado e respeitando as decisões E1–E7 e os limites do plano Xano Free (10 requisições/20 s).

## Goals / Non-Goals

- **Goals:**
  - Verificar o estado real de execução nas portas locais disponíveis (3090, 3091, 3092) e capturar evidências objetivas de layout/fluxo sem mutações.
  - Validar todos os gates técnicos obrigatórios (`unittest`, `reflex compile`, `git diff --check`, `openspec validate --all --strict`).
  - Conferir contratos Xano em modo somente leitura (`xano workspace pull` sem `--env` nem `--records`).
  - Auditar controles de segurança, autorização no backend e ausência de vazamento de dados sensíveis.
  - Entregar matriz de achados classificados e roteiro de ensaio seguro para a demonstração.
- **Non-Goals:**
  - Corrigir defeitos encontrados durante a auditoria (eventuais correções exigirão change própria aprovada).
  - Executar fluxos destrutivos ou com escrita (compra E2E, reset de senha, upload, importação, exclusão).
  - Alterar specs consolidadas ou realizar commit/push sem autorização explícita.

## Decisions

1. **Execução em worktree separado:** usar `.worktrees/audit-delivery-readiness` (branch `audit-delivery-readiness`) a partir de `main`, mantendo `main` limpa durante toda a auditoria.
2. **Ordem sequencial das frentes:** executar na ordem `01-runtime` → `02-code-specs-gates` → `03-xano-readonly` → `04-security` → `05-demo-readiness`, registrando um arquivo Markdown dedicado por frente em `evidence/`.
3. **Proteção contra HTTP 429 e mutações:** limitar inspeções de runtime às rotas essenciais, nunca repetir varredura de 23 detalhes de produto, não submeter checkout/pagamento e usar o perfil já configurado no Chrome DevTools MCP sem reiniciar ou abrir segunda instância no mesmo perfil.
4. **Higiene de `reflex compile`:** restaurar `reflex.lock/*` imediatamente após `reflex compile` para não deixar ruído no working tree.
5. **Classificação padronizada:** todo achado deve ser classificado em exatamente uma categoria: `bloqueador de demo`, `pós-entrega`, `limitação documentada` ou `falso positivo`.

## Risks / Trade-offs

- **Sessão de navegador indisponível:** se a sessão `ADMINISTRADOR` ou `CLIENTE` (403 conhecido) não estiver ativa na instância local, a frente `01-runtime` registra a limitação sem buscar credenciais nem resetar senhas.
- **Rate limit Xano Free:** o `xano workspace pull` e eventuais leituras serão espaçados e restritos ao mínimo necessário para evitar HTTP 429.
