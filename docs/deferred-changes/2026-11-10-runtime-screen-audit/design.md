## Context

A análise estática já cobriu specs, testes, rotas, navegação, XanoScripts e higiene do repositório. O que falta é observação em execução. O app tem 7 rotas (`/`, `/catalogo`, `/cliente`, `/carrinho`, `/checkout`, `/pedidos`, `/interno`) e 7 seções internas (`dashboard`, `clientes`, `atendimentos`, `pedidos`, `catalogo`, `produtos`, `importacao`). O `.env` local já contém as URLs do Xano; o Playwright carrega o mesmo arquivo.

## Goals / Non-Goals

**Goals:**

- Provar que cada tela carrega com o backend real.
- Identificar defeitos observáveis com rota, perfil, ação, esperado e obtido.
- Classificar cada defeito como bloqueador de demo, correção imediata, pós-entrega ou falso positivo.
- Devolver o escopo fechado da change de correção.

**Non-Goals:**

- Corrigir qualquer defeito nesta change.
- Criar telas ou capabilities novas.
- Alterar Xano, schemas, registros ou variáveis de ambiente.
- Executar compra, importação, upload, inativação ou exclusão.
- Substituir os testes automatizados ou o E2E existente.

## Decisions

- **Execução em vez de leitura de código.** A análise estática já foi feita e não encontrou tela ausente; somente a execução revela fluxo quebrado. Alternativa descartada: ampliar a leitura estática, que não produz prova.
- **Somente leitura.** Login é permitido por ser necessário para observar as áreas autenticadas. Toda ação que grava — compra, importação, upload, cadastro, inativação, exclusão — fica registrada como bloqueada, não executada. Isso preserva E6 e evita poluir o workspace compartilhado.
- **Evidência sanitizada.** Capturas sem CPF, e-mail completo, telefone, senha, hash ou token. Dados pessoais são borrados antes de salvar. Registros sintéticos já existentes podem ser citados por identificador técnico, nunca por dado pessoal.
- **Classificação por impacto na entrega.** Um defeito só é "bloqueador de demo" se impedir uma jornada que o vídeo precisa mostrar. O restante vira correção posterior ou limitação documentada.
- **Timebox de uma sessão.** A auditoria não vira investigação aberta: se uma tela não carregar por motivo externo (rede, 429, conta ausente), o bloqueio é registrado e a auditoria segue.

## Risks / Trade-offs

- **Xano Free com rate limit** → percorrer as telas com pausas e registrar 429 como bloqueio, sem insistir.
- **Contas internas ausentes ou inativas** → registrar como bloqueio de acesso e propor provisionamento na change seguinte.
- **Captura expondo dado pessoal** → aplicar máscara antes de salvar; em dúvida, descrever a tela em texto em vez de publicar a imagem.
- **Auditoria virar desculpa para não entregar** → timebox explícito e saída obrigatória: inventário + lista de defeitos.

## Migration Plan

Não há migração. A change produz documentos e capturas. Reversão consiste em remover `evidence/` e arquivar a change como não executada.
