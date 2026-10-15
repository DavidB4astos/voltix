## 1. Primitivas compartilhadas

- [x] 1.1 Adicionar `feedback_alert`, `status_badge` e helpers de botão (primário/secundário/destrutivo) reutilizando os tokens existentes; verificação: nenhum token novo fora do design e handlers/State inalterados.
- [x] 1.2 Aplicar as primitivas nas páginas existentes (catálogo, conta, carrinho, checkout, pedidos, interno); verificação: rótulos, mensagens e handlers preservados.

## 2. Carrinho, checkout e pedidos

- [x] 2.1 Padronizar a apresentação de itens do carrinho, resumo e totais; verificação: quantidades, totais e ações inalterados.
- [x] 2.2 Melhorar checkout (endereço, método e resumo) e pedidos (status via badge e ação de pagamento) sem alterar comportamento.

## 3. Catálogo e cards

- [x] 3.1 Alinhar imagem, preço e ações dos cards em 375/768/1280; verificação: sem overflow e com dados/ações preservados.

## 4. Painel administrativo (visual simples)

- [x] 4.1 Aplicar espaçamento/agrupamento e as primitivas compartilhadas; verificação: navegação, controles condicionais e permissões de Administrador inalterados.

## 5. Verificação

- [x] 5.1 Executar testes Playwright responsivos (375/768/1280) e smoke de navegação.
- [x] 5.2 Executar `python -m unittest discover -s tests` e `reflex compile`.
- [x] 5.3 Executar `openspec validate melhorar-ux-ui-ap2 --strict`.
