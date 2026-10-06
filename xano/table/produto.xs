table produto {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
    timestamp updated_at? {
      visibility = "private"
    }

    text nome?
    text descricao?
    text especificacoes_tecnicas?
    text imagem_principal?
    int categoria_id
    int marca_id
    enum status?="ATIVO" {
      values = ["ATIVO", "INATIVO"]
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "categoria_id", op: "asc"}]}
    {type: "btree", field: [{name: "marca_id", op: "asc"}]}
  ]

  tags = ["voltix:product-management"]
}
