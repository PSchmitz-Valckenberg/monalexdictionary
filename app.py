import os
from flask import Flask, render_template, request
import mysql.connector
import logging
from dotenv import load_dotenv  # Import the function


app = Flask(__name__, template_folder='templates')
load_dotenv()


mysql_host = os.environ.get("MYSQL_HOST","localhost")
mysql_user = os.environ.get("MYSQL_USER", "root")
mysql_password = os.environ.get("MYSQL_PASSWORD", "Benamira05")
mysql_database = os.environ.get("MYSQL_DATABASE", "mydictionary")


# JawsDB MySQL configuration
mysql_url = os.environ.get("JAWSDB_URL")

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
    # Your view logic for the "conjugaison" endpoint
    return render_template('conjugaison.html')

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=mysql_host,
            user=mysql_user,
            password=mysql_password,
            database=mysql_database
        )
        return connection
    except mysql.connector.Error as e:
        app.logger.error(f"Error connecting to the database: {e}")
        return None

# Your routes and views go here...

@app.route('/search', methods=['GET'])
def search():
    word = request.args.get('searchInput')

    connection = get_db_connection()
    if connection is None:
        # Handle the error here
        return "Error connecting to the database"

    cursor = connection.cursor()

    sql_query = "SELECT french_word FROM dictionary_real WHERE french_word LIKE %s"
    search_term = f"%{word}%"  # Define the search_term here
    cursor.execute(sql_query, (search_term,))
    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('search.html', results=results)



if __name__ == "__main__":
    # Use the PORT environment variable if available (for Heroku)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)






