query "orders/{order_id}/status" verb=POST {
  api_group = "Voltix Internal Orders"
  auth = "user"

  input {
    int order_id filters=min:1

    // Only forward operational steps are accepted; CANCELADO is not a target here.
    enum status {
      values = ["EM_PREPARACAO", "ENVIADO", "ENTREGUE"]
    }
  }

  stack {
    db.get user {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "role", "status"]
    } as $internal_user

    precondition ($internal_user != null && $internal_user.status == "ATIVO" && $internal_user.role == "ADMINISTRADOR") {
      error_type = "accessdenied"
      error = "Active administrator access is required."
    }

    var $codigo {
      value = null
    }

    var $status_anterior {
      value = null
    }

    var $status_atual {
      value = null
    }

    var $alterado {
      value = false
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

        var.update $status_anterior {
          value = $order.status
        }

        var.update $status_atual {
          value = $order.status
        }

        conditional {
          if ($input.status == $order.status) {
            // Same target: idempotent success, nothing is written.
            var.update $alterado {
              value = false
            }
          }

          else {
            var $proximo_status {
              value = null
            }

            conditional {
              if ($order.status == "PAGAMENTO_CONFIRMADO") {
                var.update $proximo_status {
                  value = "EM_PREPARACAO"
                }
              }

              elseif ($order.status == "EM_PREPARACAO") {
                var.update $proximo_status {
                  value = "ENVIADO"
                }
              }

              elseif ($order.status == "ENVIADO") {
                var.update $proximo_status {
                  value = "ENTREGUE"
                }
              }
            }

            precondition ($proximo_status != null && $input.status == $proximo_status) {
              error_type = "badrequest"
              error = "Invalid order status transition."
            }

            db.edit pedido {
              field_name = "id"
              field_value = $order.id
              data = {
                status: $input.status
                updated_at: now
              }
            } as $updated_order

            var.update $status_atual {
              value = $updated_order.status
            }

            var.update $alterado {
              value = true
            }
          }
        }
      }
    }
  }

  response = {
    pedido_id: $input.order_id
    codigo: $codigo
    status_anterior: $status_anterior
    status_atual: $status_atual
    alterado: $alterado
  }
  tags = ["voltix:internal-orders"]
  guid = "fI2zXn8RiO-j_mVymCxgccA6FiM"
}
