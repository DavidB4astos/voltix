query "checkout/confirm" verb=POST {
  api_group = "Voltix Customer"
  auth = "CLIENTE"

  input {
    int endereco_id filters=min:1
    enum metodo_pagamento {
      values = ["PIX", "CARTAO", "BOLETO"]
    }
    json revisao
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
      field_value = $input.endereco_id
    } as $address

    precondition (
      $address != null &&
      $address.cliente_id == $auth.id &&
      $address.status == "ATIVO"
    ) {
      error_type = "badrequest"
      error = "An active address belonging to this customer is required."
    }

    db.query carrinho {
      where = $db.carrinho.cliente_id == $auth.id
      return = {type: "single"}
    } as $cart

    precondition ($cart != null) {
      error_type = "badrequest"
      error = "The cart is empty."
    }

    db.query item_carrinho {
      join = {
        variacao_produto: {
          table: "variacao_produto"
          type: "inner"
          where: $db.item_carrinho.variacao_produto_id == $db.variacao_produto.id
        }
        produto: {
          table: "produto"
          type: "inner"
          where: $db.variacao_produto.produto_id == $db.produto.id
        }
      }
      eval = {
        produto_nome: $db.produto.nome
        produto_status: $db.produto.status
        variacao_nome: $db.variacao_produto.nome_ou_descricao
        sku: $db.variacao_produto.sku
        variacao_status: $db.variacao_produto.status
        preco: $db.variacao_produto.preco
        estoque: $db.variacao_produto.quantidade_disponivel
        subtotal: $db.variacao_produto.preco * $db.item_carrinho.quantidade
        disponivel: $db.produto.status == "ATIVO" && $db.variacao_produto.status == "ATIVO" && $db.variacao_produto.quantidade_disponivel >= $db.item_carrinho.quantidade
      }
      where = $db.item_carrinho.carrinho_id == $cart.id
      sort = {id: "asc"}
      output = ["id", "variacao_produto_id", "quantidade"]
    } as $cart_items

    precondition (($cart_items|count) > 0) {
      error_type = "badrequest"
      error = "The cart is empty."
    }

    var $review_items {
      value = []
    }

    var $review_snapshot {
      value = []
    }

    var $subtotal {
      value = 0
    }

    var $all_available {
      value = true
    }

    foreach ($cart_items) {
      each as $item {
        var.update $review_items {
          value = $review_items|push:{
            item_id: $item.id
            variacao_id: $item.variacao_produto_id
            produto_nome: $item.produto_nome
            variacao_nome: $item.variacao_nome
            sku: $item.sku
            quantidade: $item.quantidade
            preco_unitario: $item.preco
            subtotal: $item.subtotal
            produto_status: $item.produto_status
            variacao_status: $item.variacao_status
            estoque_disponivel: $item.estoque
            disponivel: $item.disponivel
          }
        }

        var.update $review_snapshot {
          value = $review_snapshot|push:{
            item_id: $item.id
            variacao_id: $item.variacao_produto_id
            quantidade: $item.quantidade
            preco_unitario: $item.preco
            estoque_disponivel: $item.estoque
            produto_status: $item.produto_status
            variacao_status: $item.variacao_status
          }
        }

        var.update $subtotal {
          value = $subtotal + $item.subtotal
        }

        conditional {
          if ($item.disponivel == false) {
            var.update $all_available {
              value = false
            }
          }
        }
      }
    }

    var $confirmed {
      value = false
    }

    var $review_changed {
      value = false
    }

    var $order_id {
      value = null
    }

    var $order_code {
      value = null
    }

    db.transaction {
      stack {
        db.get endereco {
          field_name = "id"
          field_value = $input.endereco_id
        } as $current_address

        precondition (
          $current_address != null &&
          $current_address.cliente_id == $auth.id &&
          $current_address.status == "ATIVO"
        ) {
          error_type = "badrequest"
          error = "An active address belonging to this customer is required."
        }

        db.query carrinho {
          where = $db.carrinho.cliente_id == $auth.id
          return = {type: "single"}
        } as $current_cart

        precondition ($current_cart != null) {
          error_type = "badrequest"
          error = "The cart is empty."
        }

        db.query item_carrinho {
          join = {
            variacao_produto: {
              table: "variacao_produto"
              type: "inner"
              where: $db.item_carrinho.variacao_produto_id == $db.variacao_produto.id
            }
            produto: {
              table: "produto"
              type: "inner"
              where: $db.variacao_produto.produto_id == $db.produto.id
            }
          }
          eval = {
            produto_nome: $db.produto.nome
            produto_status: $db.produto.status
            variacao_nome: $db.variacao_produto.nome_ou_descricao
            sku: $db.variacao_produto.sku
            variacao_status: $db.variacao_produto.status
            preco: $db.variacao_produto.preco
            estoque: $db.variacao_produto.quantidade_disponivel
            subtotal: $db.variacao_produto.preco * $db.item_carrinho.quantidade
            disponivel: $db.produto.status == "ATIVO" && $db.variacao_produto.status == "ATIVO" && $db.variacao_produto.quantidade_disponivel >= $db.item_carrinho.quantidade
          }
          where = $db.item_carrinho.carrinho_id == $current_cart.id
          sort = {id: "asc"}
          output = ["id", "variacao_produto_id", "quantidade"]
        } as $current_cart_items

        precondition (($current_cart_items|count) > 0) {
          error_type = "badrequest"
          error = "The cart is empty."
        }

        var.update $review_items {
          value = []
        }

        var.update $review_snapshot {
          value = []
        }

        var.update $subtotal {
          value = 0
        }

        var.update $all_available {
          value = true
        }

        foreach ($current_cart_items) {
          each as $item {
            var.update $review_items {
              value = $review_items|push:{
                item_id: $item.id
                variacao_id: $item.variacao_produto_id
                produto_nome: $item.produto_nome
                variacao_nome: $item.variacao_nome
                sku: $item.sku
                quantidade: $item.quantidade
                preco_unitario: $item.preco
                subtotal: $item.subtotal
                produto_status: $item.produto_status
                variacao_status: $item.variacao_status
                estoque_disponivel: $item.estoque
                disponivel: $item.disponivel
              }
            }

            var.update $review_snapshot {
              value = $review_snapshot|push:{
                item_id: $item.id
                variacao_id: $item.variacao_produto_id
                quantidade: $item.quantidade
                preco_unitario: $item.preco
                estoque_disponivel: $item.estoque
                produto_status: $item.produto_status
                variacao_status: $item.variacao_status
              }
            }

            var.update $subtotal {
              value = $subtotal + $item.subtotal
            }

            conditional {
              if ($item.disponivel == false) {
                var.update $all_available {
                  value = false
                }
              }
            }
          }
        }

        conditional {
          if (
            ($review_snapshot|json_encode) !=
            ($input.revisao|json_encode)
          ) {
            var.update $review_changed {
              value = true
            }
          }

          else {
            conditional {
              if ($all_available == true) {
                security.create_uuid as $order_uuid

                db.add pedido {
                  data = {
                    cliente_id: $auth.id
                    endereco_id: $current_address.id
                    codigo: "VTX-" + $order_uuid
                    data_pedido: now
                    status: "AGUARDANDO_PAGAMENTO"
                    subtotal: $subtotal
                    valor_frete: 0
                    valor_total: $subtotal
                    entrega_cep: $current_address.cep
                    entrega_logradouro: $current_address.logradouro
                    entrega_numero: $current_address.numero
                    entrega_complemento: $current_address.complemento
                    entrega_bairro: $current_address.bairro
                    entrega_cidade: $current_address.cidade
                    entrega_estado: $current_address.estado
                    entrega_identificacao: $current_address.identificacao
                    updated_at: now
                  }
                } as $created_order

                foreach ($current_cart_items) {
                  each as $item {
                    db.add item_pedido {
                      data = {
                        pedido_id: $created_order.id
                        variacao_produto_id: $item.variacao_produto_id
                        quantidade: $item.quantidade
                        preco_unitario: $item.preco
                        updated_at: now
                      }
                    } as $created_order_item
                  }
                }

                db.add pagamento {
                  data = {
                    pedido_id: $created_order.id
                    metodo: $input.metodo_pagamento
                    valor: $subtotal
                    status: "PENDENTE"
                    updated_at: now
                  }
                } as $created_payment

                foreach ($cart_items) {
                  each as $item {
                    db.del item_carrinho {
                      field_name = "id"
                      field_value = $item.id
                    }
                  }
                }

                db.patch carrinho {
                  field_name = "id"
                  field_value = $current_cart.id
                  data = {updated_at: now}
                } as $updated_cart

                var.update $confirmed {
                  value = true
                }

                var.update $order_id {
                  value = $created_order.id
                }

                var.update $order_code {
                  value = $created_order.codigo
                }
              }
            }
          }
        }
      }
    }
  }

  response = {
    confirmado: $confirmed
    revisao_alterada: $review_changed
    pedido_id: $order_id
    codigo: $order_code
    subtotal: $subtotal
    valor_frete: 0
    valor_total: $subtotal
    itens: $review_items
    revisao: $review_snapshot
    endereco_id: $address.id
    endereco: {
      cep: $address.cep
      logradouro: $address.logradouro
      numero: $address.numero
      complemento: $address.complemento
      bairro: $address.bairro
      cidade: $address.cidade
      estado: $address.estado
      identificacao: $address.identificacao
    }
  }
  tags = ["voltix:checkout-orders"]
}
