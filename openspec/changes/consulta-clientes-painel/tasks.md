## 1. Preparação e revisão
- [x] 1.1 Ler rascunho adiado, schema local, autenticação, rotas e decisões E2/E4.
- [x] 1.2 Propor contrato coerente, minimização, filtros e paginação com cenários verificáveis.
- [x] 1.3 Revisar/aprovar o contrato proposto antes de implementar, incluindo máscaras de contatos e detalhe.

## 2. Backend e contrato
- [ ] 2.1 Confirmar schema real e sintaxe suportada por metadados, sem dados pessoais reais.
- [ ] 2.2 Implementar dois endpoints com autorização e whitelist/máscaras no Xano, filtros combinados e paginação real; não publicar draft antigo.
- [ ] 2.3 Validar sintaxe e permissões negativas/positivas dos dois endpoints em contexto autorizado, incluindo Cliente com id coincidente.

## 3. Integração e desktop
- [x] 3.1 Implementar modelos/normalização e chamadas State server-side com sessão interna privada e configuração documentada sem segredos.
- [x] 3.2 Implementar área Clientes em /interno para os dois perfis, com filtros, paginação, detalhe, acessibilidade e feedback, sem liberar gestão de produtos.
- [x] 3.3 Invalidar respostas obsoletas e limpar dados na troca/perda de sessão; tratar 429 com retry limitado.

## 4. Verificação e encerramento
- [x] 4.1 Testar autorização, filtros combinados, máscaras curtas/inválidas, paginação, payload inesperado, erro/429 e corrida de respostas com fixtures isoladas.
- [x] 4.2 Verificar desktop com fixtures sem PII real e preservar evidências sanitizadas; não fazer mutações Xano para criar cenário.
- [ ] 4.3 Rodar verificações apropriadas e OpenSpec, documentar limites; só declarar funcional após validação Xano.
- [ ] 4.4 Revisar diff, arquivar somente quando tudo concluído e criar commit separado.
