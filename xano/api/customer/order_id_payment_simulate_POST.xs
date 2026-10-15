query "orders/{order_id}/payment/simulate" verb=POST {
  api_group = "Voltix Customer"
  auth = "CLIENTE"

  input {
    int order_id filters=min:1
  }

  stack {
    db.get CLIENTE {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "status"]
    } as $customer

    precondition ($customer != null && $customer.status == "ATIVO") {
      error_type = "accessdenied"
      error = "Active customer access is required."
    }

    db.get pedido {
      field_name = "id"
      field_value = $input.order_id
    } as $order

    precondition ($order != null && $order.cliente_id == $auth.id) {
      error_type = "notfound"
      error = "Order not found."
    }

    db.query pagamento {
      where = $db.pagamento.pedido_id == $order.id
      return = {type: "single"}
    } as $payment

    precondition ($payment != null) {
      error_type = "standard"
      error = "Order payment record is unavailable."
    }

    precondition ($payment.valor == $order.valor_total) {
      error_type = "standard"
      error = "Order payment data is inconsistent."
    }

    var $simulated {
      value = false
    }

    db.transaction {
      stack {
        db.get pedido {
          field_name = "id"
          field_value = $input.order_id
        } as $current_order

        precondition (
          $current_order != null &&
          $current_order.cliente_id == $auth.id
        ) {
          error_type = "notfound"
          error = "Order not found."
        }

        db.query pagamento {
          where = $db.pagamento.pedido_id == $current_order.id
          return = {type: "single"}
        } as $current_payment

        precondition (
          $current_payment != null &&
          $current_payment.valor == $current_order.valor_total
        ) {
          error_type = "standard"
          error = "Order payment data is inconsistent."
        }

        conditional {
          if (
            $current_order.status == "PAGAMENTO_CONFIRMADO" &&
            $current_payment.status == "APROVADO"
          ) {
            var.update $simulated {
              value = false
            }
          }

          else {
            precondition (
              $current_order.status == "AGUARDANDO_PAGAMENTO" &&
              $current_payment.status == "PENDENTE"
            ) {
              error_type = "badrequest"
              error = "Payment cannot be simulated in the current order state."
            }

            db.edit pagamento {
              field_name = "id"
              field_value = $current_payment.id
              data = {
                status: "APROVADO"
                updated_at: now
              }
            } as $approved_payment

            db.edit pedido {
              field_name = "id"
              field_value = $current_order.id
              data = {
                status: "PAGAMENTO_CONFIRMADO"
                updated_at: now
              }
            } as $confirmed_order

            var.update $simulated {
              value = true
            }
          }
        }
      }
    }

    db.get pedido {
      field_name = "id"
      field_value = $input.order_id
    } as $result_order

    db.query pagamento {
      where = $db.pagamento.pedido_id == $result_order.id
      return = {type: "single"}
    } as $result_payment
  }

  response = {
    simulado: true
    alterado: $simulated
    pedido_id: $result_order.id
    codigo: $result_order.codigo
    pedido_status: $result_order.status
    pagamento: {
      metodo: $result_payment.metodo
      valor: $result_payment.valor
      status: $result_payment.status
    }
  }
  tags = ["voltix:order-payment"]
  guid = "jaT0wmt61lf4HyQOkW-v75OSpPA"
}
