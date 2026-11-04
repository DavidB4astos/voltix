# Verificação — defaults de schema Xano

Data: 03/11/2026.

## Método
- `xano workspace pull --profile voltix --workspace 147981 --directory <pasta temporária>`; não foram usados `--env`, `--draft`, `--records` ou `--verbose`.
- Pull concluído: 98 documentos de metadados. A pasta temporária ficou fora do repositório do Voltix.
- Comparação dos schemas publicados de `table/endereco.xs` e `table/pedido.xs` com os arquivos locais correspondentes.
- Busca estática por todas as referências e gravações de `principal` e `valor_frete` nos arquivos XanoScript locais.

## Resultado
| Campo | Local | Publicado | Escrita local revisada |
|---|---|---|---|
| `endereco.principal` | `bool principal?=false` | `bool principal?` | `customer_addresses_POST` define `principal: $input.principal == true` antes de criar o endereço. |
| `pedido.valor_frete` | `decimal valor_frete?=0` | `decimal valor_frete?` | `checkout_confirm_POST` define `valor_frete: 0` ao criar o pedido. |

Os metadados publicados não declaram defaults explícitos para esses campos. Os caminhos atuais revisados enviam valores explicitamente; não foi identificado impacto nesses fluxos. Não é possível concluir por esta leitura qual seria o comportamento do banco numa inserção que omita os campos.

## Limites
- Nenhum registro foi consultado, criado, atualizado ou removido.
- Nenhuma query ou schema foi publicado.
- Nenhuma inserção omitindo os campos foi executada; o fallback efetivo do runtime permanece sem prova.
- Esta checagem não declara sincronização total entre XanoScript local e publicado.

## Artefatos conferidos
- `xano/table/endereco.xs` e `xano/table/pedido.xs`.
- `xano/api/customer/customer_addresses_POST.xs`.
- `xano/api/customer/checkout_confirm_POST.xs`.
- Pull de metadados publicado do workspace `147981`, branch padrão selecionada pelo perfil (`live`).
