query "variations" verb=GET {
  api_group = "Product Management"
  auth = "user"

  input {
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

    db.query variacao_produto {
      return = {type: "list"}
      sort = {sku: "asc"}
      output = [
        "id",
        "produto_id",
        "nome_ou_descricao",
        "sku",
        "preco",
        "quantidade_disponivel",
        "status",
        "created_at",
        "updated_at"
      ]
    } as $variations
  }

  response = $variations
  tags = ["voltix:product-management"]
}
