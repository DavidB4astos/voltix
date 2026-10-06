query "login" verb=POST {
  api_group = "Voltix Customer"

  input {
    email email filters=trim|lower
    text password
  }

  stack {
    db.get CLIENTE {
      field_name = "email"
      field_value = $input.email
      output = ["id", "nome_completo", "cpf", "email", "telefone", "password", "status"]
    } as $customer

    precondition ($customer != null) {
      error_type = "accessdenied"
      error = "Invalid Credentials."
    }

    precondition ($customer.status == "ATIVO") {
      error_type = "accessdenied"
      error = "Invalid Credentials."
    }

    security.check_password {
      text_password = $input.password
      hash_password = $customer.password
    } as $password_matches

    precondition ($password_matches) {
      error_type = "accessdenied"
      error = "Invalid Credentials."
    }

    security.create_auth_token {
      table = "CLIENTE"
      extras = {}
      expiration = 86400
      id = $customer.id
    } as $auth_token
  }

  response = {
    authToken: $auth_token
    customer: {
      id: $customer.id
      nome_completo: $customer.nome_completo
      cpf: $customer.cpf
      email: $customer.email
      telefone: $customer.telefone
      status: $customer.status
    }
  }
  tags = ["voltix:customer"]
}
