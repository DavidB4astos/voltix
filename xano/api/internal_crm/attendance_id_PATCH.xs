query "atendimentos/{attendance_id}" verb=PATCH {
  api_group = "Voltix Internal CRM"
  auth = "user"

  input {
    int attendance_id filters=min:1
    text assunto? filters=trim
    text descricao? filters=trim
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

    precondition (($input.assunto != null || $input.descricao != null || $input.data_atendimento != null) && ($input.assunto == null || (($input.assunto|strlen) >= 1 && ($input.assunto|strlen) <= 200)) && ($input.descricao == null || (($input.descricao|strlen) >= 1 && ($input.descricao|strlen) <= 2000))) {
      error_type = "inputerror"
      error = "Provide a valid attendance field to update."
    }

    db.get atendimento {
      field_name = "id"
      field_value = $input.attendance_id
    } as $attendance

    precondition ($attendance != null) {
      error_type = "notfound"
      error = "Attendance not found."
    }

    precondition ($attendance.status == "ABERTO" || $attendance.status == "EM_ATENDIMENTO") {
      error_type = "badrequest"
      error = "Closed attendances cannot be edited."
    }

    var $updates {
      value = {updated_at: now}
    }

    conditional {
      if ($input.assunto != null) {
        var.update $updates {
          value = $updates|set:"assunto":$input.assunto
        }
      }
    }

    conditional {
      if ($input.descricao != null) {
        var.update $updates {
          value = $updates|set:"descricao":$input.descricao
        }
      }
    }

    conditional {
      if ($input.data_atendimento != null) {
        var.update $updates {
          value = $updates|set:"data_atendimento":$input.data_atendimento
        }
      }
    }

    db.transaction {
      stack {
        db.patch atendimento {
          field_name = "id"
          field_value = $input.attendance_id
          data = $updates
        } as $updated_attendance
      }
    }
  }

  response = $updated_attendance
  tags = ["voltix:attendance-management"]
}
