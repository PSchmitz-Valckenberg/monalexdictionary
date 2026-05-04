import os
from urllib.parse import urlparse

from flask import Flask, render_template, request
import mysql.connector
from dotenv import load_dotenv


app = Flask(__name__, template_folder='templates')
load_dotenv()


def get_positive_int(name, default, maximum=None):
    value = int(os.environ.get(name, default))
    if value < 1:
        raise ValueError(f"{name} must be at least 1.")
    if maximum is not None and value > maximum:
        raise ValueError(f"{name} must be at most {maximum}.")
    return value


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

if not MYSQL_TABLE.replace("_", "").isalnum():
    raise ValueError("MYSQL_TABLE must contain only letters, numbers, and underscores.")

@app.route('/exceptions_premier.html', )
def exceptions_premier():
    return render_template('exceptions_premier.html')

@app.route('/exception_deuxieme.html',  endpoint='exceptions_deuxieme')
def exception_deuxieme():
    return render_template('exceptions_deuxieme.html')


@app.route('/premier.html')
def premier():
    return render_template('premier.html')

@app.route('/deuxieme.html')
def deuxieme():
    return render_template('deuxieme.html')

@app.route('/troisieme.html')
def troisieme():
    return render_template('troisieme.html')


@app.route('/etre_conjugation')
def etre_conjugation():
    app.logger.debug("etre_conjugation view function is executed.")
    return render_template('etre_conjugation.html')

@app.route('/avoir_conjugation')
def avoir_conjugation():
    return render_template('avoir_conjugation.html')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/conjugaison', methods=['GET'])
def conjugaison():
    return render_template('conjugaison.html')

def get_db_connection():
    try:
        return mysql.connector.connect(**MYSQL_CONFIG)
    except mysql.connector.Error as e:
        app.logger.error(f"Error connecting to the database: {e}")
        return None

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('searchInput', '').strip()

    if not query:
        return render_template('search.html', query=query, results=[], searched=False)

    connection = get_db_connection()
    if connection is None:
        return render_template(
            'search.html',
            query=query,
            results=[],
            searched=True,
            error_message="Connexion à la base de données impossible.",
        ), 503

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
        results = cursor.fetchall()
    except mysql.connector.Error as e:
        app.logger.error(f"Error running search query: {e}")
        return render_template(
            'search.html',
            query=query,
            results=[],
            searched=True,
            error_message="La recherche a échoué.",
        ), 500
    finally:
        cursor.close()
        connection.close()

    return render_template('search.html', query=query, results=results, searched=True)


@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error_message="Page introuvable."), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('error.html', error_message="Erreur interne du serveur."), 500



if __name__ == "__main__":
    # Use the PORT environment variable if available (for Heroku)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)



