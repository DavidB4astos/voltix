// Delete CLIENTE record.
query "cliente/{cliente_id}" verb=DELETE {
  api_group = "DB_XANO_BASTOS"

  input {
    int cliente_id? filters=min:1
  }

  stack {
    db.del CLIENTE {
      field_name = "id"
      field_value = $input.cliente_id
    }
  }

  response = null
  guid = "Uru99cw23t6_lpIvjbYcA1aXXhw"
}