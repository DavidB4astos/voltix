query "atendimentos" verb=GET {
  api_group = "Voltix Internal CRM"
  auth = "user"

  input {
    int cliente_id? filters=min:1
    text status?=TODOS filters=trim
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

    precondition (($input.status == "TODOS" || $input.status == "ABERTO" || $input.status == "EM_ATENDIMENTO" || $input.status == "FINALIZADO" || $input.status == "CANCELADO") && $input.page >= 1 && $input.per_page >= 1 && $input.per_page <= 50) {
      error_type = "inputerror"
      error = "Invalid attendance filters or pagination."
    }

    db.query atendimento {
      where = ($input.cliente_id == null || $db.atendimento.cliente_id == $input.cliente_id) && ($input.status == "TODOS" || $db.atendimento.status == $input.status)
      sort = {data_atendimento: "desc", id: "desc"}
      return = {
        type  : "list"
        paging: {
          page    : $input.page
          per_page: $input.per_page
          totals  : true
        }
      }

      output = [
        "items.id"
        "items.cliente_id"
        "items.usuario_interno_id"
        "items.pedido_id"
        "items.assunto"
        "items.descricao"
        "items.status"
        "items.data_atendimento"
        "items.created_at"
        "items.updated_at"
        "itemsTotal"
        "pageTotal"
      ]
    } as $page_result

    var $total_pages {
      value = 0
    }

    conditional {
      if ($page_result.itemsTotal > 0) {
        var.update $total_pages {
          value = $page_result.pageTotal
        }
      }
    }
  }

  response = {
    items      : $page_result.items
    page       : $input.page
    per_page   : $input.per_page
    total_items: $page_result.itemsTotal
    total_pages: $total_pages
  }
  tags = ["voltix:attendance-management"]
}
