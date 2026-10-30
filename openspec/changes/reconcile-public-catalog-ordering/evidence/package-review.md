# Revisão pré-publicação — 30/10/2026

Git inicial limpo e sincronizado. Snapshot novo de 98 documentos externo ao Git, sem registros ou variáveis de ambiente.

Pacote contém somente duas queries com GUID preservado:
- GET categories: adicionar sort name asc.
- GET products/{product_id}: adicionar sort sku asc às variações.

A comparação normalizada confirma que retirar essas ordenações torna cada query igual ao snapshot. Campos, filtros ATIVO, erro notfound, acesso anônimo e respostas permanecem intactos. Nenhuma operação de escrita está presente. A listagem products coincide sob normalização documentada de formatação e posicionamento do return list; não integra o pacote. Não se afirma equivalência semântica geral do workspace.

Dry-run CLI no workspace 147981:
```
API Endpoints ~2 updated
UPDATE query categories GET
UPDATE query products/{product_id} GET
```

OpenSpec strict: válido. Suíte: 187 testes, OK, 2.745s. A primeira invocação da suíte foi feita fora da raiz do projeto e falhou na importação; a execução correta na raiz passou. ResourceWarnings existentes de respostas HTTP simuladas foram observados, sem falhas.

Publicação ainda não realizada. A change permanece aberta; não consolidar spec nem arquivar antes de conferir a versão publicada e leituras públicas. Nenhum registro foi alterado. Hashes do pacote em package-review.json.
