## Context
Cadastro usa POST /cliente e edição usa PATCH /cliente/{cliente_id}. As versões locais protegidas já satisfazem o contrato e têm testes estáticos e de State existentes. Corrigir drift de publicação, sem reescrever a capability.
## Decisions
- Pacote externo ao repositório contendo exclusivamente quatro queries locais e GUIDs preservados. Não enviar api_group, table, env ou records.
- GET de coleção torna-se consulta da própria identidade, nunca lista global. GET por id verifica propriedade antes da leitura. PATCH usa whitelist explícita e mantém CPF/status/credenciais fora do input/output. DELETE autentica/verifica propriedade e rejeita sempre, sem operação de remoção.
- Preservar POST de cadastro e rotas /login e /me. Não escolher outro canonical ou enviar workspace inteiro.
- Pull fresco anterior e hashes para garantir revisão sobre estado atual; dry-run com transaction padrão. Revisar contagem/escopo antes da publicação; não usar --force, --delete, --sync, --records, --env ou --no-transaction.
- Backups de metadados ficam fora do Git; não fazer rollback automático para código vulnerável. Se houver erro, interromper e examinar o diff, sem apagar dados ou modificar outra área.
## Verification
Suite existente; conferir igualdade do pacote com quatro fontes versionadas e identidades/GUIDs com snapshot fresco. Dry-run apenas quatro atualizações. Após publicação autorizada: novo pull e comparação normalizada, GET anônimo/credencial inválida; PATCH/DELETE negativos apenas após comprovar código publicado seguro, usando ID fictício inexistente, sem mutação de clientes reais. Caso validação autenticada não mutante dependa de conta de teste, registrar pendência e não arquivar como concluída sem evidências necessárias.
