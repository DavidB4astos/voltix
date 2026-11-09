query "atendimentos/{attendance_id}/status" verb=POST {
  api_group = "Voltix Internal CRM"
  auth = "user"

  input {
    int attendance_id filters=min:1
    enum status {
      values = ["EM_ATENDIMENTO", "FINALIZADO", "CANCELADO"]
    }
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
        db.get atendimento {
          field_name = "id"
          field_value = $input.attendance_id
        } as $attendance

        precondition ($attendance != null) {
          error_type = "notfound"
          error = "Attendance not found."
        }

        var.update $status_anterior {
          value = $attendance.status
        }

        var.update $status_atual {
          value = $attendance.status
        }

        conditional {
          if ($input.status == $attendance.status) {
            // Same target: idempotent success, nothing is written.
            var.update $alterado {
              value = false
            }
          }

          else {
            precondition ($attendance.status == "ABERTO" || $attendance.status == "EM_ATENDIMENTO") {
              error_type = "badrequest"
              error = "Closed attendances cannot change status."
            }

            conditional {
              if ($input.status == "FINALIZADO" || $input.status == "CANCELADO") {
                precondition ($internal_user.role == "ADMINISTRADOR" || $attendance.usuario_interno_id == $internal_user.id) {
                  error_type = "accessdenied"
                  error = "Only the responsible internal user or an administrator can finish or cancel an attendance."
                }
              }
            }

            var $valid_transition {
              value = false
            }

            conditional {
              if ($attendance.status == "ABERTO" && $input.status == "EM_ATENDIMENTO") {
                var.update $valid_transition {
                  value = true
                }
              }

              elseif (($attendance.status == "ABERTO" || $attendance.status == "EM_ATENDIMENTO") && ($input.status == "FINALIZADO" || $input.status == "CANCELADO")) {
                var.update $valid_transition {
                  value = true
                }
              }
            }

            precondition ($valid_transition == true) {
              error_type = "badrequest"
              error = "Invalid attendance status transition."
            }

            db.patch atendimento {
              field_name = "id"
              field_value = $attendance.id
              data = {
                status: $input.status
                updated_at: now
              }
            } as $updated_attendance

            var.update $status_atual {
              value = $updated_attendance.status
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
    atendimento_id: $input.attendance_id
    status_anterior: $status_anterior
    status_atual: $status_atual
    alterado: $alterado
  }
  tags = ["voltix:attendance-management"]
  guid = "5mI3RPdbX8pY79Rq3F7JtykQgnc"
}
