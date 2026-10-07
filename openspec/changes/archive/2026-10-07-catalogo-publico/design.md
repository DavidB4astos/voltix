## Context

Consulte [proposal.md](./proposal.md) para motivação e [specs/public-catalog/spec.md](./specs/public-catalog/spec.md) para o contrato funcional. A aplicação Reflex já centraliza chamadas Xano em lógica Python/State. Os GETs atuais de Produto e Categoria/Marca são administrativos; a imagem de Produto é gravada no armazenamento nativo do Xano com acesso privado. Produto mantém associações existentes mesmo quando Categoria ou Marca ficam inativas.

## Goals / Non-Goals

**Goals:**
- Separar leitura pública das operações administrativas já existentes.
- Entregar somente dados de catálogo necessários ao visitante, filtrados no backend.
- Manter o fluxo HTTP de dados como Interface Reflex -> State/lógica Python -> Xano.
- Disponibilizar imagens privadas sem expor o caminho de armazenamento.

**Non-Goals:**
- Alterar tabelas, status, vínculos ou endpoints das Changes administrativas.
- Tornar arquivos do catálogo permanentemente públicos.
- Introduzir autenticação de cliente ou qualquer operação de compra.

## Decisions

1. **Criar endpoints Xano de leitura pública separados.** Um endpoint lista categorias `ATIVO`; outro lista produtos `ATIVO` e aceita filtro opcional por categoria ativa; um endpoint de detalhes retorna apenas produto `ATIVO` e suas variações `ATIVO`. As respostas usam campos explicitamente selecionados, incluindo preço e quantidade no nível de VariaçãoProduto. A alternativa de reaproveitar GETs administrativos foi descartada porque eles exigem administrador e retornam estados que não são próprios da navegação pública.

2. **Manter a decisão de visibilidade no status da própria entidade.** Produto `ATIVO` permanece visível mesmo se uma associação histórica apontar para Categoria ou Marca `INATIVO`, coerente com a spec de gestão de produtos que preserva esses vínculos. Categorias inativas não são listadas nem aceitas como filtro; nomes de categorias e marcas inativas não são expostos como classificação pública. Nenhum status ou relacionamento será alterado como efeito da consulta.

3. **Usar página pública Reflex desacoplada da área interna.** Registrar uma rota própria (por exemplo, `/catalogo`) que não dependa do fluxo de login da página interna. Eventos de carregamento, filtro e detalhe acionam State/Python, que consulta os endpoints Xano via HTTP sem credencial administrativa. Não fazer chamadas de dados do catálogo diretamente do navegador.

4. **Assinar URLs de imagens no backend.** Para imagem privada, o endpoint de leitura obtém uma URL temporária assinada pelo armazenamento nativo Xano; somente essa URL é retornada para renderização, nunca o caminho privado. A alternativa de mudar os arquivos para acesso público foi descartada para não alterar a política de armazenamento já aprovada. A validade da URL é limitada pelo mecanismo de assinatura do Xano; o carregamento/atualização da página obtém URL nova quando necessário.

5. **Falhas permanecem explícitas.** State valida respostas e representa carregamento, resultado vazio e erro sem transformar uma falha de rede ou HTTP em catálogo vazio ou sucesso. As URLs dos endpoints públicos são configuráveis por ambiente e não requerem token.

## Risks / Trade-offs

- [Assinaturas de imagem expiram enquanto uma página permanece aberta] -> Obter uma URL nova ao recarregar os dados e oferecer nova tentativa; não persistir nem versionar URLs assinadas.
- [Endpoints sem autenticação podem ser consultados por qualquer pessoa] -> Limitar a operações GET, filtrar status no backend, selecionar apenas campos públicos e não incluir caminhos privados ou dados internos.
- [Produto ativo pode estar relacionado a categoria/marca inativa] -> Preservar a regra aprovada de não alterar vínculos existentes; omitir a classificação inativa sem ocultar o produto nem inferir uma cascata de status.
- [O ambiente Xano pode não conter as estruturas/endpoints de gestão de produtos] -> Publicar e verificar primeiro a dependência `gestao-produtos` no ambiente autorizado; se a publicação estiver bloqueada, não contornar a permissão e não declarar E2E real concluído.

## Migration Plan

1. Confirmar que Produto, VariacaoProduto, Categoria e Marca e os endpoints de gestão requeridos estão disponíveis no ambiente Xano autorizado.
2. Publicar os novos endpoints somente de leitura e configurar localmente as URLs públicas necessárias.
3. Implantar a rota pública Reflex e validar consulta anônima, filtros, detalhes, estados de falha e imagem assinada.
4. Em caso de rollback, remover/desabilitar apenas a rota e os endpoints públicos desta Change; preservar dados e operações administrativas existentes.

## Open Questions

Nenhuma decisão funcional permanece pendente para a proposta.
