query "products/{product_id}/image" verb=POST {
  api_group = "Product Management"
  auth = "user"

  input {
    int product_id filters=min:1
    file image_file
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

    storage.create_image {
      value = $input.image_file
      access = "private"
      filename = $input.image_file.name
    } as $stored_image

    db.patch produto {
      field_name = "id"
      field_value = $input.product_id
      data = {
        imagem_principal: $stored_image.path
        updated_at: now
      }
    } as $updated_product
  }

  response = $updated_product
  tags = ["voltix:product-management"]
}
