table CLIENTE {
  auth = true

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
    timestamp updated_at? {
      visibility = "private"
    }
  
    // ID DO USUARIO PK
    int USER_ID?
  
    text CELULAR_CLIENT? filters=trim
  
    text nome_completo? filters=trim
    text cpf filters=trim
    email? email filters=trim|lower
    text telefone? filters=trim
    password? password {
      visibility = "internal"
    }
    enum status?="ATIVO" {
      values = ["ATIVO", "INATIVO"]
      visibility = "private"
    }
  
    // FK
    int status_cliente_id? {
      table = "STATUS_CLIENTE"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree|unique", field: [{name: "cpf", op: "asc"}]}
    {type: "btree|unique", field: [{name: "email", op: "asc"}]}
  ]

  tags = ["módulo 01"]
  guid = "y2LsJE7WQuxMCUHyQx_yDZpcIIU"
}