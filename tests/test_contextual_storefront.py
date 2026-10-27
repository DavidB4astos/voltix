import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
import voltix.voltix as app

class ContextualEntryTests(unittest.IsolatedAsyncioTestCase):
    def state(self, **params):
        return SimpleNamespace(router=SimpleNamespace(url=SimpleNamespace(query_parameters=params)), public_category_id='6', public_catalog_search='old', close_public_product_details=Mock(),load_public_catalog=AsyncMock(),load_public_product_details=AsyncMock())
    async def test_category_link_sets_filter(self):
        state=self.state(category_id='3')
        await app.State.enter_public_catalog.fn(state)
        self.assertEqual(state.public_category_id,'3')
        self.assertEqual(state.public_catalog_search,'')
        state.load_public_catalog.assert_awaited_once()
        state.load_public_product_details.assert_not_awaited()
    async def test_product_link_opens_detail(self):
        state=self.state(product_id='25')
        await app.State.enter_public_catalog.fn(state)
        state.load_public_product_details.assert_awaited_once_with(25)
        self.assertEqual(state.public_category_id,'')
    async def test_invalid_parameters_do_not_load_detail(self):
        for value in ['-1','0','abc','1.2','9'*100,'１２']:
            state=self.state(category_id=value,product_id=value)
            await app.State.enter_public_catalog.fn(state)
            state.load_public_product_details.assert_not_awaited()
            if value!='0':self.assertEqual(state.public_category_id,'')
    async def test_home_clears_previous_selection(self):
        state=self.state()
        await app.State.enter_public_home.fn(state)
        self.assertEqual(state.public_category_id,'')
        self.assertEqual(state.public_catalog_search,'')
        state.close_public_product_details.assert_called_once()
        state.load_public_catalog.assert_awaited_once()

if __name__=='__main__':unittest.main()
