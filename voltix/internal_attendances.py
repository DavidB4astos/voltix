"""Strict, sanitized contract for internal attendance operations."""

import math
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .internal_customers import customer_date_display, positive_int


ATTENDANCE_STATUSES = frozenset({
    "ABERTO",
    "EM_ATENDIMENTO",
    "FINALIZADO",
    "CANCELADO",
})

ATTENDANCE_FIELDS = frozenset({
    "id",
    "cliente_id",
    "usuario_interno_id",
    "pedido_id",
    "assunto",
    "descricao",
    "status",
    "data_atendimento",
    "created_at",
    "updated_at",
})


@dataclass
class Attendance:
    id: int
    cliente_id: int
    usuario_interno_id: int
    pedido_id: int | None
    cliente_display: str
    pedido_display: str
    responsavel_display: str
    assunto: str
    descricao: str
    status: str
    data_atendimento: str
    data_atendimento_display: str
    data_atendimento_input: str
    created_at: str
    created_at_display: str
    updated_at: str
    updated_at_display: str


@dataclass
class AttendanceStatusResult:
    atendimento_id: int
    status_anterior: str
    status_atual: str
    alterado: bool


def _text(value: Any, field: str, *, maximum: int) -> str:
    if not isinstance(value, str):
        raise ValueError(f"Invalid attendance {field}.")
    text = value.strip()
    if not text or len(text) > maximum:
        raise ValueError(f"Invalid attendance {field}.")
    return text


def _date(value: Any, field: str) -> tuple[str, str]:
    if value is None:
        return "", "Data indisponível"
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise ValueError(f"Invalid attendance {field}.")
    if isinstance(value, (int, float)) and not math.isfinite(value):
        raise ValueError(f"Invalid attendance {field}.")
    raw = str(value)
    return raw, customer_date_display(value)


def datetime_local_value(value: Any) -> str:
    """Render an Xano/ISO timestamp as a datetime-local value in UTC."""
    try:
        if isinstance(value, bool) or value is None:
            return ""
        if isinstance(value, (int, float)) or re.fullmatch(r"-?\d+(?:\.\d+)?", str(value)):
            date = datetime.fromtimestamp(float(value) / 1000, tz=timezone.utc)
        else:
            date = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            if date.tzinfo is None:
                date = date.replace(tzinfo=timezone.utc)
            date = date.astimezone(timezone.utc)
        return date.strftime("%Y-%m-%dT%H:%M")
    except (ValueError, OverflowError, OSError):
        return ""


def attendance_filters(cliente_id: int | None, status: str, page: int,
                       per_page: int = 20) -> dict:
    if cliente_id is not None:
        cliente_id = positive_int(cliente_id)
    if status not in ATTENDANCE_STATUSES | {"TODOS"}:
        raise ValueError("Invalid attendance status.")
    parameters = {
        "status": status,
        "page": positive_int(page),
        "per_page": positive_int(per_page, 50),
    }
    if cliente_id is not None:
        parameters["cliente_id"] = cliente_id
    return parameters


def attendance_record(value: Any) -> Attendance:
    if not isinstance(value, dict) or set(value) != ATTENDANCE_FIELDS:
        raise ValueError("Invalid attendance record.")
    status = value["status"]
    if status not in ATTENDANCE_STATUSES:
        raise ValueError("Invalid attendance status.")
    pedido_id = value["pedido_id"]
    if pedido_id is not None:
        pedido_id = positive_int(pedido_id)
    record_id = positive_int(value["id"])
    cliente_id = positive_int(value["cliente_id"])
    usuario_interno_id = positive_int(value["usuario_interno_id"])
    data_raw, data_display = _date(value["data_atendimento"], "date")
    created_raw, created_display = _date(value["created_at"], "created date")
    updated_raw, updated_display = _date(value["updated_at"], "updated date")
    return Attendance(
        record_id,
        cliente_id,
        usuario_interno_id,
        pedido_id,
        f"Cliente #{cliente_id}",
        f"Pedido #{pedido_id}" if pedido_id is not None else "Sem pedido",
        f"Responsável #{usuario_interno_id}",
        _text(value["assunto"], "subject", maximum=200),
        _text(value["descricao"], "description", maximum=2000),
        status,
        data_raw,
        data_display,
        datetime_local_value(value["data_atendimento"]),
        created_raw,
        created_display,
        updated_raw,
        updated_display,
    )


def attendance_page(value: Any, *, page: int,
                    per_page: int = 20) -> tuple[list[Attendance], int, int]:
    expected = {"items", "page", "per_page", "total_items", "total_pages"}
    if not isinstance(value, dict) or set(value) != expected:
        raise ValueError("Invalid attendance page.")
    if (type(value["page"]) is not int or type(value["per_page"]) is not int
            or value["page"] != page or value["per_page"] != per_page):
        raise ValueError("Mismatched attendance page.")
    total, pages = value["total_items"], value["total_pages"]
    if type(total) is not int or type(pages) is not int or total < 0 or pages != (total + per_page - 1) // per_page:
        raise ValueError("Invalid attendance totals.")
    if not isinstance(value["items"], list) or len(value["items"]) != max(0, min(per_page, total - (page - 1) * per_page)):
        raise ValueError("Invalid attendance page size.")
    items = [attendance_record(item) for item in value["items"]]
    if len({item.id for item in items}) != len(items):
        raise ValueError("Duplicate attendances.")
    return items, total, pages


def status_result(value: Any) -> AttendanceStatusResult:
    if not isinstance(value, dict) or set(value) != {
            "atendimento_id", "status_anterior", "status_atual", "alterado"}:
        raise ValueError("Invalid attendance status result.")
    if value["status_anterior"] not in ATTENDANCE_STATUSES or value["status_atual"] not in ATTENDANCE_STATUSES:
        raise ValueError("Invalid attendance status result.")
    if type(value["alterado"]) is not bool:
        raise ValueError("Invalid attendance status result.")
    return AttendanceStatusResult(
        positive_int(value["atendimento_id"]),
        value["status_anterior"],
        value["status_atual"],
        value["alterado"],
    )
