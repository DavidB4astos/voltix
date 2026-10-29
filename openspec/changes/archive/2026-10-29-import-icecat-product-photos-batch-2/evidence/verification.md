# Verificação — lote Icecat 2 — 29/10/2026

- Auditoria inicial: main sincronizada com GitHub em 18e7919. Change antiga corrigir-regressoes-catalogo encerrada com evidências, tarefas e sincronização de spec; commit 36e7923. Texto corrompido do primeiro requisito substituído pelo delta UTF-8 íntegro.
- Lote atual separado da auditoria. Somente três fotos e manifesto; código, testes, Xano e dependências sem alteração neste incremento.
- Conta própria: HTTP 200 e DemoAccount=false para os três modelos. Metadados sanitizados em source-match.json, sem usuário, senha, accessKey ou token.
- Stinger 2 preto: 519T1AA, Icecat 95717517, VTX-DEMO-006. SoloCast preto: 4P5P8AA, Icecat 94377174, VTX-DEMO-008. Archer T3U: Icecat 79344020, VTX-DEMO-018; não é versão Plus/Nano.
- Detalhes públicos reais consultados: Stinger 2 3,5mm/50mm, SoloCast USB/cardioide/tap-to-mute, T3U USB3/AC1300 dual-band. Cadastro não declara revisão de hardware T3U, nenhuma revisão foi inventada.
- Imagens originais vistas antes da inclusão: fundo branco, modelo correspondente e boa definição. Preservadas byte a byte, sem recorte ou conversão. Hashes conferidos após importação.
- Créditos OCL, origem, aviso de database-right e ausência de garantia preservados. Não atribuir fotografia a pessoa desconhecida; crédito identifica o fornecedor.
- 166 testes passaram em 1,505s. Aplicativo compilou a 100% e foi iniciado para conferência no navegador.
- Desktop: catálogo com imagens e três detalhes inspecionados. DOM confirmou arquivo local carregado, SKU e aviso de licença em cada detalhe. Capturas de catálogo, Stinger, SoloCast e T3U anexas.
- Nenhum botão de compra acionado e nenhum dado remoto alterado. API Icecat não é chamada por visitantes. As fotos são servidas localmente.
- Cobertura: 8 fotos aprovadas / 20 produtos demo; 12 pendentes. Três registros adicionais de teste não fazem parte deste manifesto e não foram alterados.
- Arquivos de dependências regenerados serão guardados em cópia local ignorada e as versões Git recuperadas após encerrar os processos de conferência.
