## Contexto e evidências
- Fonte local CLIENTE: nome_completo/email/created_at, não nome/e-mail/data_cadastro. user possui role FUNCIONARIO/ADMINISTRADOR e status ATIVO/INATIVO.
- auth/internal_access_GET.xs já verifica auth=user, existência, perfil e status. Reutilizar padrão nos dois novos endpoints, sem depender da proteção do frontend.
- /interno é a rota existente; /admin não está registrado. Não criar uma rota /admin pressuposta pelo draft.
- Arquivos adiados permanecem intactos em docs/deferred-changes/2026-10-27-consulta-clientes-admin/. E2 do roadmap prevalece sobre ADMIN-only do rascunho.

## Contrato proposto para revisão
Grupo: Voltix Internal Customers; caminhos relativos ao grupo (URL publicada só após obter metadados reais).

GET customers: q opcional, trim, no máximo 100 caracteres; status ATIVO (padrão), INATIVO ou TODOS; page inteiro >=1 (padrão 1); per_page inteiro entre 1 e 50 (padrão 20). Entrada inválida é rejeitada, não ampliada silenciosamente. Busca parcial case-insensitive em nome_completo OU email; status combinado com AND. Espaços no termo equivalem a ausência. Não buscar por CPF/telefone.

Resposta: {items: [{id, nome_completo, email_masked, telefone_masked, status, created_at}], page, per_page, total_items, total_pages}. Ordenação estável nome_completo ascendente, id ascendente. Filtro novo volta à página 1 e limpa seleção. Página além da última retorna items=[] e contagem real; total_pages=0 quando total_items=0. Paginação e busca devem ocorrer no Xano, sem trazer toda a tabela para paginar no Reflex. Validar sintaxe/custo antes de publicação, sem presumir suporte ao draft.

GET customers/{customer_id}: id inteiro positivo; mesma autorização; resposta {id, nome_completo, email_masked, telefone_masked, cpf_masked, status, created_at}. Inexistente retorna not found somente após autorização; sem consultar pedidos ou endereços. Cliente INATIVO pode ser consultado por interno autorizado, preservando histórico.

## Máscaras propostas
- E-mail: usar apenas a parte antes de @; mostrar até três caracteres, sempre ocultando pelo menos um caractere dessa parte; acrescentar cinco asteriscos e omitir domínio. maria@example.test → mar*****; ab@example.test → a*****; a@example.test → *****. Ausente/inválido → null, sem ecoar entrada bruta.
- Telefone: normalizar dígitos; se houver mais de quatro, retornar ***** seguido dos últimos quatro; caso contrário *****; ausente → null.
- CPF: somente se houver 11 dígitos, retornar ***.***.***- seguido dos dois últimos; inválido/ausente → null. Nunca oferecer revelação de CPF nesta change.
- Backend aplica máscaras e whitelist antes da resposta; State guarda só valores sanitizados. Não serializar registro bruto, USER_ID, CELULAR_CLIENT, password, hash, reset, token ou campos extras. Não logar corpo, termo de busca ou Authorization.

## Integração e UX desktop
Reutilizar sessão interna privada e validar antes da leitura. FUNCIONARIO e ADMINISTRADOR ativos veem Clientes; gestão de produtos continua ADMIN-only. State faz GET server-side com token interno; nunca token Cliente. Configuração proposta XANO_INTERNAL_CUSTOMERS_URL e XANO_INTERNAL_CUSTOMER_DETAILS_URL, sem URLs privadas em specs/evidências. A área só entra em funcionamento após endpoints e configuração validados.

Busca submetida por botão/Enter, sem chamada a cada tecla. Status, limpar filtros, resultados, paginação anterior/próxima e painel de detalhe com fechamento acessível. Estados distintos: carregando, vazio, erro, 429 e sem permissão. Alterar filtro cancela/invalida resultados e detalhes anteriores; uma resposta atrasada não pode repor filtro ou cliente obsoleto. Logout/sessão inválida limpa lista, detalhe, contagens e mensagens com dados. Falha 401/403 nunca dispara loop de retry.

429: respeitar Retry-After válido, até uma repetição e apenas se espera <=30 s; ausente/inválido ou maior, exibir mensagem com tentativa manual. Não bloquear a interface nem repetir indefinidamente. Reutilizar helper se satisfizer contrato; sem alterar política global de outros fluxos.

## Riscos e gates
1. Schema real e sintaxe Xano não verificados remotamente nesta preparação. Conferir só metadados antes de publicar, nunca coletar lista real de clientes para teste.
2. auth=user e auth=CLIENTE precisam distinguir emissor/tabela mesmo com IDs iguais. Testar tokens de tipo errado, usuário ausente/inativo e ambos os perfis permitidos nos dois endpoints.
3. Taxa de requisições e volume: limites históricos não são medição atual. Paginar no backend, evitar N+1 e consultas em paralelo por linha.
4. Testes Python com fixtures isoladas validam frontend/contrato; não provam execução de autorização no Xano. Não declarar feature pronta nem arquivar sem validação Xano autorizada e evidências negativas/positivas.
5. Não publicar via workspace push amplo; qualquer publicação futura é restrita a estes endpoints após revisão. Não executar o draft adiado.

## Plano de entrega
Preparação OpenSpec → revisão do contrato → implementação isolada e testes → validação Xano em contexto autorizado → desktop com fixtures sem dados reais → evidências, archive e commit. Se houver bloqueio externo, registrar trabalho pendente; não arquivar como concluído.
