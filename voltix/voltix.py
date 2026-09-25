"""Voltix Reflex application."""

import asyncio
import json
import os
import urllib.error
import urllib.request
from typing import Any

import reflex as rx

from rxconfig import config


XANO_HEALTH_URL_ENV = "XANO_HEALTH_URL"
XANO_LOGIN_URL_ENV = "XANO_LOGIN_URL"
XANO_ME_URL_ENV = "XANO_ME_URL"
XANO_INTERNAL_ACCESS_URL_ENV = "XANO_INTERNAL_ACCESS_URL"


def _required_environment_url(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required environment variable: {name}.")
    return value


def _request_xano_json(
    url: str,
    *,
    method: str = "GET",
    payload: dict[str, object] | None = None,
    authorization: str | None = None,
) -> dict[str, object]:
    headers = {"Accept": "application/json"}
    body = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(payload).encode("utf-8")
    if authorization:
        headers["Authorization"] = authorization

    request = urllib.request.Request(
        url,
        data=body,
        headers=headers,
        method=method,
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        if response.status < 200 or response.status >= 300:
            raise ValueError(f"Xano returned unexpected HTTP status {response.status}.")
        response_payload = json.loads(response.read().decode("utf-8"))

    if not isinstance(response_payload, dict):
        raise ValueError("Xano response must be a JSON object.")
    return response_payload


async def _server_side_xano_request(
    url: str,
    *,
    method: str = "GET",
    payload: dict[str, object] | None = None,
    authorization: str | None = None,
) -> dict[str, object]:
    return await asyncio.to_thread(
        _request_xano_json,
        url,
        method=method,
        payload=payload,
        authorization=authorization,
    )


def _request_xano_health(url: str) -> dict[str, str]:
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json"},
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        if response.status < 200 or response.status >= 300:
            raise ValueError(f"Xano returned unexpected HTTP status {response.status}.")
        payload = json.loads(response.read().decode("utf-8"))

    if not isinstance(payload, dict):
        raise ValueError("Xano health response must be a JSON object.")

    expected_payload = {
        "status": "ok",
        "service": "voltix-xano",
        "integration": "available",
    }
    if payload != expected_payload:
        raise ValueError("Xano health response does not match the expected contract.")
    return expected_payload


class State(rx.State):
    integration_loading: bool = False
    integration_status: str = "idle"
    integration_message: str = "Integration check has not run."
    integration_payload: str = ""
    login_loading: bool = False
    login_status: str = "idle"
    login_message: str = ""
    is_authenticated: bool = False
    user_id: int | None = None
    user_name: str = ""
    user_email: str = ""
    user_role: str = ""
    user_status: str = ""
    session_status: str = "idle"
    session_message: str = ""
    _auth_token: str = ""

    def _clear_authentication_state(
        self,
        message: str,
        *,
        session_status: str = "error",
    ):
        self._auth_token = ""
        self.is_authenticated = False
        self.user_id = None
        self.user_name = ""
        self.user_email = ""
        self.user_role = ""
        self.user_status = ""
        self.login_loading = False
        self.login_status = "idle"
        self.login_message = ""
        self.session_status = session_status
        self.session_message = message

    @rx.event
    async def login(self, email: str, password: str):
        self.login_loading = True
        self.login_status = "loading"
        self.login_message = ""
        self.is_authenticated = False
        self.user_id = None
        self._auth_token = ""

        try:
            login_url = _required_environment_url(XANO_LOGIN_URL_ENV)
            response = await _server_side_xano_request(
                login_url,
                method="POST",
                payload={"email": email, "password": password},
            )
            auth_token = response.get("authToken")
            response_user_id = response.get("user_id")
            if (
                not isinstance(auth_token, str)
                or not auth_token.strip()
                or not isinstance(response_user_id, int)
            ):
                raise ValueError("Invalid login response.")
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
            self.login_loading = False
            self.login_status = "error"
            self.login_message = "Não foi possível autenticar. Verifique suas credenciais."
            self.is_authenticated = False
            self.user_id = None
            self._auth_token = ""
            return

        self.login_loading = False
        self.login_status = "success"
        self.login_message = "Autenticação realizada com sucesso."
        self.is_authenticated = True
        self.user_id = response_user_id
        self._auth_token = auth_token.strip()

    @rx.event
    async def submit_login(self, form_data: dict[str, Any]):
        email = form_data.get("email", "").strip()
        password = form_data.get("password", "")
        if not email or not password:
            self.login_loading = False
            self.login_status = "error"
            self.login_message = "Informe e-mail e senha."
            return
        await self.login(email, password)

    @rx.event
    async def validate_session(self):
        if not self._auth_token:
            self._clear_authentication_state(
                "Não foi possível validar a sessão."
            )
            return

        self.session_status = "loading"
        self.session_message = ""

        try:
            me_url = _required_environment_url(XANO_ME_URL_ENV)
            authorization = "Bearer " + self._auth_token
            identity_response = await _server_side_xano_request(
                me_url,
                method="GET",
                authorization=authorization,
            )
            identity_id = identity_response.get("id")
            identity_name = identity_response.get("name")
            identity_email = identity_response.get("email")
            identity_role = identity_response.get("role")
            identity_status = identity_response.get("status")
            if (
                not isinstance(identity_id, int)
                or isinstance(identity_id, bool)
                or not isinstance(identity_name, str)
                or not identity_name
                or not isinstance(identity_email, str)
                or not identity_email
                or identity_role not in {"FUNCIONARIO", "ADMINISTRADOR"}
                or identity_status != "ATIVO"
            ):
                raise ValueError("Invalid authenticated identity response.")

            internal_access_url = _required_environment_url(
                XANO_INTERNAL_ACCESS_URL_ENV
            )
            access_response = await _server_side_xano_request(
                internal_access_url,
                method="GET",
                authorization=authorization,
            )
            if access_response.get("authorized") is not True:
                raise ValueError("Internal access was not authorized.")
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ):
            self._clear_authentication_state(
                "Não foi possível validar a sessão."
            )
            return

        self.user_id = identity_id
        self.user_name = identity_name
        self.user_email = identity_email
        self.user_role = identity_role
        self.user_status = identity_status
        self.is_authenticated = True
        self.session_status = "success"
        self.session_message = "Sessão validada com sucesso."

    @rx.event
    async def enter_internal_area(self):
        await self.validate_session()

    @rx.event
    async def logout(self):
        self._clear_authentication_state(
            "Sess\u00e3o encerrada.",
            session_status="idle",
        )

    @rx.event
    async def check_integration(self):
        self.integration_loading = True
        self.integration_status = "loading"
        self.integration_message = "Checking the Reflex-Xano integration..."
        self.integration_payload = ""

        health_url = os.getenv(XANO_HEALTH_URL_ENV, "").strip()
        if not health_url:
            self.integration_loading = False
            self.integration_status = "error"
            self.integration_message = (
                f"Missing required environment variable: {XANO_HEALTH_URL_ENV}."
            )
            return

        try:
            payload = await asyncio.to_thread(_request_xano_health, health_url)
        except urllib.error.HTTPError as error:
            self.integration_loading = False
            self.integration_status = "error"
            self.integration_message = (
                f"Xano health check failed with HTTP status {error.code}."
            )
            return
        except urllib.error.URLError as error:
            self.integration_loading = False
            self.integration_status = "error"
            self.integration_message = f"Xano health check could not reach the backend: {error.reason}."
            return
        except (TimeoutError, ValueError, json.JSONDecodeError) as error:
            self.integration_loading = False
            self.integration_status = "error"
            self.integration_message = f"Xano health check failed: {error}"
            return

        self.integration_loading = False
        self.integration_status = "success"
        self.integration_message = "Reflex-Xano integration is available."
        self.integration_payload = json.dumps(payload, sort_keys=True)


def index() -> rx.Component:
    protected_area = rx.cond(
        (State.is_authenticated) & (State.session_status == "success"),
        rx.vstack(
            rx.heading("Voltix", size="8"),
            rx.text("\u00c1rea interna", size="5"),
            rx.text("Acesso autorizado.", color="green"),
            rx.text(State.user_name),
            rx.text(State.user_email),
            rx.text(State.user_role),
            rx.text(State.user_status),
            rx.button(
                "Sair",
                on_click=State.logout,
            ),
            spacing="3",
            align="center",
        ),
        rx.fragment(),
    )

    return rx.container(
        rx.vstack(
            rx.heading("Voltix", size="8"),
            rx.text("Acesso interno", size="5"),
            rx.text(
                "Entre com as credenciais do seu usuário interno.",
                color="gray",
            ),
            rx.form(
                rx.vstack(
                    rx.input(
                        name="email",
                        type="email",
                        placeholder="E-mail",
                        required=True,
                        width="100%",
                    ),
                    rx.input(
                        name="password",
                        type="password",
                        placeholder="Senha",
                        required=True,
                        width="100%",
                    ),
                    rx.button(
                        rx.cond(State.login_loading, "Entrando...", "Entrar"),
                        type="submit",
                        disabled=State.login_loading,
                        width="100%",
                    ),
                    width="100%",
                    spacing="4",
                ),
                on_submit=State.submit_login,
                width="100%",
            ),
            rx.cond(
                State.login_status != "idle",
                rx.text(State.login_message),
                rx.fragment(),
            ),
            rx.cond(
                (State.login_status == "success")
                & (State.session_status != "success"),
                rx.button(
                    "Acessar área interna",
                    on_click=State.enter_internal_area,
                ),
                rx.fragment(),
            ),
            protected_area,
            align="center",
            justify="center",
            spacing="5",
            width="100%",
            max_width="28rem",
            min_height="100vh",
        ),
        padding="4",
    )


app = rx.App()
app.add_page(index)
