// Change the authenticated internal user's password after checking the current one.
query "profile/password" verb=POST {
  api_group = "Voltix Internal Users"
  auth = "user"

  input {
    text current_password
    text new_password filters=min:8|minAlpha:1|minDigit:1
    text confirm_password filters=trim
  }

  stack {
    db.get user {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "password", "role", "status"]
    } as $profile_user

    precondition ($profile_user != null && $profile_user.password != null && $profile_user.status == "ATIVO" && ($profile_user.role == "FUNCIONARIO" || $profile_user.role == "ADMINISTRADOR")) {
      error_type = "accessdenied"
      error = "Active internal access is required."
    }

    precondition ($input.new_password == $input.confirm_password) {
      error_type = "badrequest"
      error = "Password confirmation does not match."
    }

    security.check_password {
      text_password = $input.current_password
      hash_password = $profile_user.password
    } as $password_matches

    precondition ($password_matches) {
      error_type = "badrequest"
      error = "The current password is incorrect."
    }

    precondition ($input.new_password != $input.current_password) {
      error_type = "badrequest"
      error = "The new password must differ from the current password."
    }

    db.edit user {
      field_name = "id"
      field_value = $auth.id
      enforce_hidden_fields = false
      data = {password: $input.new_password}
    } as $updated_password
  }

  response = {
    updated: true
  }

  tags = ["voltix:internal-users"]
  guid = "1Y0yvKfp1tSGz8ES8F530rzl__y1"
}
