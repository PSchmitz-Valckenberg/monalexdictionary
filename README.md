# Monalex Dictionary 🇫🇷➡️🇲🇨

A web-based translation dictionary for converting French words into Monégasque (Monegasque), built using Flask and MySQL.

## 🌍 Purpose

Monalex is a linguistic microproject designed to preserve and promote the Monégasque language by providing a lightweight digital dictionary with a simple, intuitive web interface.

---

## ⚙️ Features

- 🔤 Word translation: French → Monégasque
- 🧠 Relational database using MySQL (import via `dictionary.sql`)
- 🌐 Web interface via Flask (Jinja2 templates, HTML/CSS)
- 📦 Clean project structure with static assets and templates
- 🔁 Easily extendable with new vocabulary entries

---

## 🛠️ Tech Stack

| Layer         | Technology    |
|--------------|---------------|
| Backend      | Python 3.11, Flask |
| Frontend     | HTML, CSS, Jinja2 |
| Database     | MySQL |
| Deployment   | Localhost (Flask) |

---

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Import the database dump into MySQL, then adjust `.env` if your local database
name or credentials differ:

```bash
mysql -u root -p dictionary < dictionary.sql
flask --app app run
```

The dictionary search uses the `dictionary` table from `dictionary.sql` by
default. Override `MYSQL_TABLE` in `.env` only if you import the data under a
different table name.
