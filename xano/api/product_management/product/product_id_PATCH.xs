query "products/{product_id}" verb=PATCH {
  api_group = "Product Management"
  auth = "user"

  input {
    int product_id filters=min:1
    text nome? filters=trim
    text descricao?
    text especificacoes_tecnicas?
    int categoria_id?
    int marca_id?
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

    db.get produto {
      field_name = "id"
      field_value = $input.product_id
    } as $product

    precondition ($product != null) {
      error_type = "notfound"
      error = "Product not found."
    }

    precondition (
      $input.nome != null ||
      $input.descricao != null ||
      $input.especificacoes_tecnicas != null ||
      ($input.categoria_id != null && $input.categoria_id > 0) ||
      ($input.marca_id != null && $input.marca_id > 0) ||
      $input.status != null
    ) {
      error_type = "inputerror"
      error = "Provide at least one product field to update."
    }

    conditional {
      if ($input.categoria_id != null && $input.categoria_id > 0 && $input.categoria_id != $product.categoria_id) {
        db.get categoria {
          field_name = "id"
          field_value = $input.categoria_id
          output = ["id", "status"]
        } as $category

        precondition ($category != null && $category.status == "ATIVO") {
          error_type = "badrequest"
          error = "An active category is required for a new association."
        }
      }
    }

    conditional {
      if ($input.marca_id != null && $input.marca_id > 0 && $input.marca_id != $product.marca_id) {
        db.get marca {
          field_name = "id"
          field_value = $input.marca_id
          output = ["id", "status"]
        } as $brand

        precondition ($brand != null && $brand.status == "ATIVO") {
          error_type = "badrequest"
          error = "An active brand is required for a new association."
        }
      }
    }

    var $updates {
      value = {updated_at: now}
    }

    conditional {
      if ($input.nome != null) {
        var.update $updates {
          value = $updates|set:"nome":$input.nome
        }
      }
    }

    conditional {
      if ($input.descricao != null) {
        var.update $updates {
          value = $updates|set:"descricao":$input.descricao
        }
      }
    }

    conditional {
      if ($input.especificacoes_tecnicas != null) {
        var.update $updates {
          value = $updates|set:"especificacoes_tecnicas":$input.especificacoes_tecnicas
        }
      }
    }

    conditional {
      if ($input.categoria_id != null && $input.categoria_id > 0) {
        var.update $updates {
          value = $updates|set:"categoria_id":$input.categoria_id
        }
      }
    }

    conditional {
      if ($input.marca_id != null && $input.marca_id > 0) {
        var.update $updates {
          value = $updates|set:"marca_id":$input.marca_id
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

    db.patch produto {
      field_name = "id"
      field_value = $input.product_id
      data = $updates
    } as $updated_product
  }

  response = $updated_product
  tags = ["voltix:product-management"]
  guid = "YJOD1IemBD5iLEfVD1EIPRpi5Vc"
}
