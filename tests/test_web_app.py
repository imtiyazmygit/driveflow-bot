import unittest

from app import create_app


class WebAppTests(unittest.TestCase):
    def test_home_page_renders(self):
        app = create_app()
        client = app.test_client()
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Booking Automation', response.data)


if __name__ == '__main__':
    unittest.main()
