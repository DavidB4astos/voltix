query "addresses/{address_id}" verb=PATCH {
  api_group = "Voltix Customer"
  auth = "CLIENTE"

  input {
    int address_id filters=min:1
    text cep? filters=trim
    text logradouro? filters=trim
    text numero? filters=trim
    text complemento? filters=trim
    text bairro? filters=trim
    text cidade? filters=trim
    text estado? filters=trim
    text identificacao? filters=trim
    bool principal?
    enum status? {
      values = ["ATIVO", "INATIVO"]
    }
  }

  stack {
    db.get CLIENTE {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "status"]
    } as $customer

    precondition ($customer != null && $customer.status == "ATIVO") {
      error_type = "accessdenied"
      error = "Active customer access is required."
    }

    db.get endereco {
      field_name = "id"
      field_value = $input.address_id
    } as $address

    precondition ($address != null && $address.cliente_id == $auth.id) {
      error_type = "notfound"
      error = "Address not found."
    }

    precondition (
      $input.cep != null ||
      $input.logradouro != null ||
      $input.numero != null ||
      $input.complemento != null ||
      $input.bairro != null ||
      $input.cidade != null ||
      $input.estado != null ||
      $input.identificacao != null ||
      $input.principal != null ||
      $input.status != null
    ) {
      error_type = "inputerror"
      error = "Provide at least one address field to update."
    }

    precondition (
      $input.principal != true ||
      $address.status == "ATIVO" ||
      $input.status == "ATIVO"
    ) {
      error_type = "badrequest"
      error = "An inactive address cannot be primary."
    }

    precondition ($input.principal != true || $input.status != "INATIVO") {
      error_type = "badrequest"
      error = "An inactive address cannot be primary."
    }

    var $updates {
      value = {updated_at: now}
    }

    conditional {
      if ($input.cep != null) {
        var.update $updates {
          value = $updates|set:"cep":$input.cep
        }
      }
    }

    conditional {
      if ($input.logradouro != null) {
        var.update $updates {
          value = $updates|set:"logradouro":$input.logradouro
        }
      }
    }

    conditional {
      if ($input.numero != null) {
        var.update $updates {
          value = $updates|set:"numero":$input.numero
        }
      }
    }

    conditional {
      if ($input.complemento != null) {
        var.update $updates {
          value = $updates|set:"complemento":$input.complemento
        }
      }
    }

    conditional {
      if ($input.bairro != null) {
        var.update $updates {
          value = $updates|set:"bairro":$input.bairro
        }
      }
    }

    conditional {
      if ($input.cidade != null) {
        var.update $updates {
          value = $updates|set:"cidade":$input.cidade
        }
      }
    }

    conditional {
      if ($input.estado != null) {
        var.update $updates {
          value = $updates|set:"estado":$input.estado
        }
      }
    }

    conditional {
      if ($input.identificacao != null) {
        var.update $updates {
          value = $updates|set:"identificacao":$input.identificacao
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

    conditional {
      if ($input.status == "INATIVO") {
        var.update $updates {
          value = $updates|set:"principal":false
        }
      }
    }

    conditional {
      if ($input.status != "INATIVO" && $input.principal != null) {
        var.update $updates {
          value = $updates|set:"principal":$input.principal
        }
      }
    }

    conditional {
      if ($input.principal == true && $input.status != "INATIVO") {
        db.transaction {
          stack {
            db.query endereco {
              where = $db.endereco.cliente_id == $auth.id
              return = {type: "list"}
            } as $customer_addresses

            foreach ($customer_addresses) {
              each as $customer_address {
                db.patch endereco {
                  field_name = "id"
                  field_value = $customer_address.id
                  data = {principal: false, updated_at: now}
                } as $cleared_address
              }
            }

            db.patch endereco {
              field_name = "id"
              field_value = $input.address_id
              data = $updates
            } as $updated_address
          }
        }
      }
    }

    conditional {
      if ($input.principal != true) {
        db.patch endereco {
          field_name = "id"
          field_value = $input.address_id
          data = $updates
        } as $updated_address
      }
    }
  }

  response = $updated_address
  tags = ["voltix:customer-addresses"]
}
