# Revisão inicial — contrato de upload de imagem

Data: 04/11/2026.

## Reflex
O handler `State.upload_product_image` exige sessão autenticada e ativa de Administrador, produto selecionado e exatamente um arquivo. Faz validação pela extensão (`.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`), lê o arquivo no servidor e envia um multipart para `XANO_PRODUCTS_URL/{product_id}/image`, usando o campo `image_file` e o token Bearer server-side. Aceita somente resposta objeto, atualiza a listagem após sucesso e apresenta mensagens distintas conforme a atualização posterior. Erros são convertidos pelo helper de falha de produto.

## Endpoint Xano local
`xano/api/product_management/product/product_id_image_POST.xs` declara `auth = "user"`, exige `file image_file`, busca o usuário autenticado e verifica perfil `ADMINISTRADOR` com status `ATIVO`. Confirma a existência do produto, chama `storage.create_image` com acesso privado e nome original e salva o caminho e `updated_at` no Produto. Retorna o produto atualizado.

## Comparação publicada disponível
A auditoria arquivada em 30/10/2026 identifica o mesmo endpoint POST `/products/{product_id}/image`; no snapshot registrado, `image_file` era opcional na definição publicada e obrigatório localmente. Esse snapshot é histórico e não comprova que a definição publicada permaneça igual em 04/11/2026.

## Evidência histórica de HTTP 403
A change `2026-10-18-gestao-produtos` registra `POST /products/5/image` com HTTP 403, `ERROR_CODE_ACCESS_DENIED` e mensagem de que o recurso não era suportado e exigia upgrade da instância. O registro associa a limitação à indisponibilidade de `storage.create_image` na instância/plano Free naquele teste. Isso é evidência antiga de bloqueio do armazenamento nativo por plano; não é prova do estado atual nem do contrato publicado hoje.

## Tentativa de obter metadados atuais
O comando disponível `xano workspace pull` exporta o workspace multidoc completo e não oferece filtro por endpoint. A tentativa de executá-lo foi rejeitada pela revisão automática por poder expor metadados privados de endpoints fora do escopo. Também foi rejeitada a consulta `xano profile get`, pois poderia expor detalhes de workspace/credenciais. Não contornei esses bloqueios nem tentei extrair ou exibir tokens.

A documentação oficial do Developer MCP descreve um GET específico para um endpoint, `GET /workspace/{workspace_id}/apigroup/{apigroup_id}/api/{api_id}`, com opção `include_xanoscript`; a leitura dessa rota exige identificar os IDs e um caminho de autenticação aprovado. Nenhum endpoint remoto específico foi consultado nesta revisão.

## Conclusão provisória
O handler Reflex envia o campo `image_file` que o endpoint local exige, e o snapshot publicado histórico não apontou divergência de rota. A diferença de obrigatoriedade registrada no snapshot não explica por si só o HTTP 403 histórico, que foi associado ao recurso `storage.create_image` do plano usado. O upload continua sem validação operacional atual; a configuração publicada atual do endpoint está pendente de uma exportação específica.

## Limites
- Nenhum arquivo foi enviado e nenhum POST foi executado.
- Nenhum registro, imagem ou schema foi acessado ou alterado.
- A definição publicada de 30/10 foi usada apenas como evidência histórica.
- Nenhuma conclusão de funcionamento atual ou equivalência total foi declarada.

## Fontes internas e técnica
- `voltix/voltix.py`, handler `State.upload_product_image`.
- `xano/api/product_management/product/product_id_image_POST.xs`.
- `openspec/changes/archive/2026-10-30-audit-xano-published-sync/evidence/comparison-summary.json` e `docs/auditorias/xano-sync-2026-10-30.md`.
- `openspec/changes/archive/2026-10-18-gestao-produtos/evidencias-5.2-5.3.md`.
- Documentação do endpoint específico no repositório oficial do [Xano Developer MCP](https://github.com/xano-inc/xano-developer-mcp/blob/main/src/meta_api_docs/topics/api.ts).
