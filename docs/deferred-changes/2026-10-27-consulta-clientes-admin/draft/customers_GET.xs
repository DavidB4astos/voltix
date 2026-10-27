query "customers" verb=GET {
  api_group = "Voltix Admin"

  auth = "user"

  input {
    text status? filters=trim
    text q?
  }

  stack {
    var $users {
      value = []
    }

    db.get user {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "role", "status"]
    } as $user

    precondition ($user != null) {
      error_type = "accessdenied"
      error = "Usuário não autenticado."
    }

    precondition (
      $user.role == "ADMINISTRADOR"
    ) {
      error_type = "accessdenied"
      error = "Acesso restrito a ADMINISTRADOR."
    }

    precondition ($user.status == "ATIVO") {
      error_type = "accessdenied"
      error = "Acesso restrito a ADMINISTRADOR ATIVO."
    }

    var $customers {
      value = []
    }

    conditional {
      if ($input.status != null && $input.status != "") {
        db.get CLIENTE {
          field_name = "status"
          field_value = $input.status
          output = ["id", "status"]
        } as $statusFilter

        precondition ($statusFilter != null && $statusFilter.status == $input.status) {
          error_type = "notfound"
          error = "Status informado não encontrado."
        }
      }
    }

    conditional {
      if ($input.q != null && $input.q != "") {
        db.query CLIENTE {
          return = {type: "list"}
          where = ($db.CLIENTE.nome includes $input.q) OR ($db.CLIENTE.e-mail includes $input.q)
          sort = {nome: "asc"}
          output = [
            "id",
            "nome",
            "e-mail",
            "telefone",
            "data_cadastro",
            "status"
          ]
        } as $filteredClients

        var.update $customers {
          value = $filteredClients
        }
      } else {
        db.query CLIENTE {
          return = {type: "list"}
          where = $db.CLIENTE.status == "ATIVO"
          sort = {nome: "asc"}
          output = [
            "id",
            "nome",
            "e-mail",
            "telefone",
            "data_cadastro",
            "status"
          ]
        } as $allClients

        var.update $customers {
          value = $allClients
        }
      }
    }

    var $customer_list {
      value = []
    }

    foreach ($cliente) {
      each as $cliente {
        var $eMailMasked {
          value = left($cliente.e-mail, 3) + "***"
        }

        var.update $customer_list {
          value = $customer_list|push:{
            id: $cliente.id
            nome: $cliente.nome
            e-mail: $eMailMasked
            telefone: $cliente.telefone
            data_cadastro: $cliente.data_cadastro
            status: $cliente.status
          }
        }
      }
    }
  }

  response = $customer_list
  tags = ["voltix:admin-customers"]
}