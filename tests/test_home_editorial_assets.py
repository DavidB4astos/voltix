import os
import unittest
from unittest.mock import patch

import voltix.voltix as app


class HomeEditorialAssetsTests(unittest.TestCase):
    def test_missing_editorial_photo_is_omitted(self):
        exists = os.path.isfile
        with patch.object(app.os.path, 'isfile', side_effect=lambda name: False if str(name).endswith('vtx-editorial-mx-master-3s.jpg') else exists(name)):
            rendered = str(app.home_page())
        self.assertNotIn('/demo/vtx-editorial-mx-master-3s.jpg', rendered)
        self.assertIn('/demo/vtx-home-workspace-v2.webp', rendered)

    def test_missing_license_omits_editorial(self):
        manifest = {'products': [], 'editorial_images': [{
            'role': 'home_editorial', 'status': 'approved',
            'file': 'vtx-editorial-mx-master-3s.jpg',
            'attribution': 'Author', 'source_url': 'https://example.invalid/photo',
        }]}
        with patch.object(app.json, 'load', return_value=manifest):
            rendered = str(app.home_page())
        self.assertNotIn('/demo/vtx-editorial-mx-master-3s.jpg', rendered)

    def test_missing_hero_uses_local_graphic_fallback(self):
        exists = os.path.isfile
        with patch.object(app.os.path, 'isfile', side_effect=lambda name: False if str(name).endswith('vtx-home-workspace-v2.webp') else exists(name)):
            rendered = str(app.home_page())
        self.assertNotIn('/demo/vtx-home-workspace-v2.webp', rendered)
        self.assertIn('vx-hero__graphic', rendered)


if __name__ == '__main__':
    unittest.main()
