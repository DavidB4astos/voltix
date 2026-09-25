// Verify access to the protected internal area
query "auth/internal-access" verb=GET {
  api_group = "Authentication"
  auth = "user"

  input {
  }

  stack {
    // Get the user record based on the auth ID
    db.get user {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "role", "status"]
    } as $user

    // Reject an authenticated token without a matching user record
    precondition ($user != null) {
      error_type = "accessdenied"
      error = "Invalid authenticated user."
    }

    // Accept only approved internal-user profiles
    precondition (
      $user.role == "FUNCIONARIO" ||
      $user.role == "ADMINISTRADOR"
    ) {
      error_type = "accessdenied"
      error = "Invalid authenticated user."
    }

    // Only active internal users may access the protected area
    precondition ($user.status == "ATIVO") {
      error_type = "accessdenied"
      error = "Internal access is not available."
    }
  }

  response = {
    authorized: true
  }
  tags = ["voltix:internal-access"]
  guid = "uVAZ81hO72G0w2qKVfYxU4puJbM"
}
