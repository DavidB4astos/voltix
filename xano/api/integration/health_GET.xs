query "integration/health" verb=GET {
  api_group = "Integration"

  input {
  }

  stack {
  }

  response = {
    status: "ok"
    service: "voltix-xano"
    integration: "available"
  }
  guid = "6XiWXpFc_1mS4nR4zXb7a7aMxmE"
}
