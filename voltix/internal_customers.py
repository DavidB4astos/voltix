"""Strict, sanitized contract for internal customer reads."""

import asyncio
import math
import re
import urllib.error
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable


ORDER_STATUSES = frozenset({
    "AGUARDANDO_PAGAMENTO",
    "PAGAMENTO_CONFIRMADO",
    "EM_PREPARACAO",
    "ENVIADO",
    "ENTREGUE",
    "CANCELADO",
})


@dataclass
class InternalOrderItem:
    variacao_id: int
    sku: str
    nome_ou_descricao: str
    quantidade: int
    preco_unitario: str
    subtotal: str


@dataclass
class InternalOrder:
    id: int
    codigo: str
    data_pedido: str
    data_pedido_display: str
    status: str
    subtotal: str
    valor_frete: str
    valor_total: str
    itens: list[InternalOrderItem]


@dataclass
class InternalCustomer:
    id: int
    nome_completo: str
    email_masked: str
    telefone_masked: str
    status: str
    created_at: str
    cpf_masked: str = ""
    created_at_display: str = ""


def customer_date_display(value: str | int | float) -> str:
    """Render Xano milliseconds or an ISO date with an explicit timezone."""
    try:
        if isinstance(value, (int, float)) or re.fullmatch(r"-?\d+(?:\.\d+)?", value):
            date = datetime.fromtimestamp(float(value) / 1000, tz=timezone.utc)
        else:
            date = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if date.tzinfo is None:
                date = date.replace(tzinfo=timezone.utc)
            date = date.astimezone(timezone.utc)
        return date.strftime("%d/%m/%Y às %H:%M (UTC)")
    except (ValueError, OverflowError, OSError):
        return "Data indisponível"


def positive_int(value: Any, maximum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError("Invalid positive integer.")
    if maximum is not None and value > maximum:
        raise ValueError("Integer outside allowed range.")
    return value


def query_parameters(q: str, status: str, page: int, per_page: int = 20) -> dict:
    term = q.strip()
    if len(term) > 100 or status not in {"ATIVO", "INATIVO", "TODOS"}:
        raise ValueError("Invalid customer filters.")
    return {"q": term, "status": status, "page": positive_int(page),
            "per_page": positive_int(per_page, 50)}


EMAIL_PATTERN = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


def customer_update_payload(nome_completo: str, email: str, telefone: str, *,
                            current_name: str) -> dict:
    """Build a partial update body; blank fields mean 'keep the current value'."""
    if not all(isinstance(value, str) for value in
               (nome_completo, email, telefone, current_name)):
        raise ValueError("Invalid customer update input.")
    payload = {}
    name = nome_completo.strip()
    if name and name != current_name.strip():
        if len(name) > 300:
            raise ValueError("Invalid customer name.")
        payload["nome_completo"] = name
    mail = email.strip().lower()
    if mail:
        if len(mail) > 254 or not EMAIL_PATTERN.fullmatch(mail):
            raise ValueError("Invalid customer email.")
        payload["email"] = mail
    phone = telefone.strip()
    if phone:
        if len(phone) > 30:
            raise ValueError("Invalid customer phone.")
        payload["telefone"] = phone
    return payload


def customer_status_payload(status: str) -> dict:
    if not isinstance(status, str) or status not in {"ATIVO", "INATIVO"}:
        raise ValueError("Invalid customer status.")
    return {"status": status}


def customer_record(value: Any, *, detail: bool = False) -> InternalCustomer:
    if not isinstance(value, dict):
        raise ValueError("Invalid customer record.")
    allowed = {"id", "nome_completo", "email_masked", "telefone_masked", "status", "created_at"}
    if detail:
        allowed.add("cpf_masked")
    if set(value) != allowed:
        raise ValueError("Unexpected customer fields.")
    record_id = positive_int(value["id"])
    name = value["nome_completo"]
    if not isinstance(name, str) or not name.strip() or len(name) > 300:
        raise ValueError("Invalid customer name.")
    if value["status"] not in {"ATIVO", "INATIVO"}:
        raise ValueError("Invalid customer status.")
    masks = {}
    for key, pattern in [("email_masked", r"[^@*\s]{0,3}\*{5}"),
                         ("telefone_masked", r"\*{5}(?:[0-9]{4})?"),
                         ("cpf_masked", r"\*{3}\.\*{3}\.\*{3}-[0-9]{2}")]:
        raw = value.get(key)
        if raw is not None and (not isinstance(raw, str) or not re.fullmatch(pattern, raw)):
            raise ValueError("Unsanitized customer contact.")
        masks[key] = raw or ""
    created = value["created_at"]
    if isinstance(created, bool) or not isinstance(created, (str, int, float)):
        raise ValueError("Invalid customer timestamp.")
    if isinstance(created, (int, float)) and not math.isfinite(created):
        raise ValueError("Invalid customer timestamp.")
    return InternalCustomer(record_id, name.strip(), masks["email_masked"],
                            masks["telefone_masked"], value["status"], str(created), masks["cpf_masked"],
                            customer_date_display(created))


def customer_page(value: Any, *, page: int, per_page: int = 20) -> tuple[list[InternalCustomer], int, int]:
    if not isinstance(value, dict) or set(value) != {"items", "page", "per_page", "total_items", "total_pages"}:
        raise ValueError("Invalid customer page.")
    if type(value["page"]) is not int or type(value["per_page"]) is not int or value["page"] != page or value["per_page"] != per_page:
        raise ValueError("Mismatched customer page.")
    total, pages = value["total_items"], value["total_pages"]
    if type(total) is not int or type(pages) is not int or total < 0 or pages != (total + per_page - 1) // per_page:
        raise ValueError("Invalid customer totals.")
    if not isinstance(value["items"], list) or len(value["items"]) != max(0, min(per_page, total - (page - 1) * per_page)):
        raise ValueError("Invalid customer page size.")
    items = [customer_record(item) for item in value["items"]]
    if len({item.id for item in items}) != len(items):
        raise ValueError("Duplicate customers.")
    return items, total, pages


def _history_text(value: Any, field: str, *, allow_none: bool = False, max_length: int = 300) -> str:
    if value is None and allow_none:
        return ""
    if not isinstance(value, str):
        raise ValueError(f"Invalid order {field}.")
    text = value.strip()
    if not text or len(text) > max_length:
        raise ValueError(f"Invalid order {field}.")
    return text


def _history_decimal(value: Any, field: str) -> str:
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise ValueError(f"Invalid order {field}.")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"Invalid order {field}.")
    text = value.strip() if isinstance(value, str) else str(value)
    if not re.fullmatch(r"-?\d+(?:\.\d+)?", text):
        raise ValueError(f"Invalid order {field}.")
    return text


def _history_date(value: Any) -> str:
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise ValueError("Invalid order date.")
    if isinstance(value, (int, float)) and not math.isfinite(value):
        raise ValueError("Invalid order date.")
    return str(value)


def _history_day(value: Any, field: str) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValueError(f"Invalid {field} date.")
    text = value.strip()
    if not text:
        return ""
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        raise ValueError(f"Invalid {field} date.")
    try:
        datetime.strptime(text, "%Y-%m-%d")
    except ValueError as error:
        raise ValueError(f"Invalid {field} date.") from error
    return text


def history_parameters(status: str, date_from: str | None, date_to: str | None,
                       page: int, per_page: int = 20) -> dict:
    if status not in ORDER_STATUSES | {"TODOS"}:
        raise ValueError("Invalid history status.")
    start, end = _history_day(date_from, "start"), _history_day(date_to, "end")
    if start and end and start > end:
        raise ValueError("Invalid history period.")
    parameters = {"status": status, "page": positive_int(page),
                  "per_page": positive_int(per_page, 50)}
    if start:
        parameters["from"] = start
    if end:
        parameters["to"] = end
    return parameters


def order_item_record(value: Any) -> InternalOrderItem:
    if not isinstance(value, dict) or set(value) != {
            "variacao_id", "sku", "nome_ou_descricao", "quantidade",
            "preco_unitario", "subtotal"}:
        raise ValueError("Invalid order item.")
    return InternalOrderItem(
        positive_int(value["variacao_id"]),
        _history_text(value["sku"], "sku", allow_none=True, max_length=100),
        _history_text(value["nome_ou_descricao"], "description", allow_none=True),
        positive_int(value["quantidade"]),
        _history_decimal(value["preco_unitario"], "unit price"),
        _history_decimal(value["subtotal"], "item subtotal"),
    )


def order_record(value: Any) -> InternalOrder:
    if not isinstance(value, dict) or set(value) != {
            "id", "codigo", "data_pedido", "status", "subtotal", "valor_frete",
            "valor_total", "itens"}:
        raise ValueError("Invalid order record.")
    if value["status"] not in ORDER_STATUSES:
        raise ValueError("Invalid order status.")
    if not isinstance(value["itens"], list):
        raise ValueError("Invalid order items.")
    data_pedido = _history_date(value["data_pedido"])
    return InternalOrder(
        positive_int(value["id"]),
        _history_text(value["codigo"], "code", max_length=100),
        data_pedido,
        customer_date_display(data_pedido),
        value["status"],
        _history_decimal(value["subtotal"], "subtotal"),
        _history_decimal(value["valor_frete"], "freight"),
        _history_decimal(value["valor_total"], "total"),
        [order_item_record(item) for item in value["itens"]],
    )


def order_history_page(value: Any, *, customer_id: int, page: int,
                       per_page: int = 20) -> tuple[list[InternalOrder], int, int]:
    expected = {"cliente_id", "items", "page", "per_page", "total_items", "total_pages"}
    if not isinstance(value, dict) or set(value) != expected:
        raise ValueError("Invalid order history page.")
    if (type(value["cliente_id"]) is not int or value["cliente_id"] != customer_id
            or type(value["page"]) is not int or type(value["per_page"]) is not int
            or value["page"] != page or value["per_page"] != per_page):
        raise ValueError("Mismatched order history page.")
    total, pages = value["total_items"], value["total_pages"]
    if type(total) is not int or type(pages) is not int or total < 0 or pages != (total + per_page - 1) // per_page:
        raise ValueError("Invalid order history totals.")
    if not isinstance(value["items"], list) or len(value["items"]) != max(0, min(per_page, total - (page - 1) * per_page)):
        raise ValueError("Invalid order history page size.")
    items = [order_record(item) for item in value["items"]]
    if len({item.id for item in items}) != len(items):
        raise ValueError("Duplicate orders.")
    return items, total, pages


async def bounded_read(request: Callable[[], Awaitable[Any]], *, sleep=asyncio.sleep) -> Any:
    """At most one retry, only for a usable Retry-After up to 30 seconds."""
    try:
        return await request()
    except urllib.error.HTTPError as error:
        if error.code != 429:
            raise
        try:
            delay = float(error.headers.get("Retry-After", ""))
        except (TypeError, ValueError, AttributeError):
            raise error
        if not math.isfinite(delay) or not 0 <= delay <= 30:
            raise error
        error.close()
        await sleep(delay)
    return await request()
