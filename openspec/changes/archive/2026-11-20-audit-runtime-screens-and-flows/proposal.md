## Why

A auditoria estática concluiu que as 25 specs estão implementadas e que nenhuma rota ou seção interna está órfã. Ainda assim, não há prova de que as telas **funcionam em execução**: a validação responsiva foi apenas documental, o upload de imagem tem HTTP 403 histórico e nenhuma jornada foi percorrida neste ciclo. Antes de gravar o vídeo de entrega ou abrir correções, é preciso separar "tela que não existe" de "tela que existe e falha".

## What Changes

- Executar o app localmente contra o Xano configurado e percorrer as 9 rotas públicas e as 9 seções internas (inventário atualizado em 20/11/2026; o rascunho de 10/11/2026 previa 7 e 7).
- Registrar, por tela, se ela carrega, quais estados aparecem (vazio, carregando, erro) e quais ações estão disponíveis.
- Percorrer as jornadas de Visitante, Cliente, FUNCIONARIO e ADMINISTRADOR em modo somente leitura.
- Verificar visualmente as larguras 375, 768 e 1280 px nas telas principais.
- Produzir um inventário de telas e uma lista de defeitos classificada por severidade, com evidência sanitizada.
- Definir, a partir dos defeitos, o escopo exato da change de correção seguinte.

Reativada em 20/11/2026 por causa da entrega em três dias. Desde o rascunho original, o app ganhou o painel de CRM, a seção Usuários, Categorias e marcas e as páginas de recuperação de senha; também já foram corrigidos a exibição monetária (`fix-money-display`) e os filtros inválidos de senha (`fix-internal-users-password-filters`).

## Capabilities

Nenhuma capability de produto é alterada. Auditoria documental com `skip_specs: true`.

## Impact

- Código de produção: nenhuma alteração.
- Xano: nenhuma publicação, schema ou registro alterado.
- Dados: nenhuma compra, importação, cadastro, inativação ou exclusão será executada.
- Evidências: capturas e relatórios sanitizados, sem CPF, e-mail, telefone, senha, hash ou token.
- Dependências e configuração: nenhuma nova.
