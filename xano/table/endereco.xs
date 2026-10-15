table endereco {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
    timestamp updated_at? {
      visibility = "private"
    }

    int cliente_id {
      table = "CLIENTE"
    }
    text cep? filters=trim
    text logradouro? filters=trim
    text numero? filters=trim
    text complemento? filters=trim
    text bairro? filters=trim
    text cidade? filters=trim
    text estado? filters=trim
    text identificacao? filters=trim
    bool principal?=false
    enum status?="ATIVO" {
      values = ["ATIVO", "INATIVO"]
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "cliente_id", op: "asc"}]}
  ]

  tags = ["voltix:customer-addresses"]
  guid = "i3nbTAJsbFSHRVfaBjBSWwn-0aQ"
}
