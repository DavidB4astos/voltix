# Evidência 01 — Runtime e telas

Data: 20/11/2026  
Modo: Somente leitura (sem mutações, sem submissão de pedido/pagamento, sem reset de senha)

## 1. Disponibilidade das instâncias locais

Verificado via `Invoke-WebRequest` em `http://localhost:<porta>/`:

| Porta | Status HTTP | Observação |
|---|---|---|
| `3090` | `200` | Instância respondendo |
| `3091` | `200` | Instância respondendo |
| `3092` | `200` | Instância respondendo |

## 2. Verificação HTTP das rotas principais (porta `3092`)

| Rota | Status HTTP | Tamanho da resposta | Observação |
|---|---|---|---|
| `/` | `200` | `21680 bytes` | Home pública acessível |
| `/catalogo` | `200` | `18980 bytes` | Catálogo público acessível |
| `/carrinho` | `200` | `16725 bytes` | Rota do carrinho acessível |
| `/checkout` | `200` | `16235 bytes` | Rota de checkout acessível (sem submissão) |
| `/entrar` | `404` | — | Rota não utilizada (login/conta verificados na frente de código) |
| `/interno` | `200` | `17688 bytes` | Rota do workspace interno acessível |

## 3. Inspeção visual via Chrome DevTools MCP (1280/768/375 px)

- **Resultado:** **Limitação documentada** — não foi possível conectar ao Chrome via `chrome_devtools` MCP.
- **Erro observado:** `Could not find DevToolsActivePort for chrome at C:\Users\David Bastos\AppData\Local\Google\Chrome\User Data\DevToolsActivePort (ENOENT)`.
- **Regra respeitada:** conforme instrução operacional, o navegador não foi reiniciado e nenhuma segunda instância foi aberta no mesmo perfil.
- **Impacto na auditoria:**
  - Não foi possível inspecionar DOM renderizado, layout em 1280/768/375 px, console do navegador nem sessão autenticada `ADMINISTRADOR` nesta execução.
  - O login de Cliente (403 histórico) permanece não retestado em runtime (sem reset de senha).
  - A evidência visual/responsiva mais recente em runtime permanece referenciada na auditoria anterior arquivada (`2026-11-20-audit-full-demo-readiness`).
