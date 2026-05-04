import json
import os
import sqlite3
from urllib.parse import urlparse

from flask import Flask, jsonify, render_template, request
import mysql.connector
from dotenv import load_dotenv


app = Flask(__name__, template_folder='templates')
load_dotenv()

APP_NAME = "Monalex Dictionary"
APP_VERSION = os.environ.get("APP_VERSION", "0.2.0")
DEFAULT_OPENAI_MODEL = "gpt-5.4-mini"
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)

AI_EXPLANATION_SCHEMA = {
    "type": "object",
    "properties": {
        "summary_fr": {
            "type": "string",
            "description": "Short learner-friendly French explanation.",
        },
        "usage_notes": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Two or three practical notes about usage or nuance.",
        },
        "examples": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "fr": {"type": "string"},
                    "monegasque": {"type": "string"},
                },
                "required": ["fr", "monegasque"],
                "additionalProperties": False,
            },
            "description": "Two short French/Monégasque example pairs.",
        },
        "memory_tip": {
            "type": "string",
            "description": "A concrete memory tip in French.",
        },
        "practice_question": {
            "type": "string",
            "description": "A short practice question for the learner.",
        },
    },
    "required": [
        "summary_fr",
        "usage_notes",
        "examples",
        "memory_tip",
        "practice_question",
    ],
    "additionalProperties": False,
}

AI_RESPONSE_FORMAT = {
    "format": {
        "type": "json_schema",
        "name": "monalex_ai_explanation",
        "strict": True,
        "schema": AI_EXPLANATION_SCHEMA,
    }
}

AI_INSTRUCTIONS = (
    "Tu es un assistant pédagogique pour Monalex, un dictionnaire français-"
    "monégasque. Utilise uniquement l'entrée fournie. N'invente pas "
    "d'étymologie ou de règle grammaticale non visible dans l'entrée. "
    "Réponds en français clair, avec des exemples courts et prudents."
)


def get_positive_int(name, default, maximum=None):
    value = int(os.environ.get(name, default))
    if value < 1:
        raise ValueError(f"{name} must be at least 1.")
    if maximum is not None and value > maximum:
        raise ValueError(f"{name} must be at most {maximum}.")
    return value


def get_bool_env(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def validate_mysql_table_name(table_name):
    if not table_name.replace("_", "").isalnum():
        raise ValueError("MYSQL_TABLE must contain only letters, numbers, and underscores.")


def get_mysql_config():
    mysql_url = os.environ.get("JAWSDB_URL")
    if mysql_url:
        parsed_url = urlparse(mysql_url)
        return {
            "host": parsed_url.hostname,
            "port": parsed_url.port or 3306,
            "user": parsed_url.username,
            "password": parsed_url.password,
            "database": parsed_url.path.lstrip("/"),
        }

    return {
        "host": os.environ.get("MYSQL_HOST", "localhost"),
        "port": int(os.environ.get("MYSQL_PORT", 3306)),
        "user": os.environ.get("MYSQL_USER", "root"),
        "password": os.environ.get("MYSQL_PASSWORD", ""),
        "database": os.environ.get("MYSQL_DATABASE", "dictionary"),
    }


MYSQL_CONFIG = get_mysql_config()
MYSQL_TABLE = os.environ.get("MYSQL_TABLE", "dictionary")
SEARCH_LIMIT = get_positive_int("SEARCH_LIMIT", 50, maximum=200)
AI_INPUT_LIMIT = get_positive_int("AI_INPUT_LIMIT", 1200, maximum=4000)
ENABLE_SQLITE_FALLBACK = get_bool_env("ENABLE_SQLITE_FALLBACK", default=True)
SQLITE_FALLBACK_PATH = os.environ.get(
    "SQLITE_FALLBACK_PATH",
    os.path.join(app.instance_path, "monalex_dictionary.sqlite3"),
)
validate_mysql_table_name(MYSQL_TABLE)


@app.route("/exceptions_premier.html")
@app.route("/exceptions/premier")
def exceptions_premier():
    return render_template("exceptions_premier.html")


@app.route("/exception_deuxieme.html", endpoint="exceptions_deuxieme")
@app.route("/exceptions/deuxieme", endpoint="exceptions_deuxieme")
def exception_deuxieme():
    return render_template("exceptions_deuxieme.html")


@app.route("/premier.html")
@app.route("/conjugaison/premier")
def premier():
    return render_template("premier.html")


@app.route("/deuxieme.html")
@app.route("/conjugaison/deuxieme")
def deuxieme():
    return render_template("deuxieme.html")


@app.route("/troisieme.html")
@app.route("/conjugaison/troisieme")
def troisieme():
    return render_template("troisieme.html")


@app.route("/etre_conjugation")
@app.route("/conjugaison/etre")
def etre_conjugation():
    return render_template("etre_conjugation.html")


@app.route("/avoir_conjugation")
@app.route("/conjugaison/avoir")
def avoir_conjugation():
    return render_template("avoir_conjugation.html")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/conjugaison", methods=["GET"])
def conjugaison():
    return render_template("conjugaison.html")


def get_db_connection():
    try:
        return mysql.connector.connect(**MYSQL_CONFIG)
    except mysql.connector.Error as e:
        if ENABLE_SQLITE_FALLBACK:
            app.logger.warning(f"MySQL unavailable; using SQLite fallback: {e}")
        else:
            app.logger.error(f"Error connecting to the database: {e}")
        return None


def parse_mysql_values_row(row_text):
    values = []
    current = []
    in_string = False
    escape_next = False

    for char in row_text:
        if escape_next:
            current.append(char)
            escape_next = False
            continue

        if in_string and char == "\\":
            escape_next = True
            continue

        if char == "'":
            in_string = not in_string
            continue

        if char == "," and not in_string:
            values.append("".join(current).strip())
            current = []
            continue

        current.append(char)

    values.append("".join(current).strip())
    return [None if value.upper() == "NULL" else value for value in values]


def iter_dictionary_dump_entries(sql_path="dictionary.sql"):
    with open(sql_path, "r", encoding="utf-8", errors="replace") as sql_file:
        for line in sql_file:
            if not line.startswith("INSERT INTO `dictionary` VALUES "):
                continue

            values_sql = line.partition(" VALUES ")[2].strip()
            if values_sql.endswith(";"):
                values_sql = values_sql[:-1]

            depth = 0
            start = None
            in_string = False
            escape_next = False

            for index, char in enumerate(values_sql):
                if escape_next:
                    escape_next = False
                    continue

                if in_string and char == "\\":
                    escape_next = True
                    continue

                if char == "'":
                    in_string = not in_string
                    continue

                if in_string:
                    continue

                if char == "(":
                    if depth == 0:
                        start = index + 1
                    depth += 1
                elif char == ")":
                    depth -= 1
                    if depth == 0 and start is not None:
                        row = parse_mysql_values_row(values_sql[start:index])
                        if len(row) >= 3:
                            yield int(row[0]), row[1], row[2]


def ensure_sqlite_fallback_database():
    if not ENABLE_SQLITE_FALLBACK:
        return None

    db_path = os.path.abspath(SQLITE_FALLBACK_PATH)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    has_rows = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'dictionary'"
    ).fetchone()

    if has_rows:
        return connection

    connection.execute(
        """
        CREATE TABLE dictionary (
            id INTEGER PRIMARY KEY,
            word TEXT,
            definition TEXT
        )
        """
    )
    connection.executemany(
        "INSERT INTO dictionary (id, word, definition) VALUES (?, ?, ?)",
        iter_dictionary_dump_entries(),
    )
    connection.execute("CREATE INDEX idx_dictionary_word ON dictionary(word)")
    connection.commit()
    return connection


def search_sqlite_fallback_entries(query):
    connection = ensure_sqlite_fallback_database()
    if connection is None:
        return None

    try:
        search_term = f"%{query}%"
        rows = connection.execute(
            """
            SELECT word, definition FROM dictionary
            WHERE word LIKE ? OR definition LIKE ?
            ORDER BY word
            LIMIT ?
            """,
            (search_term, search_term, SEARCH_LIMIT),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


def search_dictionary_entries(query):
    connection = get_db_connection()
    if connection is None:
        fallback_results = search_sqlite_fallback_entries(query)
        if fallback_results is not None:
            return fallback_results, None, 200
        return None, "Connexion à la base de données impossible.", 503

    cursor = connection.cursor(dictionary=True)

    try:
        search_term = f"%{query}%"
        sql_query = (
            f"SELECT word, definition FROM `{MYSQL_TABLE}` "
            "WHERE word LIKE %s OR definition LIKE %s "
            "ORDER BY word "
            f"LIMIT {SEARCH_LIMIT}"
        )
        cursor.execute(sql_query, (search_term, search_term))
        return cursor.fetchall(), None, 200
    except mysql.connector.Error as e:
        app.logger.error(f"Error running search query: {e}")
        return None, "La recherche a échoué.", 500
    finally:
        cursor.close()
        connection.close()


def is_ai_configured():
    return bool(os.environ.get("OPENAI_API_KEY"))


def clean_ai_input(value):
    return str(value or "").strip()[:AI_INPUT_LIMIT]


def generate_ai_explanation(word, definition):
    if not is_ai_configured():
        return None, "Assistant IA non configuré. Définissez OPENAI_API_KEY pour l'activer.", 503

    try:
        from openai import OpenAI, OpenAIError
    except ImportError:
        return None, "SDK OpenAI absent. Lancez pip install -r requirements.txt.", 500

    prompt = (
        "Explique cette entrée du dictionnaire pour un apprenant.\n\n"
        f"Mot français: {clean_ai_input(word)}\n"
        f"Traduction / définition monégasque: {clean_ai_input(definition)}"
    )

    try:
        client = OpenAI()
        response = client.responses.create(
            model=OPENAI_MODEL,
            instructions=AI_INSTRUCTIONS,
            input=prompt,
            text=AI_RESPONSE_FORMAT,
            max_output_tokens=900,
        )
        return json.loads(response.output_text), None, 200
    except OpenAIError as e:
        app.logger.error(f"OpenAI request failed: {e}")
        return None, "La requête vers l'assistant IA a échoué.", 502
    except (json.JSONDecodeError, AttributeError) as e:
        app.logger.error(f"Invalid AI helper response: {e}")
        return None, "L'assistant IA a renvoyé une réponse invalide.", 502


@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("searchInput", "").strip()

    if not query:
        return render_template("search.html", query=query, results=[], searched=False)

    results, error_message, status_code = search_dictionary_entries(query)
    if error_message:
        return render_template(
            "search.html",
            query=query,
            results=[],
            searched=True,
            error_message=error_message,
        ), status_code

    return render_template("search.html", query=query, results=results, searched=True)


@app.route("/api/ai/explain", methods=["POST"])
def api_ai_explain():
    payload = request.get_json(silent=True) or {}
    word = clean_ai_input(payload.get("word"))
    definition = clean_ai_input(payload.get("definition"))

    if not word or not definition:
        return jsonify({"error": "word and definition are required."}), 400

    explanation, error_message, status_code = generate_ai_explanation(word, definition)
    if error_message:
        return jsonify({"error": error_message}), status_code

    return jsonify(
        {
            "word": word,
            "definition": definition,
            "model": OPENAI_MODEL,
            "explanation": explanation,
        }
    )


@app.route("/api/search", methods=["GET"])
def api_search():
    query = request.args.get("q", request.args.get("searchInput", "")).strip()

    if not query:
        return jsonify({"query": query, "count": 0, "results": []})

    results, error_message, status_code = search_dictionary_entries(query)
    if error_message:
        return jsonify({"query": query, "error": error_message, "results": []}), status_code

    return jsonify({"query": query, "count": len(results), "results": results})


@app.route("/healthz", methods=["GET"])
def healthz():
    return jsonify(
        {
            "service": APP_NAME,
            "status": "ok",
            "version": APP_VERSION,
            "ai": {
                "configured": is_ai_configured(),
                "model": OPENAI_MODEL,
            },
        }
    )


@app.after_request
def add_security_headers(response):
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    return response


@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", error_message="Page introuvable."), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("error.html", error_message="Erreur interne du serveur."), 500


if __name__ == "__main__":
    # Use the PORT environment variable if available (for Heroku)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
