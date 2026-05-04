import unittest
from unittest.mock import patch

from flask import url_for

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
            "/conjugaison/premier",
            "/conjugaison/deuxieme",
            "/conjugaison/troisieme",
            "/conjugaison/etre",
            "/conjugaison/avoir",
            "/exceptions/premier",
            "/exceptions/deuxieme",
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

    def test_api_search_returns_json_results(self):
        cursor = FakeCursor(
            [{"word": "bonjour", "definition": "bun giurnu"}]
        )
        connection = FakeConnection(cursor)

        with patch.object(app_module, "get_db_connection", return_value=connection):
            response = self.client.get("/api/search?q=bonjour")

        payload = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["query"], "bonjour")
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["results"][0]["word"], "bonjour")
        self.assertEqual(payload["results"][0]["definition"], "bun giurnu")

    def test_api_search_handles_empty_query(self):
        with patch.object(app_module, "get_db_connection") as get_db_connection:
            response = self.client.get("/api/search")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"query": "", "count": 0, "results": []})
        get_db_connection.assert_not_called()

    def test_api_search_handles_database_connection_error(self):
        with patch.object(app_module, "get_db_connection", return_value=None), patch.object(
            app_module,
            "search_sqlite_fallback_entries",
            return_value=None,
        ):
            response = self.client.get("/api/search?q=bonjour")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.get_json()["error"],
            "Connexion à la base de données impossible.",
        )

    def test_ai_explain_requires_word_and_definition(self):
        response = self.client.post("/api/ai/explain", json={"word": "bonjour"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "word and definition are required.")

    def test_ai_explain_reports_missing_configuration(self):
        with patch.dict(app_module.os.environ, {"OPENAI_API_KEY": ""}):
            response = self.client.post(
                "/api/ai/explain",
                json={"word": "bonjour", "definition": "bun giurnu"},
            )

        self.assertEqual(response.status_code, 503)
        self.assertIn("OPENAI_API_KEY", response.get_json()["error"])

    def test_ai_explain_returns_generated_payload(self):
        explanation = {
            "summary_fr": "Une salutation courante.",
            "usage_notes": ["Utilisable le matin.", "Forme polie."],
            "examples": [
                {"fr": "Bonjour.", "monegasque": "Bun giurnu."},
                {"fr": "Bonjour à tous.", "monegasque": "Bun giurnu a tüti."},
            ],
            "memory_tip": "Associe bun à bon.",
            "practice_question": "Comment saluerais-tu un ami ?",
        }

        with patch.object(
            app_module,
            "generate_ai_explanation",
            return_value=(explanation, None, 200),
        ) as generate_ai_explanation:
            response = self.client.post(
                "/api/ai/explain",
                json={"word": "bonjour", "definition": "bun giurnu"},
            )

        payload = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["word"], "bonjour")
        self.assertEqual(payload["explanation"], explanation)
        generate_ai_explanation.assert_called_once_with("bonjour", "bun giurnu")

    def test_search_handles_database_connection_error(self):
        with patch.object(app_module, "get_db_connection", return_value=None), patch.object(
            app_module,
            "search_sqlite_fallback_entries",
            return_value=None,
        ):
            response = self.client.get("/search?searchInput=accueillir")

        self.assertEqual(response.status_code, 503)
        self.assertIn(
            "Connexion à la base de données impossible.",
            response.get_data(as_text=True),
        )

    def test_search_uses_sqlite_fallback_when_mysql_is_unavailable(self):
        fallback_results = [{"word": "bonjour", "definition": "bun giurnu"}]

        with patch.object(app_module, "get_db_connection", return_value=None), patch.object(
            app_module,
            "search_sqlite_fallback_entries",
            return_value=fallback_results,
        ):
            response = self.client.get("/api/search?q=bonjour")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["results"], fallback_results)

    def test_health_endpoint_returns_service_metadata(self):
        response = self.client.get("/healthz")

        payload = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["service"], "Monalex Dictionary")
        self.assertEqual(payload["status"], "ok")
        self.assertIn("version", payload)
        self.assertIn("ai", payload)
        self.assertIn("configured", payload["ai"])
        self.assertIn("model", payload["ai"])

    def test_url_generation_prefers_clean_routes(self):
        with app_module.app.test_request_context():
            self.assertEqual(url_for("premier"), "/conjugaison/premier")
            self.assertEqual(url_for("deuxieme"), "/conjugaison/deuxieme")
            self.assertEqual(url_for("troisieme"), "/conjugaison/troisieme")
            self.assertEqual(url_for("exceptions_premier"), "/exceptions/premier")
            self.assertEqual(url_for("exceptions_deuxieme"), "/exceptions/deuxieme")

    def test_responses_include_security_headers(self):
        response = self.client.get("/")

        self.assertEqual(
            response.headers["Referrer-Policy"],
            "strict-origin-when-cross-origin",
        )
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(response.headers["X-Frame-Options"], "SAMEORIGIN")

    def test_missing_page_returns_custom_404(self):
        response = self.client.get("/missing")

        self.assertEqual(response.status_code, 404)
        self.assertIn("Page introuvable.", response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
