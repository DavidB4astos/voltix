query "brands" verb=POST {
  api_group = "Catalog Management"
  auth = "user"

  input {
    text name filters=trim
    text description? filters=trim
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

    precondition ($input.name != "") {
      error_type = "inputerror"
      error = "Brand name is required."
    }

    db.query marca {
      where = $db.marca.name == $input.name
      return = {type: "exists"}
    } as $name_exists

    precondition ($name_exists == false) {
      error_type = "badrequest"
      error = "A brand with this name already exists."
    }

    db.add marca {
      data = {
        name: $input.name
        description: $input.description
        status: "ATIVO"
        updated_at: now
      }
    } as $brand
  }

  response = $brand
  tags = ["voltix:catalog-management"]
}
