query "reports/sales" verb=GET {
  api_group = "Voltix Internal Orders"
  auth = "user"

  input {
    // Optional inclusive UTC day boundaries in YYYY-MM-DD.
    text from? filters=trim
    text to? filters=trim
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

    var $hoje {
      value = now|format_timestamp:"Y-m-d":"UTC"
    }

    var $data_inicio {
      value = $input.from
    }

    var $data_fim {
      value = $input.to
    }

    conditional {
      if ($data_fim == null) {
        var.update $data_fim {
          value = $hoje
        }
      }
    }

    conditional {
      if ($data_inicio == null) {
        var.update $data_inicio {
          value = ((($data_fim|parse_timestamp:"Y-m-d":"UTC")|to_int)|add_secs_to_timestamp:-2505600)|format_timestamp:"Y-m-d":"UTC"
        }
      }
    }

    var $inicio_ms {
      value = ($data_inicio|parse_timestamp:"Y-m-d":"UTC")|to_int
    }

    var $fim_dia_ms {
      value = ($data_fim|parse_timestamp:"Y-m-d":"UTC")|to_int
    }

    var $fim_ms {
      value = $fim_dia_ms|add_secs_to_timestamp:86399
    }

    // Inclusive period of at most 366 days (difference of at most 365 days).
    precondition ($inicio_ms <= $fim_ms && ($fim_dia_ms - $inicio_ms) <= 31536000000) {
      error_type = "inputerror"
      error = "Invalid period. Use an ascending range of at most 366 days."
    }

    db.query pedido {
      where = $db.pedido.data_pedido >= $inicio_ms && $db.pedido.data_pedido <= $fim_ms && ($db.pedido.status == "PAGAMENTO_CONFIRMADO" || $db.pedido.status == "EM_PREPARACAO" || $db.pedido.status == "ENVIADO" || $db.pedido.status == "ENTREGUE")
      sort = {data_pedido: "asc", id: "asc"}
      return = {type: "list"}
      output = ["id", "data_pedido", "status", "valor_total"]
    } as $orders

    var $faturamento {
      value = 0
    }

    var $quantidade {
      value = 0
    }

    var $por_dia {
      value = {}
    }

    var $dia {
      value = ""
    }

    var $dia_atual {
      value = null
    }

    foreach ($orders) {
      each as $order {
        var.update $faturamento {
          value = $faturamento + $order.valor_total
        }

        var.update $quantidade {
          value = $quantidade + 1
        }

        var.update $dia {
          value = $order.data_pedido|format_timestamp:"Y-m-d":"UTC"
        }

        var.update $dia_atual {
          value = $por_dia|get:$dia
        }

        conditional {
          if ($dia_atual == null) {
            var.update $por_dia {
              value = $por_dia|set:$dia:{faturamento: $order.valor_total, pedidos: 1}
            }
          }

          else {
            var.update $por_dia {
              value = $por_dia|set:$dia:{faturamento: ($dia_atual.faturamento + $order.valor_total), pedidos: ($dia_atual.pedidos + 1)}
            }
          }
        }
      }
    }

    var $dias_ordenados {
      value = $por_dia|entries|sort:"key":"text":false
    }

    var $serie_diaria {
      value = []
    }

    foreach ($dias_ordenados) {
      each as $entry {
        var.update $serie_diaria {
          value = $serie_diaria|push:{
            data: $entry.key
            faturamento: ($entry.value.faturamento|round:2)
            pedidos: $entry.value.pedidos
          }
        }
      }
    }

    var $ticket_medio {
      value = 0
    }

    conditional {
      if ($quantidade > 0) {
        var.update $ticket_medio {
          value = ($faturamento / $quantidade)|round:2
        }
      }
    }
  }

  response = {
    periodo: {
      inicio: $data_inicio
      fim: $data_fim
      timezone: "UTC"
    }
    faturamento: ($faturamento|round:2)
    pedidos: $quantidade
    ticket_medio: $ticket_medio
    status_incluidos: ["PAGAMENTO_CONFIRMADO", "EM_PREPARACAO", "ENVIADO", "ENTREGUE"]
    serie_diaria: $serie_diaria
  }
  tags = ["voltix:internal-orders"]
}
