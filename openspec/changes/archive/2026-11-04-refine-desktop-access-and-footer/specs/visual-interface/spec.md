## ADDED Requirements

### Requirement: Access surfaces and public footer have a cohesive desktop presentation
Em larguras de pelo menos 1024 px, os cartões de cadastro/login de Cliente e o cartão de login interno SHALL usar superfícies consistentes com a identidade visual Voltix, com hierarquia clara e acabamento refinado. Os cartões de entrada do Cliente SHALL acompanhar a altura do próprio conteúdo; o acesso interno SHALL usar o cabeçalho desktop compartilhado, indicar `/interno` como a rota atual e manter seu cartão de login centralizado na área principal. O rodapé público SHALL ocupar menos espaço vertical sem remover ou ocultar conteúdo, navegação ou avisos existentes. As mudanças SHALL preservar campos, textos, rotas, eventos, autorização e comportamento e SHALL NOT alterar o layout abaixo de 1024 px.

#### Scenario: Visitor opens customer sign-in and registration on desktop
- **WHEN** um visitante sem sessão abre `/cliente` em uma largura de pelo menos 1024 px
- **THEN** cadastro e login aparecem em cartões refinados lado a lado, cada um com altura adequada ao seu conteúdo
- **AND** os campos e ações existentes permanecem disponíveis

#### Scenario: Visitor opens internal access on desktop
- **WHEN** um visitante abre `/interno` em uma largura de pelo menos 1024 px
- **THEN** o cabeçalho usa os links desktop da loja, identifica Acesso interno como a rota atual e preserva os destinos existentes
- **AND** o cartão de login usa o acabamento Voltix e fica centralizado entre o cabeçalho e o rodapé

#### Scenario: Visitor reaches the public footer on desktop
- **WHEN** um visitante visualiza o rodapé público em uma largura de pelo menos 1024 px
- **THEN** o rodapé tem espaçamento vertical mais compacto e mantém marca, descrições, links, conteúdo de projeto e aviso de preços simulados

#### Scenario: Visitor uses access pages below desktop width
- **WHEN** um visitante abre `/cliente` ou `/interno` abaixo de 1024 px
- **THEN** os estilos desta change não alteram os layouts responsivos existentes
