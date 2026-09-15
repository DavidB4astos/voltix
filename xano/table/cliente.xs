table CLIENTE {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    // ID DO USUARIO PK
    int USER_ID?
  
    text CELULAR_CLIENT? filters=trim
  
    // cpf do cliente
    text cpf? filters=trim
  
    // FK
    int status_cliente_id? {
      table = "STATUS_CLIENTE"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["módulo 01"]
  guid = "y2LsJE7WQuxMCUHyQx_yDZpcIIU"
}