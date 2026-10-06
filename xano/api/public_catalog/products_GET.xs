query "products" verb=GET {
  api_group = "Public Catalog"

  input {
    int category_id? filters=min:1
  }

  stack {
    conditional {
      if ($input.category_id != null) {
        db.get categoria {
          field_name = "id"
          field_value = $input.category_id
          output = ["id", "status"]
        } as $category

        precondition ($category != null && $category.status == "ATIVO") {
          error_type = "notfound"
          error = "Category not found."
        }
      }
    }

    db.query produto {
      join = {
        categoria: {
          table: "categoria"
          type: "left"
          where: $db.produto.categoria_id == $db.categoria.id && $db.categoria.status == "ATIVO"
        }
        marca: {
          table: "marca"
          type: "left"
          where: $db.produto.marca_id == $db.marca.id && $db.marca.status == "ATIVO"
        }
      }
      eval = {
        categoria_nome: $db.categoria.name
        marca_nome: $db.marca.name
      }
      where = $db.produto.status == "ATIVO" && ($input.category_id == null || $db.produto.categoria_id == $input.category_id)
      sort = {nome: "asc"}
      output = [
        "id",
        "nome",
        "descricao",
        "especificacoes_tecnicas",
        "categoria_id",
        "marca_id",
        "status"
      ]
    } as $products
  }

  response = $products
  tags = ["voltix:public-catalog"]
}
