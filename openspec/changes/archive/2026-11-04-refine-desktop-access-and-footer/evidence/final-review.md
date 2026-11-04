# Revisão final — acessos e rodapé no desktop

## Implementação

- `/cliente`: os cartões de cadastro e login mantêm seus formulários e ações, exibem bordas e elevação discretas com acentos navy/cyan e aparecem lado a lado a partir de 1024 px. O cartão de login acompanha a altura do seu conteúdo.
- `/interno`: usa o cabeçalho desktop compartilhado, indica a rota atual no link Acesso interno, apresenta o cartão de login centralizado e usa o rodapé público compacto.
- Rodapé: reduzidos espaçamentos verticais, lacunas entre colunas e altura dos links; marca, descrições, links, conteúdo do projeto e aviso de preços simulados permanecem presentes.
- Os estilos novos permanecem restritos a larguras desktop (`min-width: 1024px`).

## Verificação

- `openspec validate 2026-11-04-refine-desktop-access-and-footer --strict`: aprovado.
- `git diff --check`: aprovado.
- `python -m py_compile voltix/voltix.py`: aprovado.
- Prévia visual em desktop do app local: conferidos `/interno` (cabeçalho, cartão e rodapé) e `/cliente` (ambos os cartões), sem enviar formulários ou alterar dados.
- Não foram executados testes automatizados. Os arquivos gerados de dependências `reflex.lock/bun.lock` e `reflex.lock/package.json` foram restaurados e ficaram fora do escopo.
