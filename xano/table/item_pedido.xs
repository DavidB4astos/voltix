table item_pedido {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
    timestamp updated_at? {
      visibility = "private"
    }

    int pedido_id {
      table = "pedido"
    }
    int variacao_produto_id {
      table = "variacao_produto"
    }
    int quantidade filters=min:1
    decimal preco_unitario
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "pedido_id", op: "asc"}]}
    {type: "btree", field: [{name: "variacao_produto_id", op: "asc"}]}
    {type: "btree|unique", field: [{name: "pedido_id", op: "asc"}, {name: "variacao_produto_id", op: "asc"}]}
  ]

  tags = ["voltix:checkout-orders"]
  guid = "wM0nj7z_RtQpoZ0vq3zzhlEA5C8"
}
