// Get CLIENTE record
query "cliente/{cliente_id}" verb=GET {
  api_group = "DB_XANO_BASTOS"

  input {
    int cliente_id? filters=min:1
  }

  stack {
    db.get CLIENTE {
      field_name = "id"
      field_value = $input.cliente_id
    } as $cliente
  
    precondition ($cliente != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $cliente
  guid = "rqndy4LGNt57nnjK936YvdY7kNE"
}