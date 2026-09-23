## 1. Backend Contract

- [x] 1.1 Criar o endpoint técnico Xano/XanoScript de saúde da integração, sem autenticação ou acesso a dados de negócio, e verificar sua resposta HTTP e payload estruturado com uma chamada direta
- [x] 1.2 Configurar os parâmetros de ambiente necessários no backend, caso existam, e verificar que nenhum segredo ou endereço privado foi versionado

## 2. Reflex Integration

- [x] 2.1 Adicionar a configuração externa do destino Xano ao ambiente de execução da lógica Python/State do Reflex e verificar que a ausência dessa configuração produz uma falha explícita sem chamada implícita
- [x] 2.2 Conectar uma ação visível da página inicial ao State/lógica Python, fazer essa camada realizar a chamada HTTP ao endpoint técnico do Xano e verificar os estados de carregamento, sucesso, resposta inválida, erro HTTP e falha de rede
- [x] 2.3 Permitir nova tentativa após falha e verificar que a interface exibe somente dados técnicos do contrato, sem acessar entidades do domínio

## 3. End-to-End Verification

- [x] 3.1 Executar a aplicação Reflex com o destino Xano configurado na camada State/lógica Python e verificar a validação ponta a ponta pelo fluxo Interface Reflex → State/lógica Python → Xano
- [x] 3.2 Repetir a verificação com backend indisponível, resposta incompatível e configuração ausente, confirmando que os erros são tratados na camada State/lógica Python e que nenhum cenário é tratado como sucesso
- [x] 3.3 Validar que a mudança não cria, lê ou altera registros de autenticação, clientes, catálogo, carrinho, pedidos, pagamentos ou CRM
