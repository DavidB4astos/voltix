query "cart" verb=GET {
  api_group = "Voltix Customer"
  auth = "CLIENTE"

  input {
  }

  stack {
    db.get CLIENTE {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "status"]
    } as $customer

    precondition ($customer != null && $customer.status == "ATIVO") {
      error_type = "accessdenied"
      error = "Active customer access is required."
    }

    db.query carrinho {
      where = $db.carrinho.cliente_id == $auth.id
      return = {type: "single"}
    } as $cart

    var $display_items {
      value = []
    }

    var $cart_id {
      value = null
    }

    var $cart_total {
      value = 0
    }

    conditional {
      if ($cart != null) {
        var.update $cart_id {
          value = $cart.id
        }

        db.query item_carrinho {
          join = {
            variacao_produto: {
              table: "variacao_produto"
              type: "inner"
              where: $db.item_carrinho.variacao_produto_id == $db.variacao_produto.id
            }
            produto: {
              table: "produto"
              type: "inner"
              where: $db.variacao_produto.produto_id == $db.produto.id
            }
          }
          eval = {
            produto_nome: $db.produto.nome
            produto_status: $db.produto.status
            variacao_nome: $db.variacao_produto.nome_ou_descricao
            variacao_sku: $db.variacao_produto.sku
            variacao_status: $db.variacao_produto.status
            preco: $db.variacao_produto.preco
            quantidade_disponivel: $db.variacao_produto.quantidade_disponivel
          }
          where = $db.item_carrinho.carrinho_id == $cart.id
          sort = {id: "asc"}
          output = [
            "id",
            "variacao_produto_id",
            "quantidade",
            "produto_nome",
            "produto_status",
            "variacao_nome",
            "variacao_sku",
            "variacao_status",
            "preco",
            "quantidade_disponivel"
          ]
        } as $cart_items

        foreach ($cart_items) {
          each as $cart_item {
            var $item_available {
              value = false
            }

            var $line_subtotal {
              value = $cart_item.preco * $cart_item.quantidade
            }

            conditional {
              if ($cart_item.produto_status == "ATIVO" && $cart_item.variacao_status == "ATIVO" && $cart_item.quantidade_disponivel >= $cart_item.quantidade) {
                var.update $item_available {
                  value = true
                }
              }
            }

            var.update $cart_total {
              value = $cart_total + $line_subtotal
            }

            var.update $display_items {
              value = $display_items|push:{
                id: $cart_item.id
                variacao_produto_id: $cart_item.variacao_produto_id
                quantidade: $cart_item.quantidade
                produto_nome: $cart_item.produto_nome
                produto_status: $cart_item.produto_status
                variacao_nome: $cart_item.variacao_nome
                variacao_sku: $cart_item.variacao_sku
                variacao_status: $cart_item.variacao_status
                preco: $cart_item.preco
                quantidade_disponivel: $cart_item.quantidade_disponivel
                subtotal: $line_subtotal
                disponivel: $item_available
              }
            }
          }
        }
      }
    }
  }

  response = {
    carrinho_id: $cart_id
    itens: $display_items
    total: $cart_total
  }
  tags = ["voltix:shopping-cart"]
  guid = "hDS3togqyTJXhnHn2PLvkD3FXdg"
}
