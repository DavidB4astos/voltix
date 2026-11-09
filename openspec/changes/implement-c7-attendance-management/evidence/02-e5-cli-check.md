# 02 — E5: verificação de consumo pela Xano CLI (09/11/2026)

## Objetivo

Tentar obter plano e consumo atuais pela CLI antes de publicar a C7.

## Comandos executados (somente leitura)

| Comando | Resultado relevante |
|---|---|
| `xano --version` | `@xano/cli/1.2.0` |
| `xano profile me -p voltix -o summary` | instância `x8ki-letl-twmt`, workspace `147981`, `Display: Free Instance` |
| `xano profile me -p voltix -o json` | `features: []`, add-ons em zero; sem contadores de uso |
| `xano workspace get -p voltix -o json` | `id`, `name`, `branch` e `preferences`; sem plano/consumo |
| `xano tenant list -p voltix -o json` | `{"items":[]}` |
| `xano platform list/get -o json` | apenas helm e imagens; sem consumo |
| `xano workspace pull --help` | existe `--records`, mas ele baixa registros (não executado) |

## Conclusão

A CLI confirma que a instância é `Free Instance`, mas **não expõe**:

- registros usados ou limite;
- requisições realizadas ou taxa aplicada;
- histórico de erros 429.

Nenhum registro foi baixado (`--records` não foi usado) e nenhuma credencial ou dado
pessoal foi registrado. A medição E5 de consumo continua pendente no dashboard do Xano;
a publicação da C7 permanece bloqueada até essa evidência e o gate explícito.
