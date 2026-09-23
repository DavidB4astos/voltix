## Why

O projeto já possui uma aplicação Reflex mínima e artefatos Xano/XanoScript, mas ainda não há um contrato verificado que demonstre a comunicação ponta a ponta entre essas duas camadas. Validar essa integração agora reduz o risco de iniciar as funcionalidades de negócio sobre uma arquitetura ou configuração incompatível.

## What Changes

- Definir uma capacidade de integração mínima entre o frontend Reflex e o backend Xano.
- Estabelecer um cenário técnico de verificação ponta a ponta, limitado à comunicação e à resposta de saúde/conectividade.
- Documentar o contrato de configuração, o fluxo de requisição e os critérios de sucesso e falha da validação.
- Não implementar autenticação, clientes, categorias, marcas, produtos, carrinho, pedidos, pagamentos, CRM ou qualquer outro fluxo de negócio.

## Capabilities

### New Capabilities

- `reflex-xano-integration`: Integração mínima e verificável entre a aplicação Reflex existente e um endpoint técnico do backend Xano.

### Modified Capabilities

Nenhuma.

## Impact

- Afeta a aplicação Reflex em `voltix/`, sua configuração de execução e a comunicação HTTP com o backend Xano.
- Afeta o contrato técnico de um endpoint Xano/XanoScript dedicado à verificação da integração, sem alterar entidades ou regras do domínio.
- Requer configuração segura e separada para a URL/base do backend, sem expor credenciais ou dados sensíveis.
- Requer validação local ou de ambiente configurado, incluindo resposta bem-sucedida e tratamento explícito de falha de comunicação.
- Não altera o modelo de domínio documentado nem os artefatos Xano de autenticação e negócio existentes.
