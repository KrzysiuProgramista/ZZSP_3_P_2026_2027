import unittest

from fastapi.testclient import TestClient

import service
from main import app

DATA = {"url": "https://example.com/a", "title": "Example", "tags": ["python"]}


class BookmarksTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        service.bookmarks.clear()
        service.next_id = 1

    def test_create(self):
        r = self.client.post("/bookmarks", json=DATA)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()["title"], "Example")
        self.assertEqual(r.json()["id"], 1)

    def test_create_bad_url(self):
        r = self.client.post("/bookmarks", json={**DATA, "url": "nope"})
        self.assertEqual(r.status_code, 422)

    def test_create_empty_title(self):
        r = self.client.post("/bookmarks", json={**DATA, "title": ""})
        self.assertEqual(r.status_code, 422)

    def test_create_long_title(self):
        r = self.client.post("/bookmarks", json={**DATA, "title": "x" * 201})
        self.assertEqual(r.status_code, 422)

    def test_list(self):
        self.client.post("/bookmarks", json=DATA)
        self.client.post("/bookmarks", json=DATA)
        self.assertEqual(len(self.client.get("/bookmarks").json()), 2)

    def test_list_by_tag(self):
        self.client.post("/bookmarks", json=DATA)
        self.client.post("/bookmarks", json={**DATA, "tags": ["other"]})
        self.assertEqual(len(self.client.get("/bookmarks?tag=python").json()), 1)
        self.assertEqual(self.client.get("/bookmarks?tag=missing").json(), [])

    def test_get_one(self):
        self.client.post("/bookmarks", json=DATA)
        self.assertEqual(self.client.get("/bookmarks/1").json()["id"], 1)

    def test_get_one_missing(self):
        self.assertEqual(self.client.get("/bookmarks/99").status_code, 404)

    def test_delete(self):
        self.client.post("/bookmarks", json=DATA)
        self.assertEqual(self.client.delete("/bookmarks/1").status_code, 204)
        self.assertEqual(self.client.get("/bookmarks/1").status_code, 404)

    def test_delete_missing(self):
        self.assertEqual(self.client.delete("/bookmarks/99").status_code, 404)


if __name__ == "__main__":
    unittest.main()
