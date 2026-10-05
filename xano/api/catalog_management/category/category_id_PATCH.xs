query "categories/{category_id}" verb=PATCH {
  api_group = "Catalog Management"
  auth = "user"

  input {
    int category_id filters=min:1
    text name? filters=trim
    text description? filters=trim
    enum status? {
      values = ["ATIVO", "INATIVO"]
    }
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

    db.get categoria {
      field_name = "id"
      field_value = $input.category_id
    } as $category

    precondition ($category != null) {
      error_type = "notfound"
      error = "Category not found."
    }

    precondition (
      ($input.name == null || $input.name != "") &&
      ($input.name != null || $input.description != null || $input.status != null)
    ) {
      error_type = "inputerror"
      error = "Provide a non-empty name or another category field to update."
    }

    conditional {
      if ($input.name != null) {
        db.query categoria {
          where = $db.categoria.name == $input.name && $db.categoria.id != $input.category_id
          return = {type: "exists"}
        } as $name_exists

        precondition ($name_exists == false) {
          error_type = "badrequest"
          error = "A category with this name already exists."
        }
      }
    }

    var $updates {
      value = {updated_at: now}
    }

    conditional {
      if ($input.name != null) {
        var.update $updates {
          value = $updates|set:"name":$input.name
        }
      }
    }

    conditional {
      if ($input.description != null) {
        var.update $updates {
          value = $updates|set:"description":$input.description
        }
      }
    }

    conditional {
      if ($input.status != null) {
        var.update $updates {
          value = $updates|set:"status":$input.status
        }
      }
    }

    db.patch categoria {
      field_name = "id"
      field_value = $input.category_id
      data = $updates
    } as $updated_category
  }

  response = $updated_category
  tags = ["voltix:catalog-management"]
}
