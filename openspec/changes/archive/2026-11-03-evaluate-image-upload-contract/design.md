## Método
1. Inspecionar o handler Reflex: perfil exigido, número e extensão de arquivos, URL, campo multipart, cabeçalhos, tratamento da resposta e atualização da listagem.
2. Conferir o endpoint local: método/rota, autenticação/autorização, nome e obrigatoriedade do campo, validações, chamada de storage, escrita do caminho no Produto e resposta.
3. Para o contrato publicado atual, preferir uma leitura somente do endpoint específico. Se a ferramenta disponível só permitir exportar o workspace completo, não usar essa opção para esta análise estreita; registrar a limitação e usar apenas evidência publicada histórica, datada.
4. Conferir a evidência histórica da resposta HTTP 403 sem repetir o envio e sem inferir uma causa além do que a evidência demonstra.
5. Registrar compatibilidade confirmada, divergências, limitações e a menor proposta de próximo passo. Não declarar upload operacional apenas com revisão estática.

## Decisões preservadas
- Sem POST ao endpoint: o upload cria arquivo e atualiza Produto, portanto é uma operação mutável.
- Sem publicação ou edição Xano, sem alteração de imagem/cadastro e sem testar com dados reais.
- A autorização administrativa no backend e a separação Reflex/Xano devem ser preservadas.
- Uma correção funcional, armazenamento alternativo ou mudança de plano exige outra change OpenSpec e aprovação individual.

## Verificação
OpenSpec estrito, revisão do diff documental e validação das referências da evidência. Nenhuma suíte funcional será executada porque a change não altera código. Se o acesso ao endpoint publicado atual não estiver disponível por uma consulta específica, reportar que o funcionamento e a configuração remota atuais continuam sem prova.
