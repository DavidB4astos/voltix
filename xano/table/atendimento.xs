// Internal CRM attendance record. Always linked to a customer and an internal
// owner, optionally to an order of the same customer.
table atendimento {
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
    int usuario_interno_id {
      table = "user"
    }
    int pedido_id? {
      table = "pedido"
    }

    text assunto filters=trim
    text descricao filters=trim
    enum status?="ABERTO" {
      values = ["ABERTO", "EM_ATENDIMENTO", "FINALIZADO", "CANCELADO"]
    }
    timestamp data_atendimento?=now
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "cliente_id", op: "asc"}]}
    {type: "btree", field: [{name: "usuario_interno_id", op: "asc"}]}
    {type: "btree", field: [{name: "pedido_id", op: "asc"}]}
    {type: "btree", field: [{name: "status", op: "asc"}]}
    {type: "btree", field: [{name: "data_atendimento", op: "desc"}]}
  ]

  tags = ["voltix:attendance-management"]
  guid = "tuUsTN1wH7wh6iOW8Z74r6eQcQA"
}
