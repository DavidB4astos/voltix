## 1. Backend público

- [x] 1.1 Criar endpoints Xano somente GET para listar Categorias `ATIVO`, listar Produtos `ATIVO` com filtro opcional por Categoria `ATIVO` e obter detalhes de Produto `ATIVO` com Variações `ATIVO`; verificar as projeções e os filtros com validação XanoScript e testes de contrato.
- [x] 1.2 Adicionar assinatura temporária para imagens principais privadas nos retornos públicos sem incluir o caminho original; verificar resposta com e sem imagem e confirmar que nenhuma operação altera tabelas.

## 2. Catálogo Reflex

- [x] 2.1 Implementar consultas anônimas no State/Python para categorias, lista filtrada e detalhes, com validação de resposta e tratamento observável de erro; verificar com testes unitários que chamadas HTTP permanecem server-side e não enviam token.
- [x] 2.2 Criar rota pública Reflex independente do login interno para listar e filtrar produtos, abrir detalhes e apresentar variações ativas com preço, estoque e indicação de estoque zero; verificar acesso sem sessão e compilar a aplicação.
- [x] 2.3 Renderizar imagens somente pelas URLs temporárias assinadas, omitindo classificações inativas e preservando produtos com associações históricas; verificar os cenários sem imagem, URL expirada/erro e associação inativa.

## 3. Validação da Change

- [x] 3.1 Executar testes automatizados para filtros de status, categoria ativa/inativa, detalhes, variações, estoque zero, ausência de imagem, erros e ausência de autenticação; verificar que os endpoints e a interface não oferecem operações de escrita ou compra.

- [x] 3.2 Validar a integração anônima no ambiente Xano autorizado, sem criar ou alterar dados de domínio; se a publicação de dependências estiver bloqueada, registrar a limitação e não declarar E2E real concluído. Executar compilação Reflex e validação OpenSpec estrita. O E2E real ficou pendente pelo bloqueio abaixo; as validações locais passaram.

  **Bloqueio externo registrado:** as URLs `XANO_PUBLIC_*` não estão configuradas neste ambiente e a publicação Xano de `gestao-produtos` foi bloqueada por `allow_push: false`; E2E real do catálogo não foi executado nem é alegado.
