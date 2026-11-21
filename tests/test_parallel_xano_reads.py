import asyncio
from types import SimpleNamespace
import unittest

import voltix.voltix as app


class ParallelXanoReadsTests(unittest.TestCase):
    def test_load_public_product_details_runs_details_and_image_concurrently(self):
        in_flight = 0
        max_in_flight = 0

        async def fake_details(env, *, record_id=None):
            nonlocal in_flight, max_in_flight
            in_flight += 1
            max_in_flight = max(max_in_flight, in_flight)
            await asyncio.sleep(0.03)
            in_flight -= 1
            return {
                "product": {
                    "id": record_id,
                    "nome": "Produto Teste",
                    "descricao": "Desc",
                    "especificacoes_tecnicas": "Spec",
                    "categoria_id": 1,
                    "marca_id": 1,
                    "status": "ATIVO",
                },
                "category_name": "Periféricos",
                "brand_name": "Voltix",
                "variations": [
                    {
                        "id": 10,
                        "produto_id": record_id,
                        "nome": "Padrão",
                        "sku": "SKU-1",
                        "preco": 99.9,
                        "quantidade_disponivel": 2,
                        "status": "ATIVO",
                    }
                ],
            }

        async def fake_image(product_id):
            nonlocal in_flight, max_in_flight
            in_flight += 1
            max_in_flight = max(max_in_flight, in_flight)
            await asyncio.sleep(0.03)
            in_flight -= 1
            return ""

        dummy = SimpleNamespace(
            public_product_loading=False,
            public_product_message="",
            public_product_detail_id=None,
            public_selected_product=None,
            _public_catalog_request=fake_details,
            _public_product_image=fake_image,
        )
        asyncio.run(app.State.load_public_product_details.fn(dummy, 7))
        self.assertEqual(max_in_flight, 2)
        self.assertIsNotNone(dummy.public_selected_product)
        self.assertEqual(dummy.public_selected_product.id, 7)


if __name__ == "__main__":
    unittest.main()
