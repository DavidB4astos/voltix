query "products/{product_id}" verb=DELETE {
  api_group = "Product Management"
  auth = "user"

  input {
    int product_id filters=min:1
  }

  stack {
    db.get user {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "role", "status"]
    } as $user

    precondition ($user != null) {
      error_type = "accessdenied"
      error = "Invalid authenticated user."
    }

    precondition ($user.role == "ADMINISTRADOR" && $user.status == "ATIVO") {
      error_type = "accessdenied"
      error = "Administrator access is required."
    }

    db.get produto {
      field_name = "id"
      field_value = $input.product_id
      output = ["id"]
    } as $product

    precondition ($product != null) {
      error_type = "notfound"
      error = "Product not found."
    }

    db.transaction {
      stack {
        db.query variacao_produto {
          where = $db.variacao_produto.produto_id == $input.product_id
          return = {type: "list"}
          output = ["id"]
        } as $variations

        var $variation_ids {
          value = []
        }

        foreach ($variations) {
          each as $variation {
            var.update $variation_ids {
              value = $variation_ids|push:$variation.id
            }
          }
        }

        var $order_item_exists {
          value = false
        }

        var $cart_item_exists {
          value = false
        }

        conditional {
          if (($variation_ids|count) > 0) {
            db.query item_pedido {
              where = $db.item_pedido.variacao_produto_id in $variation_ids
              return = {type: "exists"}
            } as $found_order_item

            var.update $order_item_exists {
              value = $found_order_item
            }

            db.query item_carrinho {
              where = $db.item_carrinho.variacao_produto_id in $variation_ids
              return = {type: "exists"}
            } as $found_cart_item

            var.update $cart_item_exists {
              value = $found_cart_item
            }
          }
        }

        precondition ($order_item_exists == false && $cart_item_exists == false) {
          error_type = "badrequest"
          error = "Product has commercial history and cannot be deleted. Inactivate it instead."
        }

        db.del variacao_produto {
          field_name = "produto_id"
          field_value = $input.product_id
        }

        db.del produto {
          field_name = "id"
          field_value = $input.product_id
        }
      }
    }
  }

  response = {
    id: $input.product_id
    deleted: true
  }
  tags = ["voltix:product-management"]
  guid = "llIS7uIUZNJLK43ouTICR_QU5zU"
}
