query "orders/{order_id}" verb=GET {
  api_group = "Voltix Internal Orders"
  auth = "user"

  input {
    int order_id filters=min:1
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

    db.get pedido {
      field_name = "id"
      field_value = $input.order_id
    } as $order

    precondition ($order != null) {
      error_type = "notfound"
      error = "Order not found."
    }

    db.get CLIENTE {
      field_name = "id"
      field_value = $order.cliente_id
      output = ["id", "nome_completo", "email"]
    } as $customer

    var $email_masked {
      value = null
    }

    conditional {
      if ($customer != null && $customer.email != null && $customer.email != "") {
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

    db.query item_pedido {
      where = $db.item_pedido.pedido_id == $order.id
      sort = {id: "asc"}
      return = {type: "list"}
    } as $order_items

    var $item_summaries {
      value = []
    }

    foreach ($order_items) {
      each as $item {
        db.get variacao_produto {
          field_name = "id"
          field_value = $item.variacao_produto_id
          output = ["id", "sku", "nome_ou_descricao"]
        } as $variation

        var.update $item_summaries {
          value = $item_summaries|push:{
            variacao_id: $item.variacao_produto_id
            sku: $variation.sku
            nome_ou_descricao: $variation.nome_ou_descricao
            quantidade: $item.quantidade
            preco_unitario: $item.preco_unitario
            subtotal: $item.preco_unitario * $item.quantidade
          }
        }
      }
    }

    db.query pagamento {
      where = $db.pagamento.pedido_id == $order.id
      return = {type: "single"}
    } as $payment

    precondition ($payment != null) {
      error_type = "standard"
      error = "Order payment record is unavailable."
    }
  }

  response = {
    id: $order.id
    codigo: $order.codigo
    data_pedido: $order.data_pedido
    status: $order.status
    cliente: {
      id: $order.cliente_id
      nome_completo: $customer.nome_completo
      email_masked: $email_masked
    }
    entrega: {
      cep: $order.entrega_cep
      logradouro: $order.entrega_logradouro
      numero: $order.entrega_numero
      complemento: $order.entrega_complemento
      bairro: $order.entrega_bairro
      cidade: $order.entrega_cidade
      estado: $order.entrega_estado
      identificacao: $order.entrega_identificacao
    }
    itens: $item_summaries
    subtotal: $order.subtotal
    valor_frete: $order.valor_frete
    valor_total: $order.valor_total
    pagamento: {
      metodo: $payment.metodo
      valor: $payment.valor
      status: $payment.status
    }
  }
  tags = ["voltix:internal-orders"]
}
