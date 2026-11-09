"""Strict, sanitized contract for internal sales dashboard reads."""

import math
import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any

STATUS_INCLUDED = (
    "PAGAMENTO_CONFIRMADO",
    "EM_PREPARACAO",
    "ENVIADO",
    "ENTREGUE",
)

STATUS_LABELS = {
    "PAGAMENTO_CONFIRMADO": "Pagamento confirmado",
    "EM_PREPARACAO": "Em preparação",
    "ENVIADO": "Enviado",
    "ENTREGUE": "Entregue",
}

PERIOD_FIELDS = frozenset({"inicio", "fim", "timezone"})
DASHBOARD_FIELDS = frozenset({
    "periodo",
    "faturamento",
    "pedidos",
    "ticket_medio",
    "status_incluidos",
    "serie_diaria",
})
DAILY_FIELDS = frozenset({"data", "faturamento", "pedidos"})

CENT = Decimal("0.01")
MAX_PERIOD_DAYS = 366


@dataclass
class DailySales:
    data: str
    data_display: str
    faturamento: str
    pedidos: int


@dataclass
class SalesDashboard:
    periodo_inicio: str
    periodo_fim: str
    periodo_timezone: str
    periodo_display: str
    faturamento: str
    pedidos: int
    ticket_medio: str
    status_incluidos_display: str
    serie_diaria: list[DailySales]


def _day(value: Any, field: str) -> tuple[str, date]:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError(f"Invalid {field} date.")
    try:
        return value, date.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f"Invalid {field} date.") from error


def _money(value: Any, field: str) -> str:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise ValueError(f"Invalid {field}.")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"Invalid {field}.")
    text = value.strip() if isinstance(value, str) else str(value)
    try:
        amount = Decimal(text)
    except InvalidOperation as error:
        raise ValueError(f"Invalid {field}.") from error
    if not amount.is_finite() or amount < 0:
        raise ValueError(f"Invalid {field}.")
    return str(amount.quantize(CENT, rounding=ROUND_HALF_UP))


def _count(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"Invalid {field}.")
    return value


def dashboard_filters(from_value: Any, to_value: Any) -> dict:
    if from_value is not None and not isinstance(from_value, str):
        raise ValueError("Invalid dashboard filters.")
    if to_value is not None and not isinstance(to_value, str):
        raise ValueError("Invalid dashboard filters.")
    start_text = (from_value or "").strip()
    end_text = (to_value or "").strip()
    start_day = end_day = None
    parameters = {}
    if start_text:
        start_text, start_day = _day(start_text, "start")
        parameters["from"] = start_text
    if end_text:
        end_text, end_day = _day(end_text, "end")
        parameters["to"] = end_text
    if start_day is not None and end_day is not None:
        if start_day > end_day or (end_day - start_day).days > MAX_PERIOD_DAYS - 1:
            raise ValueError("Invalid dashboard period.")
    return parameters


def _period(value: Any) -> tuple[str, str, date, date]:
    if not isinstance(value, dict) or set(value) != PERIOD_FIELDS:
        raise ValueError("Invalid dashboard period.")
    if value["timezone"] != "UTC":
        raise ValueError("Invalid dashboard period.")
    start_text, start_day = _day(value["inicio"], "start")
    end_text, end_day = _day(value["fim"], "end")
    if start_day > end_day or (end_day - start_day).days > MAX_PERIOD_DAYS - 1:
        raise ValueError("Invalid dashboard period.")
    return start_text, end_text, start_day, end_day


def sales_dashboard(value: Any) -> SalesDashboard:
    if not isinstance(value, dict) or set(value) != DASHBOARD_FIELDS:
        raise ValueError("Invalid sales dashboard.")
    start_text, end_text, start_day, end_day = _period(value["periodo"])
    statuses = value["status_incluidos"]
    if not isinstance(statuses, list) or tuple(statuses) != STATUS_INCLUDED:
        raise ValueError("Invalid dashboard statuses.")
    revenue = _money(value["faturamento"], "revenue")
    orders = _count(value["pedidos"], "orders")
    ticket = _money(value["ticket_medio"], "average ticket")
    entries = value["serie_diaria"]
    if not isinstance(entries, list):
        raise ValueError("Invalid dashboard series.")

    series = []
    previous_day = None
    series_orders = 0
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != DAILY_FIELDS:
            raise ValueError("Invalid dashboard series.")
        data_text, data_day = _day(entry["data"], "series")
        if data_day < start_day or data_day > end_day:
            raise ValueError("Invalid dashboard series.")
        if previous_day is not None and data_day <= previous_day:
            raise ValueError("Invalid dashboard series.")
        previous_day = data_day
        day_revenue = _money(entry["faturamento"], "series revenue")
        day_orders = _count(entry["pedidos"], "series orders")
        if day_orders < 1:
            raise ValueError("Invalid dashboard series.")
        series_orders += day_orders
        series.append(DailySales(data_text, data_day.strftime("%d/%m/%Y"),
                                 day_revenue, day_orders))

    if orders == 0:
        if revenue != "0.00" or ticket != "0.00" or series:
            raise ValueError("Invalid empty dashboard.")
    else:
        if not series or series_orders != orders:
            raise ValueError("Inconsistent dashboard series.")
        expected = (Decimal(revenue) / orders).quantize(CENT, rounding=ROUND_HALF_UP)
        if abs(Decimal(ticket) - expected) > CENT:
            raise ValueError("Inconsistent average ticket.")

    return SalesDashboard(
        start_text,
        end_text,
        "UTC",
        f"{start_day.strftime('%d/%m/%Y')} a {end_day.strftime('%d/%m/%Y')} (UTC)",
        revenue,
        orders,
        ticket,
        ", ".join(STATUS_LABELS[status] for status in STATUS_INCLUDED),
        series,
    )
