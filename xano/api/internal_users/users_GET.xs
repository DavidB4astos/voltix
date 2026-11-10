// List all internal users for an active administrator.
query users verb=GET {
  api_group = "Voltix Internal Users"
  auth = "user"

  input {
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

    db.query user {
      sort = {name: "asc", id: "asc"}
      return = {type: "list"}
      output = ["id", "name", "email", "role", "status", "created_at"]
    } as $users
  }

  response = $users
  tags = ["voltix:internal-users"]
  guid = "YlN3s8g-DhCUmf3hwbeL14kqV-vc"
}
