// Public customer registration
query cliente verb=POST {
  api_group = "DB_XANO_BASTOS"

  input {
    text nome_completo filters=trim
    text cpf filters=trim
    email email filters=trim|lower
    text telefone? filters=trim
    text password
  }

  stack {
    precondition (
      $input.nome_completo != "" &&
      $input.cpf != "" &&
      $input.password != ""
    ) {
      error_type = "inputerror"
      error = "Name, CPF, email, and password are required."
    }

    db.query CLIENTE {
      where = $db.CLIENTE.cpf == $input.cpf
      return = {type: "exists"}
    } as $cpf_exists

    precondition ($cpf_exists == false) {
      error_type = "badrequest"
      error = "A customer with this CPF already exists."
    }

    db.query CLIENTE {
      where = $db.CLIENTE.email == $input.email
      return = {type: "exists"}
    } as $email_exists

    precondition ($email_exists == false) {
      error_type = "badrequest"
      error = "A customer with this email already exists."
    }

    db.add CLIENTE {
      data = {
        nome_completo: $input.nome_completo
        cpf: $input.cpf
        email: $input.email
        telefone: $input.telefone
        password: $input.password
        status: "ATIVO"
        updated_at: now
      }
    } as $cliente
  }

  response = {
    id: $cliente.id
    nome_completo: $cliente.nome_completo
    cpf: $cliente.cpf
    email: $cliente.email
    telefone: $cliente.telefone
    status: $cliente.status
  }
  guid = "usgzHfPnwuTgQauF1eS19vDjOJs"
}