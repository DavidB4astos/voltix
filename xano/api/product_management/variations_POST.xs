query "variations" verb=POST {
  api_group = "Product Management"
  auth = "user"

  input {
    int produto_id filters=min:1
    text nome_ou_descricao?
    text sku filters=trim
    decimal preco
    decimal quantidade_disponivel
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
      field_value = $input.produto_id
      output = ["id"]
    } as $product

    precondition ($product != null) {
      error_type = "notfound"
      error = "Product not found."
    }

    precondition (
      $input.sku != "" &&
      $input.preco > 0 &&
      $input.quantidade_disponivel >= 0
    ) {
      error_type = "inputerror"
      error = "A unique SKU, positive price, and non-negative quantity are required."
    }

    db.query variacao_produto {
      where = $db.variacao_produto.sku == $input.sku
      return = {type: "exists"}
    } as $sku_exists

    precondition ($sku_exists == false) {
      error_type = "badrequest"
      error = "A variation with this SKU already exists."
    }

    db.add variacao_produto {
      data = {
        produto_id: $input.produto_id
        nome_ou_descricao: $input.nome_ou_descricao
        sku: $input.sku
        preco: $input.preco
        quantidade_disponivel: $input.quantidade_disponivel
        status: "ATIVO"
        updated_at: now
      }
    } as $variation
  }

  response = $variation
  tags = ["voltix:product-management"]
}
