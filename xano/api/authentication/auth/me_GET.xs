// Get the user record belonging to the authentication token
query "auth/me" verb=GET {
  api_group = "Authentication"
  auth = "user"

  input {
  }

  stack {
    // Get the user record based on the auth ID
    db.get user {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "name", "email", "role", "status"]
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

    // Only active internal users may access their identity
    precondition ($user.status == "ATIVO") {
      error_type = "accessdenied"
      error = "Internal access is not available."
    }
  }

  response = {
    id: $user.id
    name: $user.name
    email: $user.email
    role: $user.role
    status: $user.status
  }
  tags = ["xano:quick-start"]
  guid = "R_7_R-8SS4-WfM3GS4ieMO0_vls"
}