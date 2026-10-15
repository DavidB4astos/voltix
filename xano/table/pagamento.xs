table pagamento {
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
    enum metodo {
      values = ["PIX", "CARTAO", "BOLETO"]
    }
    decimal valor
    enum status?="PENDENTE" {
      values = ["PENDENTE", "APROVADO", "RECUSADO", "CANCELADO"]
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "pedido_id", op: "asc"}]}
  ]

  tags = ["voltix:checkout-orders"]
  guid = "O77clflILgtFnKSSjgJEZ14sJ1w"
}
