import unittest
from backend.scraper import get_headers

class TestScraper(unittest.TestCase):
    def test_get_headers(self):
        headers = get_headers()
        self.assertIn("User-Agent", headers)
        self.assertIn("Accept-Language", headers)

if __name__ == '__main__':
    unittest.main()
