# backend/app/db.py
import os, time
from typing import Generator
from queue import Queue
from backend.app.core.config import (
    DB_DRIVER,
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER,
    DB_PASSWORD,
    POOL_SIZE,
    ENV,
    IS_TEST
)

pool = None

def get_db_connection():
    #lazy loading to fix our broken bazel tests
    #If we do not import it here, we will have to do all sorts of
    #ugliness in the bazel tests
    import pyodbc
    return pyodbc.connect(
        f"DRIVER={DB_DRIVER};"
        f"SERVER={DB_HOST};"
        f"PORT={DB_PORT};"
        f"DATABASE={DB_NAME};"
        f"UID={DB_USER};"
        f"PWD={DB_PASSWORD};"
    )


#-----------------------------
# Global connection pool
#-----------------------------
#We separate this to use no pool during test
def init_pool():
    global pool

    if IS_TEST:
        pool = None
        return

    #if anything else, create the pool
    pool = Queue(maxsize=POOL_SIZE)

    max_attempts = 10
    delay = 1

    # The reason we use the below method is because if the db connection is unavailable
    # The main python app will refuse to start. Instead we try to increase the delay on
    # every retry
    for attempt in range(max_attempts):
        try:
            for _ in range(POOL_SIZE):
                pool.put(get_db_connection())
            return
        except Exception:
            if attempt == max_attempts - 1:
                raise
            time.sleep(delay)
            delay *= 2


# Only use this in FastAPI request dependencies (NOT startup code)
def get_db() -> Generator:
    if pool:
        conn = pool.get()
        #receiving the connection from the pool
        yield conn
        #returning the connection to the pool
        pool.put(conn)
    else:
        conn = get_db_connection()
        try:
            yield conn
        finally:
            conn.close()