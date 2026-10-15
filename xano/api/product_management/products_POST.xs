query "products" verb=POST {
  api_group = "Product Management"
  auth = "user"

  input {
    text nome? filters=trim
    text descricao?
    text especificacoes_tecnicas?
    int categoria_id filters=min:1
    int marca_id filters=min:1
    json variacoes
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

    db.get categoria {
      field_name = "id"
      field_value = $input.categoria_id
      output = ["id", "status"]
    } as $category

    precondition ($category != null && $category.status == "ATIVO") {
      error_type = "badrequest"
      error = "An active category is required."
    }

    db.get marca {
      field_name = "id"
      field_value = $input.marca_id
      output = ["id", "status"]
    } as $brand

    precondition ($brand != null && $brand.status == "ATIVO") {
      error_type = "badrequest"
      error = "An active brand is required."
    }

    precondition ($input.variacoes != null && ($input.variacoes|count) > 0) {
      error_type = "inputerror"
      error = "At least one product variation is required."
    }

    foreach ($input.variacoes) {
      each as $variation {
        var $clean_sku {
          value = $variation.sku|to_text|trim
        }

        precondition (
          $variation.sku != null &&
          $clean_sku != "" &&
          $variation.preco != null &&
          $variation.preco > 0 &&
          $variation.quantidade_disponivel != null &&
          $variation.quantidade_disponivel >= 0
        ) {
          error_type = "inputerror"
          error = "Each variation requires a unique SKU, positive price, and non-negative quantity."
        }

        db.query variacao_produto {
          where = $db.variacao_produto.sku == $clean_sku
          return = {type: "exists"}
        } as $sku_exists

        precondition ($sku_exists == false) {
          error_type = "badrequest"
          error = "A variation with this SKU already exists."
        }
      }
    }

    db.transaction {
      stack {
        db.add produto {
          data = {
            nome: $input.nome
            descricao: $input.descricao
            especificacoes_tecnicas: $input.especificacoes_tecnicas
            categoria_id: $input.categoria_id
            marca_id: $input.marca_id
            status: "ATIVO"
            updated_at: now
          }
        } as $product

        foreach ($input.variacoes) {
          each as $variation {
            db.add variacao_produto {
              data = {
                produto_id: $product.id
                nome_ou_descricao: $variation.nome_ou_descricao
                sku: $variation.sku|trim
                preco: $variation.preco
                quantidade_disponivel: $variation.quantidade_disponivel
                status: "ATIVO"
                updated_at: now
              }
            } as $created_variation
          }
        }
      }
    }
  }

  response = $product
  tags = ["voltix:product-management"]
  guid = "jr9c6gUFHDZF1Cundb79ySKB5jw"
}
