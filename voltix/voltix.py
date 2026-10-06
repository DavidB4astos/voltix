"""Voltix Reflex application."""

import asyncio
import json
import math
import mimetypes
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any
from uuid import uuid4

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
XANO_PRODUCTS_URL_ENV = "XANO_PRODUCTS_URL"
XANO_VARIATIONS_URL_ENV = "XANO_VARIATIONS_URL"

XanoJson = dict[str, object] | list[dict[str, object]]


@dataclass(frozen=True)
class CatalogEntry:
    id: int
    name: str
    description: str
    status: str


@dataclass(frozen=True)
class ProductVariation:
    id: int
    product_id: int
    name_or_description: str
    sku: str
    price: float
    available_quantity: float
    status: str


@dataclass(frozen=True)
class ProductEntry:
    id: int
    name: str
    description: str
    technical_specifications: str
    image_present: bool
    category_id: int
    category_name: str
    category_status: str
    brand_id: int
    brand_name: str
    brand_status: str
    status: str
    variations: list[ProductVariation]


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


def _finite_number(
    payload: object,
    *,
    minimum: Decimal,
    strictly_positive: bool = False,
) -> float:
    if isinstance(payload, bool) or not isinstance(payload, (int, float, str)):
        raise ValueError("Numeric product field has an invalid value.")
    try:
        number = Decimal(str(payload))
    except InvalidOperation as error:
        raise ValueError("Numeric product field has an invalid value.") from error
    if (
        not number.is_finite()
        or number < minimum
        or (strictly_positive and number == 0)
    ):
        raise ValueError("Numeric product field is outside the allowed range.")
    converted = float(number)
    if not math.isfinite(converted):
        raise ValueError("Numeric product field is outside the allowed range.")
    return converted


def _product_variation(payload: object) -> ProductVariation:
    if not isinstance(payload, dict):
        raise ValueError("Product variation response must be an object.")

    variation_id = payload.get("id")
    product_id = payload.get("produto_id")
    name = payload.get("nome_ou_descricao")
    sku = payload.get("sku")
    status = payload.get("status")
    if (
        not isinstance(variation_id, int)
        or isinstance(variation_id, bool)
        or not isinstance(product_id, int)
        or isinstance(product_id, bool)
        or (name is not None and not isinstance(name, str))
        or not isinstance(sku, str)
        or not sku.strip()
        or status not in {"ATIVO", "INATIVO"}
    ):
        raise ValueError("Product variation response has an invalid record.")

    return ProductVariation(
        id=variation_id,
        product_id=product_id,
        name_or_description=name or "",
        sku=sku,
        price=_finite_number(
            payload.get("preco"),
            minimum=Decimal("0"),
            strictly_positive=True,
        ),
        available_quantity=_finite_number(
            payload.get("quantidade_disponivel"),
            minimum=Decimal("0"),
        ),
        status=status,
    )


def _product_entries(
    products_payload: XanoJson,
    variations_payload: XanoJson,
    categories: list[CatalogEntry],
    brands: list[CatalogEntry],
) -> list[ProductEntry]:
    if not isinstance(products_payload, list) or not isinstance(
        variations_payload, list
    ):
        raise ValueError("Product and variation list responses must be arrays.")

    category_by_id = {entry.id: entry for entry in categories}
    brand_by_id = {entry.id: entry for entry in brands}
    variations_by_product: dict[int, list[ProductVariation]] = {}
    for item in variations_payload:
        variation = _product_variation(item)
        variations_by_product.setdefault(variation.product_id, []).append(variation)

    products: list[ProductEntry] = []
    for payload in products_payload:
        if not isinstance(payload, dict):
            raise ValueError("Product response must be an object.")
        product_id = payload.get("id")
        category_id = payload.get("categoria_id")
        brand_id = payload.get("marca_id")
        name = payload.get("nome")
        description = payload.get("descricao")
        specifications = payload.get("especificacoes_tecnicas")
        image_path = payload.get("imagem_principal")
        status = payload.get("status")
        if (
            not isinstance(product_id, int)
            or isinstance(product_id, bool)
            or not isinstance(category_id, int)
            or isinstance(category_id, bool)
            or not isinstance(brand_id, int)
            or isinstance(brand_id, bool)
            or (name is not None and not isinstance(name, str))
            or (description is not None and not isinstance(description, str))
            or (specifications is not None and not isinstance(specifications, str))
            or (image_path is not None and not isinstance(image_path, str))
            or status not in {"ATIVO", "INATIVO"}
        ):
            raise ValueError("Product response has an invalid record.")

        category = category_by_id.get(category_id)
        brand = brand_by_id.get(brand_id)
        product_variations = variations_by_product.get(product_id, [])
        if category is None or brand is None or not product_variations:
            raise ValueError("Product response has missing relationships or variations.")

        products.append(
            ProductEntry(
                id=product_id,
                name=name or "",
                description=description or "",
                technical_specifications=specifications or "",
                image_present=bool(image_path),
                category_id=category.id,
                category_name=category.name,
                category_status=category.status,
                brand_id=brand.id,
                brand_name=brand.name,
                brand_status=brand.status,
                status=status,
                variations=product_variations,
            )
        )
    return products


def _catalog_failure_message(error: Exception) -> str:
    if isinstance(error, urllib.error.HTTPError):
        if error.code in {401, 403}:
            return "Você não tem autorização para essa operação."
        if error.code == 400:
            return "Os dados foram rejeitados. Verifique o nome e tente novamente."
    return "Não foi possível concluir a operação. Tente novamente."


def _product_failure_message(error: Exception) -> str:
    if isinstance(error, ValueError) and str(error).startswith(
        "Missing required environment variable:"
    ):
        variable = str(error).split(":", maxsplit=1)[1].strip().rstrip(".")
        return f"Configuração ausente: {variable}."
    if isinstance(error, urllib.error.HTTPError):
        if error.code in {401, 403}:
            return "Você não tem autorização para essa operação."
        if error.code == 400:
            return "Os dados do produto foram rejeitados. Verifique os campos e tente novamente."
    return "Não foi possível concluir a operação do produto. Tente novamente."


def _request_xano_multipart(
    url: str,
    *,
    field_name: str,
    file_name: str,
    file_data: bytes,
    authorization: str,
) -> XanoJson:
    boundary = "----Voltix" + uuid4().hex
    safe_file_name = re.sub(r"[^A-Za-z0-9._-]", "_", os.path.basename(file_name))
    content_type = mimetypes.guess_type(safe_file_name)[0] or "application/octet-stream"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{field_name}"; filename="{safe_file_name}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n"
    ).encode("ascii") + file_data + f"\r\n--{boundary}--\r\n".encode("ascii")
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Accept": "application/json",
            "Authorization": authorization,
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status < 200 or response.status >= 300:
            raise ValueError(
                f"Xano returned unexpected HTTP status {response.status}."
            )
        response_payload = json.loads(response.read().decode("utf-8"))
    if isinstance(response_payload, dict):
        return response_payload
    if isinstance(response_payload, list) and all(
        isinstance(item, dict) for item in response_payload
    ):
        return [dict(item) for item in response_payload]
    raise ValueError("Xano response must be a JSON object or a list of objects.")


async def _server_side_xano_multipart_request(
    url: str,
    *,
    field_name: str,
    file_name: str,
    file_data: bytes,
    authorization: str,
) -> XanoJson:
    return await asyncio.to_thread(
        _request_xano_multipart,
        url,
        field_name=field_name,
        file_name=file_name,
        file_data=file_data,
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
    products: list[ProductEntry] = []
    products_loading: bool = False
    products_message: str = ""
    product_editing_id: int | None = None
    product_form_name: str = ""
    product_form_description: str = ""
    product_form_specifications: str = ""
    product_form_category_id: str = ""
    product_form_brand_id: str = ""
    variation_product_id: int | None = None
    variation_editing_id: int | None = None
    variation_form_name: str = ""
    variation_form_sku: str = ""
    variation_form_price: str = ""
    variation_form_quantity: str = ""
    product_image_message: str = ""

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
        self.products = []
        self.products_loading = False
        self.products_message = ""
        self.product_editing_id = None
        self.product_form_name = ""
        self.product_form_description = ""
        self.product_form_specifications = ""
        self.product_form_category_id = ""
        self.product_form_brand_id = ""
        self.variation_product_id = None
        self.variation_editing_id = None
        self.variation_form_name = ""
        self.variation_form_sku = ""
        self.variation_form_price = ""
        self.variation_form_quantity = ""
        self.product_image_message = ""

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

    async def _fetch_products(self) -> list[ProductEntry]:
        products = await self._catalog_request(XANO_PRODUCTS_URL_ENV)
        variations = await self._catalog_request(XANO_VARIATIONS_URL_ENV)
        return _product_entries(products, variations, self.categories, self.brands)

    async def _refresh_products(self) -> bool:
        self.products_loading = True
        self.products_message = ""
        try:
            await self._load_categories()
            await self._load_brands()
            if self.categories_message or self.brands_message:
                raise ValueError("Could not refresh product relationships.")
            self.products = await self._fetch_products()
            return True
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ) as error:
            self.products_message = _product_failure_message(error)
            return False
        finally:
            self.products_loading = False

    @rx.event
    async def load_products(self):
        await self._refresh_products()

    @rx.event
    def set_product_form_name(self, value: str):
        self.product_form_name = value

    @rx.event
    def set_product_form_description(self, value: str):
        self.product_form_description = value

    @rx.event
    def set_product_form_specifications(self, value: str):
        self.product_form_specifications = value

    @rx.event
    def set_product_form_category_id(self, value: str):
        self.product_form_category_id = value

    @rx.event
    def set_product_form_brand_id(self, value: str):
        self.product_form_brand_id = value

    @rx.event
    def set_variation_form_name(self, value: str):
        self.variation_form_name = value

    @rx.event
    def set_variation_form_sku(self, value: str):
        self.variation_form_sku = value

    @rx.event
    def set_variation_form_price(self, value: str):
        self.variation_form_price = value

    @rx.event
    def set_variation_form_quantity(self, value: str):
        self.variation_form_quantity = value

    @rx.event
    def edit_product(self, product_id: int):
        product = next((item for item in self.products if item.id == product_id), None)
        if product is None:
            self.products_message = "Produto não encontrado. Atualize a lista."
            return
        self.product_editing_id = product.id
        self.product_form_name = product.name
        self.product_form_description = product.description
        self.product_form_specifications = product.technical_specifications
        self.product_form_category_id = str(product.category_id)
        self.product_form_brand_id = str(product.brand_id)
        self.products_message = ""
        self.product_image_message = ""

    @rx.event
    def cancel_product_edit(self):
        self.product_editing_id = None
        self.product_form_name = ""
        self.product_form_description = ""
        self.product_form_specifications = ""
        self.product_form_category_id = ""
        self.product_form_brand_id = ""
        self.product_image_message = ""

    @staticmethod
    def _form_decimal(
        value: object,
        *,
        field_name: str,
        minimum: Decimal,
        strictly_positive: bool = False,
    ) -> float:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Informe {field_name}.")
        try:
            number = Decimal(value.strip())
        except InvalidOperation as error:
            raise ValueError(f"Informe um valor válido para {field_name}.") from error
        if (
            not number.is_finite()
            or number < minimum
            or (strictly_positive and number == 0)
        ):
            raise ValueError(f"Informe um valor válido para {field_name}.")
        converted = float(number)
        if not math.isfinite(converted):
            raise ValueError(f"Informe um valor válido para {field_name}.")
        return converted

    async def _save_product_form(self, form_data: dict[str, Any]):
        category_id = self.product_form_category_id.strip()
        brand_id = self.product_form_brand_id.strip()
        if not category_id or not brand_id:
            raise ValueError("Selecione uma categoria e uma marca.")
        try:
            category_id_value = int(category_id)
            brand_id_value = int(brand_id)
        except ValueError as error:
            raise ValueError("Selecione uma categoria e uma marca válidas.") from error

        payload: dict[str, object] = {
            "nome": self.product_form_name,
            "descricao": self.product_form_description,
            "especificacoes_tecnicas": self.product_form_specifications,
            "categoria_id": category_id_value,
            "marca_id": brand_id_value,
        }
        if self.product_editing_id is None:
            variation_name = form_data.get("variation_name", "")
            variation_sku = form_data.get("variation_sku", "")
            if not all(
                isinstance(value, str)
                for value in (variation_name, variation_sku)
            ):
                raise ValueError("Dados da variação inválidos.")
            clean_sku = variation_sku.strip()
            if not clean_sku:
                raise ValueError("Informe o SKU da variação.")
            price = self._form_decimal(
                form_data.get("variation_price"),
                field_name="um preço maior que zero",
                minimum=Decimal("0"),
                strictly_positive=True,
            )
            quantity = self._form_decimal(
                form_data.get("variation_quantity"),
                field_name="uma quantidade não negativa",
                minimum=Decimal("0"),
            )
            payload["variacoes"] = [
                {
                    "nome_ou_descricao": variation_name.strip(),
                    "sku": clean_sku,
                    "preco": price,
                    "quantidade_disponivel": quantity,
                }
            ]
            response = await self._catalog_request(
                XANO_PRODUCTS_URL_ENV,
                method="POST",
                payload=payload,
            )
        else:
            response = await self._catalog_request(
                XANO_PRODUCTS_URL_ENV,
                method="PATCH",
                record_id=self.product_editing_id,
                payload=payload,
            )

        if not isinstance(response, dict):
            raise ValueError("Product mutation response must be an object.")
        return self.product_editing_id is None

    @rx.event
    async def save_product(self, form_data: dict[str, Any]):
        self.products_loading = True
        self.products_message = ""
        try:
            created = await self._save_product_form(form_data)
            self.product_editing_id = None
            self.product_form_name = ""
            self.product_form_description = ""
            self.product_form_specifications = ""
            self.product_form_category_id = ""
            self.product_form_brand_id = ""
            if created:
                self.variation_form_name = ""
                self.variation_form_sku = ""
                self.variation_form_price = ""
                self.variation_form_quantity = ""
            if await self._refresh_products():
                self.products_message = (
                    "Produto criado." if created else "Produto atualizado."
                )
            else:
                self.products_message = (
                    "Operação concluída; não foi possível atualizar a lista. "
                    "Atualize para confirmar."
                )
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ) as error:
            self.products_message = _product_failure_message(error)
        finally:
            self.products_loading = False

    @rx.event
    async def toggle_product_status(self, product_id: int):
        product = next((item for item in self.products if item.id == product_id), None)
        if product is None:
            self.products_message = "Produto não encontrado. Atualize a lista."
            return
        await self._change_product_status(
            product_id,
            "INATIVO" if product.status == "ATIVO" else "ATIVO",
            "Produto",
        )

    async def _change_product_status(
        self,
        product_id: int,
        status: str,
        label: str,
    ):
        self.products_loading = True
        self.products_message = ""
        try:
            response = await self._catalog_request(
                XANO_PRODUCTS_URL_ENV,
                method="PATCH",
                record_id=product_id,
                payload={"status": status},
            )
            if not isinstance(response, dict):
                raise ValueError("Product status response must be an object.")
            if await self._refresh_products():
                self.products_message = f"Status de {label.lower()} atualizado."
            else:
                self.products_message = (
                    "Status atualizado; não foi possível atualizar a lista. "
                    "Atualize para confirmar."
                )
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ) as error:
            self.products_message = _product_failure_message(error)
        finally:
            self.products_loading = False

    @rx.event
    def begin_variation(self, product_id: int):
        if not any(item.id == product_id for item in self.products):
            self.products_message = "Produto não encontrado. Atualize a lista."
            return
        self.variation_product_id = product_id
        self.variation_editing_id = None
        self.variation_form_name = ""
        self.variation_form_sku = ""
        self.variation_form_price = ""
        self.variation_form_quantity = ""

    @rx.event
    def edit_variation(self, product_id: int, variation_id: int):
        product = next((item for item in self.products if item.id == product_id), None)
        variation = (
            next((item for item in product.variations if item.id == variation_id), None)
            if product is not None
            else None
        )
        if variation is None:
            self.products_message = "Variação não encontrada. Atualize a lista."
            return
        self.variation_product_id = product.id
        self.variation_editing_id = variation.id
        self.variation_form_name = variation.name_or_description
        self.variation_form_sku = variation.sku
        self.variation_form_price = str(variation.price)
        self.variation_form_quantity = str(variation.available_quantity)

    @rx.event
    def cancel_variation(self):
        self.variation_product_id = None
        self.variation_editing_id = None
        self.variation_form_name = ""
        self.variation_form_sku = ""
        self.variation_form_price = ""
        self.variation_form_quantity = ""

    @rx.event
    async def save_variation(self, form_data: dict[str, Any]):
        product_id = self.variation_product_id
        if product_id is None:
            self.products_message = "Selecione um produto para a variação."
            return
        self.products_loading = True
        self.products_message = ""
        try:
            name = form_data.get("variation_name", "")
            sku = form_data.get("variation_sku", "")
            if not isinstance(name, str) or not isinstance(sku, str):
                raise ValueError("Dados da variação inválidos.")
            clean_sku = sku.strip()
            if not clean_sku:
                raise ValueError("Informe o SKU da variação.")
            price = self._form_decimal(
                form_data.get("variation_price"),
                field_name="um preço maior que zero",
                minimum=Decimal("0"),
                strictly_positive=True,
            )
            quantity = self._form_decimal(
                form_data.get("variation_quantity"),
                field_name="uma quantidade não negativa",
                minimum=Decimal("0"),
            )
            payload: dict[str, object] = {
                "nome_ou_descricao": name.strip(),
                "sku": clean_sku,
                "preco": price,
                "quantidade_disponivel": quantity,
            }
            if self.variation_editing_id is None:
                payload["produto_id"] = product_id
                response = await self._catalog_request(
                    XANO_VARIATIONS_URL_ENV,
                    method="POST",
                    payload=payload,
                )
            else:
                response = await self._catalog_request(
                    XANO_VARIATIONS_URL_ENV,
                    method="PATCH",
                    record_id=self.variation_editing_id,
                    payload=payload,
                )
            if not isinstance(response, dict):
                raise ValueError("Variation mutation response must be an object.")
            self.cancel_variation()
            if await self._refresh_products():
                self.products_message = "Variação salva."
            else:
                self.products_message = (
                    "Variação salva; não foi possível atualizar a lista. "
                    "Atualize para confirmar."
                )
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ) as error:
            self.products_message = _product_failure_message(error)
        finally:
            self.products_loading = False

    @rx.event
    async def toggle_variation_status(self, variation_id: int, status: str):
        if status not in {"ATIVO", "INATIVO"}:
            self.products_message = "Status de variação inválido."
            return
        self.products_loading = True
        self.products_message = ""
        try:
            response = await self._catalog_request(
                XANO_VARIATIONS_URL_ENV,
                method="PATCH",
                record_id=variation_id,
                payload={"status": status},
            )
            if not isinstance(response, dict):
                raise ValueError("Variation status response must be an object.")
            if await self._refresh_products():
                self.products_message = "Status da variação atualizado."
            else:
                self.products_message = (
                    "Status atualizado; não foi possível atualizar a lista. "
                    "Atualize para confirmar."
                )
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ) as error:
            self.products_message = _product_failure_message(error)
        finally:
            self.products_loading = False

    @rx.event
    async def upload_product_image(self, files: list[rx.UploadFile]):
        if (
            not self._auth_token
            or not self.is_authenticated
            or self.session_status != "success"
            or self.user_role != "ADMINISTRADOR"
            or self.user_status != "ATIVO"
        ):
            self.product_image_message = "Você não tem autorização para essa operação."
            return
        if self.product_editing_id is None:
            self.product_image_message = "Selecione um produto para associar a imagem."
            return
        if len(files) != 1:
            self.product_image_message = "Selecione exatamente uma imagem."
            return

        file = files[0]
        if os.path.splitext(file.name)[1].lower() not in {
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".webp",
        }:
            self.product_image_message = (
                "Formato de imagem não suportado. Use JPG, PNG, GIF ou WEBP."
            )
            return

        self.products_loading = True
        self.product_image_message = ""
        try:
            image_data = await file.read()
            base_url = _required_environment_url(XANO_PRODUCTS_URL_ENV).rstrip("/")
            response = await _server_side_xano_multipart_request(
                f"{base_url}/{self.product_editing_id}/image",
                field_name="image_file",
                file_name=file.name,
                file_data=image_data,
                authorization="Bearer " + self._auth_token,
            )
            if not isinstance(response, dict):
                raise ValueError("Product image response must be an object.")
            if await self._refresh_products():
                self.product_image_message = "Imagem principal atualizada."
            else:
                self.product_image_message = (
                    "Imagem enviada; não foi possível atualizar a lista. "
                    "Atualize para confirmar."
                )
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ) as error:
            self.product_image_message = _product_failure_message(error)
        finally:
            self.products_loading = False

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
            await self._refresh_products()

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

    def product_form() -> rx.Component:
        category_choices = rx.foreach(
            State.categories,
            lambda entry: rx.cond(
                (entry.status == "ATIVO")
                | (
                    State.product_form_category_id == entry.id.to_string()
                ),
                rx.select.item(
                    entry.name
                    + rx.cond(entry.status == "INATIVO", " (INATIVA)", ""),
                    value=entry.id.to_string(),
                ),
                rx.fragment(),
            ),
        )
        brand_choices = rx.foreach(
            State.brands,
            lambda entry: rx.cond(
                (entry.status == "ATIVO")
                | (
                    State.product_form_brand_id == entry.id.to_string()
                ),
                rx.select.item(
                    entry.name
                    + rx.cond(entry.status == "INATIVO", " (INATIVA)", ""),
                    value=entry.id.to_string(),
                ),
                rx.fragment(),
            ),
        )
        return rx.form(
            rx.vstack(
                rx.heading(
                    rx.cond(
                        State.product_editing_id != None,
                        "Editar produto",
                        "Cadastrar produto",
                    ),
                    size="4",
                ),
                rx.input(
                    placeholder="Nome do produto",
                    value=State.product_form_name,
                    on_change=State.set_product_form_name,
                    disabled=State.products_loading,
                    width="100%",
                ),
                rx.text_area(
                    placeholder="Descrição",
                    value=State.product_form_description,
                    on_change=State.set_product_form_description,
                    disabled=State.products_loading,
                    width="100%",
                ),
                rx.text_area(
                    placeholder="Especificações técnicas",
                    value=State.product_form_specifications,
                    on_change=State.set_product_form_specifications,
                    disabled=State.products_loading,
                    width="100%",
                ),
                rx.select.root(
                    rx.select.trigger(placeholder="Selecione uma categoria"),
                    rx.select.content(category_choices),
                    value=State.product_form_category_id,
                    on_change=State.set_product_form_category_id,
                    disabled=State.products_loading,
                    width="100%",
                ),
                rx.select.root(
                    rx.select.trigger(placeholder="Selecione uma marca"),
                    rx.select.content(brand_choices),
                    value=State.product_form_brand_id,
                    on_change=State.set_product_form_brand_id,
                    disabled=State.products_loading,
                    width="100%",
                ),
                rx.cond(
                    State.product_editing_id == None,
                    rx.vstack(
                        rx.heading("Variação inicial obrigatória", size="3"),
                        rx.input(
                            name="variation_name",
                            placeholder="Nome ou descrição da variação (opcional)",
                            disabled=State.products_loading,
                            width="100%",
                        ),
                        rx.input(
                            name="variation_sku",
                            placeholder="SKU",
                            required=True,
                            disabled=State.products_loading,
                            width="100%",
                        ),
                        rx.input(
                            name="variation_price",
                            type="number",
                            step="any",
                            placeholder="Preço (maior que zero)",
                            required=True,
                            disabled=State.products_loading,
                            width="100%",
                        ),
                        rx.input(
                            name="variation_quantity",
                            type="number",
                            step="any",
                            placeholder="Quantidade disponível (zero ou maior)",
                            required=True,
                            disabled=State.products_loading,
                            width="100%",
                        ),
                        align="stretch",
                        width="100%",
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    State.product_editing_id != None,
                    rx.vstack(
                        rx.text(
                            rx.cond(
                                State.products.length() > 0,
                                "Produto existente: imagem principal opcional.",
                                "",
                            ),
                            color="gray",
                        ),
                        rx.upload(
                            rx.text("Selecione uma imagem JPG, PNG, GIF ou WEBP"),
                            id="product-main-image",
                            accept={
                                "image/jpeg": [".jpg", ".jpeg"],
                                "image/png": [".png"],
                                "image/gif": [".gif"],
                                "image/webp": [".webp"],
                            },
                            max_files=1,
                            disabled=State.products_loading,
                            width="100%",
                        ),
                        rx.button(
                            "Enviar imagem principal",
                            type="button",
                            on_click=State.upload_product_image(
                                rx.upload_files("product-main-image")
                            ),
                            disabled=State.products_loading,
                        ),
                        rx.text(State.product_image_message, color="gray"),
                        align="stretch",
                        width="100%",
                    ),
                    rx.fragment(),
                ),
                rx.hstack(
                    rx.button(
                        rx.cond(
                            State.product_editing_id != None,
                            "Salvar produto",
                            "Criar produto",
                        ),
                        type="submit",
                        disabled=State.products_loading,
                    ),
                    rx.cond(
                        State.product_editing_id != None,
                        rx.button(
                            "Cancelar edição",
                            type="button",
                            on_click=State.cancel_product_edit,
                            disabled=State.products_loading,
                        ),
                        rx.fragment(),
                    ),
                    spacing="2",
                ),
                align="stretch",
                spacing="3",
                width="100%",
            ),
            on_submit=State.save_product,
            width="100%",
        )

    def variation_form() -> rx.Component:
        return rx.cond(
            State.variation_product_id != None,
            rx.form(
                rx.vstack(
                    rx.heading(
                        rx.cond(
                            State.variation_editing_id != None,
                            "Editar variação",
                            "Adicionar variação",
                        ),
                        size="4",
                    ),
                    rx.input(
                        name="variation_name",
                        placeholder="Nome ou descrição (opcional)",
                        value=State.variation_form_name,
                        on_change=State.set_variation_form_name,
                        disabled=State.products_loading,
                        width="100%",
                    ),
                    rx.input(
                        name="variation_sku",
                        placeholder="SKU",
                        value=State.variation_form_sku,
                        on_change=State.set_variation_form_sku,
                        required=True,
                        disabled=State.products_loading,
                        width="100%",
                    ),
                    rx.input(
                        name="variation_price",
                        type="number",
                        step="any",
                        placeholder="Preço (maior que zero)",
                        value=State.variation_form_price,
                        on_change=State.set_variation_form_price,
                        required=True,
                        disabled=State.products_loading,
                        width="100%",
                    ),
                    rx.input(
                        name="variation_quantity",
                        type="number",
                        step="any",
                        placeholder="Quantidade disponível (zero ou maior)",
                        value=State.variation_form_quantity,
                        on_change=State.set_variation_form_quantity,
                        required=True,
                        disabled=State.products_loading,
                        width="100%",
                    ),
                    rx.hstack(
                        rx.button(
                            "Salvar variação",
                            type="submit",
                            disabled=State.products_loading,
                        ),
                        rx.button(
                            "Cancelar",
                            type="button",
                            on_click=State.cancel_variation,
                            disabled=State.products_loading,
                        ),
                        spacing="2",
                    ),
                    align="stretch",
                    width="100%",
                ),
                on_submit=State.save_variation,
                width="100%",
            ),
            rx.fragment(),
        )

    product_management = rx.cond(
        State.user_role == "ADMINISTRADOR",
        rx.vstack(
            rx.heading("Gestão de produtos", size="6"),
            product_form(),
            rx.hstack(
                rx.heading("Produtos cadastrados", size="5"),
                rx.button(
                    "Atualizar lista",
                    on_click=State.load_products,
                    disabled=State.products_loading,
                ),
                justify="between",
                width="100%",
            ),
            rx.text(State.products_message, color="gray"),
            rx.cond(
                State.products_loading,
                rx.text("Carregando produtos..."),
                rx.fragment(),
            ),
            rx.foreach(
                State.products,
                lambda product: rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.heading(
                                rx.cond(
                                    product.name != "",
                                    product.name,
                                    "Produto #" + product.id.to_string(),
                                ),
                                size="4",
                            ),
                            rx.badge(product.status),
                            justify="between",
                            width="100%",
                        ),
                        rx.text(product.description, color="gray"),
                        rx.text(product.technical_specifications, color="gray"),
                        rx.text(
                            "Categoria: "
                            + product.category_name
                            + " ("
                            + product.category_status
                            + ")"
                        ),
                        rx.text(
                            "Marca: "
                            + product.brand_name
                            + " ("
                            + product.brand_status
                            + ")"
                        ),
                        rx.text(
                            rx.cond(
                                product.image_present,
                                "Imagem principal cadastrada",
                                "Sem imagem principal",
                            ),
                            color="gray",
                        ),
                        rx.hstack(
                            rx.button(
                                "Editar produto",
                                on_click=State.edit_product(product.id),
                                disabled=State.products_loading,
                            ),
                            rx.button(
                                rx.cond(
                                    product.status == "ATIVO",
                                    "Inativar produto",
                                    "Reativar produto",
                                ),
                                on_click=State.toggle_product_status(product.id),
                                disabled=State.products_loading,
                            ),
                            rx.button(
                                "Adicionar variação",
                                on_click=State.begin_variation(product.id),
                                disabled=State.products_loading,
                            ),
                            spacing="2",
                        ),
                        rx.heading("Variações", size="3"),
                        rx.foreach(
                            product.variations,
                            lambda variation: rx.vstack(
                                rx.hstack(
                                    rx.text(
                                        rx.cond(
                                            variation.name_or_description != "",
                                            variation.name_or_description,
                                            variation.sku,
                                        ),
                                        weight="bold",
                                    ),
                                    rx.badge(variation.status),
                                    justify="between",
                                    width="100%",
                                ),
                                rx.text(
                                    "SKU: "
                                    + variation.sku
                                    + " | Preço: "
                                    + variation.price.to_string()
                                    + " | Disponível: "
                                    + variation.available_quantity.to_string()
                                ),
                                rx.hstack(
                                    rx.button(
                                        "Editar variação",
                                        on_click=State.edit_variation(
                                            product.id,
                                            variation.id,
                                        ),
                                        disabled=State.products_loading,
                                    ),
                                    rx.button(
                                        rx.cond(
                                            variation.status == "ATIVO",
                                            "Inativar variação",
                                            "Reativar variação",
                                        ),
                                        on_click=State.toggle_variation_status(
                                            variation.id,
                                            rx.cond(
                                                variation.status == "ATIVO",
                                                "INATIVO",
                                                "ATIVO",
                                            ),
                                        ),
                                        disabled=State.products_loading,
                                    ),
                                    spacing="2",
                                ),
                                align="stretch",
                                width="100%",
                                padding="2",
                                border_bottom="1px solid var(--gray-4)",
                            ),
                        ),
                        align="stretch",
                        spacing="2",
                        width="100%",
                    ),
                    border="1px solid var(--gray-5)",
                    border_radius="8px",
                    padding="4",
                    width="100%",
                ),
            ),
            variation_form(),
            align="stretch",
            spacing="3",
            width="100%",
        ),
        rx.fragment(),
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
            product_management,
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
