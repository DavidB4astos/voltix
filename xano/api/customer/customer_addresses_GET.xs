query "addresses" verb=GET {
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

    db.query endereco {
      where = $db.endereco.cliente_id == $auth.id
      return = {type: "list"}
    } as $addresses
  }

  response = $addresses
  tags = ["voltix:customer-addresses"]
}
