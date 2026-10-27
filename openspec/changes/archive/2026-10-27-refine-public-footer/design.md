## Decisions
- site_footer recebe public_storefront=False por padrão; constrói o legado e só oferece nova variante quando solicitado. page_shell recebe public_footer=False e encaminha o opt-in. Cada página pública declara o opt-in, Home usa site_footer diretamente.
- A nova variante usa elemento footer e duas navs com nomes distintos: Explorar a loja e Sua conta no rodapé. Link de área interna no bloco Projeto, com descrição verdadeira do ambiente acadêmico.
- Marca é texto em link, não um H1 adicional. Nenhum dado de sessão é necessário para montar o rodapé; pedidos continua aplicando o acesso existente.
- CSS sob .vx-footer. Variante desktop visível a partir de 1024px; legado continua em telas menores. Links simples com alvo de 44px e foco cyan. Sem animação necessária.
- A mudança substitui a restrição antiga de não tocar no rodapé apenas para a variante desktop pública. Conteúdo central, header, routes e backend permanecem.

## Validation
Testes de opt-in/rotas, compilação e OpenSpec strict; navegador em 1440/1024px e controle mobile. Conferir links no contexto do rodapé, foco e aviso de simulação. Comparar internal default com legado.
