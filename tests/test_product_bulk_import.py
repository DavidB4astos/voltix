import asyncio
import io
import os
import unittest
import zipfile
from pathlib import Path
from unittest.mock import AsyncMock, patch
from urllib.error import HTTPError
from xml.sax.saxutils import escape

import voltix.voltix as app

_XLSX_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
_XLSX_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def _csv_bytes(rows):
    text = "\n".join(";".join(str(value) for value in row) for row in rows)
    return text.encode("utf-8-sig")


def _column_letter(index):
    letters = ""
    index += 1
    while index:
        index, remainder = divmod(index - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters


def _xlsx_bytes(rows, *, formula_cell=None):
    sheet_rows = []
    for row_index, row in enumerate(rows, start=1):
        cells = []
        for column_index, value in enumerate(row):
            reference = f"{_column_letter(column_index)}{row_index}"
            if formula_cell == reference:
                cells.append(
                    f'<c r="{reference}"><f>1+1</f><v>2</v></c>'
                )
            else:
                cells.append(
                    f'<c r="{reference}" t="inlineStr"><is><t>'
                    f"{escape(str(value))}</t></is></c>"
                )
        sheet_rows.append(f'<row r="{row_index}">{"".join(cells)}</row>')
    worksheet = (
        f'<?xml version="1.0"?><worksheet xmlns="{_XLSX_NS}">'
        f'<sheetData>{"".join(sheet_rows)}</sheetData></worksheet>'
    )
    workbook = (
        f'<?xml version="1.0"?><workbook xmlns="{_XLSX_NS}" '
        f'xmlns:r="{_XLSX_REL_NS}"><sheets><sheet name="Sheet1" '
        'sheetId="1" r:id="rId1"/></sheets></workbook>'
    )
    relationships = (
        '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats'
        '.org/package/2006/relationships"><Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships'
        '/worksheet" Target="worksheets/sheet1.xml"/></Relationships>'
    )
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("xl/workbook.xml", workbook)
        archive.writestr("xl/_rels/workbook.xml.rels", relationships)
        archive.writestr("xl/worksheets/sheet1.xml", worksheet)
    return buffer.getvalue()


def _data_rows(*rows):
    return [list(row) for row in rows]


def _product_entry(name, category, brand, variations, product_id=1):
    return app.ProductEntry(
        id=product_id,
        name=name,
        description="d",
        technical_specifications="s",
        image_present=False,
        category_id=category.id,
        category_name=category.name,
        category_status=category.status,
        brand_id=brand.id,
        brand_name=brand.name,
        brand_status=brand.status,
        status="ATIVO",
        variations=[
            app.ProductVariation(
                id=index + 1,
                product_id=product_id,
                name_or_description=variation[0],
                sku=variation[1],
                price=variation[2],
                available_quantity=variation[3],
                status="ATIVO",
            )
            for index, variation in enumerate(variations)
        ],
    )


_HEADER = list(app.BULK_IMPORT_HEADERS)
_VALID_ROW = [
    "Notebook",
    "Notebook simples",
    "8 GB",
    "Computadores",
    "Voltix",
    "Padrão",
    "SKU-1",
    "10.00",
    "2",
]


class _FakeBulkState:
    _bulk_import_is_admin = app.State._bulk_import_is_admin
    _refresh_products = AsyncMock(return_value=True)
    _auth_token = "unit-test-placeholder"
    is_authenticated = True
    session_status = "success"
    user_role = "ADMINISTRADOR"
    user_status = "ATIVO"
    products = []
    bulk_import_preview = []
    bulk_import_report = []
    bulk_import_message = ""
    bulk_import_progress = ""
    bulk_import_loading = False
    bulk_import_has_valid = False
    bulk_import_cancel_requested = False
    _bulk_import_valid_groups = []
    _bulk_import_last_request_at = 0.0
    _bulk_import_in_progress = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc_info):
        return False


class _FakeEmployeeBulkState(_FakeBulkState):
    user_role = "FUNCIONARIO"


class _FakeCatalogState:
    _catalog_request = app.State._catalog_request
    _auth_token = "unit-test-placeholder"
    is_authenticated = True
    session_status = "success"
    user_role = "ADMINISTRADOR"
    user_status = "ATIVO"


class _FakeUpload:
    def __init__(self, name, data):
        self.name = name
        self._data = data

    async def read(self):
        return self._data


class BulkImportParsingTests(unittest.TestCase):
    def test_csv_parser_reads_semicolon_file_with_bom(self):
        data = _csv_bytes([_HEADER, _VALID_ROW])
        rows = app._bulk_import_parse("dados.csv", data)
        self.assertEqual(rows, [_VALID_ROW])

    def test_xlsx_parser_reads_inline_strings(self):
        data = _xlsx_bytes([_HEADER, _VALID_ROW])
        rows = app._bulk_import_parse("dados.xlsx", data)
        self.assertEqual(rows, [_VALID_ROW])

    def test_xlsx_parser_rejects_formulas(self):
        data = _xlsx_bytes([_HEADER, _VALID_ROW], formula_cell="G2")
        with self.assertRaisesRegex(ValueError, "fórmulas"):
            app._bulk_import_parse("dados.xlsx", data)

    def test_parser_rejects_legacy_xls_extension(self):
        with self.assertRaisesRegex(ValueError, "\\.xls"):
            app._bulk_import_parse("dados.xls", b"anything")

    def test_parser_rejects_unsupported_extension(self):
        with self.assertRaisesRegex(ValueError, "Formato não suportado"):
            app._bulk_import_parse("dados.txt", b"anything")

    def test_parser_rejects_oversized_file(self):
        oversize = b"a" * (app.BULK_IMPORT_MAX_BYTES + 1)
        with self.assertRaisesRegex(ValueError, "2 MB"):
            app._bulk_import_parse("dados.csv", oversize)

    def test_parser_rejects_invalid_headers(self):
        data = _csv_bytes([["nome", "descricao"], _VALID_ROW])
        with self.assertRaisesRegex(ValueError, "Cabeçalhos inválidos"):
            app._bulk_import_parse("dados.csv", data)

    def test_parser_rejects_more_than_max_rows(self):
        rows = [_HEADER] + [
            list(_VALID_ROW)
            for _ in range(app.BULK_IMPORT_MAX_ROWS + 1)
        ]
        for index, row in enumerate(rows[1:], start=1):
            row[0] = f"Produto {index}"
            row[6] = f"SKU-{index}"
        data = _csv_bytes(rows)
        with self.assertRaisesRegex(ValueError, "200 linhas"):
            app._bulk_import_parse("dados.csv", data)

    def test_parser_rejects_more_than_max_products(self):
        rows = [_HEADER]
        for index in range(app.BULK_IMPORT_MAX_PRODUCTS + 1):
            row = list(_VALID_ROW)
            row[0] = f"Produto {index}"
            row[6] = f"SKU-{index}"
            rows.append(row)
        data = _csv_bytes(rows)
        with self.assertRaisesRegex(ValueError, "50 produtos"):
            app._bulk_import_parse("dados.csv", data)


class BulkImportFieldTests(unittest.TestCase):
    def test_price_accepts_decimal_comma_and_rejects_invalid(self):
        self.assertEqual(app._bulk_import_price("12,50"), 12.5)
        self.assertEqual(app._bulk_import_price("10.00"), 10.0)
        for value in ("", "abc", "0", "-1", "1.234"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                app._bulk_import_price(value)

    def test_quantity_requires_non_negative_integer(self):
        self.assertEqual(app._bulk_import_quantity("2"), 2)
        self.assertEqual(app._bulk_import_quantity("0"), 0)
        for value in ("", "abc", "-1", "1.5"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                app._bulk_import_quantity(value)


class BulkImportValidationTests(unittest.TestCase):
    def setUp(self):
        self.categories = [app.CatalogEntry(3, "Computadores", "desc", "ATIVO")]
        self.brands = [app.CatalogEntry(4, "Voltix", "desc", "ATIVO")]
        self.products = []

    def test_valid_row_is_grouped_and_marked_valid(self):
        preview, groups = app._bulk_import_validate(
            _data_rows(_VALID_ROW),
            self.categories,
            self.brands,
            self.products,
        )
        self.assertEqual(len(preview), 1)
        self.assertEqual(preview[0].status, app.BULK_IMPORT_VALID_STATUS)
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].product_name, "Notebook")
        self.assertEqual(groups[0].variations[0].price, 10.0)
        self.assertEqual(groups[0].variations[0].quantity, 2)

    def test_missing_required_field_is_reported_as_error(self):
        row = list(_VALID_ROW)
        row[6] = ""
        preview, groups = app._bulk_import_validate(
            _data_rows(row), self.categories, self.brands, self.products
        )
        self.assertEqual(preview[0].status, app.BULK_IMPORT_ERROR_STATUS)
        self.assertIn("obrigatórios", preview[0].reason)
        self.assertEqual(groups, [])

    def test_duplicate_sku_in_file_invalidates_second_row(self):
        first = list(_VALID_ROW)
        second = list(_VALID_ROW)
        second[0] = "Monitor"
        preview, groups = app._bulk_import_validate(
            _data_rows(first, second),
            self.categories,
            self.brands,
            self.products,
        )
        self.assertEqual(preview[0].status, app.BULK_IMPORT_VALID_STATUS)
        self.assertEqual(preview[1].status, app.BULK_IMPORT_ERROR_STATUS)
        self.assertIn("duplicado", preview[1].reason)
        self.assertEqual(len(groups), 1)

    def test_existing_product_is_marked_duplicate(self):
        products = [
            _product_entry(
                "Notebook",
                self.categories[0],
                self.brands[0],
                [("Padrão", "OUTRO-SKU", 5.0, 1.0)],
            )
        ]
        preview, groups = app._bulk_import_validate(
            _data_rows(_VALID_ROW),
            self.categories,
            self.brands,
            products,
        )
        self.assertEqual(preview[0].status, app.BULK_IMPORT_DUPLICATE_STATUS)
        self.assertEqual(groups, [])

    def test_missing_and_inactive_category_are_errors(self):
        row = list(_VALID_ROW)
        row[3] = "Inexistente"
        preview, _ = app._bulk_import_validate(
            _data_rows(row), self.categories, self.brands, self.products
        )
        self.assertIn("não encontrada", preview[0].reason)

        inactive = [app.CatalogEntry(3, "Computadores", "desc", "INATIVO")]
        preview, _ = app._bulk_import_validate(
            _data_rows(_VALID_ROW), inactive, self.brands, self.products
        )
        self.assertEqual(preview[0].status, app.BULK_IMPORT_ERROR_STATUS)
        self.assertIn("inativa", preview[0].reason)

    def test_inconsistent_grouping_invalidates_all_rows(self):
        first = list(_VALID_ROW)
        second = list(_VALID_ROW)
        second[4] = "Outra"
        preview, _ = app._bulk_import_validate(
            _data_rows(first, second),
            self.categories,
            [app.CatalogEntry(4, "Outra", "desc", "ATIVO")],
            self.products,
        )
        self.assertEqual(preview[0].status, app.BULK_IMPORT_ERROR_STATUS)
        self.assertEqual(preview[1].status, app.BULK_IMPORT_ERROR_STATUS)
        self.assertIn("Agrupamento", preview[0].reason)


class BulkImportStateTests(unittest.TestCase):
    def _state(self, cls=_FakeBulkState):
        state = cls()
        state._refresh_products = AsyncMock(return_value=True)
        return state

    def test_preview_requires_active_administrator(self):
        state = self._state(_FakeEmployeeBulkState)
        state._bulk_import_load_catalog = AsyncMock()
        asyncio.run(
            app.State.preview_bulk_import.fn(
                state, [_FakeUpload("dados.csv", _csv_bytes([_HEADER, _VALID_ROW]))]
            )
        )
        self.assertIn("autorização", state.bulk_import_message)
        state._bulk_import_load_catalog.assert_not_called()

    def test_preview_builds_preview_and_enables_confirmation(self):
        state = self._state()
        state._bulk_import_load_catalog = AsyncMock(
            return_value=(
                [app.CatalogEntry(3, "Computadores", "d", "ATIVO")],
                [app.CatalogEntry(4, "Voltix", "d", "ATIVO")],
                [],
            )
        )
        asyncio.run(
            app.State.preview_bulk_import.fn(
                state, [_FakeUpload("dados.csv", _csv_bytes([_HEADER, _VALID_ROW]))]
            )
        )
        self.assertEqual(len(state.bulk_import_preview), 1)
        self.assertTrue(state.bulk_import_has_valid)
        self.assertEqual(len(state._bulk_import_valid_groups), 1)
        self.assertFalse(state.bulk_import_loading)

    def test_preview_reports_parse_error(self):
        state = self._state()
        state._bulk_import_load_catalog = AsyncMock()
        asyncio.run(
            app.State.preview_bulk_import.fn(
                state, [_FakeUpload("dados.xls", b"data")]
            )
        )
        self.assertIn(".xls", state.bulk_import_message)
        state._bulk_import_load_catalog.assert_not_called()

    def _confirm_state(self, products=None, request=None):
        state = self._state()
        state._bulk_import_valid_groups = [
            app.BulkImportGroup(
                product_name="Notebook",
                description="d",
                specifications="s",
                category_name="Computadores",
                brand_name="Voltix",
                variations=(
                    app.BulkImportVariation("Padrão", "SKU-1", 10.0, 2),
                ),
            )
        ]
        state._bulk_import_load_catalog = AsyncMock(
            return_value=(
                [app.CatalogEntry(3, "Computadores", "d", "ATIVO")],
                [app.CatalogEntry(4, "Voltix", "d", "ATIVO")],
                products or [],
            )
        )
        state._bulk_import_request = request or AsyncMock(return_value={"id": 9})
        state._bulk_import_wait = AsyncMock()
        return state

    def test_confirm_posts_group_with_expected_payload(self):
        state = self._confirm_state()
        asyncio.run(app.State.confirm_bulk_import.fn(state))
        call = state._bulk_import_request.await_args
        self.assertEqual(call.args[0], app.XANO_PRODUCTS_URL_ENV)
        self.assertEqual(call.kwargs["method"], "POST")
        self.assertEqual(call.kwargs["payload"]["categoria_id"], 3)
        self.assertEqual(call.kwargs["payload"]["marca_id"], 4)
        self.assertEqual(
            call.kwargs["payload"]["variacoes"],
            [
                {
                    "nome_ou_descricao": "Padrão",
                    "sku": "SKU-1",
                    "preco": 10.0,
                    "quantidade_disponivel": 2,
                }
            ],
        )
        self.assertEqual(
            state.bulk_import_report[0].outcome, app.BULK_IMPORT_CREATED_OUTCOME
        )
        self.assertIn("concluída", state.bulk_import_message)
        state._refresh_products.assert_awaited_once()

    def test_confirm_skips_existing_products(self):
        products = [
            _product_entry(
                "Notebook",
                app.CatalogEntry(3, "Computadores", "d", "ATIVO"),
                app.CatalogEntry(4, "Voltix", "d", "ATIVO"),
                [("Padrão", "OUTRO", 5.0, 1.0)],
            )
        ]
        state = self._confirm_state(products=products)
        asyncio.run(app.State.confirm_bulk_import.fn(state))
        state._bulk_import_request.assert_not_awaited()
        self.assertEqual(
            state.bulk_import_report[0].outcome, app.BULK_IMPORT_SKIPPED_OUTCOME
        )

    def test_confirm_stops_on_authorization_failure(self):
        failure = HTTPError("https://example.invalid", 403, "Forbidden", {}, None)
        state = self._confirm_state(
            request=AsyncMock(side_effect=failure)
        )
        asyncio.run(app.State.confirm_bulk_import.fn(state))
        self.assertIn("autorização", state.bulk_import_message)
        self.assertEqual(
            state.bulk_import_report[0].outcome, app.BULK_IMPORT_FAILED_OUTCOME
        )
        failure.close()

    def test_confirm_treats_existing_sku_conflict_as_skipped(self):
        body = io.BytesIO(b'{"message":"A variation with this SKU already exists."}')
        failure = HTTPError("https://example.invalid", 400, "Bad Request", {}, body)
        state = self._confirm_state(request=AsyncMock(side_effect=failure))
        asyncio.run(app.State.confirm_bulk_import.fn(state))
        self.assertEqual(
            state.bulk_import_report[0].outcome, app.BULK_IMPORT_SKIPPED_OUTCOME
        )
        failure.close()

    def test_ambiguous_429_on_post_is_not_reported_as_success(self):
        """A rate-limited write must never be presented as success.

        A 429 does not guarantee the write was not persisted. The safe
        behaviour is to surface a failure (retryable) rather than assume the
        product was created. Re-sending the same file is the safe resumption
        path because the backend rejects duplicate SKUs.
        """
        body = io.BytesIO(b'{"message":"ERROR_CODE_TOO_MANY_REQUESTS"}')
        failure = HTTPError(
            "https://example.invalid", 429, "Too Many", {}, body
        )
        state = self._confirm_state(request=AsyncMock(side_effect=failure))
        asyncio.run(app.State.confirm_bulk_import.fn(state))
        self.assertNotEqual(
            state.bulk_import_report[0].outcome, app.BULK_IMPORT_CREATED_OUTCOME
        )
        self.assertEqual(
            state.bulk_import_report[0].outcome, app.BULK_IMPORT_FAILED_OUTCOME
        )
        self.assertIn("requisições", state.bulk_import_report[0].detail)
        failure.close()

    def test_confirm_continues_after_one_group_fails(self):
        """One failing group must not stop the remaining groups."""
        second = app.BulkImportGroup(
            product_name="Monitor",
            description="d",
            specifications="s",
            category_name="Computadores",
            brand_name="Voltix",
            variations=(app.BulkImportVariation("Padrão", "SKU-2", 5.0, 1),),
        )
        state = self._confirm_state()
        state._bulk_import_valid_groups.append(second)
        failure = HTTPError("https://example.invalid", 500, "Server", {}, None)
        calls = {"n": 0}

        async def flaky(*args, **kwargs):
            calls["n"] += 1
            if calls["n"] == 1:
                raise failure
            return {"id": 9}

        state._bulk_import_request = AsyncMock(side_effect=flaky)
        asyncio.run(app.State.confirm_bulk_import.fn(state))
        outcomes = [r.outcome for r in state.bulk_import_report]
        self.assertEqual(
            outcomes,
            [app.BULK_IMPORT_FAILED_OUTCOME, app.BULK_IMPORT_CREATED_OUTCOME],
        )
        failure.close()

    def test_confirm_can_be_cancelled_between_groups(self):
        state = self._confirm_state()
        state._bulk_import_valid_groups.append(
            app.BulkImportGroup(
                product_name="Monitor",
                description="d",
                specifications="s",
                category_name="Computadores",
                brand_name="Voltix",
                variations=(app.BulkImportVariation("Padrão", "SKU-2", 5.0, 1),),
            )
        )

        async def cancel_after_first(*args, **kwargs):
            state.bulk_import_cancel_requested = True
            return {"id": 9}

        state._bulk_import_request = AsyncMock(side_effect=cancel_after_first)
        asyncio.run(app.State.confirm_bulk_import.fn(state))
        self.assertEqual(state._bulk_import_request.await_count, 1)
        self.assertIn("cancelada", state.bulk_import_message)
        self.assertIn("Criados: 1", state.bulk_import_message)
        self.assertEqual(state.bulk_import_progress, "")
        self.assertFalse(state.bulk_import_loading)
        self.assertFalse(state._bulk_import_in_progress)

    def test_confirm_cancelled_during_catalog_load_never_posts(self):
        state = self._confirm_state()

        async def load_catalog_and_cancel():
            state.bulk_import_cancel_requested = True
            return (
                [app.CatalogEntry(3, "Computadores", "d", "ATIVO")],
                [app.CatalogEntry(4, "Voltix", "d", "ATIVO")],
                [],
            )

        state._bulk_import_load_catalog = AsyncMock(
            side_effect=load_catalog_and_cancel
        )
        asyncio.run(app.State.confirm_bulk_import.fn(state))
        state._bulk_import_request.assert_not_awaited()
        self.assertEqual(state.bulk_import_report, [])
        self.assertIn("cancelada", state.bulk_import_message)
        self.assertIn("Criados: 0", state.bulk_import_message)
        self.assertFalse(state.bulk_import_loading)
        self.assertFalse(state._bulk_import_in_progress)

    def test_confirm_reports_progress_with_counters_and_clears_it(self):
        state = self._confirm_state()
        seen = []

        async def load_catalog():
            seen.append(state.bulk_import_progress)
            return (
                [app.CatalogEntry(3, "Computadores", "d", "ATIVO")],
                [app.CatalogEntry(4, "Voltix", "d", "ATIVO")],
                [],
            )

        async def request(*args, **kwargs):
            seen.append(state.bulk_import_progress)
            return {"id": 9}

        state._bulk_import_load_catalog = AsyncMock(side_effect=load_catalog)
        state._bulk_import_request = AsyncMock(side_effect=request)
        asyncio.run(app.State.confirm_bulk_import.fn(state))
        self.assertEqual(seen[0], "Carregando catálogo...")
        self.assertIn("Processando 1/1: Notebook", seen[1])
        self.assertIn("criados: 0, pulados: 0, falhas: 0", seen[1])
        self.assertEqual(state.bulk_import_progress, "")
        self.assertIn("concluída", state.bulk_import_message)
        self.assertIn("Criados: 1", state.bulk_import_message)
        self.assertFalse(state.bulk_import_loading)
        self.assertFalse(state._bulk_import_in_progress)

    def test_confirm_is_rejected_while_another_import_is_running(self):
        state = self._confirm_state()
        state._bulk_import_in_progress = True
        asyncio.run(app.State.confirm_bulk_import.fn(state))
        state._bulk_import_load_catalog.assert_not_awaited()
        state._bulk_import_request.assert_not_awaited()
        self.assertEqual(state.bulk_import_message, "")
        self.assertFalse(state.bulk_import_loading)

    def test_preview_is_blocked_while_import_is_running(self):
        state = self._state()
        state.bulk_import_loading = True
        state._bulk_import_load_catalog = AsyncMock()
        asyncio.run(
            app.State.preview_bulk_import.fn(
                state, [_FakeUpload("dados.csv", _csv_bytes([_HEADER, _VALID_ROW]))]
            )
        )
        self.assertIn("Aguarde", state.bulk_import_message)
        state._bulk_import_load_catalog.assert_not_awaited()

    def test_reset_is_blocked_while_import_is_running(self):
        state = self._state()
        state.bulk_import_loading = True
        state.bulk_import_preview = ["x"]
        state.bulk_import_report = ["y"]
        app.State.reset_bulk_import.fn(state)
        self.assertEqual(state.bulk_import_preview, ["x"])
        self.assertEqual(state.bulk_import_report, ["y"])

    def test_reset_clears_preview_and_report(self):
        state = self._state()
        state.bulk_import_preview = ["x"]
        state.bulk_import_report = ["y"]
        state.bulk_import_has_valid = True
        app.State.reset_bulk_import.fn(state)
        self.assertEqual(state.bulk_import_preview, [])
        self.assertEqual(state.bulk_import_report, [])
        self.assertFalse(state.bulk_import_has_valid)


class BulkImportRequestTests(unittest.TestCase):
    def test_catalog_request_forwards_retry_rate_limit(self):
        os.environ[app.XANO_PRODUCTS_URL_ENV] = (
            "https://example.invalid/api:voltix-product-management/products"
        )
        mocked_request = AsyncMock(return_value=[])

        async def run():
            with patch("voltix.voltix._server_side_xano_request", mocked_request):
                await app.State._catalog_request(
                    _FakeCatalogState(),
                    app.XANO_PRODUCTS_URL_ENV,
                    method="POST",
                    payload={"a": 1},
                    retry_rate_limit=True,
                )
            self.assertTrue(mocked_request.call_args.kwargs["retry_rate_limit"])

        asyncio.run(run())

    def test_post_rate_limit_is_retried_only_when_opted_in(self):
        class _Response:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def read(self):
                return b'{"id": 1}'

        attempts = {"count": 0}

        def fake_urlopen(request, timeout=10):
            attempts["count"] += 1
            if attempts["count"] == 1:
                raise HTTPError(
                    request.full_url, 429, "Too Many", {}, io.BytesIO(b"")
                )
            return _Response()

        with patch(
            "voltix.voltix.urllib.request.urlopen", side_effect=fake_urlopen
        ), patch("voltix.voltix.time.sleep"):
            result = app._request_xano_json(
                "https://example.invalid/api/products",
                method="POST",
                payload={"a": 1},
                retry_rate_limit=True,
            )
        self.assertEqual(result, {"id": 1})
        self.assertEqual(attempts["count"], 2)

    def test_post_rate_limit_is_not_retried_by_default(self):
        failure = HTTPError(
            "https://example.invalid", 429, "Too Many", {}, io.BytesIO(b"")
        )
        with patch(
            "voltix.voltix.urllib.request.urlopen", side_effect=failure
        ):
            with self.assertRaises(HTTPError):
                app._request_xano_json(
                    "https://example.invalid/api/products",
                    method="POST",
                    payload={"a": 1},
                )
        failure.close()


class BulkImportInterfaceTests(unittest.TestCase):
    def test_bulk_import_ui_is_admin_only_and_present_in_protected_area(self):
        source = Path("voltix/voltix.py").read_text(encoding="utf-8")
        bulk_ui = source.split("    bulk_import_management = rx.cond(", 1)[1]
        bulk_ui = bulk_ui.split("    catalog_management = rx.cond(", 1)[0]
        self.assertIn('State.user_role == "ADMINISTRADOR"', bulk_ui)
        self.assertIn("State.preview_bulk_import", bulk_ui)
        self.assertIn("State.confirm_bulk_import", bulk_ui)
        self.assertIn("State.cancel_bulk_import", bulk_ui)
        protected = source.split("    protected_area = rx.cond(", 1)[1]
        protected = protected.split("    return page_shell(", 1)[0]
        self.assertIn("bulk_import_management", protected)


if __name__ == "__main__":
    unittest.main()
