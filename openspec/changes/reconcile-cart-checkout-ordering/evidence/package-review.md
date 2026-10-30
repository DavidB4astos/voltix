# Revisão do pacote — 30/10/2026

Snapshot recente: 98 documentos, fora do Git, sem registros/env/drafts. Git estava limpo e sincronizado no início.

Pacote preparado diretamente dos três endpoints publicados. Adiciona somente sort id asc nas quatro consultas de item_carrinho: uma no GET cart, uma no POST review e duas no POST confirm (a segunda dentro da transação). Remover essas linhas recupera o texto anterior ignorando espaços. GUIDs preservados; hashes em package-review.json.

Dry-run:
```
API Endpoints ~3 updated
UPDATE query cart GET
UPDATE query checkout/confirm POST
UPDATE query checkout/review POST
```

Sem grupos, tabelas ou registros no pacote. Nenhum POST de compra foi executado. O código de gravação já existente da confirmação não foi modificado. Não foi feita publicação nesta preparação.

Comparação local/publicado: além de sort, há diferenças de type inner explícito nos joins, posicionamento de propriedades e return list explícito. Confirm também simplifica uma comparação booleana. Esses elementos publicados foram preservados. Não afirmar sincronização completa ou alterar joins por suposição. A referência oficial consultada foi registrada em design.md; o default efetivo ainda não foi demonstrado em ambiente isolado.

Verificação: OpenSpec strict válido; 188 testes passaram em 1.998s. Novo teste protege cada leitura de itens, vínculo ao carrinho correto e ordenação, incluindo releitura transacional. Testes existentes de revisão obsoleta, indisponibilidade e propriedade continuam passando. ResourceWarnings de HTTP simulados já existentes, sem falhas.

Próximo: autorização do pacote concreto, publicação restrita, pull independente e rejeições seguras de GET cart sem sessão. Não arquivar enquanto pendentes. Testes locais não comprovam compra autenticada no Xano e não serão apresentados como E2E remoto.
