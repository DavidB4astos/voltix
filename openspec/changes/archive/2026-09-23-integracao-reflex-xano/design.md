## Context

A aplicação Reflex atual é mínima, com uma página inicial registrada em `voltix/voltix.py` e configuração básica em `rxconfig.py`. O repositório já contém APIs Xano/XanoScript, incluindo grupos de autenticação e endpoints ligados a tabelas de negócio, mas não possui um contrato técnico dedicado à validação da comunicação. A solução deve respeitar a separação definida em `docs/project-overview.md`: Reflex como interface, Xano como backend e dados gerenciados pelo Xano.

## Goals / Non-Goals

**Goals:**

- Criar um ponto de verificação técnico, estável e sem dependência de dados do domínio.
- Permitir que a aplicação Reflex execute a chamada e apresente estados de sucesso e falha de forma observável.
- Isolar o destino do backend por configuração de ambiente e manter segredos fora do código.
- Definir uma verificação repetível para ambiente local e para um ambiente Xano configurado.

**Non-Goals:**

- Introduzir autenticação ou autorização de usuário.
- Criar ou alterar tabelas, entidades, regras de estoque, pedidos, pagamentos ou CRM.
- Reutilizar endpoints de negócio existentes como prova de integração.
- Definir a infraestrutura de produção, CI/CD ou observabilidade permanente.

## Decisions

### Endpoint técnico dedicado

Será usado um endpoint Xano/XanoScript dedicado à saúde da integração, com resposta pequena e versionável. Isso evita acoplar a primeira prova de comunicação a autenticação, permissões ou dados que podem mudar. Consultar um endpoint de clientes ou `auth/me` foi considerado, mas rejeitado por introduzir dependências de domínio ou credenciais antes de a conectividade básica estar comprovada.

### Contrato de resposta explícito

O contrato deverá distinguir resposta HTTP de sucesso de payload válido, permitindo que o frontend rejeite respostas incompletas ou inesperadas. O frontend não converterá timeout, erro HTTP ou resposta inválida em estado de sucesso.

### Configuração externa do destino

O endereço do backend será fornecido por configuração própria do ambiente de execução do Reflex. Nenhum token, segredo ou URL privada será embutido em `voltix/voltix.py`, e a ausência da configuração será tratada como erro explícito. Um endereço fixo local foi considerado, mas não atende à execução contra diferentes ambientes Xano.

### Fluxo de comunicação mediado pelo State

A ação visível na página inicial acionará um handler do State/lógica Python da aplicação Reflex. Essa camada será responsável por obter a configuração do destino, realizar a chamada HTTP ao endpoint técnico do Xano, validar a resposta e atualizar o estado apresentado pela interface. O fluxo adotado será explicitamente **Interface Reflex → State/lógica Python → Xano**; a chamada ao backend não será implementada como comunicação HTTP direta executada no navegador.

Um teste isolado da função HTTP foi considerado insuficiente porque não comprova a ligação entre a ação da interface, a execução do State e o endpoint Xano. A verificação deverá cobrir o fluxo completo e observar os estados de carregamento, sucesso, falha e nova tentativa na interface.

## Risks / Trade-offs

- [O ambiente Xano pode não estar acessível durante a validação] → Manter a configuração do destino explícita, executar a chamada na camada State/lógica Python e registrar o resultado como falha de integração, sem fallback silencioso.
- [A configuração ou o ambiente de execução Python podem impedir a chamada ao Xano] → Validar a disponibilidade do destino, tratar erros HTTP, timeout e rede na camada State e expor à interface uma falha explícita, sem pressupor comunicação direta do navegador.
- [O contrato técnico pode evoluir sem compatibilidade] → Usar payload mínimo, nomes estáveis e validação explícita da resposta antes de atualizar o estado de sucesso.
- [A prova pode ser confundida com uma feature de negócio] → Manter endpoint, interface e tarefas isolados, sem consultas ou mutações de entidades do domínio.

## Migration Plan

1. Adicionar o endpoint técnico no conjunto de APIs Xano da Change.
2. Configurar o destino do backend no ambiente de execução da lógica Python/State do Reflex usado para validação.
3. Conectar a ação da página inicial ao State, executar a chamada HTTP ao endpoint Xano nessa camada e verificar os cenários de sucesso, erro e configuração ausente.
4. Em caso de rollback, remover a ação e o endpoint técnico da Change, sem migração de dados ou alteração das APIs de negócio.

## Open Questions

Nenhuma questão em aberto altera o contrato ou a abordagem desta Change. O endereço concreto do ambiente Xano será informado somente na configuração de execução durante a implementação.
