query "cart/items/{item_id}" verb=DELETE {
  api_group = "Voltix Customer"
  auth = "CLIENTE"

  input {
    int item_id filters=min:1
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
        db.del item_carrinho {
          field_name = "id"
          field_value = $item.id
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
    removido: true
  }
  tags = ["voltix:shopping-cart"]
}
