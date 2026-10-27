import asyncio
import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

import voltix.voltix as app


class _CatalogState:
    _public_catalog_request = app.State._public_catalog_request
    _fetch_public_products = app.State._fetch_public_products
    _load_public_catalog_data = app.State._load_public_catalog_data
    public_category_id = ''
    public_catalog_search = ''
    public_categories = []
    public_products = []
    public_catalog_loaded = False
    public_catalog_loading = False
    public_catalog_message = ''


class PublicCatalogHttpRecoveryTests(unittest.TestCase):
    def test_retry_recovers_after_real_local_http_503(self):
        calls = []
        recovery = threading.Event()

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                calls.append((self.path, self.headers.get('Authorization')))
                if not recovery.is_set():
                    status, payload = 503, {'message': 'local test failure'}
                elif self.path == '/categories':
                    status, payload = 200, [{'id': 2, 'name': 'Monitores', 'description': '', 'status': 'ATIVO'}]
                else:
                    status, payload = 200, []
                body = json.dumps(payload).encode()
                self.send_response(status)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(app._reset_public_catalog_cache)
        app._reset_public_catalog_cache()
        base = f'http://127.0.0.1:{server.server_port}'
        state = _CatalogState()

        async def run():
            with patch.dict('os.environ', {
                app.XANO_PUBLIC_CATEGORIES_URL_ENV: base + '/categories',
                app.XANO_PUBLIC_PRODUCTS_URL_ENV: base + '/products',
            }):
                with self.assertLogs(app.PUBLIC_CATALOG_LOGGER, level='WARNING'):
                    await app.State.load_public_catalog.fn(state)
                self.assertTrue(state.public_catalog_loaded)
                self.assertFalse(state.public_catalog_loading)
                self.assertIn('Não foi possível', state.public_catalog_message)
                self.assertEqual(len(calls), 1)
                recovery.set()
                await app.State.load_public_catalog.fn(state)
                self.assertEqual(state.public_catalog_message, '')
                self.assertFalse(state.public_catalog_loading)
                self.assertEqual(state.public_categories[0].name, 'Monitores')
                self.assertEqual(state.public_products, [])
                self.assertEqual([path for path, _ in calls], ['/categories', '/categories', '/products'])
                self.assertTrue(all(auth is None for _, auth in calls))

        try:
            asyncio.run(run())
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == '__main__':
    unittest.main()
