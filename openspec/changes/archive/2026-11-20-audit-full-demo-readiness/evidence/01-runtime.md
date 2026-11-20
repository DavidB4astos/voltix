# Evidência 01 — Runtime e telas (20/11/2026)

## Objetivo

Inventariar rotas públicas e seções internas em 1280/768/375 px e avaliar as quatro jornadas da demo
sem qualquer mutação.

## Ambiente

- Servidor de produção local `http://localhost:3092` (instância limpa, respondendo HTTP 200).
- Chrome DevTools MCP com viewport emulado `1280x800x1`, `768x1024x1` e `375x812x1`, DPR 1,
  color scheme claro.
- Backend Xano real configurado no ambiente; nenhuma requisição de escrita emitida nesta auditoria.
- Baseline comparativo: `openspec/changes/archive/2026-11-20-audit-runtime-screens-and-flows/evidence/01-screen-inventory.md`.

## 1. Inventário de rotas (9 rotas × 3 viewports)

Para cada combinação foram medidos: `<h1>` renderizado, presença de texto "Carregando", excesso de
largura (`scrollWidth - clientWidth` do `<html>`) e badge "Built with Reflex".

| Rota | H1 | 1280 | 768 | 375 |
| --- | --- | --- | --- | --- |
| `/` | Tecnologia premium para elevar o seu setup. | carrega, overflow 0, sem badge | carrega, overflow 0, sem badge | carrega, overflow 0, sem badge |
| `/catalogo` | Catálogo de produtos | carrega, overflow 0, sem badge | carrega, overflow 0, sem badge | carrega, overflow 0, sem badge |
| `/cliente` | Minha conta | carrega, overflow 0, sem badge | carrega, overflow 0, sem badge | carrega, overflow 0, sem badge |
| `/carrinho` | Seu carrinho | carrega, overflow 0, sem badge | carrega, overflow 0, sem badge | carrega, overflow 0, sem badge |
| `/checkout` | Checkout | carrega, overflow 0, sem badge | carrega, overflow 0, sem badge | carrega, overflow 0, sem badge |
| `/pedidos` | Meus pedidos | carrega, overflow 0, sem badge | carrega, overflow 0, sem badge | carrega, overflow 0, sem badge |
| `/interno` | Acesso interno | carrega, overflow 0, sem badge | carrega, overflow 0, sem badge | carrega, overflow 0, sem badge |
| `/interno/recuperar-senha` | Recuperar senha | carrega, overflow 0, sem badge | carrega, overflow 0, sem badge | carrega, overflow 0, sem badge |
| `/interno/redefinir-senha` | Redefinir senha | carrega, overflow 0, sem badge | carrega, overflow 0, sem badge | carrega, overflow 0, sem badge |

Total: 27 combinações rota/viewport, todas com `overflow=0`, nenhum texto "Carregando" residual e
nenhum badge do framework. Nenhuma regressão responsiva em relação ao baseline.

## 2. Console do navegador

Nenhuma mensagem `[error]` ou `[warn]` em qualquer rota, em 1280 px ou 375 px. Mensagens
informativas/accessibility:

| Rota | Mensagem | Classificação |
| --- | --- | --- |
| `/catalogo` | `[issue] A form field element should have an id or name attribute (count: 1)` | pós-entrega (acessibilidade) |
| `/cliente`, `/interno`, `/interno/recuperar-senha`, `/interno/redefinir-senha` | `[issue] An element doesn't have an autocomplete attribute` + `[verbose] [DOM] Input elements should have autocomplete attributes` | pós-entrega (acessibilidade) |

Falso positivo identificado: a árvore de acessibilidade mostra um nó `generic description="Connection
Error:"` na raiz da página; no DOM ele é um `<div title="Connection Error: ">` vazio, sem texto
visível e sem efeito na interface. Não é erro de conexão real.

## 3. Jornada catálogo → detalhe → carrinho

- `/catalogo` exibe `Catálogo · 20 produtos`, filtro por categoria, busca e `Limpar filtros` desabilitado
  no estado inicial.
- Cards mostram `a partir de R$ 119,90`, `a partir de R$ 59,90`, `a partir de R$ 349,90` etc. e o
  placeholder de imagem quando aplicável (`Imagem não disponível` presente no DOM).
- Clique em `Ver detalhes` no primeiro card abriu o painel "DETALHES DO PRODUTO" com imagem, SKU
  `VTX-DEMO-018`, `R$ 119,90`, `Disponível: 12 em estoque`, variações, especificações técnicas e botão
  de adicionar ao carrinho. **O botão de adicionar não foi acionado.**
- `/carrinho` sem sessão exibe corretamente "Seu carrinho começa na sua conta" / "Entre como Cliente
  para acessar seu carrinho".
- Nenhuma requisição `POST`/`PUT`/`PATCH`/`DELETE` foi registrada na rede durante a jornada.

## 4. Jornada ADMIN

- `/interno` sem sessão exibe o formulário "Entre com as credenciais do seu usuário interno" e o link
  de recuperação, sem vazar dados internos.
- A sessão de ADMINISTRADOR usada no baseline foi perdida quando o processo Chrome stale foi
  encerrado para destravar o DevTools; o perfil de teste não permite restabelecê-la sem credencial,
  e credenciais não foram lidas, exibidas ou reenviadas nesta auditoria.
- Portanto, as 9 seções internas (Dashboard, CRM, Clientes, Atendimentos, Pedidos, Produtos,
  Categorias e marcas, Importação, Usuários) **não foram reabertas ao vivo nesta execução**. A conferência
  de badges, ações e valores monetários em uma linha permanece registrada no baseline de 20/11 e na
  evidência final de `fix-demo-blockers` (tabela de pedidos com `R$ 119,90` e `R$ 2999,90`, sem
  quebras). Nenhuma ação de inativar, excluir ou avançar status foi executada.
- Classificação: **limitação documentada** para esta rodada, não bloqueador de demo — o comportamento
  já havia sido verificado com sessão válida na mesma data e o código não mudou desde `79f57a5`.

## 5. Login de Cliente (403 conhecido)

- `/cliente` exibe formulário de cadastro e formulário "Entrar como Cliente", ambos com os campos
  esperados; nenhum valor sensível é preenchido ou exposto no DOM.
- O 403 histórico na autenticação de Cliente não foi reemitido: refazer o login exigiria `POST` ao
  endpoint Xano, contrariando a regra desta change de não enviar `POST` e de não resetar senha.
- A jornada autenticada de Cliente (carrinho → checkout → pedidos) permanece como **limitação
  documentada**, com os estados de bloqueio de sessão verificados nas rotas `/carrinho`, `/checkout`
  e `/pedidos`.

## 6. Checkout/pedido simulado

- `/checkout` sem sessão mostra "Escolha a entrega, revise os valores e confirme seu pedido" e o bloco
  "Entre na sua conta para continuar" / "Entre como Cliente para finalizar o pedido".
- `/pedidos` mostra "Consulte o histórico e os valores registrados em cada compra" e o bloco "Seu
  histórico fica na sua conta".
- Não houve submissão de pedido nem de pagamento; a lista de requisições de rede não contém `POST`
  para `checkout`, `orders` ou `payment`.

## Limitações

- Sessão ADMINISTRADOR indisponível nesta execução; seções internas não reabertas ao vivo (item 4).
- Login de Cliente não reemitido para evitar `POST` e exposição de credenciais (item 5).
- Nenhuma captura PNG foi gerada: o inventário usa DOM, H1, overflow e console, conforme o padrão da
  auditoria anterior.
- Não foi repetida a varredura de 23 detalhes de produto que já provocou `ERROR_CODE_TOO_MANY_REQUESTS`
  no plano Free.
