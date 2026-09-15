// Status do cliente
table STATUS_CLIENTE {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    // status do cliente
    text STATUS_CLIENT? filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["módulo 01"]
  guid = "Dyq6WXNyzWrz9TDiKga1_pnWsYk"
}