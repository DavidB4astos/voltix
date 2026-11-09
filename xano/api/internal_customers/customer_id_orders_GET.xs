query "customers/{customer_id}/orders" verb=GET {
  api_group = "Voltix Internal Customers"
  auth = "user"

  input {
    int customer_id filters=min:1
    text status?=TODOS filters=trim
    // Optional inclusive UTC day boundaries in YYYY-MM-DD.
    text from? filters=trim
    text to? filters=trim
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

    precondition ($input.customer_id > 0 && ($input.status == "TODOS" || $input.status == "AGUARDANDO_PAGAMENTO" || $input.status == "PAGAMENTO_CONFIRMADO" || $input.status == "EM_PREPARACAO" || $input.status == "ENVIADO" || $input.status == "ENTREGUE" || $input.status == "CANCELADO") && $input.page >= 1 && $input.per_page >= 1 && $input.per_page <= 50) {
      error_type = "inputerror"
      error = "Invalid history filters or pagination."
    }

    conditional {
      if ($input.from != null) {
        precondition ("^[0-9]{4}-[0-9]{2}-[0-9]{2}$"|regex_matches:$input.from) {
          error_type = "inputerror"
          error = "Invalid start date. Use YYYY-MM-DD."
        }
      }
    }

    conditional {
      if ($input.to != null) {
        precondition ("^[0-9]{4}-[0-9]{2}-[0-9]{2}$"|regex_matches:$input.to) {
          error_type = "inputerror"
          error = "Invalid end date. Use YYYY-MM-DD."
        }
      }
    }

    db.get CLIENTE {
      field_name = "id"
      field_value = $input.customer_id
      output = ["id"]
    } as $customer

    precondition ($customer != null) {
      error_type = "notfound"
      error = "Customer not found."
    }

    var $has_from {
      value = $input.from != null
    }

    var $has_to {
      value = $input.to != null
    }

    var $from_ms {
      value = null
    }

    var $to_ms {
      value = null
    }

    conditional {
      if ($has_from) {
        var.update $from_ms {
          value = ($input.from|parse_timestamp:"Y-m-d":"UTC")|to_int
        }
      }
    }

    conditional {
      if ($has_to) {
        var.update $to_ms {
          value = (($input.to|parse_timestamp:"Y-m-d":"UTC")|to_int)|add_secs_to_timestamp:86399
        }
      }
    }

    precondition ($has_from == false || $has_to == false || $from_ms <= $to_ms) {
      error_type = "inputerror"
      error = "Invalid period. The start date must not be after the end date."
    }

    db.query pedido {
      where = $db.pedido.cliente_id == $input.customer_id && ($input.status == "TODOS" || $db.pedido.status == $input.status) && ($has_from == false || $db.pedido.data_pedido >= $from_ms) && ($has_to == false || $db.pedido.data_pedido <= $to_ms)
      sort = {data_pedido: "desc", id: "desc"}
      return = {
        type  : "list"
        paging: {
          page    : $input.page
          per_page: $input.per_page
          totals  : true
        }
      }

      output = ["items.id", "items.codigo", "items.data_pedido", "items.status", "items.subtotal", "items.valor_frete", "items.valor_total", "itemsTotal", "pageTotal"]
    } as $page_result

    var $order_ids {
      value = []
    }

    foreach ($page_result.items) {
      each as $order {
        var.update $order_ids {
          value = $order_ids|push:$order.id
        }
      }
    }

    var $raw_items {
      value = []
    }

    conditional {
      if (($order_ids|count) > 0) {
        db.query item_pedido {
          where = $db.item_pedido.pedido_id in $order_ids
          sort = {id: "asc"}
          return = {type: "list"}
          output = ["id", "pedido_id", "variacao_produto_id", "quantidade", "preco_unitario"]
        } as $items_result

        var.update $raw_items {
          value = $items_result
        }
      }
    }

    var $variation_ids {
      value = []
    }

    foreach ($raw_items) {
      each as $item {
        var.update $variation_ids {
          value = $variation_ids|push:$item.variacao_produto_id
        }
      }
    }

    var $raw_variations {
      value = []
    }

    conditional {
      if (($variation_ids|count) > 0) {
        db.query variacao_produto {
          where = $db.variacao_produto.id in $variation_ids
          return = {type: "list"}
          output = ["id", "sku", "nome_ou_descricao"]
        } as $variations_result

        var.update $raw_variations {
          value = $variations_result
        }
      }
    }

    var $variacoes {
      value = {}
    }

    foreach ($raw_variations) {
      each as $variation {
        var $map_key {
          value = $variation.id|to_text
        }

        var.update $variacoes {
          value = $variacoes|set:$map_key:{sku: $variation.sku, nome_ou_descricao: $variation.nome_ou_descricao}
        }
      }
    }

    var $itens_por_pedido {
      value = {}
    }

    foreach ($raw_items) {
      each as $item {
        var $item_order_key {
          value = $item.pedido_id|to_text
        }

        var $item_variation_key {
          value = $item.variacao_produto_id|to_text
        }

        var $variation_info {
          value = $variacoes|get:$item_variation_key
        }

        var $sku {
          value = null
        }

        var $nome_ou_descricao {
          value = null
        }

        conditional {
          if ($variation_info != null) {
            var.update $sku {
              value = $variation_info.sku
            }

            var.update $nome_ou_descricao {
              value = $variation_info.nome_ou_descricao
            }
          }
        }

        var $line {
          value = {
            variacao_id: $item.variacao_produto_id
            sku: $sku
            nome_ou_descricao: $nome_ou_descricao
            quantidade: $item.quantidade
            preco_unitario: $item.preco_unitario
            subtotal: ($item.preco_unitario * $item.quantidade)
          }
        }

        var $current_items {
          value = $itens_por_pedido|get:$item_order_key
        }

        conditional {
          if ($current_items == null) {
            var $new_items {
              value = []
            }

            var.update $new_items {
              value = $new_items|push:$line
            }

            var.update $itens_por_pedido {
              value = $itens_por_pedido|set:$item_order_key:$new_items
            }
          }

          else {
            var.update $itens_por_pedido {
              value = $itens_por_pedido|set:$item_order_key:($current_items|push:$line)
            }
          }
        }
      }
    }

    var $orders {
      value = []
    }

    foreach ($page_result.items) {
      each as $order {
        var $page_order_key {
          value = $order.id|to_text
        }

        var $order_items {
          value = $itens_por_pedido|get:$page_order_key
        }

        conditional {
          if ($order_items == null) {
            var.update $order_items {
              value = []
            }
          }
        }

        var.update $orders {
          value = $orders|push:{
            id: $order.id
            codigo: $order.codigo
            data_pedido: $order.data_pedido
            status: $order.status
            subtotal: $order.subtotal
            valor_frete: $order.valor_frete
            valor_total: $order.valor_total
            itens: $order_items
          }
        }
      }
    }

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
    cliente_id: $input.customer_id
    items: $orders
    page: $input.page
    per_page: $input.per_page
    total_items: $page_result.itemsTotal
    total_pages: $total_pages
  }
  tags = ["voltix:internal-customers"]
}
