// Update the authenticated internal user's own name and email.
query profile verb=PATCH {
  api_group = "Voltix Internal Users"
  auth = "user"

  input {
    text name? filters=trim
    email email? filters=trim|lower
  }

  stack {
    db.get user {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "name", "email", "role", "status"]
    } as $profile_user

    precondition ($profile_user != null && $profile_user.status == "ATIVO" && ($profile_user.role == "FUNCIONARIO" || $profile_user.role == "ADMINISTRADOR")) {
      error_type = "accessdenied"
      error = "Active internal access is required."
    }

    precondition (
      ($input.name != null || $input.email != null)
      && ($input.name == null || (($input.name|strlen) >= 1 && ($input.name|strlen) <= 300))
      && ($input.email == null || ($input.email|strlen) <= 254)
    ) {
      error_type = "inputerror"
      error = "Provide at least one valid profile field to update."
    }

    conditional {
      if ($input.email != null && $input.email != $profile_user.email) {
        db.query user {
          where = $db.user.email == $input.email && $db.user.id != $auth.id
          return = {type: "exists"}
        } as $email_exists

        precondition ($email_exists == false) {
          error_type = "badrequest"
          error = "An internal user with this email already exists."
        }
      }
    }

    var $next_name {
      value = $profile_user.name
    }

    var $next_email {
      value = $profile_user.email
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

    db.edit user {
      field_name = "id"
      field_value = $auth.id
      enforce_hidden_fields = false
      data = {
        name : $next_name
        email: $next_email
      }
    } as $updated_profile
  }

  response = {
    id    : $updated_profile.id
    name  : $updated_profile.name
    email : $updated_profile.email
    role  : $updated_profile.role
    status: $updated_profile.status
  }

  tags = ["voltix:internal-users"]
  guid = "bnR1DONDr-Px7fsjIMLHlL8urky6"
}
