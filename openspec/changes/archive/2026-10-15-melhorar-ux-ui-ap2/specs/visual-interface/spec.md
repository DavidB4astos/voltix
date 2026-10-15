## ADDED Requirements

### Requirement: Shared presentation primitives for feedback, status, and actions
O Voltix SHALL fornecer primitivas de apresentação reutilizáveis — alerta de feedback com tom semântico (erro, sucesso, aviso, neutro), badge de status e botões padronizados (primário, secundário, destrutivo) — aplicadas de forma consistente nas páginas existentes, sem alterar handlers, State, rotas ou textos funcionais.

#### Scenario: Feedback message uses a semantic tone
- **WHEN** uma tela existente apresenta erro, sucesso, aviso ou mensagem neutra
- **THEN** a mensagem é exibida com o mesmo tratamento visual do tom correspondente em todas as páginas

#### Scenario: Status is shown as a semantic badge
- **WHEN** um Pedido ou um Produto/Variação exibe seu status
- **THEN** o status aparece como um badge com cor semântica consistente, preservando o texto funcional existente

#### Scenario: Actions use standardized buttons
- **WHEN** um usuário aciona uma ação primária, secundária ou destrutiva
- **THEN** o botão segue o mesmo padrão visual em toda a aplicação, preservando rótulos e comportamento

### Requirement: Storefront and purchase surfaces align content across breakpoints
Os cards do catálogo e as superfícies de carrinho, checkout e pedidos SHALL manter alinhamento consistente de imagem, preço, status e ações em 375, 768 e 1280 px, sem rolagem horizontal e sem remover campos, ações ou mensagens existentes.

#### Scenario: Catalog cards at multiple widths
- **WHEN** o catálogo é exibido em larguras mobile, tablet ou desktop
- **THEN** os cards alinham imagem, preço e ação de forma legível, formando uma grade responsiva sem overflow

#### Scenario: Purchase summary on a narrow viewport
- **WHEN** o cliente visualiza carrinho, checkout ou pedido em tela estreita
- **THEN** resumo, totais, status e ações permanecem visíveis e legíveis sem rolagem horizontal

### Requirement: Administrative panel receives visual-only adjustments
O painel administrativo SHALL receber apenas ajustes visuais simples (espaçamento, agrupamento em cards e uso das primitivas compartilhadas), preservando a navegação, a estrutura das páginas, os controles condicionais e as permissões de Administrador existentes.

#### Scenario: Administrator uses the panel after adjustments
- **WHEN** um Administrador utiliza o painel administrativo
- **THEN** os mesmos campos, controles e permissões permanecem disponíveis, com apresentação visual consistente e sem reestruturação de navegação
