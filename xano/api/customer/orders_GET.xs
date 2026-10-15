query "orders" verb=GET {
  api_group = "Voltix Customer"
  auth = "CLIENTE"

  input {
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

    db.query pedido {
      where = $db.pedido.cliente_id == $auth.id
      sort = {data_pedido: "desc"}
      return = {type: "list"}
    } as $orders

    var $order_summaries {
      value = []
    }

    foreach ($orders) {
      each as $order {
        db.query item_pedido {
          where = $db.item_pedido.pedido_id == $order.id
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

        var.update $order_summaries {
          value = $order_summaries|push:{
            id: $order.id
            codigo: $order.codigo
            data_pedido: $order.data_pedido
            status: $order.status
            subtotal: $order.subtotal
            valor_frete: $order.valor_frete
            valor_total: $order.valor_total
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
          }
        }
      }
    }
  }

  response = $order_summaries
  tags = ["voltix:checkout-orders"]
  guid = "TuuzNNajfS5W4pEMzkAwjC5aSPU"
}
