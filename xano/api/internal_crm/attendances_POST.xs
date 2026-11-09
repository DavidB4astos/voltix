query "atendimentos" verb=POST {
  api_group = "Voltix Internal CRM"
  auth = "user"

  input {
    int cliente_id filters=min:1
    int pedido_id?
    text assunto filters=trim
    text descricao filters=trim
    timestamp data_atendimento?
  }

  stack {
    db.get user {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "role", "status"]
    } as $internal_user

    precondition ($internal_user != null && $internal_user.status == "ATIVO" && ($internal_user.role == "FUNCIONARIO" || $internal_user.role == "ADMINISTRADOR")) {
      error_type = "accessdenied"
      error = "Active internal access is required."
    }

    precondition ($input.assunto != null && ($input.assunto|strlen) >= 1 && ($input.assunto|strlen) <= 200) {
      error_type = "inputerror"
      error = "Attendance subject must have between 1 and 200 characters."
    }

    precondition ($input.pedido_id == null || $input.pedido_id >= 1) {
      error_type = "inputerror"
      error = "Invalid order id."
    }

    precondition ($input.descricao != null && ($input.descricao|strlen) >= 1 && ($input.descricao|strlen) <= 2000) {
      error_type = "inputerror"
      error = "Attendance description must have between 1 and 2000 characters."
    }

    db.get CLIENTE {
      field_name = "id"
      field_value = $input.cliente_id
      output = ["id"]
    } as $customer

    precondition ($customer != null) {
      error_type = "notfound"
      error = "Customer not found."
    }

    conditional {
      if ($input.pedido_id != null) {
        db.get pedido {
          field_name = "id"
          field_value = $input.pedido_id
          output = ["id", "cliente_id"]
        } as $order

        precondition ($order != null) {
          error_type = "notfound"
          error = "Order not found."
        }

        precondition ($order.cliente_id == $input.cliente_id) {
          error_type = "badrequest"
          error = "The order must belong to the attendance customer."
        }
      }
    }

    var $attendance {
      value = null
    }

    db.transaction {
      stack {
        conditional {
          if ($input.data_atendimento == null) {
            db.add atendimento {
              data = {
                cliente_id         : $input.cliente_id
                usuario_interno_id : $internal_user.id
                pedido_id          : $input.pedido_id
                assunto            : $input.assunto
                descricao          : $input.descricao
                status             : "ABERTO"
                updated_at         : now
              }
            } as $created_attendance

            var.update $attendance {
              value = $created_attendance
            }
          }

          else {
            db.add atendimento {
              data = {
                cliente_id         : $input.cliente_id
                usuario_interno_id : $internal_user.id
                pedido_id          : $input.pedido_id
                assunto            : $input.assunto
                descricao          : $input.descricao
                status             : "ABERTO"
                data_atendimento   : $input.data_atendimento
                updated_at         : now
              }
            } as $created_attendance_with_date

            var.update $attendance {
              value = $created_attendance_with_date
            }
          }
        }
      }
    }
  }

  response = $attendance
  tags = ["voltix:attendance-management"]
  guid = "MTwvlzJ9cWlYaSJTuTOIVFQXpaA"
}
