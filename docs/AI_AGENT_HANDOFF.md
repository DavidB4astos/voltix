# Handoff para agente de IA — Voltix

> Atualizado em 03/11/2026. Este documento resume o trabalho já realizado,
> o estado verificável do repositório e as regras para continuar o projeto com
> segurança. Não contém senhas, tokens, URLs privadas de credenciais ou dados
> pessoais de clientes.

## 1. Projeto e arquitetura

Voltix é um e-commerce acadêmico de tecnologia integrado a recursos internos
de CRM. A arquitetura aprovada é fixa:

- **Frontend:** Reflex/Python.
- **Backend e dados:** Xano/XanoScript.
- **Versionamento:** Git e GitHub.
- **Método de mudança:** OpenSpec.

Três perfis existem no produto:

- **Cliente:** catálogo, conta, carrinho, checkout e pedidos próprios.
- **Funcionário:** consulta interna de clientes.
- **Administrador:** consulta de clientes e gestão de produtos, categorias,
  marcas e importação.

Leia obrigatoriamente antes de qualquer alteração:

1. `AGENTS.md`
2. `docs/project-overview.md`
3. `docs/domain-model.md`
4. `docs/roadmap-changes.md`
5. `openspec/config.yaml`

As decisões em documentação não devem ser alteradas por suposição. Frontend,
backend e persistência devem permanecer separados. Autenticação e autorização
precisam ser garantidas pelo Xano, não só pela interface.

## 2. Regra de trabalho obrigatória

Trabalhe em **uma change por vez**:

1. Inspecione documentação, specs consolidadas e changes arquivadas.
2. Defina escopo e peça aprovação antes de criar ou alterar uma change.
3. Crie `proposal.md`, `design.md`, `tasks.md` e, se necessário, deltas em
   `specs/<capability>/spec.md`.
4. Valide com `openspec validate <change-id> --strict`.
5. Implemente apenas as tarefas aprovadas.
6. Execute verificações proporcionais ao escopo e registre evidências sem
   expor dados pessoais.
7. Atualize tarefas, faça a revisão final, arquive a change e valide todas as
   specs.
8. Faça um commit focado e confirme `git status --short --branch`.

Não arquive uma change somente porque o código compila. Arquivamento exige
escopo concluído, evidências e limitações documentadas. Não misture mudança
visual, alteração de negócio e publicação Xano na mesma change sem justificativa
explícita.

## 3. Segurança, privacidade e Xano

Nunca imprima, copie para documentos ou versione:

- `.env`, credenciais Xano, tokens, chaves de API ou conteúdo de snapshots que
  os contenham;
- dados reais de clientes, CPF sem máscara, senhas, hashes, e-mails ou pedidos;
- capturas de tela contendo registros reais.

O perfil Xano local se chama `voltix`; o workspace padrão usado pelo projeto é
o ambiente real. Portanto:

- faça **dry-run** antes de qualquer publicação;
- mostre claramente ao usuário quais documentos e rotas serão publicados;
- publique somente um pacote mínimo criado para a change, nunca o workspace
  inteiro;
- não use flags perigosas como `--force`, `--sync`, `--delete`, `--records`,
  `--env`, `--truncate` ou `--no-transaction`;
- após publicar, faça um pull independente e compare somente as queries
  pretendidas;
- não altere registros reais para provar testes.

O plano Xano atual é gratuito. Não existe ambiente isolado aprovado e o
sandbox automático do Xano não foi considerado disponível no plano atual.
Qualquer teste que escreva dados (compra, checkout, estoque, cancelamento,
importação real) exige ambiente isolado, autorizado e sem dados reais.

## 4. Estado do Git e do OpenSpec

No momento deste handoff, a branch local `main` está **1 commit à frente** de
`origin/main`:

- `2272578 docs: record administrator audit pending employee check`

Antes de prosseguir, confira o estado real com:

```powershell
git status --short --branch
git log --oneline -8
openspec list
```

Não faça `push` automaticamente. Peça confirmação ao usuário ou siga uma
autorização explícita já dada. A identidade Git aprovada para este repositório
é `David Bastos <david.bastos@live.com>`.

### Change ativa — não arquivar ainda

`openspec/changes/audit-internal-desktop-flow/`

Estado registrado: **3/6 tarefas**. A auditoria já verificou visualmente a
área interna como Administrador, mas falta concluir e registrar a verificação
como Funcionário. O usuário já informou que entrou nessa conta de teste; a
sessão do navegador deve ser reconferida antes de considerar a tarefa pronta.

Evidências já registradas nessa change:

- `01-admin-customers.*`
- `02-admin-products.*`
- `03-admin-catalog.*`
- `03b-admin-brands.png`
- `04-admin-import.*`
- `05-sign-out.*`
- `admin-observations.md`

Para finalizar a auditória, confirmar no perfil Funcionário:

- apenas **Clientes** fica disponível no menu;
- Produtos, Categorias/marcas e Importação não aparecem nem ficam acessíveis;
- nenhuma lista de clientes é carregada sem ação explícita;
- não há mutação de dados;
- registrar captura/evidência final e limitações;
- só então marcar tarefas, arquivar com OpenSpec, validar e criar commit
  documental.

## 5. Trabalho implementado e verificado

### Loja pública e desktop

A Home pública foi refinada em changes arquivadas para uma aparência premium:

- identidade navy/cyan preservada;
- hero editorial sem eyebrow/kicker, com mídia local e proveniência;
- benefícios em faixa editorial;
- categorias em apresentação tipográfica;
- vitrine de produtos com estados de carregamento, vazio e erro distintos;
- seção editorial e créditos de imagem;
- cabeçalho desktop refinado com Início, Produtos, Minha conta, Carrinho e
  Acesso interno.

As páginas desktop de catálogo, detalhes de produto, conta, carrinho, checkout,
pedidos e rodapé também receberam refinamentos arquivados. O foco aprovado foi
desktop: o layout compacto/mobile não deve ser apresentado como revisão móvel
concluída.

`localhost:3000` e `127.0.0.1:3000` mostraram aparência diferente em certa
ocasião, mas a investigação confirmou que a causa era a **largura do viewport**:
o cabeçalho compacto aparece em largura menor. Não eram duas versões do app.

### Área interna desktop

As seguintes changes foram concluídas e arquivadas:

- `refine-internal-workspace`: shell interno, sidebar e navegação por papel.
- `refine-internal-customers-desktop`: consulta somente leitura, filtros,
  máscara e detalhe de cliente.
- `refine-internal-products-desktop`: gestão de produtos e variações.
- `refine-internal-catalog-desktop`: categorias e marcas.
- `refine-internal-import-desktop`: apresentação da importação em massa.

O controle de seção interno deve continuar restrito no `State`:

- Funcionário: somente `clientes`.
- Administrador: `clientes`, `produtos`, `catalogo`, `importacao`.

Os refinamentos de Importação, Categorias e Marcas preservaram State, handlers,
parsers, limites e Xano. Foram testados com dados fictícios/isolados; importação
real não foi executada.

### Xano — reconciliações já publicadas e verificadas

Foram publicadas mudanças pequenas e específicas, todas com dry-run, pull
posterior e sem modificar registros reais:

1. `harden-published-legacy-customers`
   - proteção de quatro rotas legadas de cliente;
   - leitura própria e ativa; PATCH com whitelist; DELETE autorizado mas negado;
   - cadastro POST preservado.
2. `reconcile-xano-group-identifiers`
   - alinhamento local dos identificadores de grupos Product Management e
     Public Catalog; sem alteração de URLs ou metadados remotos.
3. `reconcile-admin-product-reads`
   - GETs administrativos de produtos e variações com guarda de Administrador,
     allowlists e ordenação.
4. `reconcile-public-catalog-ordering`
   - ordenação de categorias e variações no catálogo público.
5. `reconcile-cart-checkout-ordering`
   - ordenação determinística de itens de carrinho/checkout.

**Não declarar que todo o Xano está sincronizado.** Permanecem pendências de
joins de carrinho/checkout, defaults de schema, comportamento de upload e uma
tabela remota temporária que não deve ser excluída por suposição. Consulte:

- `docs/auditorias/xano-sync-2026-10-30.md`
- `docs/deferred-changes/2026-10-30-cart-join-runtime-tests/README.md`

### Estoque e checkout

Baixa/reserva atômica de estoque (C1) está formalmente adiada. O Xano Free não
ofereceu uma solução comprovada para a atomicidade multi-item necessária. O
checkout atual valida disponibilidade, mas não pode ser descrito como baixa ou
reserva de estoque. Não implementar solução baseada em suposição.

### Imagens de produto

Há infraestrutura de imagens locais e créditos em `assets/demo/manifest.json`.
Quinze de vinte fotos foram aprovadas. Ainda faltam imagens com modelo/direitos
verificados para: G203 LIGHTSYNC, M90, WD SN580 1TB, Ryzen 5 5600 e Archer C6.
Não usar imagem genérica, modelo parecido ou imagem gerada por IA para representar
um SKU real sem licença/proveniência adequada.

## 6. Como executar e verificar localmente

Repositório local esperado:

```text
C:\Users\David Bastos\Downloads\PROJETO VOLTIX\PROJETO VOLTIX\voltix
```

Ambiente Python do projeto:

```text
.venv-windows\Scripts\python.exe
```

Verificação de testes a partir da raiz do repositório:

```powershell
& '.\.venv-windows\Scripts\python.exe' -m unittest discover -s tests -q
```

A suíte mais recente registrada teve **188 testes aprovados**. Execute somente
os testes pertinentes quando a change for documental; não gere ruído rodando
toda a aplicação sem necessidade.

O Reflex pode alterar arquivos de dependência gerados em `reflex.lock` durante
compilação local. Não comite uma migração acidental de Bun para npm. Preserve uma
cópia local em área não versionada, revise e restaure arquivos versionados caso
a change não seja uma migração de dependências aprovada.

Para validar uma change:

```powershell
openspec validate <change-id> --strict
```

Para validar tudo após arquivar:

```powershell
openspec validate --all --strict
git diff --check
git status --short --branch
```

## 7. Próximas prioridades recomendadas

1. **Concluir `audit-internal-desktop-flow`** sem ampliar escopo.
2. Abrir uma change pequena, se o usuário aprovar, para corrigir achados da
   auditoria: associação de labels no login interno, múltiplos `h1`, formatação
   monetária e eventual contraste de texto auxiliar. Não implemente esses
   ajustes dentro da auditoria sem mudança aprovada.
3. Após C1 ter solução técnica comprovada, seguir a sequência do roadmap:
   cancelamento de pedido (C2), gestão de pedidos (C3), dashboard (C10),
   histórico CRM (C6) e atendimentos (C7).
4. Manter C1 e testes de compra E2E bloqueados até haver ambiente Xano isolado
   e autorizado.
5. Retomar o trabalho mobile somente com uma change própria.
6. Completar as cinco imagens de produto pendentes somente quando houver fonte,
   modelo e direitos comprovados.

CRM ainda não está completo: a consulta de clientes (C4) existe; histórico de
cliente, atendimentos, pedidos internos e dashboard continuam capabilities
futuras e dependem da ordem de negócio documentada.

## 8. Comandos e decisões que exigem cuidado

Use `rg` para localizar arquivos. Para Git, evite `reset --hard` e checkout
destrutivo. Para Xano, não use push global ou flags destrutivas. Não inclua
`.env`, logs de credenciais, snapshots brutos ou artefatos temporários no Git.

Antes de criar uma nova change, confirme se algo equivalente já está arquivado
em `openspec/changes/archive/` ou registrado em `docs/deferred-changes/`.
Uma change adiada é uma limitação documentada, não um recurso entregue.

## 9. Referências rápidas

- Planejamento geral: `docs/roadmap-changes.md`
- Auditoria de sincronização Xano: `docs/auditorias/xano-sync-2026-10-30.md`
- Specs consolidadas: `openspec/specs/`
- Changes abertas: `openspec/changes/`
- Changes concluídas: `openspec/changes/archive/`
- Adiamentos: `docs/deferred-changes/`
- Regras permanentes: `AGENTS.md`

Ao terminar uma sessão, deixe o repositório limpo ou explique exatamente os
arquivos pendentes, o motivo e a próxima ação segura. O próximo agente deve
preferir evidência verificável a suposições, especialmente em Xano, dados de
clientes, permissões e estoque.
