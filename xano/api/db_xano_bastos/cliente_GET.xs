// Return only the authenticated customer's identity
query cliente verb=GET {
  api_group = "DB_XANO_BASTOS"
  auth = "CLIENTE"

  input {
  }

  stack {
    db.get CLIENTE {
      field_name = "id"
      field_value = $auth.id
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
  guid = "OFo85Pk5TKS6BpakGwE9339lWv0"
}