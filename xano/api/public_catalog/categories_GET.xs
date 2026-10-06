query "categories" verb=GET {
  api_group = "Public Catalog"

  input {
  }

  stack {
    db.query categoria {
      where = $db.categoria.status == "ATIVO"
      sort = {name: "asc"}
      output = ["id", "name", "description", "status"]
    } as $categories
  }

  response = $categories
  tags = ["voltix:public-catalog"]
}
