## 1. Preparação

- [ ] 1.1 Confirmar `.env` preenchido, portas livres e ausência de change ativa concorrente — verificação: `reflex` sobe sem erro de configuração
- [ ] 1.2 Subir o app e confirmar que a home responde — verificação: HTTP 200 em `/`
- [ ] 1.3 Confirmar contas de Visitante, Cliente, FUNCIONARIO e ADMINISTRADOR — verificação: cada perfil autentica ou o bloqueio é registrado

## 2. Inventário de telas

- [ ] 2.1 Percorrer as 7 rotas públicas e registrar carregamento, estados e ações — verificação: cada rota tem evidência
- [ ] 2.2 Percorrer as 7 seções internas com ADMINISTRADOR — verificação: cada seção tem evidência ou bloqueio
- [ ] 2.3 Repetir as seções permitidas com FUNCIONARIO — verificação: diferença de permissão registrada
- [ ] 2.4 Registrar telas citadas na interface que não existem — verificação: lista de links/botões sem destino, se houver

## 3. Jornadas

- [ ] 3.1 Visitante: home, catálogo, busca, filtro por categoria, detalhe e variações — verificação: sequência concluída
- [ ] 3.2 Cliente: login, conta, endereços, carrinho, checkout e pedidos — verificação: sequência concluída sem gravar pedido
- [ ] 3.3 FUNCIONARIO: dashboard, clientes, atendimentos e pedidos — verificação: consulta concluída sem alterar registros
- [ ] 3.4 ADMINISTRADOR: catálogo, produtos, importação e transições permitidas — verificação: navegação concluída sem salvar
- [ ] 3.5 Registrar como bloqueadas as ações de escrita não executadas (compra, upload, importação, inativação, exclusão) — verificação: cada bloqueio tem motivo e impacto

## 4. Responsivo

- [ ] 4.1 Verificar 375, 768 e 1280 px nas telas públicas principais — verificação: overflow e sobreposição registrados
- [ ] 4.2 Verificar as mesmas larguras nas telas internas — verificação: overflow e sobreposição registrados

## 5. Defeitos e classificação

- [ ] 5.1 Consolidar cada defeito com rota, perfil, ação, esperado, obtido e severidade — verificação: nenhum defeito sem evidência
- [ ] 5.2 Classificar em bloqueador de demo, correção imediata, pós-entrega ou falso positivo — verificação: lista priorizada
- [ ] 5.3 Derivar o escopo fechado da change de correção — verificação: cada item tem critério de aceite

## 6. Fechamento

- [ ] 6.1 Registrar `evidence/01-screen-inventory.md` e `evidence/02-defects.md` sanitizados — verificação: nenhuma captura ou texto expõe dado pessoal
- [ ] 6.2 Validar `openspec validate audit-runtime-screens-and-flows --strict`, `openspec validate --all --strict` e `git diff --check` — verificação: tudo verde
- [ ] 6.3 Arquivar a change e registrar o resultado em `docs/roadmap-changes.md` — verificação: documentação consistente
- [ ] 6.4 Commit e push somente com autorização explícita — verificação: `git status --short --branch`
