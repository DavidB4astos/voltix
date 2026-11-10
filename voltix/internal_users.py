"""Strict contracts and payload builders for internal user management."""

import re
from dataclasses import dataclass
from typing import Any

from .internal_customers import customer_date_display

ROLES = frozenset({"FUNCIONARIO", "ADMINISTRADOR"})
STATUSES = frozenset({"ATIVO", "INATIVO"})
EMAIL_PATTERN = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
PASSWORD_MIN_LENGTH = 8
_NAME_MAX_LENGTH = 300
_EMAIL_MAX_LENGTH = 254
_USER_FIELDS = frozenset({"id", "name", "email", "role", "status", "created_at"})


@dataclass
class InternalUserEntry:
    id: int
    name: str
    email: str
    role: str
    status: str
    created_at_display: str
    created_at: str = ""


def _positive_id(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError("Invalid internal user id.")
    return value


def _name(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("Invalid internal user name.")
    text = value.strip()
    if not text or len(text) > _NAME_MAX_LENGTH:
        raise ValueError("Invalid internal user name.")
    return text


def _email(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("Invalid internal user email.")
    mail = value.strip().lower()
    if len(mail) > _EMAIL_MAX_LENGTH or not EMAIL_PATTERN.fullmatch(mail):
        raise ValueError("Invalid internal user email.")
    return mail


def _password(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("Invalid password.")
    password = value.strip()
    if (
        len(password) < PASSWORD_MIN_LENGTH
        or not re.search(r"[A-Za-z]", password)
        or not re.search(r"[0-9]", password)
    ):
        raise ValueError("Password must contain at least 8 characters, a letter and a digit.")
    return password


def _role(value: Any) -> str:
    if not isinstance(value, str) or value.strip() not in ROLES:
        raise ValueError("Invalid internal user role.")
    return value.strip()


def _status(value: Any) -> str:
    if not isinstance(value, str) or value.strip() not in STATUSES:
        raise ValueError("Invalid internal user status.")
    return value.strip()


def internal_user_record(payload: Any, *, detail: bool = False) -> InternalUserEntry:
    """Parse the management allowlist and reject unexpected sensitive fields."""
    if not isinstance(payload, dict):
        raise ValueError("Internal user response must be an object.")
    expected = _USER_FIELDS
    if set(payload) - expected:
        raise ValueError("Unexpected internal user field.")
    created_at = payload.get("created_at")
    if detail and created_at is None:
        raise ValueError("Missing internal user creation date.")
    return InternalUserEntry(
        id=_positive_id(payload.get("id")),
        name=_name(payload.get("name")),
        email=_email(payload.get("email")),
        role=_role(payload.get("role")),
        status=_status(payload.get("status")),
        created_at="" if created_at is None else str(created_at),
        created_at_display=(
            customer_date_display(created_at)
            if isinstance(created_at, (int, float, str)) and created_at != ""
            else ""
        ),
    )


def internal_user_list(payload: Any) -> list[InternalUserEntry]:
    if not isinstance(payload, list):
        raise ValueError("Internal user list must be an array.")
    return [internal_user_record(item, detail=True) for item in payload]


def user_create_payload(name: str, email: str, password: str, role: str) -> dict:
    return {
        "name": _name(name),
        "email": _email(email),
        "password": _password(password),
        "role": _role(role),
    }


def user_update_payload(
    name: str,
    email: str,
    role: str,
    status: str,
    *,
    current_name: str,
    current_email: str,
    current_role: str,
    current_status: str,
) -> dict:
    """Build a partial administrative update using only changed known fields."""
    for value in (name, email, role, status, current_name, current_email,
                  current_role, current_status):
        if not isinstance(value, str):
            raise ValueError("Invalid internal user update input.")
    payload: dict[str, str] = {}
    clean_name = name.strip()
    if clean_name and clean_name != current_name.strip():
        payload["name"] = _name(clean_name)
    clean_email = email.strip().lower()
    if clean_email and clean_email != current_email.strip().lower():
        payload["email"] = _email(clean_email)
    clean_role = role.strip()
    if clean_role and clean_role != current_role:
        payload["role"] = _role(clean_role)
    clean_status = status.strip()
    if clean_status and clean_status != current_status:
        payload["status"] = _status(clean_status)
    return payload


def profile_update_payload(
    name: str,
    email: str,
    *,
    current_name: str,
    current_email: str,
) -> dict:
    """Build a self-profile update; role, status and password are not accepted."""
    for value in (name, email, current_name, current_email):
        if not isinstance(value, str):
            raise ValueError("Invalid profile update input.")
    payload: dict[str, str] = {}
    clean_name = name.strip()
    if clean_name and clean_name != current_name.strip():
        payload["name"] = _name(clean_name)
    clean_email = email.strip().lower()
    if clean_email and clean_email != current_email.strip().lower():
        payload["email"] = _email(clean_email)
    return payload


def password_change_payload(
    current_password: str,
    new_password: str,
    confirm_password: str,
) -> dict:
    if not isinstance(current_password, str) or not current_password:
        raise ValueError("Current password is required.")
    password = _password(new_password)
    if not isinstance(confirm_password, str) or password != confirm_password.strip():
        raise ValueError("Password confirmation does not match.")
    if password == current_password.strip():
        raise ValueError("The new password must differ from the current password.")
    return {
        "current_password": current_password,
        "new_password": password,
        "confirm_password": password,
    }


def user_status_payload(status: str) -> dict:
    return {"status": _status(status)}


def role_label(role: str) -> str:
    return "Administrador" if role == "ADMINISTRADOR" else "Funcionário"


def status_label(status: str) -> str:
    return "Ativo" if status == "ATIVO" else "Inativo"
