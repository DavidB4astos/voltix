// Get CLIENTE record
query "cliente/{cliente_id}" verb=GET {
  api_group = "DB_XANO_BASTOS"
  auth = "CLIENTE"

  input {
    int cliente_id? filters=min:1
  }

  stack {
    precondition ($auth.id == $input.cliente_id) {
      error_type = "accessdenied"
      error = "Customers may access only their own profile."
    }

    db.get CLIENTE {
      field_name = "id"
      field_value = $input.cliente_id
      output = ["id", "nome_completo", "cpf", "email", "telefone", "status"]
    } as $cliente
  
    precondition ($cliente != null && $cliente.status == "ATIVO") {
      error_type = "accessdenied"
      error = "Active customer access is required."
    }
  }

  response = {
    id: $cliente.id
    nome_completo: $cliente.nome_completo
    cpf: $cliente.cpf
    email: $cliente.email
    telefone: $cliente.telefone
    status: $cliente.status
  }
  guid = "rqndy4LGNt57nnjK936YvdY7kNE"
}