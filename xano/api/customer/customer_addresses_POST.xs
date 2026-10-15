query "addresses" verb=POST {
  api_group = "Voltix Customer"
  auth = "CLIENTE"

  input {
    text cep? filters=trim
    text logradouro? filters=trim
    text numero? filters=trim
    text complemento? filters=trim
    text bairro? filters=trim
    text cidade? filters=trim
    text estado? filters=trim
    text identificacao? filters=trim
    bool principal?
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

    db.transaction {
      stack {
        conditional {
          if ($input.principal == true) {
            db.query endereco {
              where = $db.endereco.cliente_id == $auth.id
              return = {type: "list"}
            } as $existing_addresses

            foreach ($existing_addresses) {
              each as $existing_address {
                db.patch endereco {
                  field_name = "id"
                  field_value = $existing_address.id
                  data = {principal: false, updated_at: now}
                } as $cleared_address
              }
            }
          }
        }

        db.add endereco {
          data = {
            cliente_id: $auth.id
            cep: $input.cep
            logradouro: $input.logradouro
            numero: $input.numero
            complemento: $input.complemento
            bairro: $input.bairro
            cidade: $input.cidade
            estado: $input.estado
            identificacao: $input.identificacao
            principal: $input.principal == true
            status: "ATIVO"
            updated_at: now
          }
        } as $address
      }
    }
  }

  response = {
    id: $address.id
    cliente_id: $address.cliente_id
    cep: $address.cep
    logradouro: $address.logradouro
    numero: $address.numero
    complemento: $address.complemento
    bairro: $address.bairro
    cidade: $address.cidade
    estado: $address.estado
    identificacao: $address.identificacao
    principal: $address.principal
    status: $address.status
  }
  tags = ["voltix:customer-addresses"]
  guid = "S5zN9pqQwQku_UhpprdWfRxG6Mw"
}
