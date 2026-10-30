# Reconciliação publicada — 30/10/2026

## Escopo e compatibilidade
Dois GETs de Product Management, com GUIDs preservados. Auth user e restrição de ADMINISTRADOR ATIVO já existiam no publicado; esta entrega não concedeu novas permissões. Aplicados ordenamento nome asc / sku asc, seleção explícita de campos e erros de acesso explícitos, conforme contrato local. Produtos/variações inativos continuam incluídos para manutenção. Campos usados por _product_entries/_refresh_products foram preservados; frontend/State, URLs e demais endpoints inalterados.

## Preparação e publicação
- Snapshot fresco com 98 documentos, sem registros/env/drafts, fora do Git.
- Dry-run antes da publicação: API Endpoints ~2 updated, UPDATE products GET e variations GET. Nenhum grupo, tabela ou endpoint de escrita.
- Publicação restrita no escopo autorizado de reconciliação, por CLI interativa e confirmação do preview; sem --force/--sync/--delete/--records/--env/--no-transaction. CLI confirmou Pushed 2 documents to workspace 147981 in 2.3s.
- O terminal manteve saída pendente após a confirmação. Foi usado pull independente para comprovar o estado efetivo antes de encerrar o processo local; não foi repetido push.

## Verificação
- 186 testes locais passaram antes do envio (1,852 s) e após adotar a serialização publicada nos dois arquivos (1,797 s). Novo teste verifica allowlist exata de campos, lookup mínimo de usuário, ordenação, ausência de filtro que esconda inativos e ausência de escrita nos GETs. Suite existente verifica guard antes do acesso ao catálogo e integração/parsers.
- Pull posterior: dois GETs equivalentes ao pacote, observada a reordenação de propriedades sort/return pelo serializador. Depois os dois arquivos locais adotaram a forma publicada, removendo apenas espaços finais de linhas.
- Os outros 96 documentos não tiveram alteração normalizada; nenhum documento adicionado/removido.
- Quatro provas GET: products e variations retornaram 401 sem sessão e com token inválido. Nenhum corpo privado salvo e nenhuma leitura autenticada de catálogo usada como prova.
- Nenhum registro foi alterado. Evidência sanitizada: published-verification.json. Pacote original e hashes: package-manifest.json.

## Limites
A comparação de código publicado comprova a whitelist, ordenamento e guards implantados; as provas HTTP comprovaram negativas anônimas/token inválido. Não foram executadas leituras positivas autenticadas ou negativas com contas reais de Funcionário/Administrador inativo nesta change; não declarar esses cenários como E2E remotos. Não houve mutação de produtos ou estoque. A ordem de nomes idênticos não ganhou desempate/paginação. Upload, catálogo público, carrinho/checkout e defaults de schemas continuam fora de escopo, com divergências pendentes na auditoria geral.
