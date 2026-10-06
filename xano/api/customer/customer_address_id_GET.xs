query "addresses/{address_id}" verb=GET {
  api_group = "Voltix Customer"
  auth = "CLIENTE"

  input {
    int address_id filters=min:1
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
      field_value = $input.address_id
    } as $address

    precondition ($address != null && $address.cliente_id == $auth.id) {
      error_type = "notfound"
      error = "Address not found."
    }
  }

  response = $address
  tags = ["voltix:customer-addresses"]
}
