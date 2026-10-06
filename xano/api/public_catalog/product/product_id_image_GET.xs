query "products/{product_id}/image" verb=GET {
  api_group = "Public Catalog"

  input {
    int product_id filters=min:1
  }

  stack {
    db.get produto {
      field_name = "id"
      field_value = $input.product_id
      output = ["id", "imagem_principal", "status"]
    } as $product

    precondition ($product != null && $product.status == "ATIVO") {
      error_type = "notfound"
      error = "Product not found."
    }

    var $image_url {
      value = null
    }

    conditional {
      if ($product.imagem_principal != null && $product.imagem_principal != "") {
        storage.sign_private_url {
          pathname = $product.imagem_principal
          ttl = 3600
        } as $signed_url

        var.update $image_url {
          value = $signed_url
        }
      }
    }
  }

  response = {
    image_url: $image_url
  }
  tags = ["voltix:public-catalog"]
}
