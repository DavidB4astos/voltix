# Avaliação de ambiente Xano para C1

Data: 04/11/2026.

## Fontes verificadas

- Xano CLI local: versão 1.2.0. A ajuda de `sandbox get` diz que cria o ambiente se ainda não existir. A ajuda de `sandbox push` requer `--dry-run` e não oferece filtros include/exclude.
- Página oficial de preços: https://www.xano.com/pricing — consultada em 04/11/2026. O plano Essential aparece a US$85/mês com cobrança anual e lista `CLI sandbox environments`; o plano Free consultado não lista essa capacidade.
- Repositório oficial do CLI: https://github.com/xano-inc/cli — descreve o sandbox do CLI e os comandos `sandbox get` / `sandbox push`.

## Resultado

O CLI possui suporte ao sandbox, mas isso não comprova que a conta Voltix atual tenha direito a provisioná-lo. A documentação de preço indica que o recurso não está no Free. Não foi lido o perfil Xano nem consultado o plano da conta. Nenhum `sandbox get`, push, upgrade, teste ou alteração de registros foi executado.

## Próxima condição

Manter C1 bloqueada até o usuário confirmar um ambiente isolado gratuito e autorizado ou confirmar que já possui um plano elegível e autorizar seu uso. Se houver autorização, uma change própria deve definir o conteúdo mínimo do sandbox, mostrar o dry-run e testar rollback/concorrência sem registros reais.
