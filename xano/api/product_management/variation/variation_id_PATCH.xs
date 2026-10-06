query "variations/{variation_id}" verb=PATCH {
  api_group = "Product Management"
  auth = "user"

  input {
    int variation_id filters=min:1
    int produto_id? filters=min:1
    text nome_ou_descricao?
    text sku? filters=trim
    decimal preco?
    decimal quantidade_disponivel?
    enum status? {
      values = ["ATIVO", "INATIVO"]
    }
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
    } as $variation

    precondition ($variation != null) {
      error_type = "notfound"
      error = "Product variation not found."
    }

    precondition (
      $input.produto_id == null ||
      $input.produto_id == $variation.produto_id
    ) {
      error_type = "badrequest"
      error = "A variation cannot be reassigned to another product."
    }

    precondition (
      $input.nome_ou_descricao != null ||
      $input.sku != null ||
      $input.preco != null ||
      $input.quantidade_disponivel != null ||
      $input.status != null
    ) {
      error_type = "inputerror"
      error = "Provide at least one variation field to update."
    }

    conditional {
      if ($input.sku != null) {
        precondition ($input.sku != "") {
          error_type = "inputerror"
          error = "SKU is required."
        }

        db.query variacao_produto {
          where = $db.variacao_produto.sku == $input.sku && $db.variacao_produto.id != $input.variation_id
          return = {type: "exists"}
        } as $sku_exists

        precondition ($sku_exists == false) {
          error_type = "badrequest"
          error = "A variation with this SKU already exists."
        }
      }
    }

    precondition ($input.preco == null || $input.preco > 0) {
      error_type = "inputerror"
      error = "Price must be greater than zero."
    }

    precondition (
      $input.quantidade_disponivel == null ||
      $input.quantidade_disponivel >= 0
    ) {
      error_type = "inputerror"
      error = "Available quantity cannot be negative."
    }

    var $updates {
      value = {updated_at: now}
    }

    conditional {
      if ($input.nome_ou_descricao != null) {
        var.update $updates {
          value = $updates|set:"nome_ou_descricao":$input.nome_ou_descricao
        }
      }
    }

    conditional {
      if ($input.sku != null) {
        var.update $updates {
          value = $updates|set:"sku":$input.sku
        }
      }
    }

    conditional {
      if ($input.preco != null) {
        var.update $updates {
          value = $updates|set:"preco":$input.preco
        }
      }
    }

    conditional {
      if ($input.quantidade_disponivel != null) {
        var.update $updates {
          value = $updates|set:"quantidade_disponivel":$input.quantidade_disponivel
        }
      }
    }

    conditional {
      if ($input.status != null) {
        var.update $updates {
          value = $updates|set:"status":$input.status
        }
      }
    }

    db.patch variacao_produto {
      field_name = "id"
      field_value = $input.variation_id
      data = $updates
    } as $updated_variation
  }

  response = $updated_variation
  tags = ["voltix:product-management"]
}
