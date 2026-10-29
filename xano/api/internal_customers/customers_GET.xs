query customers verb=GET {
  api_group = "Voltix Internal Customers"
  auth = "user"

  input {
    text q? filters=trim
    text status?=ATIVO filters=trim
    int page?=1
    int per_page?=20
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
  
    precondition (($input.q|strlen) <= 100 && ($input.status == "ATIVO" || $input.status == "INATIVO" || $input.status == "TODOS") && $input.page >= 1 && $input.per_page >= 1 && $input.per_page <= 50) {
      error_type = "inputerror"
      error = "Invalid customer filters or pagination."
    }
  
    db.query CLIENTE {
      where = ($input.status == "TODOS" || $db.CLIENTE.status == $input.status) && ($input.q == "" || $db.CLIENTE.nome_completo includes $input.q || $db.CLIENTE.email includes $input.q)
      sort = {nome_completo: "asc", id: "asc"}
      return = {
        type  : "list"
        paging: {
          page    : $input.page
          per_page: $input.per_page
          totals  : true
        }
      }
    
      output = ["id", "nome_completo", "email", "telefone", "status", "created_at"]
    } as $page
  
    var $items {
      value = []
    }
  
    foreach ($page.items) {
      each as $customer {
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
      
        var.update $items {
          value = $items
            |push:```
              {
                id: $customer.id
                nome_completo: $customer.nome_completo
                email_masked: $email_masked
                telefone_masked: $phone_masked
                status: $customer.status
                created_at: $customer.created_at
              }
              ```
        }
      }
    }
  
    var $total_pages {
      value = 0
    }
  
    conditional {
      if ($page.itemsTotal > 0) {
        var.update $total_pages {
          value = $page.pageTotal
        }
      }
    }
  }

  response = {
    items      : $items
    page       : $input.page
    per_page   : $input.per_page
    total_items: $page.itemsTotal
    total_pages: $total_pages
  }

  tags = ["voltix:internal-customers"]
  guid = "gbKTPQQi6lqShpKWVov42E0ZQOI"
}