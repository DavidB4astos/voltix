query "me" verb=GET {
  api_group = "Voltix Customer"
  auth = "CLIENTE"

  input {
  }

  stack {
    db.get CLIENTE {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "nome_completo", "cpf", "email", "telefone", "status"]
    } as $customer

    precondition ($customer != null && $customer.status == "ATIVO") {
      error_type = "accessdenied"
      error = "Active customer access is required."
    }
  }

  response = {
    id: $customer.id
    nome_completo: $customer.nome_completo
    cpf: $customer.cpf
    email: $customer.email
    telefone: $customer.telefone
    status: $customer.status
  }
  tags = ["voltix:customer"]
}
