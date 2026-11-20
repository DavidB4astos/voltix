## Why

A auditoria de runtime de 20/11/2026 percorreu as 9 rotas públicas e as 9 seções internas em
1280/768/375 px. Todas carregam, mas seis defeitos são visíveis numa demonstração: o catálogo
público exibe resíduos de teste; os cards não mostram preço (contrariando o requisito consolidado
de alinhamento imagem/preço/ação); o selo "Built with Reflex" cobre o rodapé; oito produtos
ficam com o placeholder de imagem; "Acesso interno" fica fora da viewport no cabeçalho mobile;
e valores altos quebram de linha na coluna Total do painel Pedidos.

## What Changes

- **D1**: remover/inativar no Xano os produtos de teste que aparecem no catálogo público
  (`TMP-VALIDB-20261015142856-A`, `Notebook Voltix Teste Hp`, `mouse`). Operação de dados, com
  autorização explícita por gravação.
- **D2**: o endpoint público de produtos passa a informar o menor preço de variação ativa
  (`preco_minimo`) e o card do catálogo exibe `a partir de R$ <valor>` com o formato monetário já
  consolidado, sem inventar valor nem alterar o detalhe.
- **D3**: `show_built_with_reflex=False` no `rxconfig.py`, eliminando o selo que cobre o rodapé.
- **D4**: o placeholder de imagem ausente passa a ser tratado de forma padronizada (mantém a
  indicação honesta), com a limitação de conteúdo registrada.
- **D5**: cabeçalho mobile passa a acomodar "Acesso interno" sem depender de rolagem horizontal.
- **D6**: células monetárias das tabelas internas não quebram de linha.

Sem **BREAKING** changes: o endpoint público continua sem autenticação e com os mesmos campos,
somado um campo opcional.

## Capabilities

### New Capabilities

<!-- Nenhuma capability nova. -->

### Modified Capabilities

- `public-catalog`: os cards passam a expor o menor preço real de variação ativa.
- `visual-interface`: alinhamento de preço no card, cabeçalho mobile e células monetárias sem
  quebra.

## Impact

- Backend/Xano: `xano/api/public_catalog/products_GET.xs` (publicação restrita, com autorização).
- Frontend: `voltix/voltix.py` (contrato do catálogo, card), `rxconfig.py` (selo), CSS interno e
  público.
- Dados: operação de inativação/remoção de 3 produtos de teste, autorizada separadamente.
- Testes: suíte nova para o preço do card e ajustes dos testes existentes do catálogo.
- Verificação: suíte, `reflex compile`, inspeção em 1280/768/375 px e chamada ao endpoint público.
- Fora do escopo: obtenção de novas imagens (depende de fonte/direitos), correção do D7 (falso
  positivo), qualquer mudança de regras de compra ou de detalhe do produto.
