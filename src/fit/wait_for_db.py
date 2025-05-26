import time
import psycopg2
import os

def wait_for_db():
    db_url = os.getenv("DATABASE_URL", "postgresql://fituser:fitpass@db:5432/fitdb")
    while True:
        try:
            conn = psycopg2.connect(db_url)
            conn.close()
            print("✅ Database is ready!")
            break
        except psycopg2.OperationalError:
            print("⏳ Waiting for database to be ready...")
            time.sleep(1)
