"""Strict, read-only contract for the internal CRM dashboard snapshot."""

from dataclasses import dataclass
from typing import Any

from .internal_attendances import ATTENDANCE_STATUSES, Attendance
from .internal_sales import SalesDashboard


CRM_STATUS_ORDER = ("ABERTO", "EM_ATENDIMENTO", "FINALIZADO")

CRM_STATUS_LABELS = {
    "ABERTO": "Aberto",
    "EM_ATENDIMENTO": "Em atendimento",
    "FINALIZADO": "Finalizado",
    "CANCELADO": "Cancelado",
}

MAX_RECENT_ATTENDANCES = 10


@dataclass
class CrmDashboard:
    clientes_ativos: int
    atendimentos_abertos: int
    atendimentos_em_atendimento: int
    atendimentos_finalizados: int
    atendimentos_total: int
    pedidos_total: int
    recentes: list[Attendance]
    faturamento: str
    vendas_pedidos: int
    ticket_medio: str
    vendas_periodo_display: str


def _count(value: Any, field: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"Invalid {field} total.")
    return value


def crm_dashboard(
    *,
    clientes_ativos: Any,
    atendimentos_por_status: Any,
    atendimentos_total: Any,
    pedidos_total: Any,
    recentes: Any,
    vendas: Any,
) -> CrmDashboard:
    """Validate the CRM snapshot from already parsed, sanitized reads."""

    clientes_ativos = _count(clientes_ativos, "active customers")
    atendimentos_total = _count(atendimentos_total, "attendances")
    pedidos_total = _count(pedidos_total, "orders")
    if not isinstance(atendimentos_por_status, dict):
        raise ValueError("Invalid attendance status totals.")
    if set(atendimentos_por_status) != set(CRM_STATUS_ORDER):
        raise ValueError("Invalid attendance status totals.")
    counts = {
        status: _count(atendimentos_por_status[status], f"attendance {status}")
        for status in CRM_STATUS_ORDER
    }
    if not isinstance(recentes, list):
        raise ValueError("Invalid recent attendances.")
    if len(recentes) > MAX_RECENT_ATTENDANCES:
        raise ValueError("Too many recent attendances.")
    if any(not isinstance(item, Attendance) for item in recentes):
        raise ValueError("Invalid recent attendances.")
    if any(item.status not in ATTENDANCE_STATUSES for item in recentes):
        raise ValueError("Invalid recent attendance status.")
    if len({item.id for item in recentes}) != len(recentes):
        raise ValueError("Duplicate recent attendances.")
    if len(recentes) > atendimentos_total:
        raise ValueError("Recent attendances exceed the total.")
    if not isinstance(vendas, SalesDashboard):
        raise ValueError("Invalid sales summary.")
    return CrmDashboard(
        clientes_ativos=clientes_ativos,
        atendimentos_abertos=counts["ABERTO"],
        atendimentos_em_atendimento=counts["EM_ATENDIMENTO"],
        atendimentos_finalizados=counts["FINALIZADO"],
        atendimentos_total=atendimentos_total,
        pedidos_total=pedidos_total,
        recentes=recentes,
        faturamento=vendas.faturamento,
        vendas_pedidos=vendas.pedidos,
        ticket_medio=vendas.ticket_medio,
        vendas_periodo_display=vendas.periodo_display,
    )
