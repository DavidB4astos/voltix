// Edit CLIENTE record
query "cliente/{cliente_id}" verb=PATCH {
  api_group = "DB_XANO_BASTOS"
  auth = "CLIENTE"

  input {
    int cliente_id? filters=min:1
    text nome_completo? filters=trim
    email email? filters=trim|lower
    text telefone? filters=trim
  }

  stack {
    precondition ($auth.id == $input.cliente_id) {
      error_type = "accessdenied"
      error = "Customers may update only their own profile."
    }

    db.get CLIENTE {
      field_name = "id"
      field_value = $input.cliente_id
      output = ["id", "nome_completo", "cpf", "email", "telefone", "status"]
    } as $cliente

    precondition ($cliente != null && $cliente.status == "ATIVO") {
      error_type = "accessdenied"
      error = "Active customer access is required."
    }

    precondition (
      $input.nome_completo != null ||
      $input.email != null ||
      $input.telefone != null
    ) {
      error_type = "inputerror"
      error = "Provide at least one allowed profile field."
    }

    conditional {
      if ($input.email != null && $input.email != $cliente.email) {
        db.get CLIENTE {
          field_name = "email"
          field_value = $input.email
          output = ["id"]
        } as $email_owner

        precondition ($email_owner == null || $email_owner.id == $auth.id) {
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

    db.patch CLIENTE {
      field_name = "id"
      field_value = $auth.id
      data = $updates
    } as $updated_cliente
  }

  response = {
    id: $updated_cliente.id
    nome_completo: $updated_cliente.nome_completo
    cpf: $updated_cliente.cpf
    email: $updated_cliente.email
    telefone: $updated_cliente.telefone
    status: $updated_cliente.status
  }
  guid = "NG2wO-sIm1jPc_nCR8KYsfNP_Io"
}