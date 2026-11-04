import os
import tempfile
import unittest

from linkly import create_app
from linkly.utils import is_valid_url


class LinklyTests(unittest.TestCase):
    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        self.client = create_app(self.db_path).test_client()

    def tearDown(self):
        os.remove(self.db_path)

    def shorten(self, **payload):
        return self.client.post("/api/shorten", json=payload)

    def test_shorten_and_redirect(self):
        res = self.shorten(url="https://example.com/page")
        self.assertEqual(res.status_code, 201)
        code = res.get_json()["code"]
        redirect = self.client.get(f"/{code}")
        self.assertEqual(redirect.status_code, 302)
        self.assertEqual(redirect.headers["Location"], "https://example.com/page")

    def test_rejects_invalid_urls(self):
        for bad in ["", "not a url", "javascript:alert(1)", "ftp://x.com", None]:
            self.assertEqual(self.shorten(url=bad).status_code, 400, bad)

    def test_custom_code_and_conflict(self):
        self.assertEqual(self.shorten(url="https://a.com", custom_code="my-link").status_code, 201)
        self.assertEqual(self.shorten(url="https://b.com", custom_code="my-link").status_code, 409)

    def test_invalid_custom_code(self):
        self.assertEqual(self.shorten(url="https://a.com", custom_code="a b!").status_code, 400)

    def test_unknown_code_404(self):
        self.assertEqual(self.client.get("/nope123").status_code, 404)

    def test_click_stats(self):
        code = self.shorten(url="https://example.com").get_json()["code"]
        for _ in range(3):
            self.client.get(f"/{code}")
        stats = self.client.get(f"/api/stats/{code}").get_json()
        self.assertEqual(stats["total_clicks"], 3)
        self.assertEqual(len(stats["clicks_per_day"]), 1)

    def test_stats_unknown_code(self):
        self.assertEqual(self.client.get("/api/stats/missing").status_code, 404)

    def test_url_validator(self):
        self.assertTrue(is_valid_url("http://localhost:5000/x"))
        self.assertFalse(is_valid_url("https://"))
