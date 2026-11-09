query "orders/{order_id}/cancel" verb=POST {
  api_group = "Voltix Customer"
  auth = "CLIENTE"

  input {
    int order_id filters=min:1
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

    db.get pedido {
      field_name = "id"
      field_value = $input.order_id
      output = ["id", "cliente_id"]
    } as $owned_order

    precondition ($owned_order != null && $owned_order.cliente_id == $auth.id) {
      error_type = "notfound"
      error = "Order not found."
    }

    function.run "Voltix Orders/cancel_order" {
      input = {
        order_id: $input.order_id
        kind: "cliente"
      }
    } as $cancellation
  }

  response = $cancellation
  tags = ["voltix:checkout-orders"]
}
