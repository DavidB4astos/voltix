query "variations/{variation_id}/stock-adjustments" verb=POST {
  api_group = "Product Management"
  auth = "user"

  input {
    int variation_id filters=min:1
    decimal delta
  }

  stack {
    db.get user {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "role", "status"]
    } as $user

    precondition ($user != null) {
      error_type = "accessdenied"
      error = "Invalid authenticated user."
    }

    precondition ($user.role == "ADMINISTRADOR" && $user.status == "ATIVO") {
      error_type = "accessdenied"
      error = "Administrator access is required."
    }

    db.get variacao_produto {
      field_name = "id"
      field_value = $input.variation_id
      output = ["id"]
    } as $variation

    precondition ($variation != null) {
      error_type = "notfound"
      error = "Product variation not found."
    }

    precondition ($input.delta != 0) {
      error_type = "inputerror"
      error = "Stock adjustment delta must be non-zero."
    }

    var $required_quantity {
      value = 0
    }

    conditional {
      if ($input.delta < 0) {
        var.update $required_quantity {
          value = 0 - $input.delta
        }
      }
    }

    db.increment "variacao_produto" {
      where = $db.variacao_produto.id == $input.variation_id && $db.variacao_produto.quantidade_disponivel >= $required_quantity
      field_name = "quantidade_disponivel"
      value = $input.delta
      return = {type: "count"}
    } as $adjusted

    precondition ($adjusted > 0) {
      error_type = "badrequest"
      error = "Insufficient stock for this adjustment."
    }

    db.get variacao_produto {
      field_name = "id"
      field_value = $input.variation_id
      output = [
        "id"
        "produto_id"
        "nome_ou_descricao"
        "sku"
        "preco"
        "quantidade_disponivel"
        "status"
        "created_at"
        "updated_at"
      ]
    } as $updated_variation
  }

  response = $updated_variation
  tags = ["voltix:product-management"]
  guid = "NiRGIMH9OHa57klOkcqHNkk0tOc"
}
