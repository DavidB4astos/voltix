"""Voltix Reflex application."""

import asyncio
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

import reflex as rx
from dotenv import load_dotenv

from rxconfig import config


load_dotenv()

XANO_HEALTH_URL_ENV = "XANO_HEALTH_URL"
XANO_LOGIN_URL_ENV = "XANO_LOGIN_URL"
XANO_ME_URL_ENV = "XANO_ME_URL"
XANO_INTERNAL_ACCESS_URL_ENV = "XANO_INTERNAL_ACCESS_URL"
XANO_CATEGORIES_URL_ENV = "XANO_CATEGORIES_URL"
XANO_BRANDS_URL_ENV = "XANO_BRANDS_URL"

XanoJson = dict[str, object] | list[dict[str, object]]


@dataclass(frozen=True)
class CatalogEntry:
    id: int
    name: str
    description: str
    status: str


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
) -> XanoJson:
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

    if isinstance(response_payload, dict):
        return response_payload
    if isinstance(response_payload, list) and all(
        isinstance(item, dict) for item in response_payload
    ):
        return [dict(item) for item in response_payload]
    raise ValueError("Xano response must be a JSON object or a list of objects.")


async def _server_side_xano_request(
    url: str,
    *,
    method: str = "GET",
    payload: dict[str, object] | None = None,
    authorization: str | None = None,
) -> XanoJson:
    return await asyncio.to_thread(
        _request_xano_json,
        url,
        method=method,
        payload=payload,
        authorization=authorization,
    )


def _catalog_entry(payload: object) -> CatalogEntry:
    if not isinstance(payload, dict):
        raise ValueError("Catalog response must be an object.")

    record_id = payload.get("id")
    name = payload.get("name")
    description = payload.get("description")
    status = payload.get("status")
    if (
        not isinstance(record_id, int)
        or isinstance(record_id, bool)
        or not isinstance(name, str)
        or not name.strip()
        or (description is not None and not isinstance(description, str))
        or status not in {"ATIVO", "INATIVO"}
    ):
        raise ValueError("Catalog response has an invalid record.")

    return CatalogEntry(
        id=record_id,
        name=name,
        description=description or "",
        status=status,
    )


def _catalog_entries(payload: XanoJson) -> list[CatalogEntry]:
    if not isinstance(payload, list):
        raise ValueError("Catalog list response must be an array.")
    return [_catalog_entry(item) for item in payload]


def _catalog_failure_message(error: Exception) -> str:
    if isinstance(error, urllib.error.HTTPError):
        if error.code in {401, 403}:
            return "Você não tem autorização para essa operação."
        if error.code == 400:
            return "Os dados foram rejeitados. Verifique o nome e tente novamente."
    return "Não foi possível concluir a operação. Tente novamente."


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
    categories: list[CatalogEntry] = []
    categories_loading: bool = False
    categories_message: str = ""
    category_form_name: str = ""
    category_form_description: str = ""
    category_editing_id: int | None = None
    brands: list[CatalogEntry] = []
    brands_loading: bool = False
    brands_message: str = ""
    brand_form_name: str = ""
    brand_form_description: str = ""
    brand_editing_id: int | None = None

    def _clear_catalog_state(self):
        self.categories = []
        self.categories_loading = False
        self.categories_message = ""
        self.category_form_name = ""
        self.category_form_description = ""
        self.category_editing_id = None
        self.brands = []
        self.brands_loading = False
        self.brands_message = ""
        self.brand_form_name = ""
        self.brand_form_description = ""
        self.brand_editing_id = None

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
        self._clear_catalog_state()

    async def _catalog_request(
        self,
        collection_url_env: str,
        *,
        method: str = "GET",
        record_id: int | None = None,
        payload: dict[str, object] | None = None,
    ) -> XanoJson:
        if (
            not self._auth_token
            or not self.is_authenticated
            or self.session_status != "success"
            or self.user_role != "ADMINISTRADOR"
            or self.user_status != "ATIVO"
        ):
            raise ValueError("Administrator session is required.")

        url = _required_environment_url(collection_url_env).rstrip("/")
        if record_id is not None:
            url = f"{url}/{record_id}"
        return await _server_side_xano_request(
            url,
            method=method,
            payload=payload,
            authorization="Bearer " + self._auth_token,
        )

    async def _fetch_catalog_entries(
        self,
        collection_url_env: str,
    ) -> list[CatalogEntry]:
        return _catalog_entries(
            await self._catalog_request(collection_url_env)
        )

    async def _load_categories(self):
        self.categories_loading = True
        self.categories_message = ""
        try:
            self.categories = await self._fetch_catalog_entries(
                XANO_CATEGORIES_URL_ENV
            )
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ) as error:
            self.categories_message = _catalog_failure_message(error)
        finally:
            self.categories_loading = False

    async def _load_brands(self):
        self.brands_loading = True
        self.brands_message = ""
        try:
            self.brands = await self._fetch_catalog_entries(XANO_BRANDS_URL_ENV)
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ) as error:
            self.brands_message = _catalog_failure_message(error)
        finally:
            self.brands_loading = False

    @rx.event
    async def load_categories(self):
        await self._load_categories()

    @rx.event
    async def load_brands(self):
        await self._load_brands()

    @rx.event
    def set_category_form_name(self, value: str):
        self.category_form_name = value

    @rx.event
    def set_category_form_description(self, value: str):
        self.category_form_description = value

    @rx.event
    def set_brand_form_name(self, value: str):
        self.brand_form_name = value

    @rx.event
    def set_brand_form_description(self, value: str):
        self.brand_form_description = value

    def _edit_catalog_entry(
        self,
        entries: list[CatalogEntry],
        record_id: int,
        *,
        is_category: bool,
    ):
        entry = next((item for item in entries if item.id == record_id), None)
        if entry is None:
            return
        if is_category:
            self.category_editing_id = entry.id
            self.category_form_name = entry.name
            self.category_form_description = entry.description
            self.categories_message = ""
        else:
            self.brand_editing_id = entry.id
            self.brand_form_name = entry.name
            self.brand_form_description = entry.description
            self.brands_message = ""

    @rx.event
    def edit_category(self, record_id: int):
        self._edit_catalog_entry(self.categories, record_id, is_category=True)

    @rx.event
    def edit_brand(self, record_id: int):
        self._edit_catalog_entry(self.brands, record_id, is_category=False)

    @rx.event
    def cancel_category_edit(self):
        self.category_editing_id = None
        self.category_form_name = ""
        self.category_form_description = ""
        self.categories_message = ""

    @rx.event
    def cancel_brand_edit(self):
        self.brand_editing_id = None
        self.brand_form_name = ""
        self.brand_form_description = ""
        self.brands_message = ""

    async def _save_catalog_entry(
        self,
        collection_url_env: str,
        name: str,
        description: str,
        record_id: int | None,
    ):
        clean_name = name.strip()
        if not clean_name:
            raise ValueError("Informe um nome.")

        payload = {"name": clean_name, "description": description.strip()}
        response = await self._catalog_request(
            collection_url_env,
            method="PATCH" if record_id is not None else "POST",
            record_id=record_id,
            payload=payload,
        )
        if not isinstance(response, dict):
            raise ValueError("Catalog mutation response must be an object.")
        _catalog_entry(response)

    @rx.event
    async def save_category(self, form_data: dict[str, Any]):
        self.categories_loading = True
        self.categories_message = ""
        try:
            name = form_data.get("name", "")
            description = form_data.get("description", "")
            if not isinstance(name, str) or not isinstance(description, str):
                raise ValueError("Invalid category form.")
            await self._save_catalog_entry(
                XANO_CATEGORIES_URL_ENV,
                name,
                description,
                self.category_editing_id,
            )
            self.category_editing_id = None
            self.category_form_name = ""
            self.category_form_description = ""
            self.categories_message = "Categoria salva."
            self.categories = await self._fetch_catalog_entries(
                XANO_CATEGORIES_URL_ENV
            )
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ) as error:
            self.categories_message = (
                "Informe um nome para a categoria."
                if isinstance(error, ValueError) and str(error) == "Informe um nome."
                else _catalog_failure_message(error)
            )
        finally:
            self.categories_loading = False

    @rx.event
    async def save_brand(self, form_data: dict[str, Any]):
        self.brands_loading = True
        self.brands_message = ""
        try:
            name = form_data.get("name", "")
            description = form_data.get("description", "")
            if not isinstance(name, str) or not isinstance(description, str):
                raise ValueError("Invalid brand form.")
            await self._save_catalog_entry(
                XANO_BRANDS_URL_ENV,
                name,
                description,
                self.brand_editing_id,
            )
            self.brand_editing_id = None
            self.brand_form_name = ""
            self.brand_form_description = ""
            self.brands_message = "Marca salva."
            self.brands = await self._fetch_catalog_entries(XANO_BRANDS_URL_ENV)
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ) as error:
            self.brands_message = (
                "Informe um nome para a marca."
                if isinstance(error, ValueError) and str(error) == "Informe um nome."
                else _catalog_failure_message(error)
            )
        finally:
            self.brands_loading = False

    async def _set_catalog_status(
        self,
        collection_url_env: str,
        record_id: int,
        status: str,
    ):
        response = await self._catalog_request(
            collection_url_env,
            method="PATCH",
            record_id=record_id,
            payload={"status": status},
        )
        if not isinstance(response, dict):
            raise ValueError("Catalog status response must be an object.")
        _catalog_entry(response)

    @rx.event
    async def toggle_category_status(self, record_id: int):
        entry = next((item for item in self.categories if item.id == record_id), None)
        if entry is None:
            self.categories_message = "Categoria não encontrada. Atualize a lista."
            return

        self.categories_loading = True
        self.categories_message = ""
        try:
            new_status = "INATIVO" if entry.status == "ATIVO" else "ATIVO"
            await self._set_catalog_status(
                XANO_CATEGORIES_URL_ENV,
                record_id,
                new_status,
            )
            self.categories = await self._fetch_catalog_entries(
                XANO_CATEGORIES_URL_ENV
            )
            self.categories_message = "Status da categoria atualizado."
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ) as error:
            self.categories_message = _catalog_failure_message(error)
        finally:
            self.categories_loading = False

    @rx.event
    async def toggle_brand_status(self, record_id: int):
        entry = next((item for item in self.brands if item.id == record_id), None)
        if entry is None:
            self.brands_message = "Marca não encontrada. Atualize a lista."
            return

        self.brands_loading = True
        self.brands_message = ""
        try:
            new_status = "INATIVO" if entry.status == "ATIVO" else "ATIVO"
            await self._set_catalog_status(
                XANO_BRANDS_URL_ENV,
                record_id,
                new_status,
            )
            self.brands = await self._fetch_catalog_entries(XANO_BRANDS_URL_ENV)
            self.brands_message = "Status da marca atualizado."
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ) as error:
            self.brands_message = _catalog_failure_message(error)
        finally:
            self.brands_loading = False

    @rx.event
    async def login(self, email: str, password: str):
        self._clear_catalog_state()
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
            if not isinstance(response, dict):
                raise ValueError("Invalid login response.")
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
            if not isinstance(identity_response, dict):
                raise ValueError("Invalid authenticated identity response.")
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
            if (
                not isinstance(access_response, dict)
                or access_response.get("authorized") is not True
            ):
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
        if (
            self.session_status == "success"
            and self.user_role == "ADMINISTRADOR"
            and self.user_status == "ATIVO"
        ):
            await self._load_categories()
            await self._load_brands()

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
    def catalog_section(
        title: str,
        entries: list[CatalogEntry],
        loading: bool,
        message: str,
        refresh_event: rx.EventHandler,
        form_name: str,
        form_description: str,
        editing_id: int | None,
        name_change_event: rx.EventHandler,
        description_change_event: rx.EventHandler,
        save_event: rx.EventHandler,
        cancel_event: rx.EventHandler,
        edit_event: rx.EventHandler,
        status_event: rx.EventHandler,
    ) -> rx.Component:
        return rx.box(
            rx.vstack(
                rx.hstack(
                    rx.heading(title, size="5"),
                    rx.button(
                        "Atualizar lista",
                        on_click=refresh_event,
                        disabled=loading,
                    ),
                    justify="between",
                    width="100%",
                ),
                rx.form(
                    rx.vstack(
                        rx.input(
                            name="name",
                            type="text",
                            placeholder=f"Nome de {title.lower()}",
                            value=form_name,
                            on_change=name_change_event,
                            required=True,
                            disabled=loading,
                            width="100%",
                        ),
                        rx.input(
                            name="description",
                            type="text",
                            placeholder="Descrição (opcional)",
                            value=form_description,
                            on_change=description_change_event,
                            disabled=loading,
                            width="100%",
                        ),
                        rx.hstack(
                            rx.button(
                                rx.cond(
                                    editing_id != None,
                                    "Salvar alterações",
                                    f"Adicionar {title[:-1].lower()}",
                                ),
                                type="submit",
                                disabled=loading,
                            ),
                            rx.cond(
                                editing_id != None,
                                rx.button(
                                    "Cancelar",
                                    type="button",
                                    on_click=cancel_event,
                                    disabled=loading,
                                ),
                                rx.fragment(),
                            ),
                            spacing="2",
                        ),
                        align="stretch",
                        spacing="2",
                    ),
                    on_submit=save_event,
                    width="100%",
                ),
                rx.text(message, color="gray"),
                rx.cond(
                    loading,
                    rx.text("Carregando..."),
                    rx.fragment(),
                ),
                rx.foreach(
                    entries,
                    lambda entry: rx.hstack(
                        rx.text(entry.name, weight="bold"),
                        rx.text(entry.description, color="gray"),
                        rx.badge(entry.status),
                        rx.button(
                            "Editar",
                            on_click=edit_event(entry.id),
                            disabled=loading,
                        ),
                        rx.button(
                            rx.cond(
                                entry.status == "ATIVO",
                                "Inativar",
                                "Reativar",
                            ),
                            on_click=status_event(entry.id),
                            disabled=loading,
                        ),
                        justify="between",
                        width="100%",
                        padding="2",
                        border_bottom="1px solid var(--gray-5)",
                    ),
                ),
                align="stretch",
                spacing="3",
                width="100%",
            ),
            border="1px solid var(--gray-5)",
            border_radius="8px",
            padding="4",
            width="100%",
        )

    catalog_management = rx.cond(
        State.user_role == "ADMINISTRADOR",
        rx.vstack(
            rx.heading("Gestão do catálogo", size="6"),
            catalog_section(
                "Categorias",
                State.categories,
                State.categories_loading,
                State.categories_message,
                State.load_categories,
                State.category_form_name,
                State.category_form_description,
                State.category_editing_id,
                State.set_category_form_name,
                State.set_category_form_description,
                State.save_category,
                State.cancel_category_edit,
                State.edit_category,
                State.toggle_category_status,
            ),
            catalog_section(
                "Marcas",
                State.brands,
                State.brands_loading,
                State.brands_message,
                State.load_brands,
                State.brand_form_name,
                State.brand_form_description,
                State.brand_editing_id,
                State.set_brand_form_name,
                State.set_brand_form_description,
                State.save_brand,
                State.cancel_brand_edit,
                State.edit_brand,
                State.toggle_brand_status,
            ),
            spacing="4",
            align="stretch",
            width="100%",
        ),
        rx.fragment(),
    )

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
            catalog_management,
            spacing="3",
            align="center",
            width="100%",
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
