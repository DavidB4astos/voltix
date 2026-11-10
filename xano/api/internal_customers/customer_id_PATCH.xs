// Administrative update of CLIENTE contact data and status.
query "customers/{customer_id}" verb=PATCH {
  api_group = "Voltix Internal Customers"
  auth = "user"

  input {
    int customer_id filters=min:1
    text nome_completo? filters=trim
    email email? filters=trim|lower
    text telefone? filters=trim
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
      ($input.nome_completo != null || $input.email != null || $input.telefone != null || $input.status != null)
      && ($input.nome_completo == null || (($input.nome_completo|strlen) >= 1 && ($input.nome_completo|strlen) <= 300))
      && ($input.email == null || ($input.email|strlen) <= 254)
      && ($input.telefone == null || (($input.telefone|strlen) >= 1 && ($input.telefone|strlen) <= 30))
    ) {
      error_type = "inputerror"
      error = "Provide at least one valid customer field to update."
    }

    db.get CLIENTE {
      field_name = "id"
      field_value = $input.customer_id
      output = [
        "id"
        "nome_completo"
        "email"
        "telefone"
        "cpf"
        "status"
        "created_at"
      ]
    } as $customer

    precondition ($customer != null) {
      error_type = "notfound"
      error = "Customer not found."
    }

    conditional {
      if ($input.email != null && $input.email != $customer.email) {
        db.query CLIENTE {
          where = $db.CLIENTE.email == $input.email && $db.CLIENTE.id != $input.customer_id
          return = {type: "exists"}
        } as $email_exists

        precondition ($email_exists == false) {
          error_type = "badrequest"
          error = "A customer with this email already exists."
        }
      }
    }

    var $updates {
      value = {updated_at: now}
    }

    conditional {
      if ($input.nome_completo != null) {
        var.update $updates {
          value = $updates|set:"nome_completo":$input.nome_completo
        }
      }
    }

    conditional {
      if ($input.email != null) {
        var.update $updates {
          value = $updates|set:"email":$input.email
        }
      }
    }

    conditional {
      if ($input.telefone != null) {
        var.update $updates {
          value = $updates|set:"telefone":$input.telefone
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

    db.transaction {
      stack {
        db.patch CLIENTE {
          field_name = "id"
          field_value = $input.customer_id
          data = $updates
        } as $updated_customer
      }
    }

    var $email_masked {
      value = null
    }

    var $phone_masked {
      value = null
    }

    var $cpf_masked {
      value = null
    }

    conditional {
      if ($updated_customer.email != null && $updated_customer.email != "") {
        var $email_parts {
          value = $updated_customer.email|split:"@"
        }

        conditional {
          if (($email_parts|count) == 2) {
            var $local {
              value = $email_parts|first
            }

            var $visible {
              value = 0
            }

            conditional {
              if (($local|strlen) > 3) {
                var.update $visible {
                  value = 3
                }
              }

              elseif (($local|strlen) > 1) {
                var.update $visible {
                  value = ($local|strlen) - 1
                }
              }
            }

            var.update $email_masked {
              value = ($local|substr:0:$visible) ~ "*****"
            }
          }
        }
      }
    }

    conditional {
      if ($updated_customer.telefone != null && $updated_customer.telefone != "") {
        var $digits {
          value = $updated_customer.telefone|regex_replace:"/[^0-9]/":""
        }

        conditional {
          if (($digits|strlen) > 4) {
            var $start {
              value = ($digits|strlen) - 4
            }

            var.update $phone_masked {
              value = "*****" ~ ($digits|substr:$start:4)
            }
          }

          else {
            var.update $phone_masked {
              value = "*****"
            }
          }
        }
      }
    }

    conditional {
      if ($updated_customer.cpf != null) {
        var $cpf_digits {
          value = $updated_customer.cpf|regex_replace:"/[^0-9]/":""
        }

        conditional {
          if (($cpf_digits|strlen) == 11) {
            var.update $cpf_masked {
              value = "***.***.***-" ~ ($cpf_digits|substr:9:2)
            }
          }
        }
      }
    }
  }

  response = {
    id             : $updated_customer.id
    nome_completo  : $updated_customer.nome_completo
    email_masked   : $email_masked
    telefone_masked: $phone_masked
    status         : $updated_customer.status
    created_at     : $updated_customer.created_at
    cpf_masked     : $cpf_masked
  }

  tags = ["voltix:internal-customers"]
  guid = "0pBqUqLkVaUx9l5N8HX2sf2suzY"
}
