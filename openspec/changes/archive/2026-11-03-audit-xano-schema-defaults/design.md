## Escopo
Conferir apenas os defaults declarados para `endereco.principal` e `pedido.valor_frete` na representação publicada do workspace Voltix e revisar os pontos locais de persistência correspondentes.

## Método
1. Revisar `AGENTS.md`, overview, modelo de domínio, roadmap e configuração OpenSpec.
2. Fazer pull somente de metadados publicados do workspace 147981 com perfil `voltix`, sem incluir drafts, variáveis de ambiente ou registros.
3. Comparar as linhas de schema com os arquivos locais e localizar todas as gravações relevantes no código XanoScript local.
4. Registrar somente conclusões diretamente sustentadas pela representação e pelo código. Não inferir o fallback efetivo do banco para inserções que omitam um campo.
5. Atualizar esta auditoria e o roadmap com a diferença, o impacto observado e a limitação.

## Decisão
A cópia de metadados publicada representa `endereco.principal` e `pedido.valor_frete` sem defaults explícitos (`bool principal?` e `decimal valor_frete?`); a versão local declara `false` e `0`. Nos caminhos atuais revisados, `customer_addresses_POST` calcula e envia `principal`, e `checkout_confirm_POST` envia `valor_frete: 0`. Assim, não há evidência de impacto nesses caminhos nem necessidade demonstrada de mudar o Xano. A semântica de uma gravação que omita esses campos permanece não verificada; não será testada com inserção de dados reais.

## Verificação
OpenSpec estrito, revisão do diff documental e `git diff --check`. Não executar testes funcionais nem publicar Xano: nenhuma lógica executável mudou. Registrar que o pull não incluiu ambiente, drafts ou registros.
