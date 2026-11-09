query "orders" verb=GET {
  api_group = "Voltix Internal Orders"
  auth = "user"

  input {
    text q?="" filters=trim
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

    precondition (($input.q|strlen) <= 100 && ($input.status == "TODOS" || $input.status == "AGUARDANDO_PAGAMENTO" || $input.status == "PAGAMENTO_CONFIRMADO" || $input.status == "EM_PREPARACAO" || $input.status == "ENVIADO" || $input.status == "ENTREGUE" || $input.status == "CANCELADO") && $input.page >= 1 && $input.per_page >= 1 && $input.per_page <= 50) {
      error_type = "inputerror"
      error = "Invalid order filters or pagination."
    }

    db.query CLIENTE {
      where = $input.q != "" && $db.CLIENTE.nome_completo includes $input.q
      output = ["id"]
      return = {type: "list"}
    } as $matching_customers

    var $customer_ids {
      value = []
    }

    foreach ($matching_customers) {
      each as $customer {
        var.update $customer_ids {
          value = $customer_ids|push:$customer.id
        }
      }
    }

    db.query pedido {
      where = ($input.status == "TODOS" || $db.pedido.status == $input.status) && ($input.q == "" || $db.pedido.codigo includes $input.q || $db.pedido.cliente_id in $customer_ids)
      sort = {data_pedido: "desc", id: "desc"}
      return = {
        type  : "list"
        paging: {
          page    : $input.page
          per_page: $input.per_page
          totals  : true
        }
      }

      output = ["items.id", "items.codigo", "items.data_pedido", "items.status", "items.cliente_id", "items.subtotal", "items.valor_frete", "items.valor_total", "itemsTotal", "pageTotal"]
    } as $page_result

    var $items {
      value = []
    }

    foreach ($page_result.items) {
      each as $order {
        db.get CLIENTE {
          field_name = "id"
          field_value = $order.cliente_id
          output = ["id", "nome_completo"]
        } as $order_customer

        db.query item_pedido {
          where = $db.item_pedido.pedido_id == $order.id
          return = {type: "count"}
        } as $item_count

        var.update $items {
          value = $items|push:{
            id: $order.id
            codigo: $order.codigo
            data_pedido: $order.data_pedido
            status: $order.status
            cliente: {
              id: $order.cliente_id
              nome_completo: $order_customer.nome_completo
            }
            itens_count: $item_count
            subtotal: $order.subtotal
            valor_frete: $order.valor_frete
            valor_total: $order.valor_total
          }
        }
      }
    }
  }

  response = {
    items: $items
    page: $input.page
    per_page: $input.per_page
    items_total: $page_result.itemsTotal
    page_total: $page_result.pageTotal
  }
  tags = ["voltix:internal-orders"]
  guid = "tUE2qV0smb9WtKkQOylnyL_PSVQ"
}
