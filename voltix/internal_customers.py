"""Strict, sanitized contract for internal customer reads."""

import asyncio
import math
import re
import urllib.error
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable


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
