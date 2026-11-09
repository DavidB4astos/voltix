"""Strict, sanitized contract for internal order operations."""

import math
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .internal_customers import (ORDER_STATUSES, InternalOrderItem,
                                 customer_date_display, order_item_record,
                                 positive_int)

ORDER_FIELDS = frozenset({
    "id",
    "codigo",
    "data_pedido",
    "status",
    "cliente",
    "itens_count",
    "subtotal",
    "valor_frete",
    "valor_total",
})

ORDER_DETAIL_FIELDS = frozenset({
    "id",
    "codigo",
    "data_pedido",
    "status",
    "cliente",
    "entrega",
    "itens",
    "subtotal",
    "valor_frete",
    "valor_total",
    "pagamento",
})

DELIVERY_FIELDS = frozenset({
    "cep",
    "logradouro",
    "numero",
    "complemento",
    "bairro",
    "cidade",
    "estado",
    "identificacao",
})


@dataclass
class OrderCustomer:
    id: int
    nome_completo: str
    email_masked: str


@dataclass
class OrderDelivery:
    cep: str
    logradouro: str
    numero: str
    complemento: str
    bairro: str
    cidade: str
    estado: str
    identificacao: str


@dataclass
class OrderPayment:
    metodo: str
    valor: str
    status: str


@dataclass
class OrderSummary:
    id: int
    codigo: str
    data_pedido: str
    data_pedido_display: str
    status: str
    cliente_id: int
    cliente_nome: str
    cliente_email_masked: str
    cliente_display: str
    itens_count: int
    itens_count_display: str
    subtotal: str
    valor_frete: str
    valor_total: str


@dataclass
class OrderDetail:
    id: int
    codigo: str
    data_pedido: str
    data_pedido_display: str
    status: str
    cliente_id: int
    cliente_nome: str
    cliente_email_masked: str
    cliente_display: str
    entrega_cep: str
    entrega_logradouro: str
    entrega_numero: str
    entrega_complemento: str
    entrega_bairro: str
    entrega_cidade: str
    entrega_estado: str
    entrega_identificacao: str
    endereco_linha: str
    endereco_cidade: str
    cep_display: str
    identificacao_display: str
    itens: list[InternalOrderItem]
    subtotal: str
    valor_frete: str
    valor_total: str
    pagamento_metodo: str
    pagamento_valor: str
    pagamento_status: str
    pagamento_metodo_display: str
    pagamento_status_display: str


@dataclass
class OrderStatusResult:
    pedido_id: int
    codigo: str
    status_anterior: str
    status_atual: str
    alterado: bool


def _text(value: Any, field: str, *, maximum: int, allow_none: bool = False) -> str:
    if value is None and allow_none:
        return ""
    if not isinstance(value, str):
        raise ValueError(f"Invalid order {field}.")
    text = value.strip()
    if not text or len(text) > maximum:
        raise ValueError(f"Invalid order {field}.")
    return text


def _decimal(value: Any, field: str) -> str:
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise ValueError(f"Invalid order {field}.")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"Invalid order {field}.")
    text = value.strip() if isinstance(value, str) else str(value)
    if not re.fullmatch(r"-?\d+(?:\.\d+)?", text):
        raise ValueError(f"Invalid order {field}.")
    return text


def _date(value: Any) -> tuple[str, str]:
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise ValueError("Invalid order date.")
    if isinstance(value, (int, float)) and not math.isfinite(value):
        raise ValueError("Invalid order date.")
    raw = str(value)
    return raw, customer_date_display(value)


def _email_masked(value: Any) -> str:
    if value is None:
        return ""
    if not isinstance(value, str) or not re.fullmatch(r"[^@*\s]{0,3}\*{5}", value):
        raise ValueError("Unsanitized customer email.")
    return value


def _customer(value: Any, *, detail: bool) -> OrderCustomer:
    expected = {"id", "nome_completo", "email_masked"} if detail else {"id", "nome_completo"}
    if not isinstance(value, dict) or set(value) != expected:
        raise ValueError("Invalid order customer.")
    return OrderCustomer(
        positive_int(value["id"]),
        _text(value["nome_completo"], "customer name", maximum=300),
        _email_masked(value.get("email_masked")) if detail else "",
    )


def _delivery(value: Any) -> OrderDelivery:
    if not isinstance(value, dict) or set(value) != DELIVERY_FIELDS:
        raise ValueError("Invalid order delivery.")
    return OrderDelivery(
        _text(value["cep"], "cep", maximum=20, allow_none=True),
        _text(value["logradouro"], "street", maximum=300, allow_none=True),
        _text(value["numero"], "number", maximum=50, allow_none=True),
        _text(value["complemento"], "complement", maximum=200, allow_none=True),
        _text(value["bairro"], "district", maximum=150, allow_none=True),
        _text(value["cidade"], "city", maximum=150, allow_none=True),
        _text(value["estado"], "state", maximum=100, allow_none=True),
        _text(value["identificacao"], "identification", maximum=100, allow_none=True),
    )


def _payment(value: Any) -> OrderPayment:
    if not isinstance(value, dict) or set(value) != {"metodo", "valor", "status"}:
        raise ValueError("Invalid order payment.")
    return OrderPayment(
        _text(value["metodo"], "payment method", maximum=100, allow_none=True),
        _decimal(value["valor"], "payment value"),
        _text(value["status"], "payment status", maximum=100, allow_none=True),
    )


def _items(value: Any) -> list[InternalOrderItem]:
    if not isinstance(value, list):
        raise ValueError("Invalid order items.")
    return [order_item_record(item) for item in value]


def _address_line(delivery: OrderDelivery) -> str:
    parts = [part for part in (
        delivery.logradouro, delivery.numero, delivery.complemento) if part]
    return ", ".join(parts) if parts else "Indisponível"


def _address_city(delivery: OrderDelivery) -> str:
    location = " - ".join(part for part in (delivery.cidade, delivery.estado) if part)
    parts = [part for part in (delivery.bairro, location) if part]
    return ", ".join(parts) if parts else "Indisponível"


def _items_count(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("Invalid order item count.")
    return value


def _items_display(count: int) -> str:
    return "1 item" if count == 1 else f"{count} itens"


def order_filters(q: str, status: str, page: int, per_page: int = 20) -> dict:
    if not isinstance(q, str) or not isinstance(status, str):
        raise ValueError("Invalid order filters.")
    term = q.strip()
    if len(term) > 100 or status not in ORDER_STATUSES | {"TODOS"}:
        raise ValueError("Invalid order filters.")
    return {"q": term, "status": status, "page": positive_int(page),
            "per_page": positive_int(per_page, 50)}


def order_summary_record(value: Any) -> OrderSummary:
    if not isinstance(value, dict) or set(value) != ORDER_FIELDS:
        raise ValueError("Invalid order record.")
    status = value["status"]
    if status not in ORDER_STATUSES:
        raise ValueError("Invalid order status.")
    customer = _customer(value["cliente"], detail=False)
    data_raw, data_display = _date(value["data_pedido"])
    count = _items_count(value["itens_count"])
    return OrderSummary(
        positive_int(value["id"]),
        _text(value["codigo"], "code", maximum=100),
        data_raw,
        data_display,
        status,
        customer.id,
        customer.nome_completo,
        "",
        customer.nome_completo,
        count,
        _items_display(count),
        _decimal(value["subtotal"], "subtotal"),
        _decimal(value["valor_frete"], "freight"),
        _decimal(value["valor_total"], "total"),
    )


def order_summary_page(value: Any, *, page: int,
                       per_page: int = 20) -> tuple[list[OrderSummary], int, int]:
    expected = {"items", "page", "per_page", "items_total", "page_total"}
    if not isinstance(value, dict) or set(value) != expected:
        raise ValueError("Invalid order page.")
    if (type(value["page"]) is not int or type(value["per_page"]) is not int
            or value["page"] != page or value["per_page"] != per_page):
        raise ValueError("Mismatched order page.")
    total, pages = value["items_total"], value["page_total"]
    if (type(total) is not int or type(pages) is not int or total < 0
            or pages != (total + per_page - 1) // per_page):
        raise ValueError("Invalid order totals.")
    if not isinstance(value["items"], list) or len(value["items"]) != max(
            0, min(per_page, total - (page - 1) * per_page)):
        raise ValueError("Invalid order page size.")
    items = [order_summary_record(item) for item in value["items"]]
    if len({item.id for item in items}) != len(items):
        raise ValueError("Duplicate orders.")
    return items, total, pages


def order_detail(value: Any, *, order_id: int) -> OrderDetail:
    if not isinstance(value, dict) or set(value) != ORDER_DETAIL_FIELDS:
        raise ValueError("Invalid order detail.")
    record_id = positive_int(value["id"])
    if record_id != positive_int(order_id):
        raise ValueError("Unexpected order detail.")
    status = value["status"]
    if status not in ORDER_STATUSES:
        raise ValueError("Invalid order status.")
    customer = _customer(value["cliente"], detail=True)
    delivery = _delivery(value["entrega"])
    payment = _payment(value["pagamento"])
    data_raw, data_display = _date(value["data_pedido"])
    return OrderDetail(
        record_id,
        _text(value["codigo"], "code", maximum=100),
        data_raw,
        data_display,
        status,
        customer.id,
        customer.nome_completo,
        customer.email_masked,
        customer.nome_completo,
        delivery.cep,
        delivery.logradouro,
        delivery.numero,
        delivery.complemento,
        delivery.bairro,
        delivery.cidade,
        delivery.estado,
        delivery.identificacao,
        _address_line(delivery),
        _address_city(delivery),
        f"CEP {delivery.cep}" if delivery.cep else "Indisponível",
        delivery.identificacao or "Indisponível",
        _items(value["itens"]),
        _decimal(value["subtotal"], "subtotal"),
        _decimal(value["valor_frete"], "freight"),
        _decimal(value["valor_total"], "total"),
        payment.metodo,
        payment.valor,
        payment.status,
        payment.metodo or "Indisponível",
        payment.status or "Indisponível",
    )


def order_status_result(value: Any, *, order_id: int) -> OrderStatusResult:
    if not isinstance(value, dict) or set(value) != {
            "pedido_id", "codigo", "status_anterior", "status_atual", "alterado"}:
        raise ValueError("Invalid order status result.")
    if value["status_anterior"] not in ORDER_STATUSES or value["status_atual"] not in ORDER_STATUSES:
        raise ValueError("Invalid order status result.")
    if type(value["alterado"]) is not bool:
        raise ValueError("Invalid order status result.")
    record_id = positive_int(value["pedido_id"])
    if record_id != positive_int(order_id):
        raise ValueError("Unexpected order status result.")
    return OrderStatusResult(
        record_id,
        _text(value["codigo"], "code", maximum=100),
        value["status_anterior"],
        value["status_atual"],
        value["alterado"],
    )
