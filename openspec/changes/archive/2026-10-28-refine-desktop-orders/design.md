## Decisions
Componentes puros para cards/conteúdo, com callbacks e condição de simulação recebidos da página real. Rótulos traduzem códigos conhecidos apenas na apresentação; desconhecidos permanecem visíveis. Preservar data retornada, identificador comercial e snapshots monetários. Contagem identifica linhas de itens, sem sugerir soma de unidades. Atualizações/desenho do resumo ficam desabilitados enquanto há requisição/simulação relevante. Nenhum novo evento ou fluxo de pagamento/cancelamento.

## Verification
Suíte existente, compilação e AST dos handlers/modelos e demais páginas. Prévia isolada: histórico, resumo pendente/elegível, pedido pago sem botão, loading, vazio, erro, simulação em progresso e larguras 1440/1024, com controle estreito. Verificar foco e rótulos. Nunca acionar simulação real ou consultar dados pessoais de cliente. Registrar limites: fixture não comprova integração autenticada real.
