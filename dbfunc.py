
import os
import mysql.connector

# Database configuration
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": os.getenv("DB_PASSWORD"),
    "database": "ilyas2farow",
    "port": 3306
}


def get_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        print("DB Connection Error:", err)
        return None


# =========================
# FETCH (SELECT QUERIES)
# =========================
def fetch_all(query, params=None):
    conn = get_connection()
    if not conn:
        return []

    cur = None
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(query, params or ())
        return cur.fetchall()

    except Exception as e:
        print("Fetch error:", e)
        return []

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# =========================
# INSERT / UPDATE / DELETE
# =========================
def execute_query(query, params=None):
    conn = get_connection()
    if not conn:
        return False

    cur = None
    try:
        cur = conn.cursor()
        cur.execute(query, params or ())
        conn.commit()
        return True

    except Exception as e:
        print("Execute error:", e)
        conn.rollback()
        return False

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
