import os
import sqlite3
import time

from filelock import FileLock

from app.config import settings


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.sqlite_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def _sql_signature() -> str:
    stat = os.stat(settings.dictionary_sql_path)
    return f"{stat.st_mtime_ns}:{stat.st_size}"


def _parse_row(row_text: str) -> list:
    values, current = [], []
    in_string = escape_next = False
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
    return [None if v.upper() == "NULL" else v for v in values]


def _iter_entries():
    with open(settings.dictionary_sql_path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if not line.startswith("INSERT INTO `dictionary` VALUES "):
                continue
            values_sql = line.partition(" VALUES ")[2].strip().rstrip(";")
            depth, start = 0, None
            in_string = escape_next = False
            for i, char in enumerate(values_sql):
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
                        start = i + 1
                    depth += 1
                elif char == ")":
                    depth -= 1
                    if depth == 0 and start is not None:
                        row = _parse_row(values_sql[start:i])
                        if len(row) >= 3:
                            yield int(row[0]), row[1], row[2]


def ensure_db() -> None:
    os.makedirs(os.path.dirname(os.path.abspath(settings.sqlite_path)), exist_ok=True)
    lock_path = settings.sqlite_path + ".lock"
    with FileLock(lock_path, timeout=60):
        conn = sqlite3.connect(settings.sqlite_path)
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            try:
                sig = conn.execute(
                    "SELECT value FROM cache_metadata WHERE key = 'source_signature'"
                ).fetchone()
                count = conn.execute("SELECT COUNT(*) FROM dictionary").fetchone()[0]
                if sig and sig[0] == _sql_signature() and count > 0:
                    return
            except sqlite3.Error:
                pass

            conn.executescript("""
                DROP TABLE IF EXISTS dictionary;
                DROP TABLE IF EXISTS cache_metadata;
                DROP TABLE IF EXISTS ai_response_cache;
                CREATE TABLE dictionary (
                    id INTEGER PRIMARY KEY,
                    word TEXT,
                    definition TEXT
                );
                CREATE TABLE cache_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                CREATE TABLE ai_response_cache (
                    cache_key TEXT PRIMARY KEY,
                    response_json TEXT NOT NULL,
                    created_at INTEGER NOT NULL
                );
            """)
            conn.executemany(
                "INSERT INTO dictionary (id, word, definition) VALUES (?, ?, ?)",
                _iter_entries(),
            )
            conn.execute("CREATE INDEX idx_word ON dictionary(word)")
            conn.execute("CREATE INDEX idx_def ON dictionary(definition)")
            count = conn.execute("SELECT COUNT(*) FROM dictionary").fetchone()[0]
            conn.executemany(
                "INSERT INTO cache_metadata (key, value) VALUES (?, ?)",
                {
                    "source_signature": _sql_signature(),
                    "row_count": str(count),
                    "rebuilt_at": str(int(time.time())),
                }.items(),
            )
            conn.commit()
        finally:
            conn.close()
