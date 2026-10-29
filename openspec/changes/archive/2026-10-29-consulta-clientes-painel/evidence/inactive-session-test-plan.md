# Teste controlado de sessão interna inativa

## Autorização
Em 29/10/2026, o usuário aprovou explicitamente emitir sessão de uma conta interna fictícia ativa, inativá-la temporariamente, testar os dois GETs de clientes internos e restaurar o status original. Essa autorização específica substitui a restrição anterior de não alterar registros para criar cenários, somente para esta conta e este teste.

## Alvo e limites
- Conta existente Usuario Funcionario Teste, tabela user 748950, registro 5, perfil FUNCIONARIO e status original ATIVO, confirmados por consulta filtrada exata via Metadata API.
- Único campo alterável: status; atualização parcial em um único row_id. Nenhuma criação, exclusão, senha, permissão, catálogo ou cliente será alterado.
- Antes da mudança, conferir novamente identidade, perfil e status. Guardar status original e impressão dos demais campos, sem persistir conteúdo privado.
- O usuário insere as credenciais pela interface. Nenhuma senha/token será solicitada ou registrada em evidência.

## Sequência automática preparada
1. Após login bem-sucedido da conta de teste específica, validar sessão ativa nos GETs (lista sem correspondência e detalhe de ID inexistente).
2. Gravar diário local de restauração antes de escrever. Iniciar proteção independente de restauração com prazo de 60 segundos.
3. Alterar somente status para INATIVO e reler para confirmar.
4. Enviar a mesma sessão já emitida aos dois GETs. Esperar acesso negado em ambos.
5. Restaurar ATIVO em bloco finally e reler. Conferir que os demais campos mantêm a mesma impressão.
6. Registrar apenas códigos HTTP e booleanos de confirmação/restauração. Só declarar aprovado com restauração confirmada.

## Situação
Preparado; aguarda login da conta de teste. Nenhuma inativação executada na preparação. O cenário de Cliente com ID coincidente continua separado e não será presumido a partir deste teste.

## Resultado
Executado após login confirmado pelo usuário: lista/detalhe negados com 403 enquanto INATIVO. Restaurado ATIVO; demais campos inalterados; diário sem restauração pendente. Ver inactive-session-denied.json e publication.md.
