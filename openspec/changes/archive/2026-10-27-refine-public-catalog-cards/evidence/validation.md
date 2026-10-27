# Verificação dos cards — 27/10/2026

- 165 testes aprovados (163 anteriores e dois para créditos completos/seguros e cópia sem mutação do cache). Compilação Reflex concluída em 8,987 s. OpenSpec strict válido.
- Comparação AST contra HEAD anterior à implementação: State/eventos, outras páginas e selected_product_details são idênticos. Apenas composição de product_card, carga da folha e acesso de leitura aos créditos foram alterados no catálogo.
- Navegador com dados reais: MOUSE + Periféricos retorna três produtos; dois placeholders honestos e uma foto do modelo correto. Frames de mesma altura e botões alinhados pela base. Nome dos produtos em H2; um H1 visível na listagem sem detalhe aberto.
- Foto do mouse e foto do K120 usam contain, sem recorte. Crédito do mouse: Hayden Schiff / CC BY 4.0; teclado: TaurusEmerald / CC BY-SA 4.0. Fonte e licença visíveis; atribuição original no title/aria-label da fonte.
- Botão do MX Master alcançado pelo teclado, outline sólido e 44px; Enter abre o painel existente do produto correto. Painel/compra não foram redesenhados nem houve envio de compra.
- Limpar filtros restaura 23 produtos; busca teclado retorna um. Busca e categoria permanecem no fluxo já implementado.
- 1440/1280/1024px conferidos sem overflow; controle 390px também sem overflow. As imagens presentes carregaram; URL ausente usa placeholder. URLs remotas expiradas não foram simuladas nesta change.

## Instância de verificação e limites
O servidor local inicialmente estava parado (3000/8000 recusavam conexão). O iniciador padrão encerrou com Unexpected exit from worker-1. Para concluir a verificação, usou-se o frontend Reflex existente e o backend ASGI do aplicativo em um processo Granian embedded local, já instalado, sem adicionar dependências ou modificar configuração permanente. O backend respondeu e os dados públicos e botões acima funcionaram. Isso não comprova estabilidade do iniciador padrão; essa questão permanece separada desta mudança de cards.

Nenhum registro Xano, autenticação ou regra comercial foi alterado. Não houve login, checkout completo, auditoria WCAG integral ou push. As fotos ausentes continuam ausentes, sem substituição por outro modelo. O rótulo genérico Connection Error ainda aparece no DOM, mas as consultas e ações descritas foram conferidas nesta instância.
