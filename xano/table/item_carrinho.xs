table item_carrinho {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
    timestamp updated_at? {
      visibility = "private"
    }

    int carrinho_id {
      table = "carrinho"
    }
    int variacao_produto_id {
      table = "variacao_produto"
    }
    int quantidade filters=min:1
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "carrinho_id", op: "asc"}]}
    {type: "btree", field: [{name: "variacao_produto_id", op: "asc"}]}
    {type: "btree|unique", field: [{name: "carrinho_id", op: "asc"}, {name: "variacao_produto_id", op: "asc"}]}
  ]

  tags = ["voltix:shopping-cart"]
  guid = "4UQlPTL-zZxywmKHY1Mvkjjy5aE"
}
