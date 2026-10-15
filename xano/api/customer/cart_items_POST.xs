query "cart/items" verb=POST {
  api_group = "Voltix Customer"
  auth = "CLIENTE"

  input {
    int variacao_id filters=min:1
    int quantidade filters=min:1
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

    db.get variacao_produto {
      field_name = "id"
      field_value = $input.variacao_id
      output = ["id", "produto_id", "preco", "quantidade_disponivel", "status"]
    } as $variation

    precondition ($variation != null && $variation.status == "ATIVO") {
      error_type = "badrequest"
      error = "An active product variation is required."
    }

    db.get produto {
      field_name = "id"
      field_value = $variation.produto_id
      output = ["id", "status"]
    } as $product

    precondition ($product != null && $product.status == "ATIVO") {
      error_type = "badrequest"
      error = "An active product is required."
    }

    precondition ($input.quantidade <= $variation.quantidade_disponivel) {
      error_type = "badrequest"
      error = "Requested quantity exceeds available stock."
    }

    db.query carrinho {
      where = $db.carrinho.cliente_id == $auth.id
      return = {type: "single"}
    } as $existing_cart

    var $cart {
      value = $existing_cart
    }

    db.transaction {
      stack {
        conditional {
          if ($existing_cart == null) {
            db.add carrinho {
              data = {
                cliente_id: $auth.id
                updated_at: now
              }
            } as $created_cart

            var.update $cart {
              value = $created_cart
            }
          }
        }

        db.patch carrinho {
          field_name = "id"
          field_value = $cart.id
          data = {updated_at: now}
        } as $updated_cart

        db.query item_carrinho {
          where = $db.item_carrinho.carrinho_id == $cart.id && $db.item_carrinho.variacao_produto_id == $input.variacao_id
          return = {type: "single"}
        } as $existing_item

        conditional {
          if ($existing_item != null) {
            db.patch item_carrinho {
              field_name = "id"
              field_value = $existing_item.id
              data = {
                quantidade: $input.quantidade
                updated_at: now
              }
            } as $item
          }

          else {
            db.add item_carrinho {
              data = {
                carrinho_id: $cart.id
                variacao_produto_id: $variation.id
                quantidade: $input.quantidade
                updated_at: now
              }
            } as $item
          }
        }
      }
    }
  }

  response = {
    id: $item.id
    carrinho_id: $cart.id
    variacao_produto_id: $item.variacao_produto_id
    quantidade: $item.quantidade
  }
  tags = ["voltix:shopping-cart"]
  guid = "lMHPdjjcnSzCTo0s837EB76cwSw"
}
