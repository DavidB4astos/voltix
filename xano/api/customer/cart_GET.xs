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

    var $cart_items {
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
            subtotal: $db.variacao_produto.preco * $db.item_carrinho.quantidade
            disponivel: $db.produto.status == "ATIVO" && $db.variacao_produto.status == "ATIVO" && $db.variacao_produto.quantidade_disponivel >= $db.item_carrinho.quantidade
          }
          where = $db.item_carrinho.carrinho_id == $cart.id
          sort = {id: "asc"}
          output = [
            "id",
            "variacao_produto_id",
            "quantidade"
          ]
        } as $cart_items

        foreach ($cart_items) {
          each as $cart_item {
            var.update $cart_total {
              value = $cart_total + $cart_item.subtotal
            }
          }
        }
      }
    }
  }

  response = {
    carrinho_id: $cart_id
    itens: $cart_items
    total: $cart_total
  }
  tags = ["voltix:shopping-cart"]
}
