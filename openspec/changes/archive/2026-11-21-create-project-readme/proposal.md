## Why

A entrega acadêmica do projeto Voltix exige um `README.md` na raiz do repositório público do GitHub funcionando como manual de uso completo do aplicativo web para qualquer pessoa interessada. Atualmente o repositório não possui `README.md` na raiz.

## What Changes

- Criar `README.md` na raiz do repositório seguindo fielmente a estrutura solicitada:
  1. **Apresentação**: nome, breve descrição, problema que resolve e público-alvo.
  2. **Acesso ao aplicativo**: rotas principais, execução local com Reflex e variáveis de ambiente esperadas (referenciando `.env.example`, sem segredos).
  3. **Perfis de usuários**: `Visitante`, `Cliente`, `Funcionário` e `Administrador`, com suas responsabilidades e permissões.
  4. **Funcionalidades**: e-commerce, painel administrativo e CRM integrado.
  5. **Manual de utilização**: passo a passo organizado por perfil e jornada (ações e resultados esperados).
  6. **Exemplos de utilização**: cenário ponta a ponta com dados estritamente fictícios (sem expor CPF, e-mail, senha ou token reais).
  7. **Limitações conhecidas**: estágio transparente da versão entregue (pagamento simulado, sem emissão fiscal/frete real, upload de imagem no Xano Free, ambiente acadêmico).
- **Fora do escopo:** alterações em código Python/CSS, Xano, specs consolidadas ou inclusão de credenciais/dados reais.

## Capabilities

### New Capabilities

- Nenhuma.

### Modified Capabilities

- Nenhuma (`skip_specs: true` em `.openspec.yaml`).

## Impact

- **Worktree:** `.worktrees/create-project-readme` (branch `create-project-readme`).
- **Arquivos:** `README.md` na raiz do repositório.
- **Gates:** `git diff --check`, `openspec validate --all --strict` (e conferência de ausência de dados sensíveis).
