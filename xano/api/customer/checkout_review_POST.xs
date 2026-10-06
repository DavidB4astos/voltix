query "checkout/review" verb=POST {
  api_group = "Voltix Customer"
  auth = "CLIENTE"

  input {
    int endereco_id filters=min:1
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

    db.get endereco {
      field_name = "id"
      field_value = $input.endereco_id
    } as $address

    precondition (
      $address != null &&
      $address.cliente_id == $auth.id &&
      $address.status == "ATIVO"
    ) {
      error_type = "badrequest"
      error = "An active address belonging to this customer is required."
    }

    db.query carrinho {
      where = $db.carrinho.cliente_id == $auth.id
      return = {type: "single"}
    } as $cart

    precondition ($cart != null) {
      error_type = "badrequest"
      error = "The cart is empty."
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
        sku: $db.variacao_produto.sku
        variacao_status: $db.variacao_produto.status
        preco: $db.variacao_produto.preco
        estoque: $db.variacao_produto.quantidade_disponivel
        subtotal: $db.variacao_produto.preco * $db.item_carrinho.quantidade
        disponivel: $db.produto.status == "ATIVO" && $db.variacao_produto.status == "ATIVO" && $db.variacao_produto.quantidade_disponivel >= $db.item_carrinho.quantidade
      }
      where = $db.item_carrinho.carrinho_id == $cart.id
      sort = {id: "asc"}
      output = ["id", "variacao_produto_id", "quantidade"]
    } as $cart_items

    precondition (($cart_items|count) > 0) {
      error_type = "badrequest"
      error = "The cart is empty."
    }

    var $review_items {
      value = []
    }

    var $review_snapshot {
      value = []
    }

    var $subtotal {
      value = 0
    }

    foreach ($cart_items) {
      each as $item {
        var.update $review_items {
          value = $review_items|push:{
            item_id: $item.id
            variacao_id: $item.variacao_produto_id
            produto_nome: $item.produto_nome
            variacao_nome: $item.variacao_nome
            sku: $item.sku
            quantidade: $item.quantidade
            preco_unitario: $item.preco
            subtotal: $item.subtotal
            produto_status: $item.produto_status
            variacao_status: $item.variacao_status
            estoque_disponivel: $item.estoque
            disponivel: $item.disponivel
          }
        }

        var.update $review_snapshot {
          value = $review_snapshot|push:{
            item_id: $item.id
            variacao_id: $item.variacao_produto_id
            quantidade: $item.quantidade
            preco_unitario: $item.preco
            estoque_disponivel: $item.estoque
            produto_status: $item.produto_status
            variacao_status: $item.variacao_status
          }
        }

        var.update $subtotal {
          value = $subtotal + $item.subtotal
        }
      }
    }
  }

  response = {
    endereco_id: $address.id
    endereco: {
      cep: $address.cep
      logradouro: $address.logradouro
      numero: $address.numero
      complemento: $address.complemento
      bairro: $address.bairro
      cidade: $address.cidade
      estado: $address.estado
      identificacao: $address.identificacao
    }
    itens: $review_items
    revisao: $review_snapshot
    subtotal: $subtotal
    valor_frete: 0
    valor_total: $subtotal
  }
  tags = ["voltix:checkout-orders"]
}
