import os
from urllib.parse import urlparse

from flask import Flask, jsonify, render_template, request
import mysql.connector
from dotenv import load_dotenv


app = Flask(__name__, template_folder='templates')
load_dotenv()

APP_NAME = "Monalex Dictionary"
APP_VERSION = os.environ.get("APP_VERSION", "0.2.0")


def get_positive_int(name, default, maximum=None):
    value = int(os.environ.get(name, default))
    if value < 1:
        raise ValueError(f"{name} must be at least 1.")
    if maximum is not None and value > maximum:
        raise ValueError(f"{name} must be at most {maximum}.")
    return value


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
        app.logger.error(f"Error connecting to the database: {e}")
        return None


def search_dictionary_entries(query):
    connection = get_db_connection()
    if connection is None:
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
    return jsonify({"service": APP_NAME, "status": "ok", "version": APP_VERSION})


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
