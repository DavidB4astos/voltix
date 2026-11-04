## Why

Ao iniciar o Reflex, a compilação da rota interna falha porque `_cart_money_text` chama `.split()` em uma variável tipada como `float`. O formatador compartilhado é usado por preços em várias telas. A falha impede iniciar a aplicação e verificar sua apresentação.

## What Changes

- Converter o valor numérico para texto no formatador compartilhado antes de aplicar a formatação existente.
- Preservar o formato visual já definido, os valores recebidos, cálculos, handlers, contratos e backend.
- Verificar que o projeto compila e que a exibição segue o mesmo padrão de moeda.

## Fora do escopo

- Alterar arredondamento, precisão financeira, armazenamento ou envio de preços.
- Modificar CSS, estrutura das telas, eventos, State, endpoints, Xano ou dados.
- Criar ou atualizar testes automatizados.

## Impacto

Correção pequena na conversão de tipo do formatador compartilhado. Não se altera o comportamento visual desejado nem capability de produto; a spec consolidada permanece válida (`skip_specs: true`).
