query "products/{product_id}" verb=GET {
  api_group = "Public Catalog"

  input {
    int product_id filters=min:1
  }

  stack {
    db.get produto {
      field_name = "id"
      field_value = $input.product_id
      output = [
        "id",
        "nome",
        "descricao",
        "especificacoes_tecnicas",
        "categoria_id",
        "marca_id",
        "status"
      ]
    } as $product

    precondition ($product != null && $product.status == "ATIVO") {
      error_type = "notfound"
      error = "Product not found."
    }

    db.get categoria {
      field_name = "id"
      field_value = $product.categoria_id
      output = ["id", "name", "status"]
    } as $category

    db.get marca {
      field_name = "id"
      field_value = $product.marca_id
      output = ["id", "name", "status"]
    } as $brand

    var $public_category_name {
      value = null
    }

    var $public_brand_name {
      value = null
    }

    conditional {
      if ($category != null && $category.status == "ATIVO") {
        var.update $public_category_name {
          value = $category.name
        }
      }
    }

    conditional {
      if ($brand != null && $brand.status == "ATIVO") {
        var.update $public_brand_name {
          value = $brand.name
        }
      }
    }

    db.query variacao_produto {
      where = $db.variacao_produto.produto_id == $input.product_id && $db.variacao_produto.status == "ATIVO"
      sort = {sku: "asc"}
      output = [
        "id",
        "produto_id",
        "nome_ou_descricao",
        "sku",
        "preco",
        "quantidade_disponivel",
        "status"
      ]
    } as $variations
  }

  response = {
    product: $product
    category_name: $public_category_name
    brand_name: $public_brand_name
    variations: $variations
  }
  tags = ["voltix:public-catalog"]
}
