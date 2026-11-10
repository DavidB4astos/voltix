# Verificação local — 10/11/2026

## Escopo verificado

- Contrato Python em `voltix/internal_users.py`: allowlist de campos, validação de
  nome, e-mail, senha (8+ caracteres, letra e número), perfil, status e payloads de
  criação, edição parcial, perfil próprio e troca de senha.
- Handlers em `voltix/voltix.py`: listagem, criação, edição, inativação/reativação
  em dois passos, perfil próprio e troca de senha, todos server-side com token
  interno e geração para descartar respostas obsoletas.
- Navegação: seção `usuarios` só para ADMINISTRADOR; `perfil` para ambos os perfis;
  valores desconhecidos ou não autorizados são rejeitados.
- XanoScript: autorização antes do negócio, allowlists, ausência de `db.del user`,
  proteção do último administrador ativo e ausência de credenciais nas respostas.

## Comandos e resultados

```text
python -m unittest discover -s tests -q
Ran 389 tests in 4.922s
OK

python -m reflex compile
Success: App compiled successfully

openspec validate implement-internal-user-management --strict
Change 'implement-internal-user-management' is valid

git diff --check
sem erros (apenas avisos de normalização LF/CRLF)
```

`reflex.lock/bun.lock` e `reflex.lock/package.json` foram restaurados com
`git checkout --`; nenhuma migração de dependências foi incluída.

## Limitações

- O teste autenticado positivo com usuário sintético não foi executado: exige
  criação de usuário real e autorização separada para escrita no Xano.
- A validação visual responsiva (375/768/1280) não foi executada nesta change.
