table variacao_produto {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
    timestamp updated_at? {
      visibility = "private"
    }

    int produto_id
    text nome_ou_descricao?
    text sku filters=trim
    decimal preco
    decimal quantidade_disponivel
    enum status?="ATIVO" {
      values = ["ATIVO", "INATIVO"]
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "produto_id", op: "asc"}]}
    {type: "btree|unique", field: [{name: "sku", op: "asc"}]}
  ]

  tags = ["voltix:product-management"]
}
