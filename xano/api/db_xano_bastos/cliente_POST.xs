// Add CLIENTE record
query cliente verb=POST {
  api_group = "DB_XANO_BASTOS"

  input {
    dblink {
      table = "CLIENTE"
    }
  }

  stack {
    db.add CLIENTE {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $cliente
  }

  response = $cliente
  guid = "usgzHfPnwuTgQauF1eS19vDjOJs"
}