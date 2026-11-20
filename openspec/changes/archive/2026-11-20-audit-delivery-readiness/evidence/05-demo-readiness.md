# Evidência 05 — Prontidão da demonstração e roteiro de ensaio

Data: 20/11/2026  
Veredito geral: **Aprovado com limitações documentadas (0 bloqueadores de demo)**

## 1. Matriz achado → jornada → classificação → próxima ação

| Achado | Jornada | Classificação | Próxima ação |
|---|---|---|---|
| Instâncias locais (`3090`, `3091`, `3092`) e rotas `/`, `/catalogo`, `/carrinho`, `/checkout`, `/interno` respondendo HTTP `200`; `445/445` testes OK; `reflex compile` OK | Todas as jornadas | — (Conferência positiva) | Manter instância alvo ativa para o ensaio |
| Chrome DevTools MCP sem conexão (`DevToolsActivePort` ENOENT), impedindo inspeção visual 1280/768/375 px e verificação de sessão `ADMINISTRADOR` nesta execução | Área interna ADMIN / Inspeção visual | **limitação documentada** | Validar depuração remota no perfil Chrome já configurado antes do ensaio sem abrir segunda instância |
| Rota `/entrar` retornou HTTP `404` | Login de Cliente | **falso positivo** | Usar a rota real registrada `/cliente` |
| Login de Cliente historicamente com HTTP `403` | Login de Cliente / Checkout | **limitação documentada** | Demonstrar estados de bloqueio/validação sem resetar senha |
| Pendências Xano conhecidas (joins de carrinho/checkout, defaults, upload `403`, `tmp_rollback_test`, prova isolada bloqueada por E6) | Carrinho / Checkout / Gestão de produtos | **limitação documentada** | Não acionar fluxos dependentes na demo; planejar em changes próprias |
| Endpoints legados `db_xano_bastos/status_cliente/*` com `auth=False` no remoto (não consumidos pelo frontend) | Nenhuma (fora da UI Voltix) | **pós-entrega** | Avaliar remoção ou proteção em change futura de higiene |
| `.venv\Scripts\python.exe` referencia `C:\Users\venda\...` nesta máquina | Execução local de testes e build | **limitação documentada** | Usar Python local com `PYTHONPATH` do `.venv\Lib\site-packages` ou recriar `.venv` pós-entrega |

## 2. Roteiro seguro de ensaio

1. **Catálogo público e detalhe:** navegar em `/` e `/catalogo`, aplicar busca/filtro e abrir **1** detalhe de produto e `/carrinho`.
2. **Área do cliente (`/cliente`):** exibir a tela e os estados de validação/bloqueio sem resetar senha.
3. **Checkout e pedidos (`/checkout`, `/pedidos`):** navegar apenas por telas e estados existentes.
4. **Workspace interno (`/interno`):** se houver sessão `ADMINISTRADOR` ativa, exibir dashboard, consulta de clientes (CPF mascarado), produtos, categorias/marcas, pedidos e atendimentos em modo leitura.

## 3. O que NÃO deve ser executado na demonstração/ensaio

- **Não** submeter pedido ou pagamento simulado no `/checkout` (bloqueado por E6).
- **Não** executar compra E2E, upload de imagem, importação em massa, inativação ou exclusão de registros reais.
- **Não** resetar senhas nem disparar e-mails reais.
- **Não** repetir varredura de 23 detalhes de produto (risco de HTTP `429` no plano Xano Free: 10 req/20 s).
- **Não** executar `xano workspace push`, `POST`, `PATCH` ou `DELETE` no ambiente remoto.
