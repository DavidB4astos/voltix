## Context

Consulte [proposal.md](./proposal.md) e as specs de [customer-access](./specs/customer-access/spec.md) e [customer-addresses](./specs/customer-addresses/spec.md). O repositório contém a tabela Xano `CLIENTE` com `USER_ID`, `CELULAR_CLIENT`, `cpf` e `status_cliente_id`, ainda sem campos completos de identidade nem autenticação. As rotas legadas `DB_XANO_BASTOS/cliente` incluem listagem/leitura sem autenticação, cadastro genérico por `dblink`, edição com `util.get_raw_input` e exclusão física. A tabela `user` autentica `UsuarioInterno`; nenhuma tabela ou API de `Endereco` ou `Pedido` está definida localmente.

## Goals / Non-Goals

**Goals:**
- Adaptar o conceito existente de Cliente sem descartar campos/dados legados.
- Reutilizar o mecanismo de senha/token do Xano, mas emitir e aceitar tokens vinculados à tabela autenticável `CLIENTE`, separados de `user`.
- Preservar rotas legadas por caminho e método, substituindo operações genéricas por comportamentos explícitos e com escopo de propriedade.
- Manter relações de endereço e consistência do endereço principal no backend.
- Centralizar comunicação HTTP no State/Python Reflex.

**Non-Goals:**
- Adaptar ou renomear a tabela `user`, a autenticação interna ou as rotas administrativas.
- Migrar automaticamente contas legadas para login, resolver dados duplicados por sobrescrita ou remover campos legados.
- Implementar pedidos; a verificação de histórico serve apenas para proteger endereços contra remoção.
- Recuperação de senha, exclusão de conta Cliente ou validações não definidas no Domain Model.

## Decisions

1. **Estender `CLIENTE` em vez de criar uma entidade concorrente.** Manter `USER_ID`, `CELULAR_CLIENT`, `cpf` e `status_cliente_id` como dados legados; acrescentar colunas distintas para nome completo, e-mail, telefone, senha protegida e status `ATIVO`/`INATIVO`, além de índices únicos por CPF e e-mail entre Clientes. Configurar `CLIENTE` como tabela autenticável. Isso preserva a identidade e os dados existentes; renomear a tabela ou criar uma segunda tabela de Cliente foi descartado por risco de divergência e referências quebradas. Os campos legados não serão tratados como equivalentes sem mapeamento aprovado.

2. **Separar autenticação por tabela e por fluxo.** Cadastro e login de Cliente usam endpoints próprios, verificam senha com as operações de segurança do Xano e criam token associado à tabela `CLIENTE`. Endpoints protegidos declaram `auth = "CLIENTE"` e validam em cada operação que `$auth.id` corresponde a Cliente existente `ATIVO`. O fluxo interno continua usando `auth = "user"` e não compartilha identidade, role ou token com Cliente. Senhas usam hash gerenciado pelo mecanismo Xano; senha, hash e token não entram nas respostas públicas de identidade.

3. **Preservar caminhos legados, não a escrita genérica.** Manter verbos e caminhos em `DB_XANO_BASTOS/cliente`, mas substituir `dblink`, `util.get_raw_input` e retornos de registros completos por entradas/projeções explícitas. `POST /cliente` realiza somente o cadastro explícito e é a única operação pública; GET e PATCH ficam limitados ao próprio Cliente autenticado e PATCH não altera CPF nem credenciais. O DELETE de Cliente permanece no caminho, mas rejeita exclusão definitiva, preservando histórico conforme o domínio. Isso foi preferido a manter as rotas anônimas/genéricas, incompatíveis com o isolamento obrigatório.

4. **Representar Endereco em tabela própria ligada ao Cliente autenticado.** Usar tipos textuais para CEP, número e demais valores descritivos, preservando zeros à esquerda e formatos conceituais; usar boolean para principal e enum `ATIVO`/`INATIVO`. Não criar obrigatoriedade adicional de campos. `cliente_id` sempre deriva da sessão, nunca do payload. Operações por ID primeiro verificam propriedade no backend.

5. **Atualizar endereço principal de forma consistente.** Ao definir um endereço como principal, limpar o indicador dos demais endereços daquele Cliente e atualizar o alvo na mesma transação. Ao inativar o endereço principal, gravar `principal = false` junto do status. Reativação não o torna principal automaticamente. A remoção física é permitida apenas para endereço próprio sem referência a Pedido; endereço utilizado é preservado e pode ser inativado.

6. **Usar State/Python para sessão e todas as requisições HTTP.** Acrescentar estado de Cliente independente dos campos e eventos de autenticação interna; armazenar o token apenas no State server-side e nunca reutilizar um token entre fluxos. Configurar URLs Xano por variáveis de ambiente; falhas e respostas inválidas permanecem observáveis.

## Risks / Trade-offs

- [Linhas legadas de `CLIENTE` podem ter CPF duplicado/vazio ou não conter dados de identidade necessários] -> Auditar dados no Xano antes de índices únicos; preservar todos os valores e bloquear a migração/publicação até conflitos serem resolvidos sem exclusão ou sobrescrita automática. Não criar login automaticamente para registros legados.
- [Rotas legadas podem ter consumidores que dependem do `dblink` ou acesso irrestrito] -> Preservar caminho e verbo, documentar a mudança de contrato para entradas explícitas e testar que leituras/escritas ficam restritas ao próprio Cliente; não manter acesso inseguro para compatibilidade.
- [A tabela `CLIENTE` não está autenticável hoje] -> Validar o suporte de autenticação Xano para essa tabela e os tokens emitidos antes de habilitar endpoints protegidos; não direcionar Cliente à tabela `user` como fallback.
- [O repositório não define `Pedido`, mas o ambiente pode conter dados/estruturas legadas] -> Antes de habilitar exclusão física de Endereco, verificar no ambiente Xano se há referências existentes a endereço. Se houver referência não mapeada ou não for possível verificar, manter a remoção bloqueada e solicitar decisão em vez de arriscar histórico.
- [Duas operações concorrentes podem tentar tornar endereços principais simultaneamente] -> Usar transação/backend como autoridade e testar que após cada operação confirmada haja no máximo um endereço principal por Cliente.

## Migration Plan

1. Inspecionar tabela `CLIENTE`, índices, valores legados e rotas no ambiente Xano autorizado; identificar duplicidades que impeçam CPF único ou novos vínculos de identidade.
2. Ampliar `CLIENTE` sem remover/renomear campos, preservar os dados legados, adicionar os índices apenas após auditoria e provisionar `Endereco`.
3. Publicar endpoints de cadastro/login e substituir o comportamento genérico das rotas legadas de Cliente por operações explícitas e owner-scoped; não tocar em `user` ou nos endpoints internos.
4. Publicar endpoints de Endereco e configurar URLs no ambiente local/implantação sem versionar credenciais.
5. Validar cadastro, login, sessão, isolamento entre Clientes, proteção de rotas internas, regras de endereço e erros; rollback deve desabilitar os novos fluxos e restaurar somente os endpoints de Cliente afetados, sem remover colunas/dados já preenchidos.

## Open Questions

Nenhuma decisão de produto permanece pendente. A inspeção pré-publicação do estado implantado de `CLIENTE` e de referências a Endereco/Pedido é um gate de segurança para evitar migração destrutiva ou remoção histórica.
