// Shared transactional core for order cancellation.
// Called by Voltix Customer (kind = "cliente") and Voltix Internal Orders (kind = "admin").
// Who may cancel which order is enforced by the calling endpoints.
function "Voltix Orders/cancel_order" {
  input {
    // Order to cancel.
    int order_id filters=min:1

    // "cliente": own order while AGUARDANDO_PAGAMENTO.
    // "admin": AGUARDANDO_PAGAMENTO or PAGAMENTO_CONFIRMADO.
    text kind filters=trim
  }

  stack {
    var $efeito {
      value = "cancelado"
    }

    var $codigo {
      value = null
    }

    db.transaction {
      stack {
        db.get pedido {
          field_name = "id"
          field_value = $input.order_id
        } as $order

        precondition ($order != null) {
          error_type = "notfound"
          error = "Order not found."
        }

        var.update $codigo {
          value = $order.codigo
        }

        conditional {
          if ($order.status == "CANCELADO") {
            var.update $efeito {
              value = "ja_cancelado"
            }
          }

          else {
            precondition (($input.kind == "cliente" && $order.status == "AGUARDANDO_PAGAMENTO") || ($input.kind == "admin" && ($order.status == "AGUARDANDO_PAGAMENTO" || $order.status == "PAGAMENTO_CONFIRMADO"))) {
              error_type = "badrequest"
              error = "Order cannot be cancelled in its current state."
            }

            db.query item_pedido {
              where = $db.item_pedido.pedido_id == $order.id
              sort = {id: "asc"}
              return = {type: "list"}
            } as $order_items

            foreach ($order_items) {
              each as $item {
                db.increment "variacao_produto" {
                  where = $db.variacao_produto.id == $item.variacao_produto_id
                  field_name = "quantidade_disponivel"
                  value = $item.quantidade
                  return = {type: "count"}
                } as $returned

                precondition ($returned > 0) {
                  error_type = "badrequest"
                  error = "Order stock could not be returned."
                }
              }
            }

            db.edit pedido {
              field_name = "id"
              field_value = $order.id
              data = {
                status: "CANCELADO"
                updated_at: now
              }
            } as $cancelled_order

            db.query pagamento {
              where = $db.pagamento.pedido_id == $order.id
              return = {type: "single"}
            } as $payment

            precondition ($payment != null) {
              error_type = "standard"
              error = "Order payment record is unavailable."
            }

            db.edit pagamento {
              field_name = "id"
              field_value = $payment.id
              data = {
                status: "CANCELADO"
                updated_at: now
              }
            } as $cancelled_payment
          }
        }
      }
    }
  }

  response = {
    pedido_id: $input.order_id
    codigo: $codigo
    pedido_status: "CANCELADO"
    efeito: $efeito
  }

  tags = ["voltix:orders"]
  guid = "HKe2JA4ZIdhoAfBE1Oz0zsjiSTs"
}
