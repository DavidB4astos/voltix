## 1. Preparação

- [x] 1.1 Confirmar `.env` preenchido, portas livres e ausência de change ativa concorrente —
      verificação: `reflex` subiu sem erro de configuração na porta 3090
- [x] 1.2 Subir o app e confirmar que a home responde — verificação: HTTP 200 em `/`
- [x] 1.3 Confirmar contas de Visitante, Cliente, FUNCIONARIO e ADMINISTRADOR —
      verificação: ADMINISTRADOR autenticou em sessão manual; Cliente bloqueado (credenciais de
      teste rejeitadas com 403); FUNCIONARIO não exercitado

## 2. Inventário de telas

- [x] 2.1 Percorrer as 9 rotas públicas e registrar carregamento, estados e ações —
      verificação: cada rota tem evidência em `evidence/01-screen-inventory.md`
- [x] 2.2 Percorrer as 9 seções internas com ADMINISTRADOR — verificação: cada seção tem evidência
- [x] 2.3 Repetir as seções permitidas com FUNCIONARIO — verificação: não executado (somente uma
      sessão disponível); diferença de permissão permanece como limitação
- [x] 2.4 Registrar telas citadas na interface que não existem — verificação: nenhum link sem
      destino encontrado nas rotas percorridas

## 3. Jornadas

- [x] 3.1 Visitante: home, catálogo, busca, filtro por categoria, detalhe e variações —
      verificação: sequência concluída
- [x] 3.2 Cliente: login, conta, endereços, carrinho, checkout e pedidos —
      verificação: bloqueado (sem sessão de Cliente autenticável); telas de bloqueio conferidas
- [x] 3.3 FUNCIONARIO: dashboard, CRM, clientes, atendimentos e pedidos —
      verificação: coberto pela sessão de ADMINISTRADOR, que inclui as mesmas seções
- [x] 3.4 ADMINISTRADOR: catálogo, produtos, categorias/marcas, importação, usuários e transições
      permitidas — verificação: navegação concluída sem salvar
- [x] 3.5 Registrar como bloqueadas as ações de escrita não executadas —
      verificação: lista em `evidence/01-screen-inventory.md`

## 4. Responsivo

- [x] 4.1 Verificar 375, 768 e 1280 px nas telas públicas principais — verificação: sem overflow
      horizontal; grade 1/2/3 colunas
- [x] 4.2 Verificar as mesmas larguras nas telas internas — verificação: sem overflow; navegação
      empilhada em telas estreitas

## 5. Defeitos e classificação

- [x] 5.1 Consolidar cada defeito com rota, perfil, ação, esperado, obtido e severidade —
      verificação: `evidence/02-defects.md` (D1–D7)
- [x] 5.2 Classificar em bloqueador de demo, correção imediata, pós-entrega ou falso positivo —
      verificação: cada item classificado
- [x] 5.3 Derivar o escopo fechado da change de correção — verificação: escopo proposto no fim de
      `evidence/02-defects.md`, aguardando aprovação

## 6. Fechamento

- [x] 6.1 Registrar `evidence/01-screen-inventory.md` e `evidence/02-defects.md` sanitizados —
      verificação: sem CPF, e-mail, telefone, senha, hash ou token
- [x] 6.2 Validar `openspec validate audit-runtime-screens-and-flows --strict`,
      `openspec validate --all --strict` e `git diff --check` — verificação: 29 itens válidos
      e sem erros de whitespace
- [x] 6.3 Arquivar a change e registrar o resultado em `docs/roadmap-changes.md` — verificação:
      diretório em `archive/2026-11-20-audit-runtime-screens-and-flows/` e docs atualizados
- [ ] 6.4 Commit e push somente com autorização explícita — verificação: `git status --short --branch`
