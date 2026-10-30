# Revisão final — 30/10/2026

## Entrega
Filtros em faixa coerente, busca explícita, atualização manual e aviso de somente leitura. Tabela com status textual, contatos protegidos, nomes de ações específicos e paginação contextual. Ficha de cliente em região nomeada e fechável, com CPF protegido e campos ausentes como Não informado. Estados inicial, loading, vazio e erro distintos.

O componente real internal_customer_panel foi extraído da fonte por AST para uma aplicação de prévia isolada com DTO InternalCustomer e State de fixture, sem importar App/State/configuração da aplicação real e sem chamadas Xano. A faixa amarela identifica a simulação. Sidebar da fixture é ilustrativa; o shell real já foi conferido na change anterior.

## Verificação
- 185 testes existentes passaram em 1,740 s; nenhuma alteração na suite foi necessária para a apresentação.
- Compilação da aplicação completa: 100% (30/29); prévia isolada também compilou. Uma compilação dry-run antecedeu a escrita da prévia principal.
- Comparação AST do State com HEAD anterior: idêntico. Handlers de busca, filtros, seleção, carregamento, reset de sessão, paginação, autorização e integração não foram alterados.
- Desktop 1440 × 1000: início, lista, detalhe, loading da lista e detalhe, vazio e erro conferidos; sem overflow horizontal da página. Tabela tem cinco cabeçalhos semânticos; região de detalhe nomeada; foco cyan de 3px.
- Na fixture: carregar, abrir/fechar detalhe por Enter, submit de busca sem resultado, limpar filtros e ir/voltar página funcionaram. São eventos simulados locais; a cobertura dos handlers reais continua na suite existente.
- Nome longo, status inativo, contatos ausentes e CPF mascarado conferidos visualmente. Nenhuma ação de editar/revelar/exportar adicionada.
- Nenhuma leitura ou mutação de clientes reais executada nesta change. Os nomes e contatos das capturas são fictícios. Totais de 23/2 páginas e três linhas representativas são valores independentes da fixture visual, não um payload de API ou validação dos limites da consulta real.
- Erro manualmente recuperável pelo comando de atualização existente; sem novas requisições automáticas, timers ou animações.

## Evidências e limites
Capturas initial, list, detail, loading, detail-loading, empty e error. detail.png registra a ficha final e identificação da simulação. Não houve nova validação remota de permissões nesta change visual; as provas C4 e do shell interno continuam preservadas. Mobile não foi foco de aceite; há empilhamento básico em larguras menores. Uma foto de fixture não comprova um fluxo remoto completo.

Arquivos gerados de dependências guardados em .local-backup/2026-10-30-lockfiles-customers-desktop e originais versionados restaurados. Prévia isolada usa o diretório temporário internal-web; sem nova dependência versionada.

Encerramento: spec internal-customers atualizada preservando os cenários anteriores; validação global strict com 16 aprovadas e 0 falhas. Nenhuma change ativa restante. Prévia principal de login conferida disponível após compilação; sem autenticação remota nova nesta etapa.
