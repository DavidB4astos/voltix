// Query all CLIENTE records
query cliente verb=GET {
  api_group = "DB_XANO_BASTOS"

  input {
  }

  stack {
    db.query CLIENTE {
      return = {type: "list"}
    } as $cliente
  }

  response = $cliente
  guid = "OFo85Pk5TKS6BpakGwE9339lWv0"
}