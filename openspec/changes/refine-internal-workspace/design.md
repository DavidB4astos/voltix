## Context
Reutilizar a implementação verificada C4 e componentes administrativos existentes. Hoje o login continua visível após autorização e as áreas são empilhadas no mesmo fluxo.

## Decisions
- Rota permanece /interno, sem nova API. Seleção local inicia em clientes, é reiniciada no login/logout e só aceita seções autorizadas. Seleção não dispara atualização ou mutação de dados.
- Navegação com botões nomeados, estado selecionado explícito e foco visível. Área principal tem título e descrição correspondentes; sem módulos futuros ou métricas simuladas.
- Sidebar navy, superfícies claras, cyan como acento e espaçamento mais generoso. CSS limitado a vx-internal; sem modificar a loja ou componentes compartilhados globalmente.
- Login separado do shell autenticado. Preservar formulário e fluxo de validação de sessão existentes, sem cadastro público interno.
- Guards de componentes administrativos e validações Xano continuam existentes. Esconder navegação não é mecanismo de autorização.

## Verification
Testes do seletor por perfil, valores inválidos e sessão não autorizada; suíte existente e compilação. Capturas desktop com dados fictícios/sem credenciais; verificar navegação por teclado, logout e ausência de links administrativos para Funcionário. Não executar mutações de catálogo durante QA. Arquivar só após verificação.
