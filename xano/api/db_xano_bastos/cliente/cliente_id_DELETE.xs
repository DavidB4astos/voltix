// Delete CLIENTE record.
query "cliente/{cliente_id}" verb=DELETE {
  api_group = "DB_XANO_BASTOS"
  auth = "CLIENTE"

  input {
    int cliente_id? filters=min:1
  }

  stack {
    precondition ($auth.id == $input.cliente_id) {
      error_type = "accessdenied"
      error = "Customers may access only their own profile."
    }

    precondition (false) {
      error_type = "accessdenied"
      error = "Permanent customer deletion is not available."
    }
  }

  response = {deleted: false}
  guid = "Uru99cw23t6_lpIvjbYcA1aXXhw"
}