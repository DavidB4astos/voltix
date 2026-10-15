query "cart/items/{item_id}" verb=PATCH {
  api_group = "Voltix Customer"
  auth = "CLIENTE"

  input {
    int item_id filters=min:1
    int quantidade filters=min:0
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

    db.get item_carrinho {
      field_name = "id"
      field_value = $input.item_id
    } as $item

    precondition ($item != null) {
      error_type = "notfound"
      error = "Cart item not found."
    }

    db.get carrinho {
      field_name = "id"
      field_value = $item.carrinho_id
      output = ["id", "cliente_id"]
    } as $cart

    precondition ($cart != null && $cart.cliente_id == $auth.id) {
      error_type = "accessdenied"
      error = "Cart item access is denied."
    }

    db.transaction {
      stack {
        conditional {
          if ($input.quantidade == 0) {
            db.del item_carrinho {
              field_name = "id"
              field_value = $item.id
            }
          }

          else {
            db.get variacao_produto {
              field_name = "id"
              field_value = $item.variacao_produto_id
              output = ["id", "produto_id", "quantidade_disponivel", "status"]
            } as $variation

            precondition ($variation != null && $variation.status == "ATIVO") {
              error_type = "badrequest"
              error = "Inactive product variations can only be removed."
            }

            db.get produto {
              field_name = "id"
              field_value = $variation.produto_id
              output = ["id", "status"]
            } as $product

            precondition ($product != null && $product.status == "ATIVO") {
              error_type = "badrequest"
              error = "Inactive products can only be removed from the cart."
            }

            precondition ($input.quantidade <= $variation.quantidade_disponivel) {
              error_type = "badrequest"
              error = "Requested quantity exceeds available stock."
            }

            db.patch item_carrinho {
              field_name = "id"
              field_value = $item.id
              data = {
                quantidade: $input.quantidade
                updated_at: now
              }
            } as $updated_item
          }
        }

        db.patch carrinho {
          field_name = "id"
          field_value = $cart.id
          data = {updated_at: now}
        } as $updated_cart
      }
    }
  }

  response = {
    id: $item.id
    removido: $input.quantidade == 0
    quantidade: $input.quantidade
  }
  tags = ["voltix:shopping-cart"]
  guid = "LIRYWTc6qj5il9E8eQGquIlFBaE"
}
