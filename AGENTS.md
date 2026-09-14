# AGENTS.md — Voltix

## 1. Documentação

- Antes de realizar alterações significativas, consultar os documentos de contexto do projeto.
- Utilizar `docs/project-overview.md` como referência para visão geral, objetivos, escopo e arquitetura definida.
- Utilizar `docs/domain-model.md` como referência para os conceitos, relacionamentos e regras do domínio.
- Manter a documentação consistente com as decisões aprovadas durante o desenvolvimento.
- Não alterar decisões documentadas sem que a mudança seja analisada e aprovada.
- Registrar decisões relevantes quando elas passarem a fazer parte permanente do projeto.

## 2. Arquitetura

- Respeitar a arquitetura e as tecnologias definidas para o projeto.
- Utilizar Reflex no frontend.
- Utilizar Xano e XanoScript no backend.
- Utilizar a infraestrutura de dados disponibilizada pelo Xano.
- Utilizar OpenSpec para orientar o desenvolvimento incremental.
- Não introduzir novas tecnologias, frameworks ou serviços sem justificativa e aprovação prévia.
- Manter separadas as responsabilidades entre frontend, backend e persistência de dados.

## 3. Código

- Reutilizar código existente quando apropriado.
- Evitar duplicação de código.
- Manter o código organizado e legível.
- Não modificar funcionalidades não relacionadas à mudança atual sem justificativa.
- Implementar somente o que estiver definido e aprovado para a mudança atual.
- Evitar complexidade desnecessária.

## 4. Segurança

- Aplicar regras de autenticação e autorização no backend.
- Não confiar apenas em validações realizadas no frontend.
- Proteger operações administrativas contra acesso de usuários não autorizados.
- Não expor dados sensíveis, credenciais ou informações de configuração.
- Respeitar as permissões definidas para clientes e usuários internos.

## 5. Desenvolvimento

- Utilizar OpenSpec para orientar as mudanças do projeto.
- Trabalhar de forma incremental, uma mudança por vez.
- Antes de implementar uma mudança, analisar e definir seu escopo.
- Não implementar funcionalidades que ainda não tenham sido analisadas e aprovadas.
- Manter cada mudança limitada ao escopo definido para ela.
- Revisar a mudança antes de avançar para a próxima.

## 6. Verificação e testes

- Toda mudança funcional deve possuir uma estratégia de verificação.
- Verificar se a implementação atende ao comportamento definido na mudança atual.
- Verificar se as regras de domínio relacionadas foram respeitadas.
- Validar os principais cenários esperados e cenários de erro relevantes.
- Não considerar uma mudança concluída enquanto sua implementação não tiver sido revisada e verificada.
