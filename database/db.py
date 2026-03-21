import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'focusdesk.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    if not os.path.exists(DB_PATH):
        conn = get_connection()
        with open(SCHEMA_PATH, 'r') as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()
        print("Database initialized.")


# ===== EXECUTE QUERY =====
def execute_query(query, params=()):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor
    except Exception as e:
        print("Database error:", e)
        return None


# ===== FETCH ALL =====
def fetch_all(query, params=()):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    except Exception as e:
        print("Fetch error:", e)
        return []


# ===== FETCH ONE =====
def fetch_one(query, params=()):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()
    except Exception as e:
        print("Fetch error:", e)
        return None