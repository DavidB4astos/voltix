table categoria {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
    timestamp updated_at? {
      visibility = "private"
    }

    text name filters=trim
    text description? filters=trim
    enum status?="ATIVO" {
      values = ["ATIVO", "INATIVO"]
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "name", op: "asc"}]}
  ]

  tags = ["voltix:catalog-management"]
}
