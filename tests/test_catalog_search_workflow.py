import asyncio
import io
import unittest
from types import MethodType, SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import voltix.voltix as app


class CatalogSearchWorkflowTests(unittest.TestCase):
    def state(self, *, category='', applied='', draft='', query='', params=None):
        state = SimpleNamespace(
            public_category_id=category, public_catalog_search=applied,
            public_catalog_search_input=draft, public_catalog_loading=False,
            router=SimpleNamespace(url=SimpleNamespace(path='/catalogo', query=query, query_parameters=params or {})),
            close_public_product_details=Mock(), load_public_catalog=AsyncMock(),
            load_public_product_details=AsyncMock(),
        )
        state._public_catalog_navigation = MethodType(app.State._public_catalog_navigation, state)
        return state

    def test_submit_trims_and_encodes_term_with_category(self):
        state = self.state(category='3')
        with patch.object(app.rx, 'redirect', return_value='redirect') as redirect:
            result = app.State.search_public_catalog.fn(state, {'search': '  mouse & teclado  '})
        redirect.assert_called_once_with('/catalogo?category_id=3&q=mouse+%26+teclado')
        self.assertEqual(result, 'redirect')
        self.assertEqual(state.public_catalog_search, 'mouse & teclado')
        self.assertEqual(state.public_catalog_search_input, 'mouse & teclado')
        self.assertTrue(state.public_catalog_loading)
        state.close_public_product_details.assert_called_once()

    def test_typing_changes_only_draft_without_request(self):
        state = self.state(applied='mouse')
        app.State.set_public_catalog_search_input.fn(state, 'teclado')
        self.assertEqual(state.public_catalog_search_input, 'teclado')
        self.assertEqual(state.public_catalog_search, 'mouse')
        state.load_public_catalog.assert_not_awaited()
        state.close_public_product_details.assert_not_called()

    def test_category_keeps_applied_query_and_discards_draft(self):
        state = self.state(applied='mouse', draft='não enviado')
        with patch.object(app.rx, 'redirect') as redirect:
            app.State.filter_public_catalog.fn(state, '4')
        redirect.assert_called_once_with('/catalogo?category_id=4&q=mouse')
        self.assertEqual(state.public_catalog_search_input, 'mouse')
        state.close_public_product_details.assert_called_once()

    def test_clear_removes_all_filters_and_detail(self):
        state = self.state(category='4', applied='mouse', draft='novo', query='category_id=4&q=mouse')
        with patch.object(app.rx, 'redirect') as redirect:
            app.State.clear_public_catalog_filters.fn(state)
        redirect.assert_called_once_with('/catalogo')
        self.assertEqual((state.public_category_id, state.public_catalog_search, state.public_catalog_search_input), ('','',''))
        state.close_public_product_details.assert_called_once()

    def test_same_query_returns_loader_instead_of_stuck_redirect(self):
        state = self.state(applied='mouse', query='q=mouse')
        with patch.object(app.rx, 'redirect') as redirect:
            result = app.State.search_public_catalog.fn(state, {'search':'mouse'})
        redirect.assert_not_called()
        self.assertIs(result, app.State.load_public_catalog)

    def test_url_entry_restores_query_and_existing_product_detail(self):
        state = self.state(params={'q':'  mouse  ', 'category_id':'4', 'product_id':'25'})
        asyncio.run(app.State.enter_public_catalog.fn(state))
        self.assertEqual((state.public_category_id, state.public_catalog_search, state.public_catalog_search_input), ('4','mouse','mouse'))
        state.load_public_catalog.assert_awaited_once()
        state.load_public_product_details.assert_awaited_once_with(25)

    def test_whitespace_term_uses_category_without_q(self):
        state = self.state(category='4')
        with patch.object(app.rx, 'redirect') as redirect:
            app.State.search_public_catalog.fn(state, {'search':'   '})
        redirect.assert_called_once_with('/catalogo?category_id=4')

    def test_form_and_url_terms_are_bounded(self):
        self.assertEqual(app._public_search_term(None), '')
        self.assertEqual(app._public_search_term(['mouse']), '')
        self.assertEqual(len(app._public_search_term('x'*150)), 100)
        state = self.state(params={'q':'x'*150})
        asyncio.run(app.State.enter_public_catalog.fn(state))
        self.assertEqual(len(state.public_catalog_search_input), 100)


    def test_failed_public_request_closes_http_response(self):
        body = io.BytesIO(b'local failure')
        error = app.urllib.error.HTTPError('https://example.invalid/catalog', 503, 'Unavailable', None, body)

        async def run():
            with patch.dict('os.environ', {app.XANO_PUBLIC_CATEGORIES_URL_ENV: 'https://example.invalid/categories'}), patch.object(app, '_server_side_xano_request', AsyncMock(side_effect=error)):
                with self.assertLogs(app.PUBLIC_CATALOG_LOGGER, level='WARNING'):
                    with self.assertRaises(app.urllib.error.HTTPError):
                        await app.State._public_catalog_request(self.state(), app.XANO_PUBLIC_CATEGORIES_URL_ENV)
        asyncio.run(run())
        self.assertTrue(body.closed)


if __name__ == '__main__':
    unittest.main()
