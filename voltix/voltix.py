"""Voltix Reflex application."""

import asyncio
import csv
import io
import json
import logging
import math
import mimetypes
import os
import re
import time
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass, replace
from decimal import Decimal, InvalidOperation
from typing import Any
from urllib.parse import urlencode, urlparse
from uuid import uuid4
from xml.etree import ElementTree

import reflex as rx
from dotenv import load_dotenv

from rxconfig import config

try:
    from .demo_images import resolve_demo_image, resolve_demo_image_named, demo_image_credit
except Exception:
    def resolve_demo_image(sku: str, existing_image_url: str) -> str:
        return existing_image_url

    def resolve_demo_image_named(
        name: str,
        sku: str,
        existing_image_url: str,
    ) -> str:
        return existing_image_url

    def demo_image_credit(image_url: str) -> dict[str, str] | None:
        return None


load_dotenv()

XANO_HEALTH_URL_ENV = "XANO_HEALTH_URL"
XANO_LOGIN_URL_ENV = "XANO_LOGIN_URL"
XANO_ME_URL_ENV = "XANO_ME_URL"
XANO_INTERNAL_ACCESS_URL_ENV = "XANO_INTERNAL_ACCESS_URL"
XANO_CATEGORIES_URL_ENV = "XANO_CATEGORIES_URL"
XANO_BRANDS_URL_ENV = "XANO_BRANDS_URL"
XANO_PRODUCTS_URL_ENV = "XANO_PRODUCTS_URL"
XANO_VARIATIONS_URL_ENV = "XANO_VARIATIONS_URL"
XANO_PUBLIC_CATEGORIES_URL_ENV = "XANO_PUBLIC_CATEGORIES_URL"
XANO_PUBLIC_PRODUCTS_URL_ENV = "XANO_PUBLIC_PRODUCTS_URL"
XANO_PUBLIC_PRODUCT_DETAILS_URL_ENV = "XANO_PUBLIC_PRODUCT_DETAILS_URL"
XANO_PUBLIC_PRODUCT_IMAGE_URL_ENV = "XANO_PUBLIC_PRODUCT_IMAGE_URL"
XANO_CUSTOMER_URL_ENV = "XANO_CUSTOMER_URL"
XANO_CUSTOMER_LOGIN_URL_ENV = "XANO_CUSTOMER_LOGIN_URL"
XANO_CUSTOMER_ME_URL_ENV = "XANO_CUSTOMER_ME_URL"
XANO_CUSTOMER_ADDRESSES_URL_ENV = "XANO_CUSTOMER_ADDRESSES_URL"
XANO_CART_URL_ENV = "XANO_CART_URL"
XANO_CHECKOUT_REVIEW_URL_ENV = "XANO_CHECKOUT_REVIEW_URL"
XANO_CHECKOUT_CONFIRM_URL_ENV = "XANO_CHECKOUT_CONFIRM_URL"
XANO_ORDERS_URL_ENV = "XANO_ORDERS_URL"
XANO_PAYMENT_SIMULATION_URL_ENV = "XANO_PAYMENT_SIMULATION_URL"

PUBLIC_CATALOG_CACHE_TTL_SECONDS = 30.0
XANO_RATE_LIMIT_MAX_ATTEMPTS = 3
XANO_RATE_LIMIT_DEFAULT_WAIT_SECONDS = 20.0
XANO_RATE_LIMIT_MAX_WAIT_SECONDS = 30.0

BULK_IMPORT_MAX_BYTES = 2 * 1024 * 1024
BULK_IMPORT_MAX_ROWS = 200
BULK_IMPORT_MAX_PRODUCTS = 50
BULK_IMPORT_REQUEST_INTERVAL_SECONDS = 3.0
BULK_IMPORT_HEADERS = (
    "produto_nome",
    "produto_descricao",
    "produto_especificacoes_tecnicas",
    "categoria_nome",
    "marca_nome",
    "variacao_nome",
    "sku",
    "preco",
    "quantidade_disponivel",
)
BULK_IMPORT_REQUIRED_FIELDS = {
    "produto_nome": "nome do produto",
    "categoria_nome": "categoria",
    "marca_nome": "marca",
    "variacao_nome": "nome da variação",
    "sku": "SKU",
    "preco": "preço",
    "quantidade_disponivel": "quantidade disponível",
}
BULK_IMPORT_VALID_STATUS = "VÁLIDA"
BULK_IMPORT_ERROR_STATUS = "ERRO"
BULK_IMPORT_DUPLICATE_STATUS = "DUPLICADA"
BULK_IMPORT_CREATED_OUTCOME = "CRIADO"
BULK_IMPORT_SKIPPED_OUTCOME = "PULADO"
BULK_IMPORT_FAILED_OUTCOME = "FALHA"

PUBLIC_CATALOG_LOGGER = logging.getLogger("voltix.public_catalog")
BULK_IMPORT_LOGGER = logging.getLogger("voltix.bulk_import")

_PUBLIC_ENDPOINT_LABELS = {
    XANO_PUBLIC_CATEGORIES_URL_ENV: "public_catalog.categories",
    XANO_PUBLIC_PRODUCTS_URL_ENV: "public_catalog.products",
    XANO_PUBLIC_PRODUCT_DETAILS_URL_ENV: "public_catalog.product_details",
    XANO_PUBLIC_PRODUCT_IMAGE_URL_ENV: "public_catalog.product_image",
}

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


@dataclass(frozen=True)
class PublicProductEntry:
    id: int
    name: str
    description: str
    technical_specifications: str
    category_name: str
    brand_name: str
    image_url: str
    variations: list[ProductVariation]


@dataclass(frozen=True)
class CustomerProfile:
    id: int
    name: str
    cpf: str
    email: str
    phone: str
    status: str


@dataclass(frozen=True)
class CustomerAddressEntry:
    id: int
    customer_id: int
    cep: str
    street: str
    number: str
    complement: str
    neighborhood: str
    city: str
    state: str
    label: str
    is_primary: bool
    status: str


@dataclass(frozen=True)
class CartItemEntry:
    id: int
    variation_id: int
    product_name: str
    variation_name: str
    sku: str
    quantity: int
    price: str
    available_quantity: str
    subtotal: str
    available: bool


@dataclass(frozen=True)
class CartSnapshot:
    id: int | None
    items: list[CartItemEntry]
    total: str


@dataclass(frozen=True)
class CheckoutAddressSnapshot:
    cep: str
    street: str
    number: str
    complement: str
    neighborhood: str
    city: str
    state: str
    label: str


@dataclass(frozen=True)
class CheckoutItemEntry:
    item_id: int
    variation_id: int
    product_name: str
    variation_name: str
    sku: str
    quantity: int
    unit_price: str
    subtotal: str
    product_status: str
    variation_status: str
    available_quantity: str
    available: bool


@dataclass(frozen=True)
class CheckoutReview:
    address_id: int
    address: CheckoutAddressSnapshot
    items: list[CheckoutItemEntry]
    revision: list[dict[str, object]]
    subtotal: str
    freight: str
    total: str


@dataclass(frozen=True)
class OrderItemSummary:
    variation_id: int
    sku: str
    variation_name: str
    quantity: int
    unit_price: str
    subtotal: str


@dataclass(frozen=True)
class OrderSummary:
    id: int
    code: str
    order_date: str
    status: str
    order_items: list[OrderItemSummary]
    subtotal: str
    freight: str
    total: str
    delivery: CheckoutAddressSnapshot
    payment_method: str
    payment_status: str
    payment_value: str


def _customer_profile(payload: object) -> CustomerProfile:
    if not isinstance(payload, dict):
        raise ValueError("Customer response must be an object.")

    customer_id = payload.get("id")
    name = payload.get("nome_completo")
    cpf = payload.get("cpf")
    email = payload.get("email")
    phone = payload.get("telefone")
    status = payload.get("status")
    if (
        not isinstance(customer_id, int)
        or isinstance(customer_id, bool)
        or not isinstance(name, str)
        or not name.strip()
        or not isinstance(cpf, str)
        or not cpf.strip()
        or not isinstance(email, str)
        or not email.strip()
        or (phone is not None and not isinstance(phone, str))
        or status != "ATIVO"
    ):
        raise ValueError("Customer response has an invalid or inactive identity.")

    return CustomerProfile(
        id=customer_id,
        name=name,
        cpf=cpf,
        email=email,
        phone=phone or "",
        status=status,
    )


def _customer_address(payload: object) -> CustomerAddressEntry:
    if not isinstance(payload, dict):
        raise ValueError("Address response must be an object.")

    address_id = payload.get("id")
    customer_id = payload.get("cliente_id")
    text_fields = {
        "cep": payload.get("cep"),
        "logradouro": payload.get("logradouro"),
        "numero": payload.get("numero"),
        "complemento": payload.get("complemento"),
        "bairro": payload.get("bairro"),
        "cidade": payload.get("cidade"),
        "estado": payload.get("estado"),
        "identificacao": payload.get("identificacao"),
    }
    primary = payload.get("principal")
    status = payload.get("status")
    if (
        not isinstance(address_id, int)
        or isinstance(address_id, bool)
        or not isinstance(customer_id, int)
        or isinstance(customer_id, bool)
        or not isinstance(primary, bool)
        or status not in {"ATIVO", "INATIVO"}
        or any(value is not None and not isinstance(value, str) for value in text_fields.values())
    ):
        raise ValueError("Address response has an invalid record.")

    return CustomerAddressEntry(
        id=address_id,
        customer_id=customer_id,
        cep=text_fields["cep"] or "",
        street=text_fields["logradouro"] or "",
        number=text_fields["numero"] or "",
        complement=text_fields["complemento"] or "",
        neighborhood=text_fields["bairro"] or "",
        city=text_fields["cidade"] or "",
        state=text_fields["estado"] or "",
        label=text_fields["identificacao"] or "",
        is_primary=primary,
        status=status,
    )


def _customer_addresses(payload: XanoJson) -> list[CustomerAddressEntry]:
    if not isinstance(payload, list):
        raise ValueError("Customer address list must be an array.")
    return [_customer_address(item) for item in payload]


def _cart_decimal(payload: object, *, strictly_positive: bool = False) -> Decimal:
    if isinstance(payload, bool) or not isinstance(payload, (int, float, str)):
        raise ValueError("Cart monetary or stock field has an invalid value.")
    try:
        number = Decimal(str(payload))
    except InvalidOperation as error:
        raise ValueError("Cart monetary or stock field has an invalid value.") from error
    if (
        not number.is_finite()
        or number < 0
        or (strictly_positive and number == 0)
    ):
        raise ValueError("Cart monetary or stock field is outside the allowed range.")
    return number


def _cart_decimal_text(number: Decimal) -> str:
    return format(number, "f")


def _cart_item(payload: object) -> CartItemEntry:
    if not isinstance(payload, dict):
        raise ValueError("Cart item response must be an object.")

    item_id = payload.get("id")
    variation_id = payload.get("variacao_produto_id")
    quantity = payload.get("quantidade")
    product_name = payload.get("produto_nome")
    variation_name = payload.get("variacao_nome")
    sku = payload.get("variacao_sku")
    product_status = payload.get("produto_status")
    variation_status = payload.get("variacao_status")
    available = payload.get("disponivel")
    if (
        not isinstance(item_id, int)
        or isinstance(item_id, bool)
        or item_id < 1
        or not isinstance(variation_id, int)
        or isinstance(variation_id, bool)
        or variation_id < 1
        or not isinstance(quantity, int)
        or isinstance(quantity, bool)
        or quantity < 1
        or (product_name is not None and not isinstance(product_name, str))
        or (variation_name is not None and not isinstance(variation_name, str))
        or not isinstance(sku, str)
        or not sku.strip()
        or product_status not in {"ATIVO", "INATIVO"}
        or variation_status not in {"ATIVO", "INATIVO"}
        or not isinstance(available, bool)
    ):
        raise ValueError("Cart item response has an invalid record.")

    price = _cart_decimal(payload.get("preco"), strictly_positive=True)
    stock = _cart_decimal(payload.get("quantidade_disponivel"))
    subtotal = _cart_decimal(payload.get("subtotal"))
    expected_available = (
        product_status == "ATIVO"
        and variation_status == "ATIVO"
        and stock >= quantity
    )
    if subtotal != price * quantity or available != expected_available:
        raise ValueError("Cart item response has inconsistent totals or availability.")

    return CartItemEntry(
        id=item_id,
        variation_id=variation_id,
        product_name=product_name or "",
        variation_name=variation_name or "",
        sku=sku,
        quantity=quantity,
        price=_cart_decimal_text(price),
        available_quantity=_cart_decimal_text(stock),
        subtotal=_cart_decimal_text(subtotal),
        available=available,
    )


def _cart_snapshot(payload: object) -> CartSnapshot:
    if not isinstance(payload, dict):
        raise ValueError("Cart response must be an object.")

    cart_id = payload.get("carrinho_id")
    items_payload = payload.get("itens")
    if (
        cart_id is not None
        and (
            not isinstance(cart_id, int)
            or isinstance(cart_id, bool)
            or cart_id < 1
        )
    ):
        raise ValueError("Cart response has an invalid cart identity.")
    if not isinstance(items_payload, list):
        raise ValueError("Cart items response must be an array.")

    items = [_cart_item(item) for item in items_payload]
    variation_ids = [item.variation_id for item in items]
    if len(variation_ids) != len(set(variation_ids)):
        raise ValueError("Cart response contains a duplicate variation.")
    if cart_id is None and items:
        raise ValueError("An empty cart identity cannot contain items.")

    total = _cart_decimal(payload.get("total"))
    calculated_total = sum(
        (_cart_decimal(item.subtotal) for item in items),
        start=Decimal("0"),
    )
    if total != calculated_total:
        raise ValueError("Cart response total does not match its item subtotals.")

    return CartSnapshot(
        id=cart_id,
        items=items,
        total=_cart_decimal_text(total),
    )


def _checkout_address_snapshot(payload: object) -> CheckoutAddressSnapshot:
    if not isinstance(payload, dict):
        raise ValueError("Delivery address snapshot must be an object.")
    fields = {
        "cep": payload.get("cep"),
        "street": payload.get("logradouro"),
        "number": payload.get("numero"),
        "complement": payload.get("complemento"),
        "neighborhood": payload.get("bairro"),
        "city": payload.get("cidade"),
        "state": payload.get("estado"),
        "label": payload.get("identificacao"),
    }
    if any(value is not None and not isinstance(value, str) for value in fields.values()):
        raise ValueError("Delivery address snapshot has an invalid field.")
    return CheckoutAddressSnapshot(
        cep=fields["cep"] or "",
        street=fields["street"] or "",
        number=fields["number"] or "",
        complement=fields["complement"] or "",
        neighborhood=fields["neighborhood"] or "",
        city=fields["city"] or "",
        state=fields["state"] or "",
        label=fields["label"] or "",
    )


def _checkout_review_item(payload: object) -> CheckoutItemEntry:
    if not isinstance(payload, dict):
        raise ValueError("Checkout review item must be an object.")
    item_id = payload.get("item_id")
    variation_id = payload.get("variacao_id")
    quantity = payload.get("quantidade")
    product_name = payload.get("produto_nome")
    variation_name = payload.get("variacao_nome")
    sku = payload.get("sku")
    product_status = payload.get("produto_status")
    variation_status = payload.get("variacao_status")
    available = payload.get("disponivel")
    if (
        not isinstance(item_id, int)
        or isinstance(item_id, bool)
        or item_id < 1
        or not isinstance(variation_id, int)
        or isinstance(variation_id, bool)
        or variation_id < 1
        or not isinstance(quantity, int)
        or isinstance(quantity, bool)
        or quantity < 1
        or (product_name is not None and not isinstance(product_name, str))
        or (variation_name is not None and not isinstance(variation_name, str))
        or not isinstance(sku, str)
        or not sku.strip()
        or product_status not in {"ATIVO", "INATIVO"}
        or variation_status not in {"ATIVO", "INATIVO"}
        or not isinstance(available, bool)
    ):
        raise ValueError("Checkout review item has an invalid record.")
    price = _cart_decimal(payload.get("preco_unitario"), strictly_positive=True)
    subtotal = _cart_decimal(payload.get("subtotal"), strictly_positive=True)
    stock = _cart_decimal(payload.get("estoque_disponivel"))
    if subtotal != price * quantity:
        raise ValueError("Checkout review item subtotal is inconsistent.")
    expected_available = (
        product_status == "ATIVO"
        and variation_status == "ATIVO"
        and stock >= quantity
    )
    if available != expected_available:
        raise ValueError("Checkout review item availability is inconsistent.")
    return CheckoutItemEntry(
        item_id=item_id,
        variation_id=variation_id,
        product_name=product_name or "",
        variation_name=variation_name or "",
        sku=sku,
        quantity=quantity,
        unit_price=_cart_decimal_text(price),
        subtotal=_cart_decimal_text(subtotal),
        product_status=product_status,
        variation_status=variation_status,
        available_quantity=_cart_decimal_text(stock),
        available=available,
    )


def _checkout_review(payload: object) -> CheckoutReview:
    if not isinstance(payload, dict):
        raise ValueError("Checkout review response must be an object.")
    address_id = payload.get("endereco_id")
    items_payload = payload.get("itens")
    revision_payload = payload.get("revisao")
    if (
        not isinstance(address_id, int)
        or isinstance(address_id, bool)
        or address_id < 1
        or not isinstance(items_payload, list)
        or not isinstance(revision_payload, list)
    ):
        raise ValueError("Checkout review identity or collections are invalid.")
    items = [_checkout_review_item(item) for item in items_payload]
    revision = [
        dict(item) if isinstance(item, dict) else None for item in revision_payload
    ]
    if (
        not items
        or len(items) != len(revision)
        or any(item is None for item in revision)
        or len({item.variation_id for item in items}) != len(items)
    ):
        raise ValueError("Checkout review contains empty or inconsistent items.")
    for item, reviewed in zip(items, revision, strict=True):
        if (
            reviewed["item_id"] != item.item_id
            or reviewed["variacao_id"] != item.variation_id
            or reviewed["quantidade"] != item.quantity
            or reviewed["produto_status"] != item.product_status
            or reviewed["variacao_status"] != item.variation_status
            or _cart_decimal(reviewed["preco_unitario"]) != _cart_decimal(item.unit_price)
            or _cart_decimal(reviewed["estoque_disponivel"])
            != _cart_decimal(item.available_quantity)
        ):
            raise ValueError("Checkout review snapshot does not match its items.")

    subtotal = _cart_decimal(payload.get("subtotal"))
    freight = _cart_decimal(payload.get("valor_frete"))
    total = _cart_decimal(payload.get("valor_total"))
    calculated_subtotal = sum(
        (_cart_decimal(item.subtotal) for item in items),
        start=Decimal("0"),
    )
    if (
        subtotal != calculated_subtotal
        or freight != 0
        or total != subtotal + freight
    ):
        raise ValueError("Checkout review totals are inconsistent.")
    return CheckoutReview(
        address_id=address_id,
        address=_checkout_address_snapshot(payload.get("endereco")),
        items=items,
        revision=[dict(item) for item in revision if item is not None],
        subtotal=_cart_decimal_text(subtotal),
        freight=_cart_decimal_text(freight),
        total=_cart_decimal_text(total),
    )


def _order_item_summary(payload: object) -> OrderItemSummary:
    if not isinstance(payload, dict):
        raise ValueError("Order item response must be an object.")
    variation_id = payload.get("variacao_id")
    quantity = payload.get("quantidade")
    sku = payload.get("sku")
    variation_name = payload.get("nome_ou_descricao")
    if (
        not isinstance(variation_id, int)
        or isinstance(variation_id, bool)
        or variation_id < 1
        or not isinstance(quantity, int)
        or isinstance(quantity, bool)
        or quantity < 1
        or not isinstance(sku, str)
        or not sku.strip()
        or (variation_name is not None and not isinstance(variation_name, str))
    ):
        raise ValueError("Order item response has an invalid record.")
    price = _cart_decimal(payload.get("preco_unitario"), strictly_positive=True)
    subtotal = _cart_decimal(payload.get("subtotal"), strictly_positive=True)
    if subtotal != price * quantity:
        raise ValueError("Order item subtotal is inconsistent.")
    return OrderItemSummary(
        variation_id=variation_id,
        sku=sku,
        variation_name=variation_name or "",
        quantity=quantity,
        unit_price=_cart_decimal_text(price),
        subtotal=_cart_decimal_text(subtotal),
    )


def _order_summary(payload: object, *, detail: bool) -> OrderSummary:
    if not isinstance(payload, dict):
        raise ValueError("Order response must be an object.")
    order_id = payload.get("id")
    code = payload.get("codigo")
    order_date = payload.get("data_pedido")
    status = payload.get("status")
    items_payload = payload.get("itens")
    if (
        not isinstance(order_id, int)
        or isinstance(order_id, bool)
        or order_id < 1
        or not isinstance(code, str)
        or not code.strip()
        or not isinstance(order_date, (int, float, str))
        or isinstance(order_date, bool)
        or not isinstance(status, str)
        or status
        not in {
            "AGUARDANDO_PAGAMENTO",
            "PAGAMENTO_CONFIRMADO",
            "EM_PREPARACAO",
            "ENVIADO",
            "ENTREGUE",
            "CANCELADO",
        }
        or not isinstance(items_payload, list)
        or not items_payload
    ):
        raise ValueError("Order response has an invalid identity or status.")
    items = [_order_item_summary(item) for item in items_payload]
    if len({item.variation_id for item in items}) != len(items):
        raise ValueError("Order response contains duplicate variations.")

    subtotal = _cart_decimal(payload.get("subtotal"))
    freight = _cart_decimal(payload.get("valor_frete"))
    total = _cart_decimal(payload.get("valor_total"))
    if (
        subtotal
        != sum(
            (_cart_decimal(item.subtotal) for item in items),
            start=Decimal("0"),
        )
        or total != subtotal + freight
    ):
        raise ValueError("Order totals are inconsistent.")

    payment = payload.get("pagamento")
    if detail:
        if not isinstance(payment, dict):
            raise ValueError("Order payment response is missing.")
        payment_method = payment.get("metodo")
        payment_status = payment.get("status")
        payment_value = _cart_decimal(payment.get("valor"))
        if (
            payment_method not in {"PIX", "CARTAO", "BOLETO"}
            or payment_status not in {"PENDENTE", "APROVADO", "RECUSADO", "CANCELADO"}
            or payment_value != total
        ):
            raise ValueError("Order payment response is inconsistent.")
    else:
        payment_method = ""
        payment_status = ""
        payment_value = total

    return OrderSummary(
        id=order_id,
        code=code,
        order_date=str(order_date),
        status=status,
        order_items=items,
        subtotal=_cart_decimal_text(subtotal),
        freight=_cart_decimal_text(freight),
        total=_cart_decimal_text(total),
        delivery=_checkout_address_snapshot(payload.get("entrega")),
        payment_method=payment_method,
        payment_status=payment_status,
        payment_value=_cart_decimal_text(payment_value),
    )


def _simulated_payment_response(
    payload: object,
    order: OrderSummary,
) -> OrderSummary:
    if not isinstance(payload, dict):
        raise ValueError("Simulated payment response must be an object.")
    payment = payload.get("pagamento")
    if not isinstance(payment, dict):
        raise ValueError("Simulated payment response is missing payment data.")

    order_id = payload.get("pedido_id")
    code = payload.get("codigo")
    order_status = payload.get("pedido_status")
    method = payment.get("metodo")
    payment_status = payment.get("status")
    payment_value = _cart_decimal(payment.get("valor"))
    if (
        payload.get("simulado") is not True
        or not isinstance(payload.get("alterado"), bool)
        or order_id != order.id
        or isinstance(order_id, bool)
        or code != order.code
        or order_status != "PAGAMENTO_CONFIRMADO"
        or method != order.payment_method
        or payment_status != "APROVADO"
        or payment_value != _cart_decimal(order.total)
    ):
        raise ValueError("Simulated payment response is inconsistent.")
    return replace(
        order,
        status="PAGAMENTO_CONFIRMADO",
        payment_status="APROVADO",
        payment_value=_cart_decimal_text(payment_value),
    )


def _cart_mutation_response(
    payload: object,
    *,
    expected_item_id: int | None = None,
    expected_variation_id: int | None = None,
    expected_removed: bool | None = None,
) -> None:
    if not isinstance(payload, dict):
        raise ValueError("Cart mutation response must be an object.")
    item_id = payload.get("id")
    variation_id = payload.get("variacao_produto_id")
    removed = payload.get("removido")
    if (
        not isinstance(item_id, int)
        or isinstance(item_id, bool)
        or item_id < 1
        or (expected_item_id is not None and item_id != expected_item_id)
        or (
            expected_variation_id is not None
            and variation_id != expected_variation_id
        )
        or (
            expected_removed is not None
            and removed is not expected_removed
        )
    ):
        raise ValueError("Cart mutation response does not match the request.")


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
    retry_rate_limit: bool | None = None,
) -> XanoJson:
    headers = {"Accept": "application/json"}
    body = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(payload).encode("utf-8")
    if authorization:
        headers["Authorization"] = authorization

    if retry_rate_limit is None:
        retry_rate_limit = method == "GET"

    attempt = 0
    while True:
        attempt += 1
        request = urllib.request.Request(
            url,
            data=body,
            headers=headers,
            method=method,
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                if response.status < 200 or response.status >= 300:
                    raise ValueError(
                        f"Xano returned unexpected HTTP status {response.status}."
                    )
                response_payload = json.loads(response.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as error:
            if (
                retry_rate_limit
                and error.code == 429
                and attempt < XANO_RATE_LIMIT_MAX_ATTEMPTS
            ):
                wait = _rate_limit_wait_seconds(error)
                error.close()
                time.sleep(wait)
                continue
            raise

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
    retry_rate_limit: bool | None = None,
) -> XanoJson:
    return await asyncio.to_thread(
        _request_xano_json,
        url,
        method=method,
        payload=payload,
        authorization=authorization,
        retry_rate_limit=retry_rate_limit,
    )


def _rate_limit_wait_seconds(error: urllib.error.HTTPError) -> float:
    header = error.headers.get("Retry-After") if error.headers else None
    if header is not None:
        try:
            seconds = float(str(header).strip())
        except (TypeError, ValueError):
            seconds = None
        if seconds is not None and seconds >= 0:
            return min(seconds, XANO_RATE_LIMIT_MAX_WAIT_SECONDS)
    return XANO_RATE_LIMIT_DEFAULT_WAIT_SECONDS


def _public_endpoint_label(url_env: str) -> str:
    return _PUBLIC_ENDPOINT_LABELS.get(url_env, "public_catalog.desconhecido")


def _public_endpoint_status(error: BaseException) -> int | None:
    if isinstance(error, urllib.error.HTTPError):
        return error.code
    return None


@dataclass
class _PublicCatalogCacheEntry:
    categories: list[CatalogEntry]
    products: list[PublicProductEntry]
    expires_at: float


_public_catalog_cache: dict[Any, _PublicCatalogCacheEntry] = {}
_public_catalog_inflight: dict[
    Any, "asyncio.Future[tuple[list[CatalogEntry], list[PublicProductEntry], str]]"
] = {}


def _reset_public_catalog_cache() -> None:
    _public_catalog_cache.clear()
    _public_catalog_inflight.clear()


def _public_catalog_cache_get(key: Any) -> _PublicCatalogCacheEntry | None:
    entry = _public_catalog_cache.get(key)
    if entry is None:
        return None
    if entry.expires_at <= time.monotonic():
        _public_catalog_cache.pop(key, None)
        return None
    return entry


def _public_catalog_cache_put(
    key: Any,
    categories: list[CatalogEntry],
    products: list[PublicProductEntry],
) -> None:
    _public_catalog_cache[key] = _PublicCatalogCacheEntry(
        categories=list(categories),
        products=list(products),
        expires_at=time.monotonic() + PUBLIC_CATALOG_CACHE_TTL_SECONDS,
    )


def _public_search_term(value: object) -> str:
    """Normalize public search without accepting arbitrary form objects."""
    return value.strip()[:100] if isinstance(value, str) else ""


async def _load_public_catalog_with_cache(
    state: "State",
    category_id: str,
    search: str = "",
) -> tuple[list[CatalogEntry], list[PublicProductEntry], str]:
    search_term = search.strip()
    key = (category_id, search_term)
    cached = _public_catalog_cache_get(key)
    if cached is not None:
        return list(cached.categories), list(cached.products), category_id

    pending = _public_catalog_inflight.get(key)
    if pending is not None:
        return await pending

    future: "asyncio.Future[tuple[list[CatalogEntry], list[PublicProductEntry], str]]" = (
        asyncio.get_running_loop().create_future()
    )
    _public_catalog_inflight[key] = future
    try:
        categories, products, category_id = await state._load_public_catalog_data(
            category_id,
            search_term,
        )
        result = (categories, products, category_id)
        _public_catalog_cache_put(key, categories, products)
        future.set_result(result)
        return result
    except BaseException as error:
        if not future.done():
            future.set_exception(error)
            future.exception()
        raise
    finally:
        _public_catalog_inflight.pop(key, None)


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


def _public_catalog_categories(payload: XanoJson) -> list[CatalogEntry]:
    categories = _catalog_entries(payload)
    if any(category.status != "ATIVO" for category in categories):
        raise ValueError("Public catalog returned an inactive category.")
    return categories


def _public_product_entry(
    payload: object,
    *,
    image_url: str = "",
    variations: list[ProductVariation] | None = None,
) -> PublicProductEntry:
    if not isinstance(payload, dict):
        raise ValueError("Public product response must be an object.")

    product_id = payload.get("id")
    name = payload.get("nome")
    description = payload.get("descricao")
    specifications = payload.get("especificacoes_tecnicas")
    category_id = payload.get("categoria_id")
    brand_id = payload.get("marca_id")
    status = payload.get("status")
    category_name = payload.get("categoria_nome")
    brand_name = payload.get("marca_nome")
    item_image_url = payload.get("image_url", "")
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
        or (category_name is not None and not isinstance(category_name, str))
        or (brand_name is not None and not isinstance(brand_name, str))
        or (item_image_url is not None and not isinstance(item_image_url, str))
        or "imagem_principal" in payload
        or status != "ATIVO"
    ):
        raise ValueError("Public product response has an invalid record.")

    if item_image_url:
        parsed_url = urlparse(item_image_url)
        if parsed_url.scheme != "https" or not parsed_url.netloc:
            raise ValueError("Public image URL must be an HTTPS URL.")

    final_image_url = image_url or item_image_url or ""

    return PublicProductEntry(
        id=product_id,
        name=name or "",
        description=description or "",
        technical_specifications=specifications or "",
        category_name=category_name or "",
        brand_name=brand_name or "",
        image_url=final_image_url,
        variations=variations or [],
    )


def _public_catalog_products(payload: XanoJson) -> list[PublicProductEntry]:
    if not isinstance(payload, list):
        raise ValueError("Public product list response must be an array.")
    return [_public_product_entry(item) for item in payload]


def _public_product_details(
    payload: XanoJson,
    *,
    image_url: str,
) -> PublicProductEntry:
    if not isinstance(payload, dict) or not isinstance(
        payload.get("product"), dict
    ):
        raise ValueError("Public product detail response must be an object.")
    product = payload["product"] | {
        "categoria_nome": payload.get("category_name"),
        "marca_nome": payload.get("brand_name"),
    }
    product_id = product.get("id")
    variation_payload = payload.get("variations")
    if not isinstance(product_id, int) or isinstance(product_id, bool):
        raise ValueError("Public product detail has an invalid identifier.")
    if not isinstance(variation_payload, list):
        raise ValueError("Public product variations must be an array.")
    variations = [_product_variation(item) for item in variation_payload]
    if any(
        variation.status != "ATIVO" or variation.product_id != product_id
        for variation in variations
    ):
        raise ValueError("Public product detail returned an invalid variation.")
    return _public_product_entry(
        product,
        image_url=image_url,
        variations=variations,
    )


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


@dataclass(frozen=True)
class BulkImportRow:
    line: int
    product_name: str
    product_description: str
    product_specifications: str
    category_name: str
    brand_name: str
    variation_name: str
    sku: str
    price: str
    quantity: str
    status: str
    reason: str


@dataclass(frozen=True)
class BulkImportVariation:
    name: str
    sku: str
    price: float
    quantity: int


@dataclass(frozen=True)
class BulkImportGroup:
    product_name: str
    description: str
    specifications: str
    category_name: str
    brand_name: str
    variations: tuple[BulkImportVariation, ...]


@dataclass(frozen=True)
class BulkImportResult:
    product_name: str
    outcome: str
    detail: str


_XLSX_MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
_XLSX_REL_NS = (
    "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
)
_XLSX_DATE_FORMAT_IDS = frozenset(
    {14, 15, 16, 17, 18, 19, 20, 21, 22, 27, 30, 36, 45, 46, 47, 50, 57}
)


def _xlsx_tag(name: str) -> str:
    return f"{{{_XLSX_MAIN_NS}}}{name}"


def _bulk_import_decimal_text(value: str) -> str:
    text = value.strip().replace(" ", "")
    if not text:
        raise ValueError("valor vazio")
    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    elif "," in text:
        text = text.replace(",", ".")
    return text


def _bulk_import_price(value: str) -> float:
    try:
        number = Decimal(_bulk_import_decimal_text(value))
    except InvalidOperation as error:
        raise ValueError("preço não numérico") from error
    if not number.is_finite() or number <= 0:
        raise ValueError("o preço deve ser maior que zero")
    if number.as_tuple().exponent < -2:
        raise ValueError("o preço deve ter no máximo duas casas decimais")
    converted = float(number)
    if not math.isfinite(converted):
        raise ValueError("preço não numérico")
    return converted


def _bulk_import_quantity(value: str) -> int:
    try:
        number = Decimal(_bulk_import_decimal_text(value))
    except InvalidOperation as error:
        raise ValueError("quantidade não numérica") from error
    if (
        not number.is_finite()
        or number < 0
        or number != number.to_integral_value()
    ):
        raise ValueError("a quantidade deve ser um inteiro maior ou igual a zero")
    return int(number)


def _bulk_import_csv_delimiter(sample: str) -> str:
    try:
        return csv.Sniffer().sniff(sample, delimiters=";,").delimiter
    except csv.Error:
        lines = sample.splitlines()
        first_line = lines[0] if lines else ""
        if first_line.count(";") > first_line.count(","):
            return ";"
        return ","


def _bulk_import_rows_from_csv(data: bytes) -> list[list[str]]:
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError("O arquivo CSV deve estar codificado em UTF-8.") from error
    if not text.strip():
        raise ValueError("O arquivo está vazio.")
    reader = csv.reader(
        io.StringIO(text),
        delimiter=_bulk_import_csv_delimiter(text[:4096]),
    )
    return [list(row) for row in reader]


def _bulk_import_xlsx_shared_strings(archive: zipfile.ZipFile) -> list[str]:
    try:
        root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
    except (KeyError, ElementTree.ParseError):
        return []
    strings: list[str] = []
    for item in root.findall(_xlsx_tag("si")):
        strings.append(
            "".join(node.text or "" for node in item.iter(_xlsx_tag("t")))
        )
    return strings


def _bulk_import_xlsx_format_is_date(format_code: str) -> bool:
    cleaned = re.sub(r'"[^"]*"|\[[^\]]*\]|\\.', "", format_code)
    return bool(re.search(r"[yYmMdDhHsS]", cleaned)) and not re.search(
        r"[0#]", cleaned
    )


def _bulk_import_xlsx_date_styles(archive: zipfile.ZipFile) -> set[int]:
    try:
        root = ElementTree.fromstring(archive.read("xl/styles.xml"))
    except (KeyError, ElementTree.ParseError):
        return set()
    custom_formats: dict[int, str] = {}
    formats = root.find(_xlsx_tag("numFmts"))
    if formats is not None:
        for num_format in formats.findall(_xlsx_tag("numFmt")):
            try:
                custom_formats[int(num_format.get("numFmtId"))] = (
                    num_format.get("formatCode") or ""
                )
            except (TypeError, ValueError):
                continue
    date_styles: set[int] = set()
    cell_formats = root.find(_xlsx_tag("cellXfs"))
    if cell_formats is not None:
        for index, cell_format in enumerate(
            cell_formats.findall(_xlsx_tag("xf"))
        ):
            try:
                num_format_id = int(cell_format.get("numFmtId"))
            except (TypeError, ValueError):
                continue
            if num_format_id in _XLSX_DATE_FORMAT_IDS or _bulk_import_xlsx_format_is_date(
                custom_formats.get(num_format_id, "")
            ):
                date_styles.add(index)
    return date_styles


def _bulk_import_xlsx_first_sheet_path(archive: zipfile.ZipFile) -> str:
    try:
        workbook = ElementTree.fromstring(archive.read("xl/workbook.xml"))
        sheets = workbook.find(_xlsx_tag("sheets"))
        if sheets is not None:
            first_sheet = sheets.find(_xlsx_tag("sheet"))
            if first_sheet is not None:
                relation_id = first_sheet.get(f"{{{_XLSX_REL_NS}}}id")
                if relation_id:
                    relations = ElementTree.fromstring(
                        archive.read("xl/_rels/workbook.xml.rels")
                    )
                    for relation in relations:
                        if relation.get("Id") == relation_id:
                            target = (relation.get("Target") or "").lstrip("/")
                            if not target:
                                break
                            return target if target.startswith("xl/") else "xl/" + target
    except (KeyError, ElementTree.ParseError):
        pass
    return "xl/worksheets/sheet1.xml"


def _bulk_import_xlsx_column_index(reference: str | None) -> int:
    match = re.match(r"([A-Za-z]+)", reference or "")
    if not match:
        raise ValueError("O arquivo XLSX possui uma célula com referência inválida.")
    index = 0
    for letter in match.group(1).upper():
        index = index * 26 + (ord(letter) - ord("A") + 1)
    return index - 1


def _bulk_import_rows_from_xlsx(data: bytes) -> list[list[str]]:
    try:
        archive = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile as error:
        raise ValueError("O arquivo XLSX é inválido.") from error
    with archive:
        shared_strings = _bulk_import_xlsx_shared_strings(archive)
        date_styles = _bulk_import_xlsx_date_styles(archive)
        try:
            sheet = ElementTree.fromstring(
                archive.read(_bulk_import_xlsx_first_sheet_path(archive))
            )
        except (KeyError, ElementTree.ParseError) as error:
            raise ValueError(
                "O arquivo XLSX não possui uma planilha legível."
            ) from error
        rows: list[list[str]] = []
        for row in sheet.iter(_xlsx_tag("row")):
            cells: dict[int, str] = {}
            for cell in row.findall(_xlsx_tag("c")):
                if cell.find(_xlsx_tag("f")) is not None:
                    raise ValueError("O arquivo XLSX não pode conter fórmulas.")
                cell_type = cell.get("t")
                style = cell.get("s")
                if cell_type in {"b", "e", "str", "d"}:
                    raise ValueError(
                        "O arquivo XLSX possui um tipo de célula não suportado."
                    )
                inline = cell.find(_xlsx_tag("is"))
                if inline is not None:
                    cells[_bulk_import_xlsx_column_index(cell.get("r"))] = "".join(
                        node.text or "" for node in inline.iter(_xlsx_tag("t"))
                    )
                    continue
                value_node = cell.find(_xlsx_tag("v"))
                raw = value_node.text if value_node is not None else ""
                if cell_type == "s":
                    try:
                        cells[_bulk_import_xlsx_column_index(cell.get("r"))] = (
                            shared_strings[int(raw)]
                        )
                    except (TypeError, ValueError, IndexError) as error:
                        raise ValueError(
                            "O arquivo XLSX possui uma célula de texto inválida."
                        ) from error
                    continue
                if style is not None:
                    try:
                        is_date = int(style) in date_styles
                    except (TypeError, ValueError):
                        is_date = False
                    if is_date:
                        raise ValueError("O arquivo XLSX não pode conter datas.")
                cells[_bulk_import_xlsx_column_index(cell.get("r"))] = raw or ""
            width = max(cells) + 1 if cells else 0
            rows.append([cells.get(index, "") for index in range(width)])
        if not rows:
            raise ValueError("O arquivo XLSX está vazio.")
        return rows


def _bulk_import_normalize_row(row: list[str]) -> list[str]:
    values = [str(value).strip() for value in row]
    if len(values) < len(BULK_IMPORT_HEADERS):
        values += [""] * (len(BULK_IMPORT_HEADERS) - len(values))
    return values[: len(BULK_IMPORT_HEADERS)]


def _bulk_import_parse(file_name: str, data: bytes) -> list[list[str]]:
    extension = os.path.splitext(file_name)[1].lower()
    if extension == ".xls":
        raise ValueError("O formato .xls não é suportado; use .xlsx.")
    if extension not in {".csv", ".xlsx"}:
        raise ValueError("Formato não suportado. Envie um arquivo .csv ou .xlsx.")
    if len(data) > BULK_IMPORT_MAX_BYTES:
        raise ValueError("O arquivo excede o limite de 2 MB.")
    if not data:
        raise ValueError("O arquivo está vazio.")
    rows = (
        _bulk_import_rows_from_csv(data)
        if extension == ".csv"
        else _bulk_import_rows_from_xlsx(data)
    )
    if not rows:
        raise ValueError("O arquivo está vazio.")
    header = tuple(str(value).strip() for value in rows[0])
    if header != BULK_IMPORT_HEADERS:
        raise ValueError(
            "Cabeçalhos inválidos. Use exatamente: "
            + ", ".join(BULK_IMPORT_HEADERS)
            + "."
        )
    data_rows = [
        row for row in rows[1:] if any(str(value).strip() for value in row)
    ]
    if not data_rows:
        raise ValueError("O arquivo não possui linhas de dados.")
    if len(data_rows) > BULK_IMPORT_MAX_ROWS:
        raise ValueError(
            f"O arquivo excede o limite de {BULK_IMPORT_MAX_ROWS} linhas."
        )
    distinct_products = {
        str(row[0]).strip() for row in data_rows if row and str(row[0]).strip()
    }
    if len(distinct_products) > BULK_IMPORT_MAX_PRODUCTS:
        raise ValueError(
            f"O arquivo excede o limite de {BULK_IMPORT_MAX_PRODUCTS} produtos."
        )
    return data_rows


def _bulk_import_record_status(record: dict[str, object]) -> str:
    if record["error"]:
        return BULK_IMPORT_ERROR_STATUS
    if record["duplicate"]:
        return BULK_IMPORT_DUPLICATE_STATUS
    return BULK_IMPORT_VALID_STATUS


def _bulk_import_validate(
    data_rows: list[list[str]],
    categories: list[CatalogEntry],
    brands: list[CatalogEntry],
    products: list[ProductEntry],
) -> tuple[list[BulkImportRow], list[BulkImportGroup]]:
    category_by_name = {entry.name.strip(): entry for entry in categories}
    brand_by_name = {entry.name.strip(): entry for entry in brands}
    existing_names = {
        product.name.strip() for product in products if product.name.strip()
    }
    existing_skus = {
        variation.sku.strip()
        for product in products
        for variation in product.variations
        if variation.sku.strip()
    }

    records: list[dict[str, object]] = []
    for offset, raw in enumerate(data_rows):
        values = _bulk_import_normalize_row(raw)
        record: dict[str, object] = {
            "line": offset + 2,
            "produto_nome": values[0],
            "produto_descricao": values[1],
            "produto_especificacoes_tecnicas": values[2],
            "categoria_nome": values[3],
            "marca_nome": values[4],
            "variacao_nome": values[5],
            "sku": values[6],
            "preco": values[7],
            "quantidade_disponivel": values[8],
            "error": "",
            "duplicate": False,
            "duplicate_reason": "",
            "price": None,
            "quantity": None,
        }
        missing = [
            label
            for key, label in BULK_IMPORT_REQUIRED_FIELDS.items()
            if not record[key]
        ]
        if missing:
            record["error"] = "Campos obrigatórios ausentes: " + ", ".join(missing) + "."
            records.append(record)
            continue
        try:
            record["price"] = _bulk_import_price(str(record["preco"]))
        except ValueError as error:
            record["error"] = f"Preço inválido: {error}."
            records.append(record)
            continue
        try:
            record["quantity"] = _bulk_import_quantity(
                str(record["quantidade_disponivel"])
            )
        except ValueError as error:
            record["error"] = f"Quantidade inválida: {error}."
            records.append(record)
            continue
        records.append(record)

    groups_by_name: dict[str, list[dict[str, object]]] = {}
    for record in records:
        name = str(record["produto_nome"])
        if name:
            groups_by_name.setdefault(name, []).append(record)
    for group_records in groups_by_name.values():
        signatures = {
            (
                record["produto_descricao"],
                record["produto_especificacoes_tecnicas"],
                record["categoria_nome"],
                record["marca_nome"],
            )
            for record in group_records
        }
        if len(signatures) > 1:
            for record in group_records:
                if not record["error"]:
                    record["error"] = (
                        "Agrupamento inconsistente: descrição, especificações, "
                        "categoria ou marca divergem para o mesmo produto."
                    )

    seen_skus: set[str] = set()
    for record in records:
        sku = str(record["sku"]).strip()
        if not sku:
            continue
        if sku in seen_skus:
            if not record["error"]:
                record["error"] = "SKU duplicado no arquivo."
        else:
            seen_skus.add(sku)

    for record in records:
        if record["error"]:
            continue
        if str(record["produto_nome"]) in existing_names:
            record["duplicate"] = True
            record["duplicate_reason"] = "Produto já existente (pulado)."
            continue
        category = category_by_name.get(str(record["categoria_nome"]))
        if category is None:
            record["error"] = "Categoria não encontrada no catálogo."
            continue
        if category.status != "ATIVO":
            record["error"] = "Categoria inativa."
            continue
        brand = brand_by_name.get(str(record["marca_nome"]))
        if brand is None:
            record["error"] = "Marca não encontrada no catálogo."
            continue
        if brand.status != "ATIVO":
            record["error"] = "Marca inativa."
            continue
        if str(record["sku"]).strip() in existing_skus:
            record["duplicate"] = True
            record["duplicate_reason"] = "SKU já existente no catálogo (pulado)."
            continue

    preview: list[BulkImportRow] = []
    for record in records:
        status = _bulk_import_record_status(record)
        reason = str(record["error"]) if record["error"] else str(record["duplicate_reason"])
        preview.append(
            BulkImportRow(
                line=int(record["line"]),
                product_name=str(record["produto_nome"]),
                product_description=str(record["produto_descricao"]),
                product_specifications=str(record["produto_especificacoes_tecnicas"]),
                category_name=str(record["categoria_nome"]),
                brand_name=str(record["marca_nome"]),
                variation_name=str(record["variacao_nome"]),
                sku=str(record["sku"]),
                price=str(record["preco"]),
                quantity=str(record["quantidade_disponivel"]),
                status=status,
                reason=reason,
            )
        )

    valid_groups: list[BulkImportGroup] = []
    for name, group_records in groups_by_name.items():
        if not all(
            _bulk_import_record_status(record) == BULK_IMPORT_VALID_STATUS
            for record in group_records
        ):
            continue
        variations = tuple(
            BulkImportVariation(
                name=str(record["variacao_nome"]),
                sku=str(record["sku"]).strip(),
                price=float(record["price"]),
                quantity=int(record["quantity"]),
            )
            for record in group_records
        )
        valid_groups.append(
            BulkImportGroup(
                product_name=name,
                description=str(group_records[0]["produto_descricao"]),
                specifications=str(
                    group_records[0]["produto_especificacoes_tecnicas"]
                ),
                category_name=str(group_records[0]["categoria_nome"]),
                brand_name=str(group_records[0]["marca_nome"]),
                variations=variations,
            )
        )
    return preview, valid_groups


def _bulk_import_failure_message(error: Exception) -> str:
    if isinstance(error, ValueError) and str(error).startswith(
        "Missing required environment variable:"
    ):
        variable = str(error).split(":", maxsplit=1)[1].strip().rstrip(".")
        return f"Configuração ausente: {variable}."
    if isinstance(error, urllib.error.HTTPError):
        if error.code in {401, 403}:
            return "Você não tem autorização para essa operação."
        if error.code == 429:
            return "Limite de requisições do catálogo atingido. Tente novamente mais tarde."
    if isinstance(error, ValueError):
        return str(error)
    return "Não foi possível concluir a operação. Tente novamente."


def _bulk_import_group_failure_message(error: Exception) -> str:
    if isinstance(error, urllib.error.HTTPError) and error.code == 429:
        return "Limite de requisições atingido."
    if isinstance(error, ValueError):
        return str(error)
    return "Falha ao gravar o produto."


def _bulk_import_error_body(error: urllib.error.HTTPError) -> str:
    try:
        return error.read().decode("utf-8", errors="replace")
    except (AttributeError, OSError, ValueError):
        return ""


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
    customer_registration_status: str = "idle"
    customer_registration_message: str = ""
    customer_login_status: str = "idle"
    customer_login_message: str = ""
    customer_authenticated: bool = False
    customer_session_status: str = "idle"
    customer_session_message: str = ""
    customer_id: int | None = None
    customer_name: str = ""
    customer_cpf: str = ""
    customer_email: str = ""
    customer_phone: str = ""
    _customer_auth_token: str = ""
    customer_profile_message: str = ""
    cart_id: int | None = None
    cart_items: list[CartItemEntry] = []
    cart_total: str = "0"
    cart_loading: bool = False
    cart_message: str = ""
    checkout_address_id: str = ""
    _checkout_review: CheckoutReview | None = None
    checkout_review_ready: bool = False
    checkout_review_items: list[CheckoutItemEntry] = []
    checkout_address_label: str = ""
    checkout_address_street: str = ""
    checkout_address_number: str = ""
    checkout_address_neighborhood: str = ""
    checkout_address_city: str = ""
    checkout_address_state: str = ""
    checkout_address_cep: str = ""
    checkout_subtotal: str = "0"
    checkout_freight: str = "0"
    checkout_total: str = "0"
    checkout_loading: bool = False
    checkout_message: str = ""
    checkout_method: str = "PIX"
    orders: list[OrderSummary] = []
    orders_loading: bool = False
    orders_message: str = ""
    _selected_order: OrderSummary | None = None
    selected_order_present: bool = False
    selected_order_code: str = ""
    selected_order_status: str = ""
    selected_order_delivery_label: str = ""
    selected_order_delivery_street: str = ""
    selected_order_delivery_number: str = ""
    selected_order_delivery_neighborhood: str = ""
    selected_order_delivery_city: str = ""
    selected_order_delivery_state: str = ""
    selected_order_delivery_cep: str = ""
    selected_order_items: list[OrderItemSummary] = []
    selected_order_subtotal: str = "0"
    selected_order_freight: str = "0"
    selected_order_total: str = "0"
    selected_order_payment_method: str = ""
    selected_order_payment_status: str = ""
    order_loading: bool = False
    payment_simulating: bool = False
    payment_message: str = ""
    customer_addresses: list[CustomerAddressEntry] = []
    customer_addresses_loading: bool = False
    customer_addresses_message: str = ""
    customer_address_editing_id: int | None = None
    customer_address_form_cep: str = ""
    customer_address_form_street: str = ""
    customer_address_form_number: str = ""
    customer_address_form_complement: str = ""
    customer_address_form_neighborhood: str = ""
    customer_address_form_city: str = ""
    customer_address_form_state: str = ""
    customer_address_form_label: str = ""
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
    public_categories: list[CatalogEntry] = []
    public_products: list[PublicProductEntry] = []
    public_catalog_loading: bool = False
    public_catalog_loaded: bool = False
    public_catalog_message: str = ""
    public_category_id: str = ""
    public_catalog_search: str = ""
    public_catalog_search_input: str = ""
    public_product_loading: bool = False
    public_product_message: str = ""
    public_product_detail_id: int | None = None
    public_selected_product: PublicProductEntry | None = None
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
    bulk_import_preview: list[BulkImportRow] = []
    bulk_import_report: list[BulkImportResult] = []
    bulk_import_message: str = ""
    bulk_import_progress: str = ""
    bulk_import_loading: bool = False
    bulk_import_has_valid: bool = False
    bulk_import_cancel_requested: bool = False
    _bulk_import_valid_groups: list[BulkImportGroup] = []
    _bulk_import_last_request_at: float = 0.0
    _bulk_import_in_progress: bool = False

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
        self.bulk_import_preview = []
        self.bulk_import_report = []
        self.bulk_import_message = ""
        self.bulk_import_progress = ""
        self.bulk_import_loading = False
        self.bulk_import_has_valid = False
        self.bulk_import_cancel_requested = False
        self._bulk_import_valid_groups = []
        self._bulk_import_last_request_at = 0.0
        self._bulk_import_in_progress = False

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
        retry_rate_limit: bool | None = None,
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
        request_kwargs: dict[str, object] = {
            "method": method,
            "payload": payload,
            "authorization": "Bearer " + self._auth_token,
        }
        if retry_rate_limit is not None:
            request_kwargs["retry_rate_limit"] = retry_rate_limit
        return await _server_side_xano_request(url, **request_kwargs)

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

    async def _public_catalog_request(
        self,
        url_env: str,
        *,
        record_id: int | None = None,
        path_suffix: str = "",
        query_params: dict[str, str] | None = None,
    ) -> XanoJson:
        url = _required_environment_url(url_env).rstrip("/")
        if record_id is not None:
            url = f"{url}/{record_id}{path_suffix}"
        if query_params:
            url = f"{url}?{urlencode(query_params)}"
        try:
            return await _server_side_xano_request(url, authorization=None)
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ) as error:
            PUBLIC_CATALOG_LOGGER.warning(
                "Falha no endpoint lógico '%s' do catálogo público (status=%s).",
                _public_endpoint_label(url_env),
                _public_endpoint_status(error),
            )
            if isinstance(error, urllib.error.HTTPError):
                error.close()
            raise

    async def _public_product_image(self, product_id: int) -> str:
        payload = await self._public_catalog_request(
            XANO_PUBLIC_PRODUCT_IMAGE_URL_ENV,
            record_id=product_id,
            path_suffix="/image",
        )
        if not isinstance(payload, dict):
            raise ValueError("Public image response must be an object.")
        image_url = payload.get("image_url")
        if image_url is None:
            return ""
        if not isinstance(image_url, str):
            raise ValueError("Public image URL has an invalid value.")
        parsed_url = urlparse(image_url)
        if parsed_url.scheme != "https" or not parsed_url.netloc:
            raise ValueError("Public image URL must be an HTTPS URL.")
        return image_url

    async def _fetch_public_products(
        self,
        category_id: str = "",
        search: str = "",
    ) -> list[PublicProductEntry]:
        query_params = {}
        if category_id:
            query_params["category_id"] = category_id
        if search.strip():
            query_params["q"] = search.strip()
        payload = await self._public_catalog_request(
            XANO_PUBLIC_PRODUCTS_URL_ENV,
            query_params=query_params if query_params else None,
        )
        products = _public_catalog_products(payload)
        return [
            replace(
                product,
                image_url=resolve_demo_image_named(
                    product.name,
                    product.variations[0].sku if product.variations else "",
                    product.image_url,
                ),
            )
            for product in products
        ]

    async def _load_public_catalog_data(
        self,
        category_id: str,
        search: str = "",
    ) -> tuple[list[CatalogEntry], list[PublicProductEntry], str]:
        categories_payload = await self._public_catalog_request(
            XANO_PUBLIC_CATEGORIES_URL_ENV
        )
        categories = _public_catalog_categories(categories_payload)
        if category_id and not any(
            str(category.id) == category_id for category in categories
        ):
            category_id = ""
        products = await self._fetch_public_products(category_id, search)
        return categories, products, category_id

    @rx.event
    async def load_public_catalog(self):
        self.public_catalog_loading = True
        self.public_catalog_message = ""
        try:
            search = getattr(self, "public_catalog_search", "").strip()
            categories, products, category_id = await _load_public_catalog_with_cache(
                self,
                self.public_category_id.strip(),
                search,
            )
            self.public_category_id = category_id
            self.public_categories = categories
            self.public_products = products
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ):
            self.public_catalog_message = (
                "Não foi possível carregar o catálogo. Tente novamente."
            )
        finally:
            self.public_catalog_loading = False
            self.public_catalog_loaded = True

    @rx.event
    async def enter_public_home(self):
        self.public_category_id = ""
        self.public_catalog_search = ""
        self.public_catalog_search_input = ""
        self.close_public_product_details()
        await self.load_public_catalog()

    @rx.event
    async def enter_public_catalog(self):
        params = self.router.url.query_parameters
        category = params.get("category_id", "")
        self.public_category_id = category if category.isascii() and category.isdigit() and len(category) <= 10 else ""
        self.public_catalog_search = _public_search_term(params.get("q", ""))
        self.public_catalog_search_input = self.public_catalog_search
        self.close_public_product_details()
        await self.load_public_catalog()
        product = params.get("product_id", "")
        if product.isascii() and product.isdigit() and len(product) <= 10 and int(product) > 0:
            await self.load_public_product_details(int(product))

    def _public_catalog_navigation(self):
        params = {}
        if self.public_category_id:
            params["category_id"] = self.public_category_id
        if self.public_catalog_search:
            params["q"] = self.public_catalog_search
        destination = "/catalogo" + ("?" + urlencode(params) if params else "")
        current = self.router.url.path + ("?" + self.router.url.query if self.router.url.query else "")
        return State.load_public_catalog if current == destination else rx.redirect(destination)

    @rx.event
    def set_public_catalog_search_input(self, value: str):
        self.public_catalog_search_input = value[:100]

    @rx.event
    def search_public_catalog(self, form_data: dict[str, Any]):
        self.public_catalog_search = _public_search_term(form_data.get("search", ""))
        self.public_catalog_search_input = self.public_catalog_search
        self.close_public_product_details()
        self.public_catalog_loading = True
        return self._public_catalog_navigation()

    @rx.event
    def filter_public_catalog(self, category_id: str):
        self.public_category_id = category_id
        self.public_catalog_search_input = self.public_catalog_search
        self.close_public_product_details()
        self.public_catalog_loading = True
        return self._public_catalog_navigation()

    @rx.event
    def clear_public_catalog_filters(self):
        self.public_category_id = ""
        self.public_catalog_search = ""
        self.public_catalog_search_input = ""
        self.close_public_product_details()
        self.public_catalog_loading = True
        return self._public_catalog_navigation()

    @rx.event
    async def load_public_product_details(self, product_id: int):
        self.public_product_loading = True
        self.public_product_message = ""
        self.public_product_detail_id = product_id
        self.public_selected_product = None
        try:
            details = await self._public_catalog_request(
                XANO_PUBLIC_PRODUCT_DETAILS_URL_ENV,
                record_id=product_id,
            )
            image_url = await self._public_product_image(product_id)
            product_payload = details.get("product") if isinstance(details, dict) else None
            variations_payload = details.get("variations") if isinstance(details, dict) else None
            first_sku = ""
            if isinstance(variations_payload, list) and variations_payload:
                first = variations_payload[0]
                if isinstance(first, dict):
                    sku = first.get("sku")
                    if isinstance(sku, str):
                        first_sku = sku
            product_name = ""
            if isinstance(product_payload, dict):
                nome = product_payload.get("nome")
                if isinstance(nome, str):
                    product_name = nome
            self.public_selected_product = _public_product_details(
                details,
                image_url=resolve_demo_image_named(
                    product_name,
                    first_sku,
                    image_url,
                ),
            )
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ):
            self.public_product_message = (
                "Não foi possível carregar os detalhes do produto. Tente novamente."
            )
        finally:
            self.public_product_loading = False

    @rx.event
    def close_public_product_details(self):
        self.public_selected_product = None
        self.public_product_message = ""
        self.public_product_detail_id = None

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

    def _bulk_import_is_admin(self) -> bool:
        return (
            bool(self._auth_token)
            and self.is_authenticated
            and self.session_status == "success"
            and self.user_role == "ADMINISTRADOR"
            and self.user_status == "ATIVO"
        )

    async def _bulk_import_wait(self) -> None:
        async with self:
            last_request_at = self._bulk_import_last_request_at
        if last_request_at:
            elapsed = time.monotonic() - last_request_at
            remaining = BULK_IMPORT_REQUEST_INTERVAL_SECONDS - elapsed
            if remaining > 0:
                await asyncio.sleep(remaining)
        async with self:
            self._bulk_import_last_request_at = time.monotonic()

    async def _bulk_import_request(
        self,
        collection_url_env: str,
        *,
        method: str = "GET",
        payload: dict[str, object] | None = None,
        throttle: bool = True,
    ) -> XanoJson:
        if throttle:
            await self._bulk_import_wait()
        return await self._catalog_request(
            collection_url_env,
            method=method,
            payload=payload,
            retry_rate_limit=True,
        )

    async def _bulk_import_load_catalog(
        self,
    ) -> tuple[list[CatalogEntry], list[CatalogEntry], list[ProductEntry]]:
        categories = _catalog_entries(
            await self._bulk_import_request(XANO_CATEGORIES_URL_ENV)
        )
        brands = _catalog_entries(
            await self._bulk_import_request(XANO_BRANDS_URL_ENV)
        )
        products_payload = await self._bulk_import_request(XANO_PRODUCTS_URL_ENV)
        variations_payload = await self._bulk_import_request(
            XANO_VARIATIONS_URL_ENV
        )
        products = _product_entries(
            products_payload, variations_payload, categories, brands
        )
        return categories, brands, products

    @rx.event
    async def preview_bulk_import(self, files: list[rx.UploadFile]):
        if self.bulk_import_loading or self._bulk_import_in_progress:
            self.bulk_import_message = "Aguarde a conclusão da operação em andamento."
            return
        self.bulk_import_message = ""
        self.bulk_import_progress = ""
        self.bulk_import_preview = []
        self.bulk_import_report = []
        self.bulk_import_has_valid = False
        self._bulk_import_valid_groups = []
        if not self._bulk_import_is_admin():
            self.bulk_import_message = "Você não tem autorização para essa operação."
            return
        if len(files) != 1:
            self.bulk_import_message = "Selecione exatamente um arquivo."
            return
        self.bulk_import_loading = True
        try:
            file = files[0]
            data = await file.read()
            data_rows = _bulk_import_parse(file.name, data)
            self._bulk_import_last_request_at = time.monotonic()
            categories, brands, products = await self._bulk_import_load_catalog()
            preview, groups = _bulk_import_validate(
                data_rows, categories, brands, products
            )
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ) as error:
            self.bulk_import_message = _bulk_import_failure_message(error)
            return
        finally:
            self.bulk_import_loading = False
        self.bulk_import_preview = preview
        self._bulk_import_valid_groups = groups
        self.bulk_import_has_valid = bool(groups)
        valid_count = sum(
            1 for row in preview if row.status == BULK_IMPORT_VALID_STATUS
        )
        self.bulk_import_message = (
            f"Pré-visualização: {len(preview)} linha(s), "
            f"{valid_count} válida(s), {len(groups)} produto(s) prontos."
        )
    @rx.event(background=True)
    async def confirm_bulk_import(self):
        async with self:
            if not self._bulk_import_is_admin():
                self.bulk_import_message = (
                    "Você não tem autorização para essa operação."
                )
                return
            if not self._bulk_import_valid_groups:
                self.bulk_import_message = "Nenhuma linha válida para importar."
                return
            if self._bulk_import_in_progress or self.bulk_import_loading:
                return
            self._bulk_import_in_progress = True
            self.bulk_import_loading = True
            self.bulk_import_message = ""
            self.bulk_import_progress = "Carregando catálogo..."
            self.bulk_import_report = []
            self.bulk_import_cancel_requested = False
            self._bulk_import_last_request_at = time.monotonic()
            groups = list(self._bulk_import_valid_groups)

        results: list[BulkImportResult] = []
        created = 0
        skipped = 0
        failed = 0
        authorization_failure = False
        cancel_requested = False
        try:
            try:
                categories, brands, products = await self._bulk_import_load_catalog()
            except (
                urllib.error.HTTPError,
                urllib.error.URLError,
                TimeoutError,
                ValueError,
                json.JSONDecodeError,
            ) as error:
                async with self:
                    self.bulk_import_message = _bulk_import_failure_message(error)
                return

            category_by_name = {entry.name.strip(): entry for entry in categories}
            brand_by_name = {entry.name.strip(): entry for entry in brands}
            existing_names = {
                product.name.strip() for product in products if product.name.strip()
            }

            for index, group in enumerate(groups, start=1):
                async with self:
                    if self.bulk_import_cancel_requested:
                        cancel_requested = True
                        break
                    self.bulk_import_progress = (
                        f"Processando {index}/{len(groups)}: {group.product_name} "
                        f"(criados: {created}, pulados: {skipped}, "
                        f"falhas: {failed})"
                    )
                if group.product_name in existing_names:
                    results.append(
                        BulkImportResult(
                            group.product_name,
                            BULK_IMPORT_SKIPPED_OUTCOME,
                            "Produto já existente.",
                        )
                    )
                    skipped += 1
                    continue
                category = category_by_name.get(group.category_name)
                brand = brand_by_name.get(group.brand_name)
                if (
                    category is None
                    or brand is None
                    or category.status != "ATIVO"
                    or brand.status != "ATIVO"
                ):
                    results.append(
                        BulkImportResult(
                            group.product_name,
                            BULK_IMPORT_FAILED_OUTCOME,
                            "Categoria ou marca indisponível.",
                        )
                    )
                    failed += 1
                    continue
                payload: dict[str, object] = {
                    "nome": group.product_name,
                    "descricao": group.description,
                    "especificacoes_tecnicas": group.specifications,
                    "categoria_id": category.id,
                    "marca_id": brand.id,
                    "variacoes": [
                        {
                            "nome_ou_descricao": variation.name,
                            "sku": variation.sku,
                            "preco": variation.price,
                            "quantidade_disponivel": variation.quantity,
                        }
                        for variation in group.variations
                    ],
                }
                await self._bulk_import_wait()
                async with self:
                    if self.bulk_import_cancel_requested:
                        cancel_requested = True
                        break
                try:
                    await self._bulk_import_request(
                        XANO_PRODUCTS_URL_ENV,
                        method="POST",
                        payload=payload,
                        throttle=False,
                    )
                except urllib.error.HTTPError as error:
                    if error.code in {401, 403}:
                        results.append(
                            BulkImportResult(
                                group.product_name,
                                BULK_IMPORT_FAILED_OUTCOME,
                                "Sessão sem autorização.",
                            )
                        )
                        authorization_failure = True
                        break
                    if error.code == 400 and "already exists" in (
                        _bulk_import_error_body(error).lower()
                    ):
                        results.append(
                            BulkImportResult(
                                group.product_name,
                                BULK_IMPORT_SKIPPED_OUTCOME,
                                "Registro já existente.",
                            )
                        )
                        skipped += 1
                        existing_names.add(group.product_name)
                        continue
                    results.append(
                        BulkImportResult(
                            group.product_name,
                            BULK_IMPORT_FAILED_OUTCOME,
                            _bulk_import_group_failure_message(error),
                        )
                    )
                    failed += 1
                    continue
                except (
                    urllib.error.URLError,
                    TimeoutError,
                    ValueError,
                ) as error:
                    results.append(
                        BulkImportResult(
                            group.product_name,
                            BULK_IMPORT_FAILED_OUTCOME,
                            _bulk_import_group_failure_message(error),
                        )
                    )
                    failed += 1
                    continue
                results.append(
                    BulkImportResult(
                        group.product_name,
                        BULK_IMPORT_CREATED_OUTCOME,
                        "",
                    )
                )
                created += 1
                existing_names.add(group.product_name)

            async with self:
                self.bulk_import_report = results
                self.bulk_import_progress = ""
                if authorization_failure:
                    self.bulk_import_message = (
                        "A importação foi interrompida por falta de autorização."
                    )
                elif cancel_requested:
                    self.bulk_import_message = (
                        f"Importação cancelada. Criados: {created}, "
                        f"pulados: {skipped}, falhas: {failed}."
                    )
                else:
                    self.bulk_import_message = (
                        f"Importação concluída. Criados: {created}, "
                        f"pulados: {skipped}, falhas: {failed}."
                    )

            try:
                async with self:
                    await self._refresh_products()
            except Exception:
                BULK_IMPORT_LOGGER.exception(
                    "bulk import product refresh failed"
                )
        except Exception:
            BULK_IMPORT_LOGGER.exception("bulk import unexpected failure")
            async with self:
                self.bulk_import_report = results
                self.bulk_import_progress = ""
                self.bulk_import_message = (
                    f"Importação interrompida por erro inesperado. "
                    f"Criados: {created}, pulados: {skipped}, falhas: {failed}."
                )
        finally:
            async with self:
                self.bulk_import_loading = False
                self._bulk_import_in_progress = False
                self.bulk_import_progress = ""
                self.bulk_import_cancel_requested = False

    @rx.event
    def cancel_bulk_import(self):
        self.bulk_import_cancel_requested = True

    @rx.event
    def reset_bulk_import(self):
        if self.bulk_import_loading or self._bulk_import_in_progress:
            return
        self.bulk_import_preview = []
        self.bulk_import_report = []
        self.bulk_import_message = ""
        self.bulk_import_progress = ""
        self.bulk_import_has_valid = False
        self._bulk_import_valid_groups = []

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

    def _set_checkout_review(self, review: CheckoutReview | None):
        self._checkout_review = review
        self.checkout_review_ready = review is not None
        self.checkout_review_items = review.items if review is not None else []
        address = review.address if review is not None else None
        self.checkout_address_label = address.label if address is not None else ""
        self.checkout_address_street = address.street if address is not None else ""
        self.checkout_address_number = address.number if address is not None else ""
        self.checkout_address_neighborhood = (
            address.neighborhood if address is not None else ""
        )
        self.checkout_address_city = address.city if address is not None else ""
        self.checkout_address_state = address.state if address is not None else ""
        self.checkout_address_cep = address.cep if address is not None else ""
        self.checkout_subtotal = review.subtotal if review is not None else "0"
        self.checkout_freight = review.freight if review is not None else "0"
        self.checkout_total = review.total if review is not None else "0"

    def _set_selected_order(self, order: OrderSummary | None):
        self._selected_order = order
        self.selected_order_present = order is not None
        self.selected_order_code = order.code if order is not None else ""
        self.selected_order_status = order.status if order is not None else ""
        delivery = order.delivery if order is not None else None
        self.selected_order_delivery_label = (
            delivery.label if delivery is not None else ""
        )
        self.selected_order_delivery_street = (
            delivery.street if delivery is not None else ""
        )
        self.selected_order_delivery_number = (
            delivery.number if delivery is not None else ""
        )
        self.selected_order_delivery_neighborhood = (
            delivery.neighborhood if delivery is not None else ""
        )
        self.selected_order_delivery_city = (
            delivery.city if delivery is not None else ""
        )
        self.selected_order_delivery_state = (
            delivery.state if delivery is not None else ""
        )
        self.selected_order_delivery_cep = delivery.cep if delivery is not None else ""
        self.selected_order_items = (
            order.order_items if order is not None else []
        )
        self.selected_order_subtotal = order.subtotal if order is not None else "0"
        self.selected_order_freight = order.freight if order is not None else "0"
        self.selected_order_total = order.total if order is not None else "0"
        self.selected_order_payment_method = (
            order.payment_method if order is not None else ""
        )
        self.selected_order_payment_status = (
            order.payment_status if order is not None else ""
        )

    def _clear_customer_session(self, message: str, *, status: str = "idle"):
        self._customer_auth_token = ""
        self.customer_authenticated = False
        self.customer_session_status = status
        self.customer_session_message = message
        self.customer_id = None
        self.customer_name = ""
        self.customer_cpf = ""
        self.customer_email = ""
        self.customer_phone = ""
        self.cart_id = None
        self.cart_items = []
        self.cart_total = "0"
        self.cart_loading = False
        self.cart_message = ""
        self.checkout_address_id = ""
        self._set_checkout_review(None)
        self.checkout_loading = False
        self.checkout_message = ""
        self.checkout_method = "PIX"
        self.orders = []
        self.orders_loading = False
        self.orders_message = ""
        self._set_selected_order(None)
        self.order_loading = False
        self.payment_simulating = False
        self.payment_message = ""
        self.customer_addresses = []
        self.customer_addresses_loading = False
        self.customer_addresses_message = ""
        self.customer_profile_message = ""
        self.customer_address_editing_id = None
        self.customer_address_form_cep = ""
        self.customer_address_form_street = ""
        self.customer_address_form_number = ""
        self.customer_address_form_complement = ""
        self.customer_address_form_neighborhood = ""
        self.customer_address_form_city = ""
        self.customer_address_form_state = ""
        self.customer_address_form_label = ""

    def _set_customer_profile(self, profile: CustomerProfile):
        self.customer_id = profile.id
        self.customer_name = profile.name
        self.customer_cpf = profile.cpf
        self.customer_email = profile.email
        self.customer_phone = profile.phone
        self.customer_authenticated = True
        self.customer_session_status = "success"

    async def _customer_request(
        self,
        url_env: str,
        *,
        method: str = "GET",
        path: str | None = None,
        record_id: int | None = None,
        payload: dict[str, object] | None = None,
    ) -> XanoJson:
        if (
            not self._customer_auth_token
            or not self.customer_authenticated
            or self.customer_session_status != "success"
            or self.customer_id is None
        ):
            raise ValueError("Active customer session is required.")

        url = _required_environment_url(url_env).rstrip("/")
        if path is not None:
            url = f"{url}/{path.strip('/')}"
        if record_id is not None:
            url = f"{url}/{record_id}"
        return await _server_side_xano_request(
            url,
            method=method,
            payload=payload,
            authorization="Bearer " + self._customer_auth_token,
        )

    async def _load_cart(self, *, clear_message: bool = True) -> bool:
        self.cart_loading = True
        if clear_message:
            self.cart_message = ""
        try:
            payload = await self._customer_request(XANO_CART_URL_ENV)
            snapshot = _cart_snapshot(payload)
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ):
            self.cart_message = (
                "Não foi possível carregar o carrinho. Tente novamente."
            )
            return False
        finally:
            self.cart_loading = False

        self.cart_id = snapshot.id
        self.cart_items = snapshot.items
        self.cart_total = snapshot.total
        return True

    @rx.event
    async def load_cart(self):
        if (
            not self._customer_auth_token
            or not self.customer_authenticated
            or self.customer_session_status != "success"
        ):
            self.cart_message = "Entre como Cliente para acessar seu carrinho."
            return
        await self._load_cart()

    async def _finish_cart_mutation(
        self,
        payload: object,
        *,
        expected_item_id: int | None = None,
        expected_variation_id: int | None = None,
        expected_removed: bool | None = None,
        success_message: str,
    ):
        _cart_mutation_response(
            payload,
            expected_item_id=expected_item_id,
            expected_variation_id=expected_variation_id,
            expected_removed=expected_removed,
        )
        if await self._load_cart(clear_message=False):
            self.cart_message = success_message
        else:
            self.cart_message = (
                "A alteração foi aceita, mas não foi possível atualizar o carrinho. "
                "Atualize para confirmar."
            )

    @rx.event
    async def add_to_cart(self, variation_id: int):
        if (
            not self._customer_auth_token
            or not self.customer_authenticated
            or self.customer_session_status != "success"
        ):
            self.cart_message = "Entre como Cliente para adicionar ao carrinho."
            return
        if not isinstance(variation_id, int) or isinstance(variation_id, bool) or variation_id < 1:
            self.cart_message = "Informe uma variação e quantidade válidas."
            return
        quantity = 1

        self.cart_loading = True
        self.cart_message = ""
        try:
            response = await self._customer_request(
                XANO_CART_URL_ENV,
                method="POST",
                path="items",
                payload={
                    "variacao_id": variation_id,
                    "quantidade": quantity,
                },
            )
            _cart_mutation_response(
                response,
                expected_variation_id=variation_id,
            )
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ):
            self.cart_message = (
                "Não foi possível adicionar a variação. Verifique disponibilidade "
                "e tente novamente."
            )
            return
        finally:
            self.cart_loading = False

        await self._finish_cart_mutation(
            response,
            expected_variation_id=variation_id,
            success_message="Variação adicionada ao carrinho.",
        )

    @rx.event
    async def update_cart_item(self, item_id: int, form_data: dict[str, Any]):
        item = next((entry for entry in self.cart_items if entry.id == item_id), None)
        raw_quantity = form_data.get("quantidade") if isinstance(form_data, dict) else None
        if item is None:
            self.cart_message = "Item não encontrado no carrinho. Atualize a lista."
            return
        if (
            not isinstance(raw_quantity, (int, str))
            or isinstance(raw_quantity, bool)
            or (isinstance(raw_quantity, str) and not raw_quantity.strip().isdigit())
            or (isinstance(raw_quantity, int) and raw_quantity < 0)
        ):
            self.cart_message = "A quantidade deve ser um inteiro não negativo."
            return
        quantity = int(raw_quantity)

        self.cart_loading = True
        self.cart_message = ""
        try:
            response = await self._customer_request(
                XANO_CART_URL_ENV,
                method="PATCH",
                path="items",
                record_id=item_id,
                payload={"quantidade": quantity},
            )
            _cart_mutation_response(
                response,
                expected_item_id=item_id,
                expected_removed=quantity == 0,
            )
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ):
            self.cart_message = (
                "Não foi possível atualizar a quantidade. A quantidade confirmada "
                "foi preservada."
            )
            return
        finally:
            self.cart_loading = False

        await self._finish_cart_mutation(
            response,
            expected_item_id=item_id,
            expected_removed=quantity == 0,
            success_message=(
                "Item removido do carrinho."
                if quantity == 0
                else "Quantidade atualizada."
            ),
        )

    @rx.event
    async def remove_cart_item(self, item_id: int):
        if not any(item.id == item_id for item in self.cart_items):
            self.cart_message = "Item não encontrado no carrinho. Atualize a lista."
            return

        self.cart_loading = True
        self.cart_message = ""
        try:
            response = await self._customer_request(
                XANO_CART_URL_ENV,
                method="DELETE",
                path="items",
                record_id=item_id,
            )
            _cart_mutation_response(
                response,
                expected_item_id=item_id,
                expected_removed=True,
            )
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ):
            self.cart_message = (
                "Não foi possível remover o item. O carrinho confirmado foi preservado."
            )
            return
        finally:
            self.cart_loading = False

        await self._finish_cart_mutation(
            response,
            expected_item_id=item_id,
            expected_removed=True,
            success_message="Item removido do carrinho.",
        )

    @rx.event
    def set_checkout_address(self, address_id: str):
        self.checkout_address_id = address_id
        self._set_checkout_review(None)
        self.checkout_message = ""

    @rx.event
    def set_checkout_method(self, method: str):
        if method in {"PIX", "CARTAO", "BOLETO"}:
            self.checkout_method = method

    @rx.event
    async def prepare_checkout(self):
        await self.validate_customer_session()
        if (
            not self._customer_auth_token
            or not self.customer_authenticated
            or self.customer_session_status != "success"
        ):
            self.checkout_message = "Entre como Cliente para iniciar o checkout."
            return
        active_addresses = [
            address
            for address in self.customer_addresses
            if address.customer_id == self.customer_id and address.status == "ATIVO"
        ]
        if not active_addresses:
            self.checkout_address_id = ""
            self.checkout_message = (
                "Cadastre um Endereço ativo na sua conta para continuar."
            )
            return
        if not any(str(address.id) == self.checkout_address_id for address in active_addresses):
            primary = next(
                (address for address in active_addresses if address.is_primary),
                active_addresses[0],
            )
            self.checkout_address_id = str(primary.id)

    @rx.event
    async def load_checkout_review(self):
        if (
            not self._customer_auth_token
            or not self.customer_authenticated
            or self.customer_session_status != "success"
        ):
            self.checkout_message = "Entre como Cliente para revisar o pedido."
            return
        if not self.checkout_address_id.isdigit():
            self.checkout_message = "Selecione um Endereço ativo."
            return
        address_id = int(self.checkout_address_id)
        address = next(
            (
                entry
                for entry in self.customer_addresses
                if entry.id == address_id
                and entry.customer_id == self.customer_id
                and entry.status == "ATIVO"
            ),
            None,
        )
        if address is None:
            self.checkout_message = "Selecione um Endereço ativo da sua conta."
            return

        self.checkout_loading = True
        self.checkout_message = ""
        try:
            response = await self._customer_request(
                XANO_CHECKOUT_REVIEW_URL_ENV,
                method="POST",
                payload={"endereco_id": address_id},
            )
            review = _checkout_review(response)
            if review.address_id != address_id:
                raise ValueError("Checkout review address mismatch.")
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ):
            self.checkout_message = (
                "Não foi possível revisar o carrinho. Nenhum pedido foi criado."
            )
            return
        finally:
            self.checkout_loading = False

        self._set_checkout_review(review)
        if any(not item.available for item in review.items):
            self.checkout_message = (
                "Há itens indisponíveis ou com estoque insuficiente. Atualize o "
                "carrinho antes de confirmar."
            )

    @rx.event
    async def confirm_checkout(self, form_data: dict[str, Any]):
        review = self._checkout_review
        if (
            not self._customer_auth_token
            or not self.customer_authenticated
            or self.customer_session_status != "success"
        ):
            self.checkout_message = "Entre como Cliente para confirmar o pedido."
            return
        if review is None:
            self.checkout_message = "Revise o carrinho antes de confirmar."
            return
        if any(not item.available for item in review.items):
            self.checkout_message = (
                "Remova ou atualize os itens indisponíveis antes de confirmar."
            )
            return
        if review.address_id != int(self.checkout_address_id or 0):
            self._set_checkout_review(None)
            self.checkout_message = "O Endereço mudou. Faça uma nova revisão."
            return
        method = str(form_data.get("metodo_pagamento", self.checkout_method))
        if method not in {"PIX", "CARTAO", "BOLETO"}:
            self.checkout_message = "Selecione um método de pagamento permitido."
            return

        self.checkout_loading = True
        self.checkout_message = ""
        try:
            response = await self._customer_request(
                XANO_CHECKOUT_CONFIRM_URL_ENV,
                method="POST",
                payload={
                    "endereco_id": review.address_id,
                    "metodo_pagamento": method,
                    "revisao": review.revision,
                },
            )
            if not isinstance(response, dict) or not isinstance(
                response.get("confirmado"), bool
            ):
                raise ValueError("Checkout confirmation response is invalid.")
            current_review = _checkout_review(response)
            if current_review.address_id != review.address_id:
                raise ValueError("Checkout confirmation address mismatch.")
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ):
            self.checkout_message = (
                "Não foi possível confirmar o pedido. O carrinho permanece "
                "disponível para revisão."
            )
            return
        finally:
            self.checkout_loading = False

        if not response["confirmado"]:
            self._set_checkout_review(current_review)
            if response.get("revisao_alterada") is True:
                self.checkout_message = (
                    "Os valores ou itens mudaram. Revise os dados atualizados e "
                    "confirme novamente."
                )
            elif any(not item.available for item in current_review.items):
                self.checkout_message = (
                    "Há itens indisponíveis ou com estoque insuficiente. "
                    "Atualize o carrinho antes de confirmar."
                )
            else:
                self.checkout_message = (
                    "O pedido não foi confirmado. Confira a revisão e tente novamente."
                )
            return

        order_id = response.get("pedido_id")
        order_code = response.get("codigo")
        if (
            not isinstance(order_id, int)
            or isinstance(order_id, bool)
            or order_id < 1
            or not isinstance(order_code, str)
            or not order_code.strip()
        ):
            self.checkout_message = (
                "O servidor confirmou o pedido, mas retornou uma confirmação "
                "inválida. Consulte seu histórico de pedidos."
            )
            return
        self._set_checkout_review(None)
        self.checkout_message = f"Pedido {order_code} confirmado."
        await self.load_customer_orders()
        await self.load_customer_order(order_id)
        return rx.redirect("/pedidos")

    @rx.event
    async def load_customer_orders(self):
        if (
            not self._customer_auth_token
            or not self.customer_authenticated
            or self.customer_session_status != "success"
        ):
            self.orders_message = "Entre como Cliente para consultar seus pedidos."
            self.orders = []
            return
        self.orders_loading = True
        self.orders_message = ""
        try:
            response = await self._customer_request(XANO_ORDERS_URL_ENV)
            if not isinstance(response, list):
                raise ValueError("Order list response must be an array.")
            orders = [_order_summary(order, detail=False) for order in response]
            if len({order.id for order in orders}) != len(orders):
                raise ValueError("Order list contains duplicate records.")
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ):
            self.orders_message = (
                "Não foi possível carregar seu histórico de pedidos."
            )
            return
        finally:
            self.orders_loading = False
        self.orders = orders

    @rx.event
    async def load_customer_order(self, order_id: int):
        if (
            not self._customer_auth_token
            or not self.customer_authenticated
            or self.customer_session_status != "success"
        ):
            self.orders_message = "Entre como Cliente para consultar seus pedidos."
            return
        if (
            not isinstance(order_id, int)
            or isinstance(order_id, bool)
            or order_id < 1
        ):
            self.orders_message = "Informe um pedido válido."
            return
        self.order_loading = True
        self.orders_message = ""
        try:
            response = await self._customer_request(
                XANO_ORDERS_URL_ENV,
                record_id=order_id,
            )
            order = _order_summary(response, detail=True)
            if order.id != order_id:
                raise ValueError("Order identity mismatch.")
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ):
            self.orders_message = "Não foi possível carregar o resumo do pedido."
            return
        finally:
            self.order_loading = False
        self._set_selected_order(order)

    @rx.event
    async def simulate_order_payment(self):
        order = self._selected_order
        if (
            not self._customer_auth_token
            or not self.customer_authenticated
            or self.customer_session_status != "success"
        ):
            self.payment_message = "Entre como Cliente para simular o pagamento."
            return
        if (
            order is None
            or order.status != "AGUARDANDO_PAGAMENTO"
            or order.payment_status != "PENDENTE"
        ):
            self.payment_message = (
                "Este pedido não está aguardando pagamento simulado."
            )
            return

        self.payment_simulating = True
        self.payment_message = ""
        try:
            response = await self._customer_request(
                XANO_PAYMENT_SIMULATION_URL_ENV,
                method="POST",
                path=f"{order.id}/payment/simulate",
            )
            updated_order = _simulated_payment_response(response, order)
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ):
            self.payment_message = (
                "Não foi possível confirmar o pagamento simulado. "
                "O estado do pedido não foi atualizado."
            )
            return
        finally:
            self.payment_simulating = False

        self._set_selected_order(updated_order)
        self.orders = [
            updated_order if entry.id == updated_order.id else entry
            for entry in self.orders
        ]
        self.payment_message = (
            "Pagamento simulado aprovado. Nenhuma cobrança real foi realizada."
        )

    @rx.event
    async def register_customer(self, form_data: dict[str, Any]):
        self.customer_registration_status = "loading"
        self.customer_registration_message = ""
        name = str(form_data.get("nome_completo", "")).strip()
        cpf = str(form_data.get("cpf", "")).strip()
        email = str(form_data.get("email", "")).strip()
        phone = str(form_data.get("telefone", "")).strip()
        password = str(form_data.get("password", ""))
        if not name or not cpf or not email or not password:
            self.customer_registration_status = "error"
            self.customer_registration_message = (
                "Informe nome completo, CPF, e-mail e senha."
            )
            return

        try:
            response = await _server_side_xano_request(
                _required_environment_url(XANO_CUSTOMER_URL_ENV),
                method="POST",
                payload={
                    "nome_completo": name,
                    "cpf": cpf,
                    "email": email,
                    "telefone": phone,
                    "password": password,
                },
            )
            profile = _customer_profile(response)
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ):
            self.customer_registration_status = "error"
            self.customer_registration_message = (
                "Não foi possível cadastrar a conta. Verifique os dados e tente novamente."
            )
            return

        self.customer_registration_status = "success"
        self.customer_registration_message = (
            f"Conta criada para {profile.name}. Faça login para continuar."
        )

    @rx.event
    async def submit_customer_registration(self, form_data: dict[str, Any]):
        await self.register_customer(form_data)

    @rx.event
    async def customer_login(self, email: str, password: str):
        self._clear_customer_session("", status="loading")
        self.customer_login_status = "loading"
        self.customer_login_message = ""
        if not email.strip() or not password:
            self.customer_login_status = "error"
            self.customer_login_message = "Informe e-mail e senha."
            self.customer_session_status = "idle"
            return

        try:
            response = await _server_side_xano_request(
                _required_environment_url(XANO_CUSTOMER_LOGIN_URL_ENV),
                method="POST",
                payload={"email": email.strip(), "password": password},
            )
            if not isinstance(response, dict):
                raise ValueError("Invalid customer login response.")
            token = response.get("authToken")
            login_profile = _customer_profile(response.get("customer"))
            if not isinstance(token, str) or not token.strip():
                raise ValueError("Invalid customer login token.")

            profile_response = await _server_side_xano_request(
                _required_environment_url(XANO_CUSTOMER_ME_URL_ENV),
                authorization="Bearer " + token.strip(),
            )
            profile = _customer_profile(profile_response)
            if profile.id != login_profile.id:
                raise ValueError("Customer session identity mismatch.")
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ):
            self._clear_customer_session(
                "Não foi possível validar o acesso do Cliente.",
                status="error",
            )
            self.customer_login_status = "error"
            self.customer_login_message = (
                "Não foi possível autenticar. Verifique suas credenciais."
            )
            return

        self._customer_auth_token = token.strip()
        self._set_customer_profile(profile)
        self.customer_login_status = "success"
        self.customer_login_message = "Acesso do Cliente validado."
        self.customer_session_message = "Sessão de Cliente ativa."
        await self._load_customer_addresses()

    @rx.event
    async def submit_customer_login(self, form_data: dict[str, Any]):
        email = str(form_data.get("email", "")).strip()
        password = str(form_data.get("password", ""))
        await self.customer_login(email, password)

    @rx.event
    async def validate_customer_session(self):
        if not self._customer_auth_token:
            self._clear_customer_session("", status="idle")
            return

        self.customer_session_status = "loading"
        try:
            profile_response = await _server_side_xano_request(
                _required_environment_url(XANO_CUSTOMER_ME_URL_ENV),
                authorization="Bearer " + self._customer_auth_token,
            )
            profile = _customer_profile(profile_response)
            if self.customer_id is not None and profile.id != self.customer_id:
                raise ValueError("Customer session identity mismatch.")
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ):
            self._clear_customer_session(
                "Não foi possível validar a sessão do Cliente.",
                status="error",
            )
            return

        self._set_customer_profile(profile)
        self.customer_session_message = "Sessão de Cliente validada."
        await self._load_customer_addresses()

    @rx.event
    async def update_customer_profile(self, form_data: dict[str, Any]):
        if not self.customer_authenticated or self.customer_id is None:
            self.customer_profile_message = "Faça login para editar seu perfil."
            return

        name = str(form_data.get("nome_completo", "")).strip()
        email = str(form_data.get("email", "")).strip()
        phone = str(form_data.get("telefone", "")).strip()
        if not name or not email:
            self.customer_profile_message = (
                "Nome completo e e-mail são obrigatórios."
            )
            return

        try:
            payload = await self._customer_request(
                XANO_CUSTOMER_URL_ENV,
                method="PATCH",
                record_id=self.customer_id,
                payload={
                    "nome_completo": name,
                    "email": email,
                    "telefone": phone,
                },
            )
            profile = _customer_profile(payload)
            if profile.id != self.customer_id:
                raise ValueError("Customer profile identity mismatch.")
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ):
            self.customer_profile_message = (
                "Não foi possível atualizar o perfil. Nenhuma alteração foi confirmada."
            )
            return

        self._set_customer_profile(profile)
        self.customer_profile_message = "Perfil atualizado."

    async def _load_customer_addresses(self) -> bool:
        self.customer_addresses_loading = True
        self.customer_addresses_message = ""
        try:
            payload = await self._customer_request(
                XANO_CUSTOMER_ADDRESSES_URL_ENV
            )
            addresses = _customer_addresses(payload)
            if any(address.customer_id != self.customer_id for address in addresses):
                raise ValueError("Customer address ownership mismatch.")
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ):
            self.customer_addresses_message = (
                "Não foi possível carregar os endereços do Cliente."
            )
            return False
        finally:
            self.customer_addresses_loading = False

        self.customer_addresses = addresses
        return True

    @rx.event
    async def load_customer_addresses(self):
        await self._load_customer_addresses()

    @rx.event
    def start_new_customer_address(self):
        self._clear_customer_address_form()

    def _clear_customer_address_form(self):
        self.customer_address_editing_id = None
        self.customer_address_form_cep = ""
        self.customer_address_form_street = ""
        self.customer_address_form_number = ""
        self.customer_address_form_complement = ""
        self.customer_address_form_neighborhood = ""
        self.customer_address_form_city = ""
        self.customer_address_form_state = ""
        self.customer_address_form_label = ""

    @rx.event
    def set_customer_address_form_cep(self, value: str):
        self.customer_address_form_cep = value

    @rx.event
    def set_customer_address_form_street(self, value: str):
        self.customer_address_form_street = value

    @rx.event
    def set_customer_address_form_number(self, value: str):
        self.customer_address_form_number = value

    @rx.event
    def set_customer_address_form_complement(self, value: str):
        self.customer_address_form_complement = value

    @rx.event
    def set_customer_address_form_neighborhood(self, value: str):
        self.customer_address_form_neighborhood = value

    @rx.event
    def set_customer_address_form_city(self, value: str):
        self.customer_address_form_city = value

    @rx.event
    def set_customer_address_form_state(self, value: str):
        self.customer_address_form_state = value

    @rx.event
    def set_customer_address_form_label(self, value: str):
        self.customer_address_form_label = value

    @rx.event
    def edit_customer_address(self, address_id: int):
        address = next(
            (item for item in self.customer_addresses if item.id == address_id),
            None,
        )
        if address is None or address.customer_id != self.customer_id:
            self.customer_addresses_message = "Endereço não encontrado."
            return

        self.customer_address_editing_id = address.id
        self.customer_address_form_cep = address.cep
        self.customer_address_form_street = address.street
        self.customer_address_form_number = address.number
        self.customer_address_form_complement = address.complement
        self.customer_address_form_neighborhood = address.neighborhood
        self.customer_address_form_city = address.city
        self.customer_address_form_state = address.state
        self.customer_address_form_label = address.label

    @rx.event
    async def save_customer_address(self, form_data: dict[str, Any]):
        if not self.customer_authenticated:
            self.customer_addresses_message = (
                "Faça login para gerenciar endereços."
            )
            return

        payload = {
            "cep": str(form_data.get("cep", "")).strip(),
            "logradouro": str(form_data.get("logradouro", "")).strip(),
            "numero": str(form_data.get("numero", "")).strip(),
            "complemento": str(form_data.get("complemento", "")).strip(),
            "bairro": str(form_data.get("bairro", "")).strip(),
            "cidade": str(form_data.get("cidade", "")).strip(),
            "estado": str(form_data.get("estado", "")).strip(),
            "identificacao": str(form_data.get("identificacao", "")).strip(),
        }
        editing_id = self.customer_address_editing_id
        try:
            response = await self._customer_request(
                XANO_CUSTOMER_ADDRESSES_URL_ENV,
                method="PATCH" if editing_id is not None else "POST",
                record_id=editing_id,
                payload=payload,
            )
            address = _customer_address(response)
            if address.customer_id != self.customer_id:
                raise ValueError("Customer address ownership mismatch.")
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ):
            self.customer_addresses_message = (
                "Não foi possível salvar o endereço. Tente novamente."
            )
            return

        self._clear_customer_address_form()
        if await self._load_customer_addresses():
            self.customer_addresses_message = "Endereço salvo."
        else:
            self.customer_addresses_message = (
                "O endereço foi salvo, mas não foi possível atualizar a lista."
            )

    @rx.event
    async def set_customer_address_primary(self, address_id: int):
        await self._update_customer_address(
            address_id,
            {"principal": True},
            success_message="Endereço principal atualizado.",
        )

    @rx.event
    async def set_customer_address_status(
        self,
        address_id: int,
        status: str,
    ):
        if status not in {"ATIVO", "INATIVO"}:
            self.customer_addresses_message = "Status de endereço inválido."
            return
        await self._update_customer_address(
            address_id,
            {"status": status},
            success_message="Status do endereço atualizado.",
        )

    async def _update_customer_address(
        self,
        address_id: int,
        payload: dict[str, object],
        *,
        success_message: str,
    ):
        if not self.customer_authenticated:
            self.customer_addresses_message = (
                "Faça login para gerenciar endereços."
            )
            return
        try:
            response = await self._customer_request(
                XANO_CUSTOMER_ADDRESSES_URL_ENV,
                method="PATCH",
                record_id=address_id,
                payload=payload,
            )
            address = _customer_address(response)
            if address.customer_id != self.customer_id:
                raise ValueError("Customer address ownership mismatch.")
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ):
            self.customer_addresses_message = (
                "Não foi possível atualizar o endereço."
            )
            return

        if await self._load_customer_addresses():
            self.customer_addresses_message = success_message

    @rx.event
    async def delete_customer_address(self, address_id: int):
        if not self.customer_authenticated:
            self.customer_addresses_message = (
                "Faça login para gerenciar endereços."
            )
            return
        try:
            response = await self._customer_request(
                XANO_CUSTOMER_ADDRESSES_URL_ENV,
                method="DELETE",
                record_id=address_id,
            )
            if not isinstance(response, dict) or response.get("deleted") is not True:
                raise ValueError("Invalid address deletion response.")
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ):
            self.customer_addresses_message = (
                "Não foi possível remover o endereço."
            )
            return

        if await self._load_customer_addresses():
            self.customer_addresses_message = "Endereço removido."

    @rx.event
    def logout_customer(self):
        self.customer_login_status = "idle"
        self.customer_login_message = ""
        self._clear_customer_session(
            "Sessão de Cliente encerrada.",
            status="idle",
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


# ---------------------------------------------------------------------------
# Identidade visual Voltix (Change design-interface-voltix)
# Somente apresentacao: tokens e componentes compartilhados.
# ---------------------------------------------------------------------------

COLOR_NAVY = "#071525"
COLOR_NAVY_SOFT = "#0F2A46"
COLOR_BLUE = "#0866D9"
COLOR_CYAN = "#00B8D9"
COLOR_CYAN_DARK = "#0086A3"
COLOR_SURFACE = "#F5F7FB"
COLOR_CARD = "#FFFFFF"
COLOR_TEXT = "#243B53"
COLOR_TEXT_MUTED = "#486581"
COLOR_BORDER = "#D9E2EC"
COLOR_SUCCESS = "#2F855A"
COLOR_WARNING = "#B7791F"
COLOR_ERROR = "#C53030"

RADIUS = "12px"
CARD_SHADOW = "0 1px 2px rgba(7, 21, 37, 0.06), 0 4px 12px rgba(7, 21, 37, 0.06)"
FOCUS_STYLE = {
    "outline": f"2px solid {COLOR_CYAN}",
    "outline_offset": "2px",
}

_TONE_COLORS = {
    "muted": COLOR_TEXT_MUTED,
    "success": COLOR_SUCCESS,
    "warning": COLOR_WARNING,
    "error": COLOR_ERROR,
}


def section_heading(text, *, size: str = "6") -> rx.Component:
    """Titulo de secao com a tipografia da identidade Voltix."""
    return rx.heading(text, size=size, color=COLOR_NAVY)


def brand_logo(size: str = "6", on_dark: bool = False) -> rx.Component:
    """Marca Voltix reutilizada no cabecalho das paginas."""
    return rx.hstack(
        rx.box(
            width="0.6rem",
            height="1.5rem",
            background=COLOR_CYAN,
            border_radius="4px",
        ),
        rx.heading(
            "Voltix",
            size=size,
            color=COLOR_CARD if on_dark else COLOR_NAVY,
            letter_spacing="-0.02em",
        ),
        spacing="2",
        align="center",
    )


_NAV_ICONS = {
    "/cliente": "user",
    "/carrinho": "shopping-cart",
}

_INTERNAL_LINKS = {"/interno"}


def site_header(
    links: list[tuple[str, str]],
    *,
    active: str = "",
    badge: str = "Loja",
    logo_href: str = "/catalogo",
    wide: bool = False,
) -> rx.Component:
    """Cabecalho em banda navy com logo, badge de area e navegacao por pills."""

    def nav_link(
        label: str,
        href: str,
        *,
        emphasized: bool = False,
    ) -> rx.Component:
        is_active = active == href
        icon = _NAV_ICONS.get(href)
        if is_active:
            color = COLOR_NAVY
            background = COLOR_CYAN
            border = "1px solid transparent"
            hover = {
                "background": COLOR_CYAN_DARK,
                "color": COLOR_CARD,
                "border": "1px solid transparent",
            }
        elif emphasized:
            color = COLOR_CYAN
            background = "rgba(0, 184, 217, 0.10)"
            border = f"1px solid {COLOR_CYAN}"
            hover = {
                "background": "rgba(0, 184, 217, 0.22)",
                "color": COLOR_CARD,
                "border": f"1px solid {COLOR_CYAN}",
            }
        else:
            color = "rgba(255,255,255,0.92)"
            background = "rgba(255,255,255,0.05)"
            border = "1px solid rgba(255,255,255,0.14)"
            hover = {
                "background": "rgba(255,255,255,0.16)",
                "color": COLOR_CARD,
                "border": "1px solid rgba(255,255,255,0.28)",
            }
        return rx.link(
            rx.hstack(
                *([rx.icon(icon, size=16)] if icon else []),
                rx.text(label),
                spacing="2",
                align="center",
            ),
            href=href,
            color=color,
            background=background,
            border=border,
            padding_x="1.25rem",
            padding_y="0.5rem",
            border_radius="9999px",
            font_weight="600" if is_active or emphasized else "500",
            font_size="0.95rem",
            white_space="nowrap",
            text_decoration="none",
            transition="background 0.15s ease, color 0.15s ease, border 0.15s ease",
            _hover=hover,
            _focus_visible=FOCUS_STYLE,
        )

    commercial = [(label, href) for label, href in links if href not in _INTERNAL_LINKS]
    internal = [(label, href) for label, href in links if href in _INTERNAL_LINKS]

    nav_items = [nav_link(label, href) for label, href in commercial]
    if internal:
        nav_items.append(
            rx.box(
                width="1px",
                height="1.6rem",
                background="rgba(255,255,255,0.20)",
                margin_x="0.5rem",
            )
        )
        nav_items.extend(
            nav_link(label, href, emphasized=True) for label, href in internal
        )

    legacy_header = rx.box(
        rx.container(
            rx.flex(
                rx.hstack(
                    rx.link(
                        brand_logo(on_dark=True),
                        href=logo_href,
                        text_decoration="none",
                        _focus_visible=FOCUS_STYLE,
                    ),
                    rx.badge(
                        badge,
                        background="rgba(0, 184, 217, 0.18)",
                        color=COLOR_CYAN,
                        border=f"1px solid {COLOR_CYAN}",
                        radius="full",
                        size="2",
                    ),
                    spacing="3",
                    align="center",
                ),
                rx.flex(
                    *nav_items,
                    spacing="3",
                    align="center",
                    wrap="wrap",
                    justify={"initial": "start", "md": "end"},
                    width=rx.breakpoints(initial="100%", md="auto"),
                ),
                direction={"initial": "column", "md": "row"},
                align={"initial": "start", "md": "center"},
                justify="between",
                spacing="3",
                width="100%",
            ),
            max_width="72rem",
            size="4" if wide else "3",
            width="100%",
            margin_x="auto" if wide else "0rem",
            padding_x="1rem" if wide else "2rem",
            padding_y="1.25rem",
        ),
        background="linear-gradient(135deg, "
        + COLOR_NAVY
        + " 0%, "
        + COLOR_NAVY_SOFT
        + " 100%)",
        border_bottom=f"3px solid {COLOR_CYAN}",
        box_shadow="0 6px 20px rgba(7, 21, 37, 0.18)",
        width="100%",
    )

    # A variante antiga permanece intacta para mobile e área interna.
    if active not in {"/", "/catalogo", "/cliente", "/carrinho", "/checkout", "/pedidos"}:
        return legacy_header

    def desktop_link(label, href, *, icon=None, secondary=False):
        classes = "vx-nav__link"
        if active == href:
            classes += " vx-nav__link--active"
        if secondary:
            classes += " vx-nav__link--secondary"
        return rx.link(
            *([rx.icon(icon, size=19, aria_hidden=True)] if icon else []),
            rx.el.span(label), href=href, class_name=classes,
            aria_current="page" if active == href else None,
        )

    extra_links = [(label, href) for label, href in commercial
                   if href not in {"/", "/catalogo", "/cliente", "/carrinho"}]
    return rx.box(
        rx.el.link(rel="stylesheet", href="/voltix-navigation.css"),
        rx.box(legacy_header, class_name="vx-nav__legacy"),
        rx.el.header(
            rx.box(
                rx.link(
                    rx.el.span(class_name="vx-nav__brand-mark", aria_hidden=True),
                    rx.el.span("Voltix", class_name="vx-nav__brand-name"),
                    href="/", class_name="vx-nav__brand", aria_label="Voltix — página inicial",
                ),
                rx.el.nav(
                    desktop_link("Início", "/"),
                    desktop_link("Produtos", "/catalogo"),
                    *[desktop_link(label, href) for label, href in extra_links],
                    aria_label="Navegação principal", class_name="vx-nav__primary",
                ),
                rx.el.nav(
                    desktop_link("Minha conta", "/cliente", icon="user"),
                    desktop_link("Carrinho", "/carrinho", icon="shopping-cart"),
                    *[desktop_link(label, href, secondary=True) for label, href in internal],
                    aria_label="Conta e acesso", class_name="vx-nav__actions",
                ),
                class_name="vx-nav__inner",
            ),
            class_name="vx-nav__desktop",
        ),
        class_name="vx-navigation", width="100%",
    )


def site_footer(*, wide: bool = False, public_storefront: bool = False) -> rx.Component:
    """Rodape compartilhado das paginas em banda navy."""
    legacy_footer = rx.box(
        rx.container(
            rx.flex(
                rx.vstack(
                    brand_logo(on_dark=True),
                    rx.text(
                        "Tecnologia premium para o seu setup.",
                        color="rgba(255,255,255,0.85)",
                        font_size="0.9rem",
                    ),
                    spacing="2",
                    align="start",
                ),
                rx.vstack(
                    rx.text(
                        "Projeto acadêmico",
                        color=COLOR_CYAN,
                        font_weight="600",
                        font_size="0.85rem",
                    ),
                    rx.text(
                        "Preços e pagamentos simulados.",
                        color="rgba(255,255,255,0.65)",
                        font_size="0.85rem",
                    ),
                    spacing="1",
                    align="start",
                ),
                direction={"initial": "column", "md": "row"},
                justify="between",
                align={"initial": "start", "md": "center"},
                gap=rx.breakpoints(initial="1.25rem", md="2rem"),
                width="100%",
            ),
            max_width="72rem",
            size="4" if wide else "3",
            width="100%",
            margin_x="auto" if wide else "0rem",
            padding_x="1rem" if wide else "2rem",
            padding_y="1.5rem",
        ),
        background="linear-gradient(135deg, "
        + COLOR_NAVY
        + " 0%, "
        + COLOR_NAVY_SOFT
        + " 100%)",
        border_top=f"3px solid {COLOR_CYAN}",
        width="100%",
    )

    if not public_storefront:
        return legacy_footer

    def footer_link(label: str, href: str):
        return rx.link(label, href=href, class_name="vx-footer__link")

    return rx.box(
        rx.el.link(rel="stylesheet", href="/voltix-footer.css"),
        rx.box(legacy_footer, class_name="vx-footer__legacy"),
        rx.el.footer(
            rx.box(
                rx.box(
                    rx.box(
                        rx.link(rx.el.span(class_name="vx-footer__mark"), "Voltix",
                                href="/", aria_label="Voltix — início pelo rodapé",
                                class_name="vx-footer__brand"),
                        rx.text("Tecnologia para trabalhar, estudar e criar.",
                                class_name="vx-footer__description"),
                        class_name="vx-footer__identity"),
                    rx.el.nav(
                        rx.text("Explorar", class_name="vx-footer__title"),
                        footer_link("Início", "/"),
                        footer_link("Produtos", "/catalogo"),
                        aria_label="Explorar a loja no rodapé",
                        class_name="vx-footer__group"),
                    rx.el.nav(
                        rx.text("Sua conta", class_name="vx-footer__title"),
                        footer_link("Minha conta", "/cliente"),
                        footer_link("Carrinho", "/carrinho"),
                        footer_link("Meus pedidos", "/pedidos"),
                        aria_label="Sua conta no rodapé",
                        class_name="vx-footer__group"),
                    rx.box(
                        rx.text("Projeto", class_name="vx-footer__title"),
                        rx.text("Uma loja de tecnologia com gestão integrada, desenvolvida como projeto acadêmico.",
                                class_name="vx-footer__description"),
                        footer_link("Acesso interno", "/interno"),
                        class_name="vx-footer__group"),
                    class_name="vx-footer__columns"),
                rx.box(
                    rx.text("Projeto acadêmico", class_name="vx-footer__notice-title"),
                    rx.text("Preços e pagamentos simulados.", class_name="vx-footer__notice-copy"),
                    class_name="vx-footer__notice"),
                class_name="vx-footer__inner"),
            class_name="vx-footer__desktop"),
        class_name="vx-footer", width="100%",
    )


def surface_card(*children, **props) -> rx.Component:
    """Superficie/card padrao para agrupar conteudo."""
    props.setdefault("background", COLOR_CARD)
    props.setdefault("border", f"1px solid {COLOR_BORDER}")
    props.setdefault("border_radius", RADIUS)
    props.setdefault("box_shadow", CARD_SHADOW)
    props.setdefault("padding", "4")
    props.setdefault("width", "100%")
    return rx.box(*children, **props)


_TONE_ICONS = {
    "error": "circle-alert",
    "success": "circle-check",
    "warning": "triangle-alert",
    "info": "info",
    "muted": "info",
}

_STATUS_SCHEMES = {
    "ATIVO": "cyan",
    "PAGAMENTO_CONFIRMADO": "green",
    "APROVADO": "green",
    "INATIVO": "gray",
    "AGUARDANDO_PAGAMENTO": "amber",
    "PENDENTE": "amber",
    "VÁLIDA": "green",
    "ERRO": "red",
    "DUPLICADA": "amber",
    "CRIADO": "green",
    "PULADO": "gray",
    "FALHA": "red",
}


def feedback_text(message, tone: str = "muted") -> rx.Component:
    """Mensagem de feedback (erro, sucesso, aviso ou neutra) com icone semantico."""
    color = _TONE_COLORS.get(tone, COLOR_TEXT_MUTED)
    icon = _TONE_ICONS.get(tone, "info")
    content = rx.hstack(
        rx.icon(icon, size=16, color=color),
        rx.text(message, color=color, font_size="0.9rem"),
        spacing="2",
        align="center",
        width="100%",
    )
    if isinstance(message, str):
        return content if message else rx.fragment()
    return rx.cond(message != "", content, rx.fragment())


def status_badge(status) -> rx.Component:
    """Badge de status com cor semantica consistente."""
    if isinstance(status, str):
        scheme = _STATUS_SCHEMES.get(status, "cyan")
    else:
        scheme = rx.match(status, *_STATUS_SCHEMES.items(), "cyan")
    return rx.badge(
        status,
        color_scheme=scheme,
        variant="soft",
        radius="full",
        size="2",
    )


def primary_button(label, **props) -> rx.Component:
    """Botao de acao primaria padronizado."""
    props.setdefault("color_scheme", "cyan")
    props.setdefault("variant", "solid")
    props.setdefault("size", "3")
    return rx.button(label, **props)


def secondary_button(label, **props) -> rx.Component:
    """Botao de acao secundaria padronizado."""
    props.setdefault("color_scheme", "gray")
    props.setdefault("variant", "soft")
    props.setdefault("size", "3")
    return rx.button(label, **props)


def danger_button(label, **props) -> rx.Component:
    """Botao de acao destrutiva padronizado."""
    props.setdefault("color_scheme", "red")
    props.setdefault("variant", "soft")
    props.setdefault("size", "3")
    return rx.button(label, **props)


def status_panel(
    icon: str,
    title,
    *,
    description=None,
    tone: str = "muted",
    action: rx.Component | None = None,
) -> rx.Component:
    """Painel compacto e centralizado para estados de erro, vazio ou aviso."""
    color = _TONE_COLORS.get(tone, COLOR_TEXT_MUTED)
    children = [
        rx.flex(
            rx.icon(icon, size=24, color=color),
            width="3rem",
            height="3rem",
            background="rgba(7, 21, 37, 0.05)",
            border_radius="9999px",
            align="center",
            justify="center",
            flex_shrink="0",
        ),
        rx.text(
            title,
            weight="bold",
            color=COLOR_NAVY,
            text_align="center",
        ),
    ]
    if description is not None:
        children.append(
            rx.text(
                description,
                color=COLOR_TEXT_MUTED,
                font_size="0.9rem",
                text_align="center",
            )
        )
    if action is not None:
        children.append(rx.box(action, margin_top="1"))
    return surface_card(
        rx.vstack(*children, spacing="3", align="center", width="100%"),
        max_width="32rem",
        margin_x="auto",
        padding="6",
    )


def empty_state(message) -> rx.Component:
    """Estado vazio distinguivel do conteudo normal."""
    return status_panel("inbox", message, tone="muted")


def loading_text(message) -> rx.Component:
    """Estado de carregamento com indicador visual."""
    return rx.hstack(
        rx.spinner(size="2", color=COLOR_CYAN),
        rx.text(message, color=COLOR_TEXT_MUTED),
        spacing="2",
        align="center",
    )


def form_field(label: str, control) -> rx.Component:
    """Campo padronizado com rotulo para os formularios Voltix."""
    return rx.vstack(
        rx.text(
            label,
            font_size="0.85rem",
            font_weight="600",
            color=COLOR_TEXT,
        ),
        control,
        align="stretch",
        spacing="1",
        width="100%",
    )


def page_shell(
    *children,
    max_width: str = "64rem",
    header: rx.Component | None = None,
    show_footer: bool = True,
    public_footer: bool = False,
    size: str = "3",
) -> rx.Component:
    """Shell de pagina: fundo claro, largura responsiva, header e footer."""
    parts = []
    if header is not None:
        parts.append(header)
    parts.append(
        rx.container(
            rx.vstack(
                *children,
                spacing="5",
                align="stretch",
                width="100%",
                flex_grow="1",
            ),
            max_width=max_width,
            size=size,
            width="100%",
            padding_x="4",
            padding_y="4",
            flex_grow="1",
        )
    )
    if show_footer:
        parts.append(site_footer(wide=size != "3", public_storefront=public_footer))
    return rx.box(
        rx.flex(
            *parts,
            direction="column",
            align="center",
            min_height="100vh",
            width="100%",
        ),
        background=COLOR_SURFACE,
        color=COLOR_TEXT,
        width="100%",
    )


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
        return surface_card(
            rx.vstack(
                rx.hstack(
                    section_heading(title, size="5"),
                    secondary_button(
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
                            primary_button(
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
                                secondary_button(
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
                feedback_text(message),
                rx.cond(
                    loading,
                    loading_text("Carregando..."),
                    rx.fragment(),
                ),
                rx.foreach(
                    entries,
                    lambda entry: rx.hstack(
                        rx.text(entry.name, weight="bold", color=COLOR_NAVY),
                        rx.text(entry.description, color=COLOR_TEXT_MUTED),
                        status_badge(entry.status),
                        secondary_button(
                            "Editar",
                            on_click=edit_event(entry.id),
                            disabled=loading,
                        ),
                        secondary_button(
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
                        border_bottom=f"1px solid {COLOR_BORDER}",
                        wrap="wrap",
                    ),
                ),
                align="stretch",
                spacing="3",
                width="100%",
            ),
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
                section_heading(
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
                        secondary_button(
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
                    primary_button(
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
                        secondary_button(
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
            background=COLOR_CARD,
            border=f"1px solid {COLOR_BORDER}",
            border_radius=RADIUS,
            box_shadow=CARD_SHADOW,
            padding="4",
        )

    def variation_form() -> rx.Component:
        return rx.cond(
            State.variation_product_id != None,
            rx.form(
                rx.vstack(
                    section_heading(
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
                        primary_button(
                            "Salvar variação",
                            type="submit",
                            disabled=State.products_loading,
                        ),
                        secondary_button(
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
                background=COLOR_CARD,
                border=f"1px solid {COLOR_BORDER}",
                border_radius=RADIUS,
                box_shadow=CARD_SHADOW,
                padding="4",
            ),
            rx.fragment(),
        )

    product_management = rx.cond(
        State.user_role == "ADMINISTRADOR",
        rx.vstack(
            section_heading("Gestão de produtos"),
            product_form(),
            rx.hstack(
                section_heading("Produtos cadastrados", size="5"),
                secondary_button(
                    "Atualizar lista",
                    on_click=State.load_products,
                    disabled=State.products_loading,
                ),
                justify="between",
                width="100%",
            ),
            feedback_text(State.products_message),
            rx.cond(
                State.products_loading,
                loading_text("Carregando produtos..."),
                rx.fragment(),
            ),
            rx.foreach(
                State.products,
                lambda product: surface_card(
                    rx.vstack(
                        rx.hstack(
                            section_heading(
                                rx.cond(
                                    product.name != "",
                                    product.name,
                                    "Produto #" + product.id.to_string(),
                                ),
                                size="4",
                            ),
                            status_badge(product.status),
                            justify="between",
                            width="100%",
                        ),
                        rx.text(product.description, color=COLOR_TEXT_MUTED),
                        rx.text(product.technical_specifications, color=COLOR_TEXT_MUTED),
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
                            secondary_button(
                                "Editar produto",
                                on_click=State.edit_product(product.id),
                                disabled=State.products_loading,
                            ),
                            secondary_button(
                                rx.cond(
                                    product.status == "ATIVO",
                                    "Inativar produto",
                                    "Reativar produto",
                                ),
                                on_click=State.toggle_product_status(product.id),
                                disabled=State.products_loading,
                            ),
                            primary_button(
                                "Adicionar variação",
                                on_click=State.begin_variation(product.id),
                                disabled=State.products_loading,
                            ),
                            spacing="2",
                        ),
                        section_heading("Variações", size="3"),
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
                                    status_badge(variation.status),
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
                                    secondary_button(
                                        "Editar variação",
                                        on_click=State.edit_variation(
                                            product.id,
                                            variation.id,
                                        ),
                                        disabled=State.products_loading,
                                    ),
                                    secondary_button(
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
                                border_bottom=f"1px solid {COLOR_BORDER}",
                            ),
                        ),
                        align="stretch",
                        spacing="2",
                        width="100%",
                    ),
                ),
            ),
            variation_form(),
            align="stretch",
            spacing="3",
            width="100%",
        ),
        rx.fragment(),
    )

    bulk_import_management = rx.cond(
        State.user_role == "ADMINISTRADOR",
        surface_card(
            rx.vstack(
                section_heading("Importar produtos em massa"),
                rx.text(
                    "Envie um arquivo CSV ou XLSX com as colunas: "
                    "produto_nome, produto_descricao, "
                    "produto_especificacoes_tecnicas, categoria_nome, "
                    "marca_nome, variacao_nome, sku, preco, "
                    "quantidade_disponivel. Limites: 200 linhas, "
                    "50 produtos e 2 MB.",
                    color=COLOR_TEXT_MUTED,
                ),
                rx.upload(
                    rx.text("Selecione um arquivo CSV ou XLSX"),
                    id="bulk-import-file",
                    accept={
                        "text/csv": [".csv"],
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [
                            ".xlsx"
                        ],
                    },
                    max_files=1,
                    disabled=State.bulk_import_loading,
                    width="100%",
                ),
                rx.hstack(
                    primary_button(
                        "Pré-visualizar",
                        type="button",
                        on_click=State.preview_bulk_import(
                            rx.upload_files("bulk-import-file")
                        ),
                        disabled=State.bulk_import_loading,
                    ),
                    secondary_button(
                        "Limpar",
                        type="button",
                        on_click=State.reset_bulk_import,
                        disabled=State.bulk_import_loading,
                    ),
                    spacing="2",
                    wrap="wrap",
                ),
                feedback_text(State.bulk_import_message),
                rx.cond(
                    State.bulk_import_loading,
                    loading_text("Processando importação..."),
                    rx.fragment(),
                ),
                rx.cond(
                    State.bulk_import_progress != "",
                    rx.text(State.bulk_import_progress, color=COLOR_TEXT_MUTED),
                    rx.fragment(),
                ),
                rx.cond(
                    State.bulk_import_preview.length() > 0,
                    rx.vstack(
                        section_heading("Pré-visualização", size="4"),
                        rx.foreach(
                            State.bulk_import_preview,
                            lambda row: surface_card(
                                rx.vstack(
                                    rx.hstack(
                                        rx.text(
                                            "Linha "
                                            + row.line.to_string()
                                            + ": "
                                            + row.product_name,
                                            weight="bold",
                                        ),
                                        status_badge(row.status),
                                        justify="between",
                                        width="100%",
                                    ),
                                    rx.text(row.reason, color=COLOR_TEXT_MUTED),
                                    align="stretch",
                                    spacing="1",
                                    width="100%",
                                ),
                            ),
                        ),
                        align="stretch",
                        spacing="2",
                        width="100%",
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    State.bulk_import_has_valid,
                    rx.hstack(
                        primary_button(
                            "Confirmar importação",
                            type="button",
                            on_click=State.confirm_bulk_import,
                            disabled=State.bulk_import_loading,
                        ),
                        secondary_button(
                            "Cancelar importação",
                            type="button",
                            on_click=State.cancel_bulk_import,
                            disabled=~State.bulk_import_loading,
                        ),
                        spacing="2",
                        wrap="wrap",
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    State.bulk_import_report.length() > 0,
                    rx.vstack(
                        section_heading("Resultado", size="4"),
                        rx.foreach(
                            State.bulk_import_report,
                            lambda item: surface_card(
                                rx.vstack(
                                    rx.hstack(
                                        rx.text(item.product_name, weight="bold"),
                                        status_badge(item.outcome),
                                        justify="between",
                                        width="100%",
                                    ),
                                    rx.text(item.detail, color=COLOR_TEXT_MUTED),
                                    align="stretch",
                                    spacing="1",
                                    width="100%",
                                ),
                            ),
                        ),
                        align="stretch",
                        spacing="2",
                        width="100%",
                    ),
                    rx.fragment(),
                ),
                align="stretch",
                spacing="3",
                width="100%",
            ),
        ),
        rx.fragment(),
    )

    catalog_management = rx.cond(
        State.user_role == "ADMINISTRADOR",
        rx.vstack(
            section_heading("Gestão do catálogo"),
            rx.grid(
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
                columns={"initial": "1", "md": "2"},
                spacing="4",
                align="start",
                width="100%",
            ),
            width="100%",
            spacing="4",
            align="stretch",
        ),
        rx.fragment(),
    )

    protected_area = rx.cond(
        (State.is_authenticated) & (State.session_status == "success"),
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.link(
                        brand_logo(),
                        href="/catalogo",
                        text_decoration="none",
                    ),
                    rx.badge("Acesso interno", color_scheme="cyan"),
                    spacing="3",
                    align="center",
                    wrap="wrap",
                ),
                secondary_button("Sair", on_click=State.logout),
                justify="between",
                width="100%",
                wrap="wrap",
            ),
            section_heading("Área interna"),
            feedback_text("Acesso autorizado.", tone="success"),
            surface_card(
                rx.vstack(
                    rx.text("Usuário: " + State.user_name, weight="bold"),
                    rx.text(State.user_email),
                    rx.text("Perfil: " + State.user_role),
                    rx.text("Status: " + State.user_status),
                    align="stretch",
                    spacing="2",
                ),
            ),
            catalog_management,
            product_management,
            bulk_import_management,
            spacing="4",
            align="stretch",
            width="100%",
        ),
        rx.fragment(),
    )

    return page_shell(
        rx.vstack(
            surface_card(
                rx.vstack(
                    rx.box(
                        width="3rem",
                        height="4px",
                        background=COLOR_CYAN,
                        border_radius="9999px",
                    ),
                    section_heading("Acesso interno", size="5"),
                    rx.text(
                        "Entre com as credenciais do seu usuário interno.",
                        color=COLOR_TEXT_MUTED,
                    ),
                    rx.form(
                        rx.vstack(
                            form_field(
                                "E-mail",
                                rx.input(
                                    name="email",
                                    type="email",
                                    placeholder="voce@empresa.com",
                                    required=True,
                                    width="100%",
                                ),
                            ),
                            form_field(
                                "Senha",
                                rx.input(
                                    name="password",
                                    type="password",
                                    placeholder="Sua senha",
                                    required=True,
                                    width="100%",
                                ),
                            ),
                            primary_button(
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
                        feedback_text(State.login_message),
                        rx.fragment(),
                    ),
                    rx.cond(
                        (State.login_status == "success")
                        & (State.session_status != "success"),
                        primary_button(
                            "Acessar área interna",
                            on_click=State.enter_internal_area,
                            width="100%",
                        ),
                        rx.fragment(),
                    ),
                    align="stretch",
                    spacing="4",
                ),
                max_width="28rem",
                margin_x="auto",
            ),
            protected_area,
            align="center",
        ),
        header=site_header(
            [
                ("Catálogo público", "/catalogo"),
                ("Área do Cliente", "/cliente"),
                ("Carrinho", "/carrinho"),
            ],
            badge="Área interna",
        ),
        max_width="56rem",
    )


def home_page() -> rx.Component:
    """Home editorial; dados e eventos continuam no fluxo público existente."""
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "demo")
    hero_available = os.path.isfile(os.path.join(assets_dir, "vtx-home-workspace-v2.webp"))
    try:
        with open(os.path.join(assets_dir, "manifest.json"), encoding="utf-8-sig") as stream:
            manifest = json.load(stream)
    except (OSError, ValueError):
        manifest = {}
    if not isinstance(manifest, dict):
        manifest = {}
    approved_images = []
    for entry in manifest.get("products", []):
        filename = entry.get("file", "")
        if entry.get("status") != "approved" or not filename or os.path.basename(filename) != filename:
            continue
        url = "/demo/" + filename
        credit = demo_image_credit(url)
        if (os.path.isfile(os.path.join(assets_dir, filename)) and credit
                and credit.get("attribution")
                and resolve_demo_image_named(entry.get("product", ""), entry.get("sku", ""), "") == url):
            approved_images.append((entry["product"], url, credit))

    def eligible(product):
        matches = rx.Var.create(False)
        for name, url, _credit in approved_images:
            matches = matches | ((product.name == name) & (product.image_url == url))
        return matches

    # Filter only the Home's presentation, never the shared catalog or its State.
    showcase = State.public_products.filter(eligible)[:4]
    loading = State.public_catalog_loading | ~State.public_catalog_loaded
    has_error = State.public_catalog_message != ""

    def photo_credit(credit: dict[str, str], *, class_name="vx-credit") -> rx.Component:
        return rx.box(
            rx.text(credit["attribution"], as_="span"),
            rx.link("Fonte", href=credit["source_url"], is_external=True),
            rx.link("Licença", href=credit["license_url"], is_external=True),
            class_name=class_name,
        )

    def section_heading(title, link_label="Ver catálogo completo"):
        return rx.box(
            rx.heading(title, as_="h2", class_name="vx-section__title"),
            rx.link(link_label, rx.icon("arrow-up-right", size=17),
                    href="/catalogo", class_name="vx-link-arrow"),
            class_name="vx-section__heading",
        )

    def hero_section():
        if hero_available:
            media = rx.box(
                rx.image(src="/demo/vtx-home-workspace-v2.webp",
                         alt="Cenário ilustrativo panorâmico de uma mesa com monitor, teclado e mouse",
                         class_name="vx-hero__photo", loading="eager"),
                rx.text("Cenário ilustrativo gerado por IA; os equipamentos não representam produtos específicos.",
                        class_name="vx-hero__caption"),
                class_name="vx-hero__media",
            )
        else:
            media = rx.box(
                rx.icon("cpu", size=72),
                rx.text("Voltix", class_name="vx-hero__graphic-name"),
                rx.text("Tecnologia para o seu setup"),
                class_name="vx-hero__media vx-hero__graphic",
            )
        return rx.el.section(
            rx.box(
                rx.box(
                    rx.heading("Tecnologia premium ",
                               rx.el.span("para elevar o seu setup."),
                               as_="h1", class_name="vx-hero__title"),
                    rx.text("Explore equipamentos e acessórios para trabalhar, estudar "
                            "e montar o seu setup.", class_name="vx-hero__copy"),
                    rx.link("Explorar produtos", rx.icon("arrow-right", size=19),
                            href="/catalogo", class_name="vx-button vx-button--primary"),
                    class_name="vx-hero__content",
                ),
                media,
                class_name="vx-container vx-hero__inner",
            ),
            class_name="vx-hero", aria_label="Conheça a Voltix",
        )

    def benefits_strip():
        items = [
            ("layout-grid", "Explore por categoria", "Encontre o que seu setup precisa."),
            ("search", "Conheça os detalhes", "Consulte informações e variações."),
            ("user", "Sua conta, seus pedidos", "Acompanhe seu histórico de compras."),
        ]
        return rx.el.section(
            *[rx.box(
                rx.box(rx.icon(icon, size=23, aria_hidden=True), class_name="vx-benefit__icon"),
                rx.box(rx.text(title, class_name="vx-benefit__title"),
                       rx.text(copy, class_name="vx-benefit__copy")),
                class_name="vx-benefit") for icon, title, copy in items],
            class_name="vx-benefits", aria_label="Benefícios da loja",
        )

    def categories_section():
        return rx.el.section(
            rx.box(
                rx.heading("Encontre seu próximo upgrade.", as_="h2", class_name="vx-section__title"),
                rx.text("Explore as categorias e descubra novas possibilidades para o seu setup.",
                        class_name="vx-section__copy"),
                rx.link("Ver catálogo completo", rx.icon("arrow-up-right", size=17),
                        href="/catalogo", class_name="vx-link-arrow"),
                class_name="vx-categories__intro",
            ),
            rx.cond(
                loading,
                rx.box(*[rx.box(class_name="vx-category-skeleton") for _ in range(3)],
                       class_name="vx-category-grid", aria_label="Carregando categorias", role="status"),
                rx.cond(
                    has_error,
                    rx.text("Categorias temporariamente indisponíveis.", role="status", class_name="vx-state-copy"),
                    rx.cond(
                        State.public_categories.length() == 0,
                        rx.text("Nenhuma categoria disponível no momento.", class_name="vx-state-copy"),
                        rx.box(
                            rx.foreach(State.public_categories, lambda category: rx.link(
                                rx.box(
                                    rx.text(category.name, class_name="vx-category__title"),
                                    rx.cond(category.description != "",
                                            rx.text(category.description, class_name="vx-category__description"),
                                            rx.fragment()),
                                    class_name="vx-category__body"),
                                rx.icon("arrow-up-right", size=23, class_name="vx-category__arrow", aria_hidden=True),
                                href="/catalogo?category_id=" + category.id.to_string(), class_name="vx-category")),
                            class_name="vx-category-grid"),
                    ),
                ),
            ),
            class_name="vx-section vx-categories",
        )

    def product_tile(product):
        return rx.el.article(
            rx.link(rx.image(src=product.image_url, alt=product.name, loading="lazy",
                             class_name="vx-product__image"),
                    href="/catalogo?product_id=" + product.id.to_string(), class_name="vx-product__media",
                    aria_label="Ver " + product.name + " no catálogo"),
            rx.box(
                rx.cond(product.brand_name != "", rx.text(product.brand_name, class_name="vx-product__brand"), rx.fragment()),
                rx.heading(rx.link(product.name, href="/catalogo?product_id=" + product.id.to_string()), as_="h3", class_name="vx-product__title"),
                rx.cond(product.category_name != "", rx.text(product.category_name, class_name="vx-product__category"), rx.fragment()),
                class_name="vx-product__body"),
            (rx.match(product.image_url,
                      *[(url, photo_credit(credit, class_name="vx-credit vx-product__credit"))
                        for _name, url, credit in approved_images], rx.fragment())
             if approved_images else rx.fragment()),
            class_name="vx-product",
        )

    def products_section():
        skeletons = rx.box(
            *[rx.box(rx.box(class_name="vx-skeleton__image"),
                     rx.box(class_name="vx-skeleton__line"),
                     rx.box(class_name="vx-skeleton__line vx-skeleton__line--short"),
                     class_name="vx-skeleton", aria_hidden=True) for _ in range(3)],
            class_name="vx-product-grid", role="status", aria_label="Carregando destaques", aria_busy=True,
        )
        content = rx.cond(
            has_error & ~State.public_catalog_loading,
            status_panel("triangle-alert", "Não foi possível carregar os destaques",
                         description=State.public_catalog_message, tone="error",
                         action=primary_button("Tentar novamente", on_click=State.load_public_catalog,
                                               disabled=State.public_catalog_loading)),
            rx.cond(loading, skeletons,
                    rx.cond(State.public_products.length() == 0,
                            rx.text("Nenhum produto disponível para exibição.", class_name="vx-state-copy"),
                            rx.box(rx.foreach(showcase, product_tile),
                                   class_name=rx.cond(showcase.length() == 3, "vx-product-grid", "vx-product-grid vx-product-grid--duo")))),
        )
        return rx.cond(
            loading | has_error | (State.public_products.length() == 0) | (showcase.length() > 0),
            rx.el.section(section_heading("Destaques da loja"), content,
                          class_name="vx-section vx-showcase", aria_label="Destaques da loja"),
            rx.fragment(),
        )

    def editorial_section():
        credit = next((entry for entry in manifest.get("editorial_images", [])
                       if entry.get("role") == "home_editorial"
                       and entry.get("status") == "approved"
                       and entry.get("file") == "vtx-editorial-mx-master-3s.jpg"), None)
        if (not credit or not all(credit.get(key) for key in
                ("attribution", "source_url", "license_url"))
                or not os.path.isfile(os.path.join(assets_dir, credit["file"]))):
            return rx.fragment()
        url = "/demo/" + credit["file"]
        return rx.el.section(
            rx.box(rx.image(src=url, alt="Vista lateral do mouse Logitech MX Master 3S, com roda e botões",
                            loading="lazy", class_name="vx-editorial__image"),
                   photo_credit(credit), class_name="vx-editorial__media"),
            rx.box(
                rx.text("LOGITECH MX MASTER 3S", class_name="vx-editorial__label"),
                rx.heading("Precisão em cada detalhe", as_="h2", class_name="vx-editorial__heading"),
                rx.text("Uma visão de perto do MX Master 3S: roda lateral, botões e acabamento "
                        "em um equipamento pensado para compor o seu espaço de trabalho.",
                        class_name="vx-editorial__copy"),
                rx.link("Ver catálogo", rx.icon("arrow-right", size=18),
                        href="/catalogo", class_name="vx-link-arrow"),
                class_name="vx-editorial__content"),
            class_name="vx-section vx-editorial",
        )

    def category_bar() -> rx.Component:
        return rx.cond(
            State.public_categories.length() > 0,
            rx.box(
                rx.container(
                    rx.hstack(
                        rx.hstack(
                            rx.icon("layout-grid", size=15, color=COLOR_BLUE),
                            rx.text(
                                "Categorias",
                                color=COLOR_NAVY,
                                font_weight="700",
                                font_size="0.85rem",
                            ),
                            spacing="2",
                            align="center",
                            flex_shrink="0",
                        ),
                        rx.box(
                            width="1px",
                            height="1.4rem",
                            background=COLOR_BORDER,
                            margin_x="0.25rem",
                            flex_shrink="0",
                        ),
                        rx.hstack(
                            rx.foreach(
                                State.public_categories,
                                lambda category: rx.link(
                                    category.name,
                                    href="/catalogo",
                                    color=COLOR_TEXT,
                                    font_size="0.88rem",
                                    font_weight="600",
                                    padding_x="0.9rem",
                                    padding_y="0.4rem",
                                    border_radius="9999px",
                                    white_space="nowrap",
                                    text_decoration="none",
                                    transition="background 0.15s ease, color 0.15s ease",
                                    _hover={
                                        "background": "rgba(8, 102, 217, 0.10)",
                                        "color": COLOR_BLUE,
                                    },
                                    _focus_visible=FOCUS_STYLE,
                                ),
                            ),
                            spacing="1",
                            align="center",
                            wrap="nowrap",
                        ),
                        spacing="3",
                        align="center",
                        width="100%",
                        overflow_x="auto",
                    ),
            max_width="72rem",
            size="4",
            width="100%",
            margin_x="auto",
            padding_x="1rem",
            padding_y="0.6rem",
                ),
                background=COLOR_CARD,
                border_bottom=f"1px solid {COLOR_BORDER}",
                width="100%",
            ),
            rx.fragment(),
        )

    def home_chrome(component):
        # Only these Home instances: the shared logo is text, not a page heading.
        if component.tag == "Heading":
            component.as_ = rx.Var.create("h2")
        for child in component.children:
            home_chrome(child)
        return component

    return rx.box(
        home_chrome(site_header([
            ("Catálogo público", "/catalogo"), ("Minha conta", "/cliente"),
            ("Carrinho", "/carrinho"), ("Acesso interno", "/interno")],
            active="/", badge="Loja", logo_href="/", wide=True)),
        rx.box(category_bar(), class_name="vx-home-category-bar", width="100%"),
        rx.el.main(rx.el.link(rel="stylesheet", href="/voltix-home.css"),
                   hero_section(),
                   rx.box(benefits_strip(), categories_section(), products_section(), editorial_section(),
                          class_name="vx-container vx-home__sections"),
                   class_name="vx-home vx-home__surface"),
        home_chrome(site_footer(wide=True, public_storefront=True)),
        width="100%", background=COLOR_SURFACE, color=COLOR_TEXT,
    )


def public_catalog_page() -> rx.Component:
    def product_card(product: PublicProductEntry) -> rx.Component:
        return surface_card(
            rx.vstack(
                rx.cond(
                    product.image_url != "",
                    rx.image(
                        src=product.image_url,
                        alt=product.name,
                        width="100%",
                        height="220px",
                        object_fit="cover",
                        border_radius=RADIUS,
                    ),
                    rx.fragment(),
                ),
                section_heading(
                    rx.cond(
                        product.name != "",
                        product.name,
                        "Produto #" + product.id.to_string(),
                    ),
                    size="4",
                ),
                rx.cond(
                    product.category_name != "",
                    rx.text("Categoria: " + product.category_name),
                    rx.fragment(),
                ),
                rx.cond(
                    product.brand_name != "",
                    rx.text("Marca: " + product.brand_name),
                    rx.fragment(),
                ),
                rx.text(product.description, color=COLOR_TEXT_MUTED, flex_grow="1"),
                rx.spacer(),
                secondary_button(
                    "Ver detalhes",
                    on_click=State.load_public_product_details(product.id),
                    disabled=State.public_product_loading,
                    width="100%",
                ),
                align="stretch",
                spacing="3",
                width="100%",
                height="100%",
            ),
            height="100%",
        )

    def selected_product_details() -> rx.Component:
        return rx.cond(
            State.public_selected_product != None,
            surface_card(
                rx.vstack(
                    rx.hstack(
                        section_heading(
                            State.public_selected_product.name,
                            size="5",
                        ),
                        secondary_button(
                            "Fechar detalhes",
                            on_click=State.close_public_product_details,
                        ),
                        justify="between",
                        width="100%",
                    ),
                    rx.cond(
                        State.public_selected_product.image_url != "",
                        rx.image(
                            src=State.public_selected_product.image_url,
                            alt=State.public_selected_product.name,
                            max_width="640px",
                            max_height="420px",
                            object_fit="contain",
                        ),
                        rx.fragment(),
                    ),
                    rx.cond(
                        State.public_selected_product.description != "",
                        rx.text(State.public_selected_product.description),
                        rx.fragment(),
                    ),
                    rx.cond(
                        State.public_selected_product.technical_specifications
                        != "",
                        rx.text(
                            "Especificações: "
                            + State.public_selected_product.technical_specifications
                        ),
                        rx.fragment(),
                    ),
                    rx.cond(
                        State.public_selected_product.category_name != "",
                        rx.text(
                            "Categoria: "
                            + State.public_selected_product.category_name
                        ),
                        rx.fragment(),
                    ),
                    rx.cond(
                        State.public_selected_product.brand_name != "",
                        rx.text(
                            "Marca: "
                            + State.public_selected_product.brand_name
                        ),
                        rx.fragment(),
                    ),
                    section_heading("Variações disponíveis", size="4"),
                    rx.cond(
                        State.public_selected_product.variations.length() == 0,
                        empty_state("Não há variações ativas disponíveis."),
                        rx.foreach(
                            State.public_selected_product.variations,
                            lambda variation: rx.box(
                                rx.vstack(
                                    rx.text(
                                        rx.cond(
                                            variation.name_or_description != "",
                                            variation.name_or_description,
                                            variation.sku,
                                        ),
                                        weight="bold",
                                        color=COLOR_NAVY,
                                    ),
                                    rx.text("SKU: " + variation.sku),
                                    rx.text("Preço: R$ " + variation.price.to_string()),
                                    rx.text(
                                        rx.cond(
                                            variation.available_quantity > 0,
                                            "Disponível: "
                                            + variation.available_quantity.to_string(),
                                            "Indisponível para compra (estoque zero)",
                                        )
                                    ),
                                    primary_button(
                                        "Adicionar ao carrinho",
                                        on_click=State.add_to_cart(variation.id),
                                        disabled=(
                                            State.cart_loading
                                            | (variation.available_quantity <= 0)
                                        ),
                                    ),
                                    align="stretch",
                                    spacing="2",
                                ),
                                border=f"1px solid {COLOR_BORDER}",
                                border_radius=RADIUS,
                                padding="3",
                                width="100%",
                                background=COLOR_SURFACE,
                            ),
                        ),
                    ),
                    feedback_text(State.cart_message, tone="error"),
                    rx.cond(
                        State.cart_message != "",
                        rx.cond(
                            State.customer_authenticated,
                            rx.link("Ver carrinho", href="/carrinho"),
                            rx.link("Entrar como Cliente", href="/cliente"),
                        ),
                        rx.fragment(),
                    ),
                    align="stretch",
                    spacing="3",
                    width="100%",
                ),
            ),
            rx.fragment(),
        )

    return page_shell(
        rx.el.link(rel="stylesheet", href="/voltix-catalog-search.css"),
        rx.vstack(
            section_heading("Catálogo de produtos"),
            rx.text(
                "Busque pelo nome do produto ou explore as categorias.",
                color=COLOR_TEXT_MUTED,
            ),
            spacing="2",
            align="start",
            width="100%",
        ),
        surface_card(
            rx.box(
                rx.form(
                    rx.box(
                        rx.box(
                            rx.el.label("Buscar no catálogo", html_for="catalog-search", class_name="vx-catalog-tools__label"),
                            rx.input(
                                id="catalog-search", name="search",
                                placeholder="Nome do produto", max_length=100,
                                value=State.public_catalog_search_input,
                                on_change=State.set_public_catalog_search_input,
                                disabled=State.public_catalog_loading,
                                class_name="vx-catalog-tools__input"),
                            class_name="vx-catalog-tools__field"),
                        rx.button(rx.icon("search", size=17, aria_hidden=True), "Buscar",
                                  type="submit", disabled=State.public_catalog_loading,
                                  class_name="vx-catalog-tools__submit"),
                        class_name="vx-catalog-tools__search-row"),
                    on_submit=State.search_public_catalog, reset_on_submit=False,
                    class_name="vx-catalog-tools__search"),
                rx.box(
                    rx.el.label("Categoria", html_for="catalog-category", class_name="vx-catalog-tools__label"),
                    rx.select.root(
                        rx.select.trigger(id="catalog-category", aria_label="Filtrar por categoria",
                                          placeholder="Todas as categorias", class_name="vx-catalog-tools__select"),
                        rx.select.content(rx.foreach(State.public_categories,
                            lambda category: rx.select.item(category.name, value=category.id.to_string()))),
                        value=State.public_category_id,
                        on_change=State.filter_public_catalog,
                        disabled=State.public_catalog_loading,
                    ),
                    class_name="vx-catalog-tools__category"),
                rx.button("Limpar filtros", type="button", on_click=State.clear_public_catalog_filters,
                          disabled=State.public_catalog_loading | ((State.public_category_id == "")
                              & (State.public_catalog_search == "") & (State.public_catalog_search_input == "")),
                          class_name="vx-catalog-tools__clear"),
                class_name="vx-catalog-tools"),
            padding="4",
        ),
        rx.cond(
            ~State.public_catalog_loading & State.public_catalog_loaded & (State.public_catalog_message == ""),
            rx.text(
                rx.cond(State.public_catalog_search != "",
                        "Resultados para “" + State.public_catalog_search + "” · ", "Catálogo · "),
                rx.cond(State.public_products.length() == 1, "1 produto",
                        State.public_products.length().to_string() + " produtos"),
                role="status", aria_live="polite", class_name="vx-catalog-results"),
            rx.fragment(),
        ),
        rx.cond(
            State.public_catalog_loading | (State.public_catalog_loaded == False),
            loading_text("Carregando catálogo..."),
            rx.fragment(),
        ),
        rx.cond(
            State.public_catalog_message != "",
            status_panel(
                "triangle-alert",
                "Não foi possível carregar o catálogo",
                description=State.public_catalog_message,
                tone="error",
                action=primary_button(
                    "Tentar novamente",
                    on_click=State.load_public_catalog,
                    disabled=State.public_catalog_loading,
                ),
            ),
            rx.fragment(),
        ),
        rx.cond(
            (State.public_catalog_loading == False)
            & (State.public_catalog_loaded == True)
            & (State.public_catalog_message == "")
            & (State.public_products.length() == 0),
            rx.cond(State.public_catalog_search != "",
                    rx.box(
                        rx.icon("search-x", size=25, color=COLOR_TEXT_MUTED, aria_hidden=True),
                        rx.heading("Nenhum produto encontrado", as_="h2"),
                        rx.text("Tente outro nome ou limpe os filtros para ampliar a busca."),
                        class_name="vx-catalog-results-empty"),
                    empty_state("Nenhum produto disponível para exibição.")),
            rx.fragment(),
        ),
        selected_product_details(),
        rx.cond(
            ~State.public_catalog_loading & State.public_catalog_loaded
            & (State.public_catalog_message == "")
            & (State.public_products.length() > 0),
            rx.grid(
                rx.foreach(State.public_products, product_card),
                columns={"initial": "1", "md": "2", "lg": "3"},
                spacing="4",
                align="stretch",
                width="100%",
            ),
            rx.fragment(),
        ),
        rx.cond(
            State.public_product_loading,
            loading_text("Carregando detalhes..."),
            rx.fragment(),
        ),
        rx.cond(
            State.public_product_message != "",
            status_panel(
                "triangle-alert",
                "Não foi possível carregar os detalhes do produto",
                description=State.public_product_message,
                tone="error",
                action=primary_button(
                    "Tentar novamente",
                    on_click=State.load_public_product_details(
                        State.public_product_detail_id
                    ),
                    disabled=State.public_product_loading,
                ),
            ),
            rx.fragment(),
        ),
        header=site_header(
            [
                ("Catálogo público", "/catalogo"),
                ("Área do Cliente", "/cliente"),
                ("Carrinho", "/carrinho"),
                ("Acesso interno", "/interno"),
            ],
            active="/catalogo",
            badge="Loja",
            logo_href="/",
        ),
        max_width="64rem",
        public_footer=True,
    )


def customer_account_page() -> rx.Component:
    def address_card(address: CustomerAddressEntry) -> rx.Component:
        return surface_card(
            rx.vstack(
                rx.hstack(
                    section_heading(
                        rx.cond(
                            address.label != "",
                            address.label,
                            "Endereço #" + address.id.to_string(),
                        ),
                        size="4",
                    ),
                    rx.cond(
                        address.is_primary,
                        rx.badge("Principal", color_scheme="cyan"),
                        rx.fragment(),
                    ),
                            status_badge(address.status),
                    justify="between",
                    width="100%",
                    wrap="wrap",
                ),
                rx.cond(
                    address.street != "",
                    rx.text("Logradouro: " + address.street),
                    rx.fragment(),
                ),
                rx.cond(
                    address.number != "",
                    rx.text("Número: " + address.number),
                    rx.fragment(),
                ),
                rx.cond(
                    address.complement != "",
                    rx.text("Complemento: " + address.complement),
                    rx.fragment(),
                ),
                rx.cond(
                    address.neighborhood != "",
                    rx.text("Bairro: " + address.neighborhood),
                    rx.fragment(),
                ),
                rx.cond(
                    address.city != "",
                    rx.text("Cidade: " + address.city),
                    rx.fragment(),
                ),
                rx.cond(
                    address.state != "",
                    rx.text("Estado: " + address.state),
                    rx.fragment(),
                ),
                rx.cond(
                    address.cep != "",
                    rx.text("CEP: " + address.cep),
                    rx.fragment(),
                ),
                rx.hstack(
                    secondary_button(
                        "Editar",
                        on_click=State.edit_customer_address(address.id),
                    ),
                    rx.cond(
                        (address.status == "ATIVO") & (address.is_primary == False),
                        secondary_button(
                            "Tornar principal",
                            on_click=State.set_customer_address_primary(address.id),
                        ),
                        rx.fragment(),
                    ),
                    rx.cond(
                        address.status == "ATIVO",
                        secondary_button(
                            "Inativar",
                            on_click=State.set_customer_address_status(
                                address.id,
                                "INATIVO",
                            ),
                        ),
                        secondary_button(
                            "Reativar",
                            on_click=State.set_customer_address_status(
                                address.id,
                                "ATIVO",
                            ),
                        ),
                    ),
                    danger_button(
                        "Remover",
                        on_click=State.delete_customer_address(address.id),
                    ),
                    wrap="wrap",
                ),
                align="stretch",
                spacing="3",
            ),
        )

    public_forms = rx.grid(
        surface_card(
            rx.vstack(
                feedback_text(State.customer_session_message, tone="error"),
                rx.box(
                    width="3rem",
                    height="4px",
                    background=COLOR_BLUE,
                    border_radius="9999px",
                ),
                rx.vstack(
                    section_heading("Criar conta de Cliente", size="5"),
                    rx.text(
                        "Cadastre-se para comprar e acompanhar seus pedidos.",
                        color=COLOR_TEXT_MUTED,
                        font_size="0.9rem",
                    ),
                    spacing="1",
                    align="start",
                    width="100%",
                ),
                rx.form(
                    rx.vstack(
                        form_field(
                            "Nome completo",
                            rx.input(
                                name="nome_completo",
                                placeholder="Ex.: Maria Silva",
                                required=True,
                                width="100%",
                            ),
                        ),
                        form_field(
                            "CPF",
                            rx.input(
                                name="cpf",
                                placeholder="000.000.000-00",
                                required=True,
                                width="100%",
                            ),
                        ),
                        form_field(
                            "E-mail",
                            rx.input(
                                name="email",
                                type="email",
                                placeholder="voce@email.com",
                                required=True,
                                width="100%",
                            ),
                        ),
                        form_field(
                            "Telefone",
                            rx.input(
                                name="telefone",
                                type="tel",
                                placeholder="(11) 99999-9999",
                                width="100%",
                            ),
                        ),
                        form_field(
                            "Senha",
                            rx.input(
                                name="password",
                                type="password",
                                placeholder="Crie uma senha",
                                required=True,
                                width="100%",
                            ),
                        ),
                        primary_button(
                            "Cadastrar",
                            type="submit",
                            disabled=State.customer_registration_status == "loading",
                        ),
                        width="100%",
                        align="stretch",
                        spacing="3",
                    ),
                    on_submit=State.submit_customer_registration,
                    width="100%",
                ),
                feedback_text(State.customer_registration_message),
                align="stretch",
                spacing="3",
                width="100%",
            ),
        ),
        surface_card(
            rx.vstack(
                rx.box(
                    width="3rem",
                    height="4px",
                    background=COLOR_CYAN,
                    border_radius="9999px",
                ),
                rx.vstack(
                    section_heading("Entrar como Cliente", size="5"),
                    rx.text(
                        "Acesse sua conta para continuar suas compras.",
                        color=COLOR_TEXT_MUTED,
                        font_size="0.9rem",
                    ),
                    spacing="1",
                    align="start",
                    width="100%",
                ),
                rx.form(
                    rx.vstack(
                        form_field(
                            "E-mail",
                            rx.input(
                                name="email",
                                type="email",
                                placeholder="voce@email.com",
                                required=True,
                                width="100%",
                            ),
                        ),
                        form_field(
                            "Senha",
                            rx.input(
                                name="password",
                                type="password",
                                placeholder="Sua senha",
                                required=True,
                                width="100%",
                            ),
                        ),
                        primary_button(
                            rx.cond(
                                State.customer_login_status == "loading",
                                "Entrando...",
                                "Entrar",
                            ),
                            type="submit",
                            disabled=State.customer_login_status == "loading",
                        ),
                        width="100%",
                        align="stretch",
                        spacing="3",
                    ),
                    on_submit=State.submit_customer_login,
                    width="100%",
                ),
                feedback_text(State.customer_login_message),
                align="stretch",
                spacing="3",
                width="100%",
            ),
        ),
        columns={"initial": "1", "lg": "2"},
        spacing="5",
        align="stretch",
        width="100%",
    )

    authenticated_customer = rx.vstack(
        rx.hstack(
            section_heading("Minha conta"),
            rx.hstack(
                rx.link(
                    "Carrinho",
                    href="/carrinho",
                    color=COLOR_TEXT_MUTED,
                    _hover={"color": COLOR_CYAN_DARK},
                ),
                rx.link(
                    "Meus pedidos",
                    href="/pedidos",
                    color=COLOR_TEXT_MUTED,
                    _hover={"color": COLOR_CYAN_DARK},
                ),
                secondary_button("Sair", on_click=State.logout_customer),
                spacing="4",
                wrap="wrap",
            ),
            justify="between",
            width="100%",
            wrap="wrap",
        ),
        surface_card(
            rx.vstack(
                rx.text(
                    "Cliente: " + State.customer_name,
                    weight="bold",
                    color=COLOR_NAVY,
                ),
                rx.text("CPF: " + State.customer_cpf, color=COLOR_TEXT_MUTED),
                rx.form(
                    rx.vstack(
                        form_field(
                            "Nome completo",
                            rx.input(
                                name="nome_completo",
                                default_value=State.customer_name,
                                placeholder="Nome completo",
                                required=True,
                                width="100%",
                            ),
                        ),
                        form_field(
                            "E-mail",
                            rx.input(
                                name="email",
                                type="email",
                                default_value=State.customer_email,
                                placeholder="E-mail",
                                required=True,
                                width="100%",
                            ),
                        ),
                        form_field(
                            "Telefone",
                            rx.input(
                                name="telefone",
                                type="tel",
                                default_value=State.customer_phone,
                                placeholder="Telefone",
                                width="100%",
                            ),
                        ),
                        primary_button("Salvar perfil", type="submit"),
                        width="100%",
                        align="stretch",
                        spacing="3",
                    ),
                    on_submit=State.update_customer_profile,
                    width="100%",
                    max_width="24rem",
                ),
                feedback_text(State.customer_profile_message),
                align="stretch",
                spacing="3",
                width="100%",
            ),
        ),
        section_heading("Meus endereços", size="5"),
        rx.hstack(
            primary_button(
                "Novo endereço",
                on_click=State.start_new_customer_address,
            ),
            secondary_button(
                "Atualizar endereços",
                on_click=State.load_customer_addresses,
                disabled=State.customer_addresses_loading,
            ),
            wrap="wrap",
        ),
        feedback_text(State.customer_addresses_message, tone="error"),
        rx.cond(
            State.customer_addresses_loading,
            loading_text("Carregando endereços..."),
            rx.fragment(),
        ),
        rx.cond(
            State.customer_address_editing_id != None,
            section_heading("Editar endereço", size="4"),
            section_heading("Novo endereço", size="4"),
        ),
        surface_card(
            rx.form(
                rx.vstack(
                    rx.grid(
                    rx.input(
                        name="cep",
                        value=State.customer_address_form_cep,
                        on_change=State.set_customer_address_form_cep,
                        placeholder="CEP",
                        width="100%",
                    ),
                    rx.input(
                        name="logradouro",
                        value=State.customer_address_form_street,
                        on_change=State.set_customer_address_form_street,
                        placeholder="Logradouro",
                        width="100%",
                    ),
                    rx.input(
                        name="numero",
                        value=State.customer_address_form_number,
                        on_change=State.set_customer_address_form_number,
                        placeholder="Número",
                        width="100%",
                    ),
                    rx.input(
                        name="complemento",
                        value=State.customer_address_form_complement,
                        on_change=State.set_customer_address_form_complement,
                        placeholder="Complemento",
                        width="100%",
                    ),
                    rx.input(
                        name="bairro",
                        value=State.customer_address_form_neighborhood,
                        on_change=State.set_customer_address_form_neighborhood,
                        placeholder="Bairro",
                        width="100%",
                    ),
                    rx.input(
                        name="cidade",
                        value=State.customer_address_form_city,
                        on_change=State.set_customer_address_form_city,
                        placeholder="Cidade",
                        width="100%",
                    ),
                    rx.input(
                        name="estado",
                        value=State.customer_address_form_state,
                        on_change=State.set_customer_address_form_state,
                        placeholder="Estado",
                        width="100%",
                    ),
                    rx.input(
                        name="identificacao",
                        value=State.customer_address_form_label,
                        on_change=State.set_customer_address_form_label,
                        placeholder="Identificação (ex.: Casa)",
                        width="100%",
                    ),
                    columns={"initial": "1", "sm": "2"},
                    spacing="3",
                    align="start",
                    width="100%",
                ),
                    rx.hstack(
                        primary_button(
                            rx.cond(
                                State.customer_address_editing_id != None,
                                "Salvar endereço",
                                "Cadastrar endereço",
                            ),
                            type="submit",
                        ),
                        rx.cond(
                            State.customer_address_editing_id != None,
                            secondary_button(
                                "Cancelar edição",
                                type="button",
                                on_click=State.start_new_customer_address,
                            ),
                            rx.fragment(),
                        ),
                        wrap="wrap",
                    ),
                    width="100%",
                    align="stretch",
                    spacing="3",
                ),
                on_submit=State.save_customer_address,
                width="100%",
            ),
        ),
        rx.cond(
            State.customer_addresses.length() == 0,
            empty_state("Nenhum endereço cadastrado."),
            rx.grid(
                rx.foreach(State.customer_addresses, address_card),
columns={"initial": "1", "md": "2"},
                spacing="4",
                align="start",
                width="100%",
            ),
        ),
        rx.fragment(),
    )

    return page_shell(
        rx.cond(
            State.customer_authenticated,
            authenticated_customer,
            public_forms,
        ),
        header=site_header(
            [
                ("Catálogo público", "/catalogo"),
                ("Área do Cliente", "/cliente"),
                ("Carrinho", "/carrinho"),
                ("Acesso interno", "/interno"),
            ],
            active="/cliente",
            badge="Área do cliente",
        ),
        max_width="56rem",
        public_footer=True,
    )


def customer_cart_page() -> rx.Component:
    def cart_item_card(item: CartItemEntry) -> rx.Component:
        return surface_card(
            rx.vstack(
                section_heading(
                    rx.cond(item.product_name != "", item.product_name, item.sku),
                    size="4",
                ),
                rx.cond(
                    item.variation_name != "",
                    rx.text("Variação: " + item.variation_name),
                    rx.fragment(),
                ),
                rx.text("SKU: " + item.sku),
                rx.cond(
                    item.available,
                    rx.badge("Disponível", color_scheme="cyan"),
                    rx.badge("Indisponível", color_scheme="red"),
                ),
                rx.text("Preço atual: R$ " + item.price),
                rx.text("Subtotal: R$ " + item.subtotal),
                rx.form(
                    rx.hstack(
                        rx.input(
                            name="quantidade",
                            type="number",
                            min="0",
                            step="1",
                            default_value=item.quantity.to_string(),
                            width="8rem",
                        ),
                        secondary_button(
                            "Atualizar quantidade",
                            type="submit",
                            disabled=State.cart_loading,
                        ),
                        wrap="wrap",
                    ),
                    on_submit=State.update_cart_item(item.id),
                ),
                danger_button(
                    "Remover item",
                    on_click=State.remove_cart_item(item.id),
                    disabled=State.cart_loading,
                ),
                align="stretch",
                spacing="2",
                width="100%",
            ),
        )

    authenticated_cart = rx.vstack(
        rx.hstack(
            rx.text(
                "Cliente: " + State.customer_name,
                weight="bold",
                color=COLOR_NAVY,
            ),
            secondary_button(
                "Atualizar carrinho",
                on_click=State.load_cart,
                disabled=State.cart_loading,
            ),
            justify="between",
            width="100%",
            wrap="wrap",
        ),
        feedback_text(State.cart_message),
        rx.cond(
            State.cart_loading,
            loading_text("Carregando carrinho..."),
            rx.fragment(),
        ),
        rx.cond(
            State.cart_items.length() == 0,
            empty_state("Seu carrinho está vazio."),
            rx.foreach(State.cart_items, cart_item_card),
        ),
        surface_card(
            rx.hstack(
                section_heading("Total:", size="5"),
                rx.heading("R$ " + State.cart_total, size="5", color=COLOR_NAVY),
                justify="between",
                width="100%",
            ),
        ),
        rx.cond(
            State.cart_items.length() > 0,
            rx.link(
                primary_button("Continuar para checkout", width="100%"),
                href="/checkout",
                text_decoration="none",
                width="100%",
            ),
            rx.fragment(),
        ),
        align="stretch",
        spacing="3",
        width="100%",
    )

    return page_shell(
        section_heading("Seu carrinho"),
        rx.cond(
            State.customer_authenticated,
            authenticated_cart,
            rx.vstack(
                rx.text(
                    "Entre como Cliente para acessar seu carrinho.",
                    color=COLOR_TEXT_MUTED,
                ),
                rx.link("Acessar conta de Cliente", href="/cliente"),
                align="stretch",
                spacing="3",
            ),
        ),
        header=site_header(
            [
                ("Catálogo público", "/catalogo"),
                ("Carrinho", "/carrinho"),
                ("Minha conta", "/cliente"),
                ("Acesso interno", "/interno"),
            ],
            active="/carrinho",
            badge="Carrinho",
        ),
        max_width="48rem",
        public_footer=True,
    )


def customer_checkout_page() -> rx.Component:
    def review_item(item: CheckoutItemEntry) -> rx.Component:
        return surface_card(
            rx.vstack(
                section_heading(
                    rx.cond(item.product_name != "", item.product_name, item.sku),
                    size="4",
                ),
                rx.text("Variação: " + item.variation_name),
                rx.text("SKU: " + item.sku),
                rx.text("Quantidade: " + item.quantity.to_string()),
                rx.text("Preço unitário atual: R$ " + item.unit_price),
                rx.text("Subtotal: R$ " + item.subtotal),
                rx.cond(
                    item.available,
                    rx.badge("Disponível", color_scheme="cyan"),
                    rx.badge("Indisponível", color_scheme="red"),
                ),
                align="stretch",
                spacing="2",
            ),
        )

    delivery_address = rx.cond(
        State.checkout_review_ready,
        surface_card(
            rx.vstack(
                section_heading("Endereço de entrega", size="4"),
            rx.text(State.checkout_address_label),
            rx.text(
                State.checkout_address_street
                + ", "
                + State.checkout_address_number
            ),
            rx.text(
                State.checkout_address_neighborhood
                + " - "
                + State.checkout_address_city
                + "/"
                + State.checkout_address_state
            ),
            rx.text("CEP: " + State.checkout_address_cep),
            align="stretch",
            spacing="2",
            width="100%",
        ),
        ),
        rx.fragment(),
    )

    checkout_review_section = rx.cond(
        State.checkout_review_ready,
        surface_card(
            rx.vstack(
                section_heading("Revise seu pedido", size="5"),
                rx.foreach(State.checkout_review_items, review_item),
                delivery_address,
                rx.text(
                    "Subtotal: R$ " + State.checkout_subtotal,
                    color=COLOR_TEXT_MUTED,
                ),
                rx.text("Frete: R$ " + State.checkout_freight, color=COLOR_TEXT_MUTED),
                section_heading("Total: R$ " + State.checkout_total, size="5"),
            rx.cond(
                State.checkout_review_items.length() > 0,
                rx.form(
                    rx.vstack(
                        rx.select.root(
                            rx.select.trigger(),
                            rx.select.content(
                                rx.select.item("PIX", value="PIX"),
                                rx.select.item("Cartão", value="CARTAO"),
                                rx.select.item("Boleto", value="BOLETO"),
                            ),
                            name="metodo_pagamento",
                            value=State.checkout_method,
                            on_change=State.set_checkout_method,
                            width="100%",
                        ),
                        rx.text(
                            "O pagamento ficará pendente. Nenhuma cobrança será "
                            "processada nesta etapa."
                        ),
                        primary_button(
                            "Confirmar pedido",
                            type="submit",
                            disabled=(
                                State.checkout_loading
                                | (State.checkout_review_items.length() == 0)
                            ),
                        ),
                        align="stretch",
                        spacing="3",
                        width="100%",
                    ),
                    on_submit=State.confirm_checkout,
                ),
                rx.fragment(),
            ),
            align="stretch",
                spacing="3",
                width="100%",
            ),
        ),
        rx.fragment(),
    )

    authenticated_checkout = rx.vstack(
        rx.text(
            "Cliente: " + State.customer_name,
            weight="bold",
            color=COLOR_NAVY,
        ),
        feedback_text(State.checkout_message, tone="error"),
        rx.cond(
            State.customer_addresses.length() == 0,
            rx.vstack(
                rx.text(
                    "Cadastre um Endereço ativo antes de continuar o checkout."
                ),
                rx.link("Gerenciar endereços", href="/cliente"),
                align="stretch",
                spacing="2",
            ),
            rx.fragment(),
        ),
        rx.select.root(
            rx.select.trigger(placeholder="Selecione o endereço de entrega"),
            rx.select.content(
                rx.foreach(
                    State.customer_addresses,
                    lambda address: rx.cond(
                        address.status == "ATIVO",
                        rx.select.item(
                            address.label
                            + " - "
                            + address.street
                            + ", "
                            + address.number,
                            value=address.id.to_string(),
                        ),
                        rx.fragment(),
                    ),
                )
            ),
            value=State.checkout_address_id,
            on_change=State.set_checkout_address,
            width="100%",
        ),
        primary_button(
            "Revisar carrinho",
            on_click=State.load_checkout_review,
            disabled=(
                State.checkout_loading
                | (State.checkout_address_id == "")
                | (State.customer_addresses.length() == 0)
            ),
        ),
        rx.cond(
            State.checkout_loading,
            loading_text("Validando itens e valores..."),
            rx.fragment(),
        ),
        checkout_review_section,
        align="stretch",
        spacing="4",
        width="100%",
    )

    return page_shell(
        section_heading("Checkout"),
        rx.cond(
            State.customer_authenticated,
            authenticated_checkout,
            rx.vstack(
                rx.text(
                    "Entre como Cliente para finalizar o pedido.",
                    color=COLOR_TEXT_MUTED,
                ),
                rx.link("Acessar conta de Cliente", href="/cliente"),
                align="stretch",
                spacing="3",
            ),
        ),
        header=site_header(
            [
                ("Catálogo público", "/catalogo"),
                ("Carrinho", "/carrinho"),
                ("Minha conta", "/cliente"),
                ("Acesso interno", "/interno"),
            ],
            active="/checkout",
            badge="Checkout",
        ),
        max_width="48rem",
        public_footer=True,
    )


def customer_orders_page() -> rx.Component:
    def order_card(order: OrderSummary) -> rx.Component:
        return surface_card(
            rx.vstack(
                section_heading("Pedido " + order.code, size="4"),
                rx.text("Data: " + order.order_date, color=COLOR_TEXT_MUTED),
                                status_badge(order.status),
                rx.text(
                    "Itens: " + order.order_items.length().to_string(),
                    color=COLOR_TEXT_MUTED,
                ),
                rx.text("Total: R$ " + order.total),
                secondary_button(
                    "Ver resumo",
                    on_click=State.load_customer_order(order.id),
                    disabled=State.order_loading,
                ),
                align="stretch",
                spacing="2",
                width="100%",
            ),
        )

    def order_item(item: OrderItemSummary) -> rx.Component:
        return rx.box(
            rx.vstack(
                rx.text(
                    rx.cond(
                        item.variation_name != "",
                        item.variation_name,
                        item.sku,
                    ),
                    weight="bold",
                    color=COLOR_NAVY,
                ),
                rx.text("SKU: " + item.sku),
                rx.text("Quantidade: " + item.quantity.to_string()),
                rx.text("Preço unitário: R$ " + item.unit_price),
                rx.text("Subtotal: R$ " + item.subtotal),
                align="stretch",
                spacing="2",
            ),
            border=f"1px solid {COLOR_BORDER}",
            border_radius=RADIUS,
            padding="3",
            width="100%",
            background=COLOR_SURFACE,
        )

    order_details = rx.cond(
        State.selected_order_present,
        surface_card(
            rx.vstack(
                rx.hstack(
                    section_heading(
                        "Pedido " + State.selected_order_code,
                        size="5",
                    ),
                            status_badge(State.selected_order_status),
                    justify="between",
                    width="100%",
                    wrap="wrap",
                ),
                section_heading("Entrega", size="4"),
                rx.text(State.selected_order_delivery_label),
                rx.text(
                    State.selected_order_delivery_street
                    + ", "
                    + State.selected_order_delivery_number
                ),
                rx.text(
                    State.selected_order_delivery_neighborhood
                    + " - "
                    + State.selected_order_delivery_city
                    + "/"
                    + State.selected_order_delivery_state
                ),
                rx.text("CEP: " + State.selected_order_delivery_cep),
                section_heading("Itens", size="4"),
                rx.foreach(State.selected_order_items, order_item),
                rx.text(
                    "Subtotal: R$ " + State.selected_order_subtotal,
                    color=COLOR_TEXT_MUTED,
                ),
                rx.text(
                    "Frete: R$ " + State.selected_order_freight,
                    color=COLOR_TEXT_MUTED,
                ),
                section_heading("Total: R$ " + State.selected_order_total, size="5"),
                rx.text(
                    "Pagamento: "
                    + State.selected_order_payment_method
                    + " — "
                    + State.selected_order_payment_status,
                    color=COLOR_TEXT_MUTED,
                ),
                rx.text(
                    "Aprovação simulada: nenhum valor será cobrado.",
                    color=COLOR_TEXT_MUTED,
                    font_size="0.85rem",
                ),
                rx.cond(
                    (State.selected_order_status == "AGUARDANDO_PAGAMENTO")
                    & (State.selected_order_payment_status == "PENDENTE"),
                    primary_button(
                        "Simular pagamento",
                        on_click=State.simulate_order_payment,
                        disabled=State.payment_simulating,
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    State.payment_simulating,
                    loading_text("Simulando pagamento..."),
                    rx.fragment(),
                ),
                feedback_text(State.payment_message),
                align="stretch",
                spacing="3",
                width="100%",
            ),
        ),
        rx.fragment(),
    )

    return page_shell(
        section_heading("Meus pedidos"),
        rx.cond(
            State.customer_authenticated,
            rx.vstack(
                feedback_text(State.orders_message, tone="error"),
                secondary_button(
                    "Atualizar histórico",
                    on_click=State.load_customer_orders,
                    disabled=State.orders_loading,
                ),
                rx.cond(
                    State.orders_loading,
                    loading_text("Carregando pedidos..."),
                    rx.fragment(),
                ),
                rx.cond(
                    State.orders.length() == 0,
                    empty_state("Você ainda não possui pedidos."),
                    rx.foreach(State.orders, order_card),
                ),
                order_details,
                align="stretch",
                spacing="4",
                width="100%",
            ),
            rx.vstack(
                rx.text(
                    "Entre como Cliente para consultar seus pedidos.",
                    color=COLOR_TEXT_MUTED,
                ),
                rx.link("Acessar conta de Cliente", href="/cliente"),
                align="stretch",
                spacing="3",
            ),
        ),
        header=site_header(
            [
                ("Catálogo público", "/catalogo"),
                ("Carrinho", "/carrinho"),
                ("Minha conta", "/cliente"),
                ("Acesso interno", "/interno"),
            ],
            active="/pedidos",
            badge="Meus pedidos",
        ),
        max_width="48rem",
        public_footer=True,
    )


app = rx.App(
    style={
        "font_family": "Inter, system-ui, -apple-system, 'Segoe UI', sans-serif",
        "background_color": COLOR_SURFACE,
        "color": COLOR_TEXT,
    },
)
app.add_page(
    index,
    route="/interno",
    title="Acesso interno | Voltix",
)
app.add_page(
    home_page,
    route="/",
    title="Voltix - tecnologia premium",
    on_load=State.enter_public_home,
)
app.add_page(
    public_catalog_page,
    route="/catalogo",
    title="Catálogo | Voltix",
    on_load=State.enter_public_catalog,
)
app.add_page(
    customer_account_page,
    route="/cliente",
    title="Minha conta | Voltix",
    on_load=State.validate_customer_session,
)
app.add_page(
    customer_cart_page,
    route="/carrinho",
    title="Carrinho | Voltix",
    on_load=State.load_cart,
)
app.add_page(
    customer_checkout_page,
    route="/checkout",
    title="Checkout | Voltix",
    on_load=State.prepare_checkout,
)
app.add_page(
    customer_orders_page,
    route="/pedidos",
    title="Meus pedidos | Voltix",
    on_load=State.load_customer_orders,
)
