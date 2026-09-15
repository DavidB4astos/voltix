// Add STATUS_CLIENTE record
query status_cliente verb=POST {
  api_group = "DB_XANO_BASTOS"

  input {
    dblink {
      table = "STATUS_CLIENTE"
    }
  }

  stack {
    db.add STATUS_CLIENTE {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $status_cliente
  }

  response = $status_cliente
  guid = "Ds3d2OMgny7B0loyuPJg8DiU98I"
}