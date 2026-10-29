## Fontes
AGENTS.md, overview, domain-model, specs consolidadas, diretórios arquivados, READMEs de adiamento, manifesto e histórico Git local. Nenhuma afirmação nova sobre publicação remota ou execução de backend.
## Reconciliação
C5 concluída; 15 fotos e cinco pendentes; C1 e rascunho de clientes permanecem adiados. Preservar E1–E7, matriz planejada, dependências e riscos. Limites do plano Xano são registros históricos a reconfirmar, não auditoria atual do serviço. C9 escrita é distinta do E2E de leitura existente.
## Decisões
Não restaurar automaticamente rascunho de clientes incompatível com E2. Remover o erro contraditório que exigia HTTP 400 em C1: a proposta adiada preserva HTTP 200/confirmado=false, sujeito ao contrato vigente na retomada. Não escolher implementação de atomicidade sem prova no plano Free. Sem mudança de autorização.
## Verificação
Conferir links locais, codificação, inventário de arquivos, cinco pendências e escopo de diff; validar OpenSpec. Sem testes funcionais novos, pois nenhum código é alterado. Histórico anterior permanece no Git.
