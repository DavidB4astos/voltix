## Implementação

`_cart_money_text` recebe `rx.Var` numérica, conforme os modelos de produto/pedido, mas usa operações de string. Converter essa variável para o tipo de texto Reflex com o método já usado pelo projeto (`Var.to_string()`) e manter intactas as operações de divisão, preenchimento e prefixo monetário atuais.

## Verificação

1. Validar a change OpenSpec em modo estrito antes da edição.
2. Inspecionar o diff para confirmar que somente a coerção de tipo do helper foi alterada.
3. Compilar/iniciar o app para confirmar que a rota `/interno` deixa de falhar ao gerar a tabela de variações.
4. Conferir a renderização do preço no navegador sem salvar capturas e sem acionar operações de escrita.

## Evidência visual

A captura fornecida pelo usuário em 04/11/2026 mostra `/interno` aberto no painel de Produtos. Os preços das variações aparecem com `R$` e vírgula decimal; a página foi renderizada sem o erro anterior. A captura não foi copiada nem salva no repositório.

## Limites

A compilação de páginas chegou a 100% após a conversão para texto. No ambiente isolado do agente, o Bun ainda falhou com `EBADF accessing temporary directory`; a validação visual foi concluída na execução local do usuário. Não foram atualizadas dependências, nem alterados dados de negócio.
