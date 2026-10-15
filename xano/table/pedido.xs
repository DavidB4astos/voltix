table pedido {
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
    int endereco_id {
      table = "endereco"
    }
    text codigo filters=trim
    timestamp data_pedido?=now
    enum status?="AGUARDANDO_PAGAMENTO" {
      values = ["AGUARDANDO_PAGAMENTO", "PAGAMENTO_CONFIRMADO", "EM_PREPARACAO", "ENVIADO", "ENTREGUE", "CANCELADO"]
    }
    decimal subtotal
    decimal valor_frete?=0
    decimal valor_total
    text entrega_cep?
    text entrega_logradouro?
    text entrega_numero?
    text entrega_complemento?
    text entrega_bairro?
    text entrega_cidade?
    text entrega_estado?
    text entrega_identificacao?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "cliente_id", op: "asc"}]}
    {type: "btree", field: [{name: "endereco_id", op: "asc"}]}
    {type: "btree|unique", field: [{name: "codigo", op: "asc"}]}
  ]

  tags = ["voltix:checkout-orders"]
  guid = "SiM3F-jgq61XzniVFjk4-tSvOrY"
}
