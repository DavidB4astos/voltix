query "atendimentos/{attendance_id}" verb=GET {
  api_group = "Voltix Internal CRM"
  auth = "user"

  input {
    int attendance_id filters=min:1
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

    db.get atendimento {
      field_name = "id"
      field_value = $input.attendance_id
    } as $attendance

    precondition ($attendance != null) {
      error_type = "notfound"
      error = "Attendance not found."
    }
  }

  response = $attendance
  tags = ["voltix:attendance-management"]
  guid = "XwbqC-3eUD4eyF7_thTfrplxuGo"
}
