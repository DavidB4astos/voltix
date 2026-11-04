## Correção

- [x] 1.1 Converter a variável de preço em texto Reflex antes das operações string existentes.
- [x] 1.2 Revisar o diff: somente a coerção de tipo do helper mudou; sem alterações em cálculos, eventos, CSS ou backend.

## Verificação

- [x] 2.1 Validar artefatos OpenSpec em modo estrito.
- [x] 2.2 Comparar o conteúdo com HEAD: somente a coerção de tipo no helper mudou; nenhum whitespace final nos arquivos revisados.
- [x] 2.3 Compilar as páginas Reflex; compilação chegou a 100% sem o erro anterior de tipo.
- [x] 2.4 Confirmar visualmente em `/interno` que os preços seguem o padrão brasileiro, sem salvar captura ou executar ações que alterem dados.

## Encerramento

- [x] 3.1 Arquivar a change concluída.
- [x] 3.2 Criar commit documental/de código focado.
