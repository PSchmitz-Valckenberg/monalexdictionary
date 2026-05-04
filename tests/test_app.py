import unittest
from unittest.mock import patch

import app as app_module


class FakeCursor:
    def __init__(self, results=None):
        self.results = results or []
        self.closed = False
        self.executed = None

    def execute(self, sql, params):
        self.executed = (sql, params)

    def fetchall(self):
        return self.results

    def close(self):
        self.closed = True


class FakeConnection:
    def __init__(self, cursor):
        self.cursor_instance = cursor
        self.closed = False

    def cursor(self, dictionary=False):
        self.dictionary_cursor = dictionary
        return self.cursor_instance

    def close(self):
        self.closed = True


class MonalexAppTests(unittest.TestCase):
    def setUp(self):
        app_module.app.config["TESTING"] = True
        self.client = app_module.app.test_client()

    def test_static_pages_render(self):
        paths = [
            "/",
            "/search",
            "/conjugaison",
            "/premier.html",
            "/deuxieme.html",
            "/troisieme.html",
            "/etre_conjugation",
            "/avoir_conjugation",
            "/exceptions_premier.html",
            "/exception_deuxieme.html",
        ]

        for path in paths:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertIn("Monalex", response.get_data(as_text=True))

    def test_empty_search_does_not_connect_to_database(self):
        with patch.object(app_module, "get_db_connection") as get_db_connection:
            response = self.client.get("/search")

        self.assertEqual(response.status_code, 200)
        get_db_connection.assert_not_called()

    def test_search_renders_database_results(self):
        cursor = FakeCursor(
            [{"word": "accueillir", "definition": "achoe-ye"}]
        )
        connection = FakeConnection(cursor)

        with patch.object(app_module, "get_db_connection", return_value=connection):
            response = self.client.get("/search?searchInput=accueillir")

        html = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(connection.dictionary_cursor)
        self.assertTrue(cursor.closed)
        self.assertTrue(connection.closed)
        self.assertIn("accueillir", html)
        self.assertIn("achoe-ye", html)
        self.assertIn("LIMIT 50", cursor.executed[0])
        self.assertEqual(cursor.executed[1], ("%accueillir%", "%accueillir%"))

    def test_search_handles_database_connection_error(self):
        with patch.object(app_module, "get_db_connection", return_value=None):
            response = self.client.get("/search?searchInput=accueillir")

        self.assertEqual(response.status_code, 503)
        self.assertIn(
            "Connexion à la base de données impossible.",
            response.get_data(as_text=True),
        )

    def test_missing_page_returns_custom_404(self):
        response = self.client.get("/missing")

        self.assertEqual(response.status_code, 404)
        self.assertIn("Page introuvable.", response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
