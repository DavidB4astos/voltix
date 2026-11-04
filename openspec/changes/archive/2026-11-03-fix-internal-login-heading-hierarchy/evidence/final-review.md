# Revisão final — hierarquia do login interno

Data: 03/11/2026.

## Resultado

A marca reutilizável `brand_logo` agora declara `as_="h2"`, mantendo o texto Voltix e os parâmetros existentes de tamanho, cor e espaçamento. O título da tela “Acesso interno” não foi alterado e continua sendo o único `h1` da tela de login. Nenhum handler, atributo de credencial, autenticação, endpoint ou dado foi modificado.

## Verificação

- `openspec validate fix-internal-login-heading-hierarchy --strict`: aprovado.
- `git diff --check`: sem erros.
- Inspeção do diff confirmou que a alteração funcional se limita a um atributo em `brand_logo`.
- Não foram executados testes automatizados nem QA visual no navegador nesta etapa.
- Os lockfiles regenerados durante a validação foram restaurados; não fazem parte da change.

## Limites

A inspeção confirma a hierarquia semântica declarada no componente, mas não inclui conferência visual ou leitura por tecnologia assistiva no navegador. A mudança afeta o componente compartilhado de marca em seus usos no cabeçalho, rodapé e shell interno, preservando sua aparência.
