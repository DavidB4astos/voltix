query "orders/{order_id}/cancel" verb=POST {
  api_group = "Voltix Internal Orders"
  auth = "user"

  input {
    int order_id filters=min:1
  }

  stack {
    db.get user {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "role", "status"]
    } as $internal_user

    precondition ($internal_user != null && $internal_user.status == "ATIVO" && $internal_user.role == "ADMINISTRADOR") {
      error_type = "accessdenied"
      error = "Active administrator access is required."
    }

    function.run "Voltix Orders/cancel_order" {
      input = {
        order_id: $input.order_id
        kind: "admin"
      }
    } as $cancellation
  }

  response = $cancellation
  tags = ["voltix:internal-orders"]
  guid = "gbhLdzuqbGXFbqmtSEZPOuefczw"
}
