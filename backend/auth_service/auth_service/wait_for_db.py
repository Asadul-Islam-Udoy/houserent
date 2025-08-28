# wait_for_db.py
import os
import time
import psycopg2

DB_NAME = os.environ.get("POSTGRES_DB_AUTH")
DB_USER = os.environ.get("POSTGRES_USER_AUTH")
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD_AUTH")
DB_HOST = os.environ.get("POSTGRES_HOST", "postgres_auth")
DB_PORT = os.environ.get("POSTGRES_PORT", 5432)

while True:
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        conn.close()
        print("Postgres is ready")
        break
    except psycopg2.OperationalError:
        print("Waiting for Postgres...")
        time.sleep(2)
