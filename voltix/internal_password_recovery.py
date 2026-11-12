"""Strict contracts and payload builders for internal password recovery."""

from typing import Any

from .internal_users import (
    EMAIL_PATTERN,
    PASSWORD_MIN_LENGTH,
    password_rules,
)

_EMAIL_MAX_LENGTH = 254
_TOKEN_MAX_LENGTH = 128
_TOKEN_MIN_LENGTH = 16


def _email(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("Invalid recovery email.")
    mail = value.strip().lower()
    if len(mail) > _EMAIL_MAX_LENGTH or not EMAIL_PATTERN.fullmatch(mail):
        raise ValueError("Invalid recovery email.")
    return mail


def _token(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("Invalid recovery token.")
    token = value.strip()
    if len(token) < _TOKEN_MIN_LENGTH or len(token) > _TOKEN_MAX_LENGTH:
        raise ValueError("Invalid recovery token.")
    if any(character.isspace() for character in token):
        raise ValueError("Invalid recovery token.")
    return token


def recovery_email_payload(email: Any) -> dict:
    return {"email": _email(email)}


def recovery_confirm_payload(email: Any, token: Any, password: Any,
                             confirm_password: Any) -> dict:
    password_value = password_rules(password)
    if not isinstance(confirm_password, str) or password_value != confirm_password.strip():
        raise ValueError("Password confirmation does not match.")
    return {
        "email": _email(email),
        "token": _token(token),
        "password": password_value,
        "confirm_password": password_value,
    }


def recovery_request_result(payload: Any) -> str:
    """Validate the generic acknowledgement; never echo provider content."""
    if not isinstance(payload, dict):
        raise ValueError("Invalid recovery response.")
    message = payload.get("message")
    if not isinstance(message, str) or not message.strip():
        raise ValueError("Invalid recovery response.")
    return "Se o e-mail estiver cadastrado, enviaremos as instruções."


def recovery_confirm_result(payload: Any) -> bool:
    if not isinstance(payload, dict):
        raise ValueError("Invalid confirmation response.")
    return payload.get("updated") is True
