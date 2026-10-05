query "categories" verb=GET {
  api_group = "Catalog Management"
  auth = "user"

  input {
  }

  stack {
    db.get user {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "role", "status"]
    } as $user

    precondition ($user != null) {
      error_type = "accessdenied"
      error = "Invalid authenticated user."
    }

    precondition ($user.role == "ADMINISTRADOR" && $user.status == "ATIVO") {
      error_type = "accessdenied"
      error = "Administrator access is required."
    }

    db.query categoria {
      return = {type: "list"}
      sort = {name: "asc"}
      output = ["id", "name", "description", "status", "created_at", "updated_at"]
    } as $categories
  }

  response = $categories
  tags = ["voltix:catalog-management"]
}
