// Confirm a password recovery using a single-use token.
// Never issues a session and never reveals whether the account exists.
query confirm verb=POST {
  api_group = "Voltix Internal Password Recovery"

  input {
    email email filters=trim|lower
    text token filters=trim
    text password filters=min:8
    text confirm_password filters=trim
  }

  stack {
    // Every failure below returns the same generic message
    precondition ($input.email != null && ($input.email|strlen) <= 254 && $input.token != null && ($input.token|strlen) >= 1) {
      error_type = "badrequest"
      error = "Link inválido ou expirado."
    }

    // Text inputs do not support minAlpha/minDigit; require one letter and one digit
    precondition (($input.password|regex_test:"[A-Za-z]") && ($input.password|regex_test:"[0-9]")) {
      error_type = "badrequest"
      error = "Link inválido ou expirado."
    }

    precondition ($input.password == $input.confirm_password) {
      error_type = "badrequest"
      error = "Link inválido ou expirado."
    }

    // Get the user record with the email from the request
    db.get user {
      field_name = "email"
      field_value = $input.email
      output = [
        "id"
        "password"
        "role"
        "status"
        "password_reset.token"
        "password_reset.expiration"
        "password_reset.used"
      ]
    } as $user

    // Only active internal users with an approved profile can reset a password
    precondition ($user != null && $user.status == "ATIVO" && ($user.role == "FUNCIONARIO" || $user.role == "ADMINISTRADOR") && $user.password_reset != null && $user.password_reset.token != null) {
      error_type = "badrequest"
      error = "Link inválido ou expirado."
    }

    precondition ($user.password_reset.used == false) {
      error_type = "badrequest"
      error = "Link inválido ou expirado."
    }

    precondition ($user.password_reset.expiration > now) {
      error_type = "badrequest"
      error = "Link inválido ou expirado."
    }

    // Validate the submitted token against the stored hash
    security.check_password {
      text_password = $input.token
      hash_password = $user.password_reset.token
    } as $verify_token

    precondition ($verify_token) {
      error_type = "badrequest"
      error = "Link inválido ou expirado."
    }

    // Verify the new password differs from the current one
    security.check_password {
      text_password = $input.password
      hash_password = $user.password
    } as $password_unchanged

    precondition ($password_unchanged == false) {
      error_type = "badrequest"
      error = "Link inválido ou expirado."
    }

    // Store the new password and consume the token in a single write
    db.edit user {
      field_name = "id"
      field_value = $user.id
      enforce_hidden_fields = false
      data = {
        password: $input.password
        password_reset: {
          token     : $user.password_reset.token
          expiration: $user.password_reset.expiration
          used      : true
        }
      }
    } as $updated_user
  }

  response = {
    updated: true
  }

  tags = ["voltix:internal-password-recovery"]
  guid = "a5Sef9pfca1qL3c0eqDPL_DFTK_"
}
