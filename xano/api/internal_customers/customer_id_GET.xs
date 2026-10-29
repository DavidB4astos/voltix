query "customers/{customer_id}" verb=GET {
  api_group = "Voltix Internal Customers"
  auth = "user"

  input {
    int customer_id
  }

  stack {
    db.get user {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "role", "status"]
    } as $internal_user
  
    precondition ($internal_user != null && $internal_user.status == "ATIVO" && ($internal_user.role == "FUNCIONARIO" || $internal_user.role == "ADMINISTRADOR")) {
      error_type = "accessdenied"
      error = "Active internal access is required."
    }
  
    precondition ($input.customer_id > 0) {
      error_type = "inputerror"
      error = "Invalid customer id."
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
      if ($customer.email != null && $customer.email != "") {
        var $email_parts {
          value = $customer.email|split:"@"
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
      if ($customer.telefone != null && $customer.telefone != "") {
        var $digits {
          value = $customer.telefone|regex_replace:"/[^0-9]/":""
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
      if ($customer.cpf != null) {
        var $cpf_digits {
          value = $customer.cpf|regex_replace:"/[^0-9]/":""
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
    id             : $customer.id
    nome_completo  : $customer.nome_completo
    email_masked   : $email_masked
    telefone_masked: $phone_masked
    status         : $customer.status
    created_at     : $customer.created_at
    cpf_masked     : $cpf_masked
  }

  tags = ["voltix:internal-customers"]
  guid = "XrlXJvPx0p_u7hUjhsB3LVKs6os"
}