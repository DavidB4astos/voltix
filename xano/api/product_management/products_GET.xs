query products verb=GET {
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

    db.query produto {
      sort = {nome: "asc"}
      return = {type: "list"}
      output = [
        "id"
        "nome"
        "descricao"
        "especificacoes_tecnicas"
        "imagem_principal"
        "categoria_id"
        "marca_id"
        "status"
        "created_at"
        "updated_at"
      ]
    } as $products
  }

  response = $products
  tags = ["voltix:product-management"]
  guid = "AgoGmCxwo3Ip91yQCVqrEwlxztg"
}
