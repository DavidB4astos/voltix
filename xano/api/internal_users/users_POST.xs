// Create an internal user with an initial password. Administrator only.
query users verb=POST {
  api_group = "Voltix Internal Users"
  auth = "user"

  input {
    text name filters=trim
    email email filters=trim|lower
    text password filters=min:8
    enum role {
      values = ["FUNCIONARIO", "ADMINISTRADOR"]
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

    precondition (($input.name|strlen) >= 1 && ($input.name|strlen) <= 300 && ($input.email|strlen) <= 254) {
      error_type = "inputerror"
      error = "Provide a valid name and email for the internal user."
    }

    // Text inputs only support min-length filters; require one letter and one digit
    precondition (($input.password|regex_test:"[A-Za-z]") && ($input.password|regex_test:"[0-9]")) {
      error_type = "badrequest"
      error = "The password must contain at least 8 characters, a letter and a digit."
    }

    db.query user {
      where = $db.user.email == $input.email
      return = {type: "exists"}
    } as $email_exists

    precondition ($email_exists == false) {
      error_type = "badrequest"
      error = "An internal user with this email already exists."
    }

    db.add user {
      enforce_hidden_fields = false
      data = {
        name    : $input.name
        email   : $input.email
        password: $input.password
        role    : $input.role
        status  : "ATIVO"
      }
    } as $created_user
  }

  response = {
    id        : $created_user.id
    name      : $created_user.name
    email     : $created_user.email
    role      : $created_user.role
    status    : $created_user.status
    created_at: $created_user.created_at
  }

  tags = ["voltix:internal-users"]
  guid = "1Ub8L3lF4spp9Idw8CvnfHjopiZt"
}
