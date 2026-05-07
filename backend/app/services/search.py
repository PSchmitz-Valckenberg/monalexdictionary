from app.config import settings
from app.database.sqlite import get_connection


def search_entries(query: str) -> list[dict]:
    conn = get_connection()
    try:
        term = f"%{query}%"
        rows = conn.execute(
            """
            SELECT word, definition FROM dictionary
            WHERE word LIKE ? OR definition LIKE ?
            ORDER BY word
            LIMIT ?
            """,
            (term, term, settings.search_limit),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_entry_at_offset(offset: int) -> dict | None:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT word, definition FROM dictionary ORDER BY id LIMIT 1 OFFSET ?",
            (offset,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_total_count() -> int:
    conn = get_connection()
    try:
        return conn.execute("SELECT COUNT(*) FROM dictionary").fetchone()[0]
    finally:
        conn.close()
