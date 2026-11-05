## Context

See `proposal.md` for motivation. Estado atual: o checkout real valida estoque na confirmação
(`xano/api/customer/checkout_confirm_POST.xs`) dentro de `db.transaction`, mas **não baixa**
nem reserva estoque — a spec consolidada de `checkout-orders` impõe "It SHALL NOT introduce
stock reduction or reservation". A C1 foi adiada porque falta prova de runtime de que o
Xano do Voltix suporta decremento atômico guardado em transação. Esta change executa apenas
essa prova, com dados sintéticos, no workspace compartilhado — uma exceção documentada a E6,
autorizada pelo usuário em 04/11/2026, sem tocar dados demo ou reais.

Restições de plataforma (verificadas em 04/11/2026):
- Plano Free: 1 workspace, 10 req/20 s, sem branching e sem backup automático.
- O perfil Xano local `voltix` aponta para o workspace real; nenhum ambiente separado existe.
- Usuário optou por não fazer exportação/snapshot prévio (risco residual aceito).

## Goals / Non-Goals

**Goals:**
- Comprovar, no runtime Voltix, que `db.increment` com condição `where` guarda de estoque é
  atômico e não permite estoque negativo.
- Comprovar rollback completo de transação multi-item quando um item não tem estoque.
- Comprovar qual resposta o sistema produz na disputa concorrente pela última unidade e seu
  mapeamento para o contrato aprovado (HTTP 200 `confirmado=false`).
- Registrar evidência sanitizada e atualizar a documentação da C1 (decisão E6, estado).
- Produzir insumos para a decisão futura de implementar a C1.

**Non-Goals:**
- Implementar a baixa no checkout real, mudar specs consolidadas ou o Reflex.
- Testar com dados demo/reais, publicar no grupo de rotas do cliente ou do checkout real.
- Resolver upload de imagem, defaults de schema ou joins de carrinho/checkout.
- Criar um plano pago ou outra conta Xano.

## Decisions

1. **Pacote de prova isolado por nome e área**
   - Uma tabela sintética `test_c1_estoque` (SKU `TEST-C1-*`, `quantidade_disponivel` inteiro
     ≥ 0, `status`) e um grupo de rotas temporário `c1_prova_temp` com 1–2 queries:
     - `c1_prova_baixa_POST`: recebe `itens[] {sku, quantidade}`; em `db.transaction`, para
       cada item aplica `db.increment` negativo com `where` incluindo
       `quantidade_disponivel >= quantidade`; verifica linhas afetadas; se alguma for zero,
       lança erro para forçar rollback e responde `confirmado=false` com lista de itens
       indisponíveis.
     - `c1_prova_estado_GET`: leitura pura do estoque sintético para verificação.
   - Alternativa considerada: reutilizar tabelas demo — rejeitada (violaria o escopo e o E6).
   - Alternativa considerada: provar só com mocks/unit tests — rejeitada (mock não comprova
     o runtime; ver `docs/deferred-changes/2026-10-30-cart-join-runtime-tests/README.md`).

2. **Publicação restrita, sempre com dry-run**
   - Monta-se o pacote mínimo (somente os arquivos sintéticos acima) e faz-se `--dry-run`
     exibindo documentos e rotas antes de publicar. Nenhuma flag destrutiva é usada.
   - Após publicar, faz-se pull independente e compara-se **somente** o pacote pretendido.
   - A publicação real exige confirmação explícita do usuário no momento da execução.

3. **Casos de teste sintéticos** (ordem de execução):
   - A. Estoque suficiente: baixa aplicada, estoque decrementado exatamente.
   - B. Estoque insuficiente em item único: zero linhas afetadas, `confirmado=false`,
     estoque inalterado.
   - C. Dois itens, segundo sem estoque: transação reverte; ambos intactos.
   - D. Concorrência: duas requisições simultâneas sobre SKU `TEST-C1-LIMITE` com estoque 1;
     exatamente uma confirma; a outra `confirmado=false`; estoque final 0.
   - E. Cross-item order em concorrência (deadlock): duas transações com os mesmos dois SKUs
     em ordem inversa; observar e documentar comportamento (sucesso, erro ou timeout).

4. **Concorrência via chamadas HTTP paralelas** (script efêmero ou 2 chamadas simultâneas a
   partir de ferramenta local), respeitando o limite de 10 req/20 s; sem loop de stress.

5. **Limpeza verificável**: após os testes, remover/desabilitar rotas e tabela sintética
   (via UI do Xano se o CLI não oferecer remoção segura) e conferir com pull/GETs que
   nenhum SKU demo, pedido, cliente ou estoque real foi alterado. Listar no relatório o que
   ficou e o motivo, se algo permanecer.

6. **Evidência sanitizada**: guardar em `evidence/` respostas HTTP, contagens de linhas e
   pulls, sem dados reais nem tokens. Atualizar roadmap, defer da C1 e handoff com o
   resultado (GO/NO-GO para a change de implementação).

7. **Exceção a E6 registrada de forma permanente** no roadmap (decisão anotada com
   justificativa de dados fictícios e autorização do usuário em 04/11/2026).

## Risks / Trade-offs

- [Publicação acidental no fluxo de produção] → dry-run obrigatório, pacote mínimo,
  confirmação do usuário antes de publicar, rotas em grupo dedicado e nomeadas `c1_prova_*`.
- [Sem snapshot prévio (decisão do usuário)] → isolamento depende 100% de nunca tocar dados
  demo/reais; checklist de verificação no início e no fim da execução. Se detectada qualquer
  divergência, interromper e reportar imediatamente.
- [Limpeza incompleta de artefatos] → verificação explícita pós-execução; resíduos listados
  na evidência com justificativa; nunca usar `--delete`/`--records` como "atalho".
- [Rate limit do Free (10 req/20 s)] → testes serializados e poucos; concorrência limitada a
  2 requisições por cenário.
- [`db.increment` com comportamento diferente do documentado] → a prova existe justamente
  para descobrir isso; se não comprovar, a C1 permanece adiada e o resultado será registrado
  como tal (falha da prova ≠ autorização para alterar o checkout real).
- [Interferência com usuários do workspace] → execução fora de horários críticos e com
  aviso ao usuário antes de cada publicação.
- [Risco de ambiguidade sobre "confirmado=false"] → o mapeamento HTTP 200 é verificado
  apenas nos casos sintéticos; não será promovido a contrato final sem a change de C1.

## Migration Plan

1. Preparar pacote sintético no repositório (XanoScript local, grupo `c1_prova_temp`).
2. Dry-run e apresentação ao usuário; aguardar confirmação explícita.
3. Publicar somente o pacote; pull independente; conferência do pacote.
4. Executar casos A–E; registrar evidências.
5. Limpeza: desabilitar/remover rotas e tabela sintética (UI ou CLI conforme permitido);
   verificar que o workspace voltou ao estado esperado.
6. Atualizar docs (roadmap, defer, handoff) com resultado e decisão GO/NO-GO; commit focado.
7. Rollback/mitigação: se qualquer etapa afetar indevidamente dados existentes, parar,
   documentar o estado e aguardar decisão do usuário antes de qualquer outra publicação.

## Open Questions

- Como o runtime reporta as linhas afetadas por `db.increment` (erro vs. contagem zero) será
  confirmado durante a execução via pull/documentação oficial e registrado na evidência —
  não altera a abordagem nem as specs desta change.
