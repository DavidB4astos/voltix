# Design — acessos e rodapé no desktop

## Decisões

- Preservar o cabeçalho desktop comum da loja navy/cyan e permitir `/interno` como rota ativa da navegação. O acesso interno permanece um link secundário destacado, com os mesmos estilos de foco e altura dos outros links.
- Dar ao cartão de login interno e aos cartões de cadastro/login de Cliente bordas, raios e sombras sutis coerentes com as superfícies existentes. Não sugerir que os cartões sejam interativos.
- Centralizar verticalmente o cartão de login interno na área entre cabeçalho e rodapé em desktop.
- Reduzir espaçamentos verticais e lacunas das colunas do rodapé público, mantendo links com alvo confortável, textos, navegações e nota acadêmica.
- Limitar todos os ajustes específicos a `@media (min-width: 1024px)`. A estrutura compacta/mobile existente não muda.

## Restrições

- Não alterar `State`, handlers, acesso, rotas, conteúdo, campos, chamadas ou dados.
- Não modificar a área interna autenticada nem o shell interno de administração.
- Não alterar imagens ou outras páginas além do cabeçalho compartilhado e rodapé visual associado.

## Verificação

- Validar os artefatos OpenSpec em modo estrito e revisar o diff.
- Conferir visualmente `/cliente` e `/interno` em desktop, sem submeter formulários ou alterar dados.
