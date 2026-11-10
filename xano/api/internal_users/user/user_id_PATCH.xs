// Partially update an internal user without changing the password or deleting it.
query "users/{user_id}" verb=PATCH {
  api_group = "Voltix Internal Users"
  auth = "user"

  input {
    int user_id filters=min:1
    text name? filters=trim
    email email? filters=trim|lower
    enum role? {
      values = ["FUNCIONARIO", "ADMINISTRADOR"]
    }
    enum status? {
      values = ["ATIVO", "INATIVO"]
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

    precondition (
      ($input.name != null || $input.email != null || $input.role != null || $input.status != null)
      && ($input.name == null || (($input.name|strlen) >= 1 && ($input.name|strlen) <= 300))
      && ($input.email == null || ($input.email|strlen) <= 254)
    ) {
      error_type = "inputerror"
      error = "Provide at least one valid internal user field to update."
    }

    db.get user {
      field_name = "id"
      field_value = $input.user_id
      output = ["id", "name", "email", "role", "status", "created_at"]
    } as $target_user

    precondition ($target_user != null) {
      error_type = "notfound"
      error = "Internal user not found."
    }

    var $self_role_change {
      value = $input.user_id == $auth.id && $input.role != null && $input.role != $target_user.role
    }

    var $self_status_change {
      value = $input.user_id == $auth.id && $input.status != null && $input.status != $target_user.status
    }

    precondition ($self_role_change == false && $self_status_change == false) {
      error_type = "badrequest"
      error = "Administrators cannot change their own role or status."
    }

    conditional {
      if ($input.email != null && $input.email != $target_user.email) {
        db.query user {
          where = $db.user.email == $input.email && $db.user.id != $input.user_id
          return = {type: "exists"}
        } as $email_exists

        precondition ($email_exists == false) {
          error_type = "badrequest"
          error = "An internal user with this email already exists."
        }
      }
    }

    var $removes_active_admin {
      value = $target_user.role == "ADMINISTRADOR" && $target_user.status == "ATIVO" && (($input.role != null && $input.role != "ADMINISTRADOR") || ($input.status != null && $input.status != "ATIVO"))
    }

    conditional {
      if ($removes_active_admin) {
        db.query user {
          where = $db.user.id != $input.user_id && $db.user.role == "ADMINISTRADOR" && $db.user.status == "ATIVO"
          return = {type: "exists"}
        } as $other_active_admin

        precondition ($other_active_admin) {
          error_type = "badrequest"
          error = "At least one active administrator must remain."
        }
      }
    }

    var $next_name {
      value = $target_user.name
    }

    var $next_email {
      value = $target_user.email
    }

    var $next_role {
      value = $target_user.role
    }

    var $next_status {
      value = $target_user.status
    }

    conditional {
      if ($input.name != null) {
        var.update $next_name {
          value = $input.name
        }
      }
    }

    conditional {
      if ($input.email != null) {
        var.update $next_email {
          value = $input.email
        }
      }
    }

    conditional {
      if ($input.role != null) {
        var.update $next_role {
          value = $input.role
        }
      }
    }

    conditional {
      if ($input.status != null) {
        var.update $next_status {
          value = $input.status
        }
      }
    }

    db.edit user {
      field_name = "id"
      field_value = $input.user_id
      enforce_hidden_fields = false
      data = {
        name  : $next_name
        email : $next_email
        role  : $next_role
        status: $next_status
      }
    } as $updated_user
  }

  response = {
    id        : $updated_user.id
    name      : $updated_user.name
    email     : $updated_user.email
    role      : $updated_user.role
    status    : $updated_user.status
    created_at: $updated_user.created_at
  }

  tags = ["voltix:internal-users"]
  guid = "tHiF56kCRG6g0O1KYCjGDMsqH71a"
}
