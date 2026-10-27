import unittest
from unittest.mock import patch

from voltix import demo_images


class CatalogCardCreditTests(unittest.TestCase):
    def credit(self):
        return {'author':'Author', 'license':'CC BY 4.0',
                'license_url':'https://creativecommons.org/licenses/by/4.0/',
                'source_url':'https://example.invalid/photo', 'attribution':'Full original title by Author'}

    def test_only_complete_safe_existing_credit_is_returned(self):
        cache = {name:self.credit() for name in ['valid.jpg','missing.jpg','../escape.jpg',r'..\escape.jpg','C:escape.jpg']}
        cache['incomplete.jpg'] = self.credit() | {'license_url':''}
        with patch.object(demo_images, '_load_credits_by_filename', return_value=cache), patch.object(demo_images.os.path, 'isfile', side_effect=lambda name: not str(name).endswith('missing.jpg')):
            result = demo_images.demo_image_credits()
        self.assertEqual(set(result), {'/demo/valid.jpg'})
        self.assertEqual(result['/demo/valid.jpg']['attribution'], 'Full original title by Author')

    def test_caller_cannot_mutate_the_credit_cache(self):
        cache = {'valid.jpg':self.credit()}
        with patch.object(demo_images, '_load_credits_by_filename', return_value=cache), patch.object(demo_images.os.path, 'isfile', return_value=True):
            result = demo_images.demo_image_credits()
            result['/demo/valid.jpg']['author'] = 'Changed'
            result.clear()
            second = demo_images.demo_image_credits()
        self.assertEqual(second['/demo/valid.jpg']['author'], 'Author')
        self.assertEqual(cache['valid.jpg']['author'], 'Author')


if __name__ == '__main__':
    unittest.main()
