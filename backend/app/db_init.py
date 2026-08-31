# backend/app/db_init.py
import time
from backend.app.db import get_db_connection

MAX_RETRIES = 10
SLEEP_SECONDS = 2


def init_db():
    """
    Initialize DB schema at startup.
    Uses direct connections and not pool to avoid starvation.
    Retries until Postgres is ready.
    """

    retries = 0

    while retries < MAX_RETRIES:
        conn = None

        try:
            conn = get_db_connection()

            with conn.cursor() as cursor:
                # Enable extensions
                cursor.execute("""
                CREATE EXTENSION IF NOT EXISTS pgcrypto;
                CREATE EXTENSION IF NOT EXISTS citext;
                """)

                # Users table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    username VARCHAR(30) UNIQUE NOT NULL,
                    role VARCHAR(16) NOT NULL DEFAULT 'user',
                    email VARCHAR(255) UNIQUE NOT NULL,
                    hashed_password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMPTZ(3) NOT NULL DEFAULT NOW()
                );
                """)

                # Posts table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id SERIAL PRIMARY KEY,
                    user_id UUID NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    text TEXT,
                    created_at TIMESTAMPTZ(3) NOT NULL DEFAULT NOW(),
                    last_modified TIMESTAMPTZ(3) DEFAULT NOW(),
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );
                """)

                # Sessions table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id UUID NOT NULL,
                    device_name VARCHAR(64),
                    user_agent TEXT,
                    ip_address TEXT,
                    user_agent_string TEXT,
                    created_at TIMESTAMPTZ(3) DEFAULT NOW(),
                    expires_at TIMESTAMPTZ(3) NOT NULL,
                    last_seen TIMESTAMPTZ(3) NOT NULL DEFAULT NOW(),
                    revoked BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );
                """)

                conn.commit()

            print("Database initialized successfully.")
            return

        except Exception as e:
            retries += 1
            print(f"Database not ready, retry {retries}/{MAX_RETRIES}: {e}")
            time.sleep(SLEEP_SECONDS)

        finally:
            try:
                conn.close()
            except:
                pass

    raise RuntimeError(
        f"Houston, we have a problem. Could not initialize database after {MAX_RETRIES} retries"
    )