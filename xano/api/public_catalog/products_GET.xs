query "products" verb=GET {
  api_group = "Public Catalog"

  input {
    int category_id?
    text q?
  }

  stack {
    var $products {
      value = []
    }

    conditional {
      if ($input.category_id != null && $input.category_id != 0) {
        db.get categoria {
          field_name = "id"
          field_value = $input.category_id
          output = ["id", "status"]
        } as $category

        precondition ($category != null && $category.status == "ATIVO") {
          error_type = "notfound"
          error = "Category not found."
        }

        conditional {
          if ($input.q != null && $input.q != "") {
            db.query produto {
              return = {type: "list"}
              where = ($db.produto.status == "ATIVO") && ($db.produto.categoria_id == $input.category_id) && ($db.produto.nome includes $input.q)
              sort = {nome: "asc"}
              output = [
                "id",
                "nome",
                "descricao",
                "especificacoes_tecnicas",
                "categoria_id",
                "marca_id",
                "imagem_principal",
                "status"
              ]
            } as $filtered_products

            var.update $products {
              value = $filtered_products
            }
          }
        }

        conditional {
          if ($input.q == null || $input.q == "") {
            db.query produto {
              return = {type: "list"}
              where = ($db.produto.status == "ATIVO") && ($db.produto.categoria_id == $input.category_id)
              sort = {nome: "asc"}
              output = [
                "id",
                "nome",
                "descricao",
                "especificacoes_tecnicas",
                "categoria_id",
                "marca_id",
                "imagem_principal",
                "status"
              ]
            } as $filtered_products

            var.update $products {
              value = $filtered_products
            }
          }
        }
      }
    }

    conditional {
      if ($input.category_id == null || $input.category_id == 0) {
        conditional {
          if ($input.q != null && $input.q != "") {
            db.query produto {
              return = {type: "list"}
              where = ($db.produto.status == "ATIVO") && ($db.produto.nome includes $input.q)
              sort = {nome: "asc"}
              output = [
                "id",
                "nome",
                "descricao",
                "especificacoes_tecnicas",
                "categoria_id",
                "marca_id",
                "imagem_principal",
                "status"
              ]
            } as $all_products

            var.update $products {
              value = $all_products
            }
          }
        }

        conditional {
          if ($input.q == null || $input.q == "") {
            db.query produto {
              return = {type: "list"}
              where = $db.produto.status == "ATIVO"
              sort = {nome: "asc"}
              output = [
                "id",
                "nome",
                "descricao",
                "especificacoes_tecnicas",
                "categoria_id",
                "marca_id",
                "imagem_principal",
                "status"
              ]
            } as $all_products

            var.update $products {
              value = $all_products
            }
          }
        }
      }
    }

    var $product_list {
      value = []
    }

    foreach ($products) {
      each as $product {
        var $category_name {
          value = null
        }

        var $brand_name {
          value = null
        }

        db.get categoria {
          field_name = "id"
          field_value = $product.categoria_id
          output = ["id", "name", "status"]
        } as $category_record

        db.get marca {
          field_name = "id"
          field_value = $product.marca_id
          output = ["id", "name", "status"]
        } as $brand_record

        conditional {
          if ($category_record != null && $category_record.status == "ATIVO") {
            var.update $category_name {
              value = $category_record.name
            }
          }
        }

        conditional {
          if ($brand_record != null && $brand_record.status == "ATIVO") {
            var.update $brand_name {
              value = $brand_record.name
            }
          }
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

        var.update $product_list {
          value = $product_list|push:{
            id: $product.id
            nome: $product.nome
            descricao: $product.descricao
            especificacoes_tecnicas: $product.especificacoes_tecnicas
            categoria_id: $product.categoria_id
            marca_id: $product.marca_id
            categoria_nome: $category_name
            marca_nome: $brand_name
            status: $product.status
            image_url: $image_url
          }
        }
      }
    }
  }

  response = $product_list
  tags = ["voltix:public-catalog"]
}
