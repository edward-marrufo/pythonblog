# backend/tests/test_db.py

from queue import Queue
from backend.app import db


# -----------------------------
# Fake connection object
# -----------------------------
# We do not need a real database connection.
# This object simply acts as a stand-in.
class FakeConnection:
    pass


# ---------------------------------------------------
# Test: pool initializes correctly
# ---------------------------------------------------
#
# Behavior being tested:
#
# init_pool() should:
#   1. create a Queue
#   2. populate it with POOL_SIZE connections
#
def test_init_pool_creates_pool_with_connections():

    # Replace real DB connection creation with fake connection objects.
    #
    # Normally this would:
    #   - import pyodbc
    #   - connect to a real database
    #
    # We do NOT want infrastructure dependencies in unit tests.
    db.get_db_connection = lambda: FakeConnection()

    # Run the real initialization logic
    db.init_pool()

    # Assert Queue object was created
    #
    # Before init_pool():
    #   db.pool = None
    #
    # After init_pool():
    #   db.pool should be a Queue object
    assert db.pool is not None

    # Assert Queue contains expected number of connections
    #
    # qsize() means:
    #   "how many objects are currently inside the Queue?"
    #
    # Since init_pool() loops POOL_SIZE times,
    # we expect exactly POOL_SIZE FakeConnections inside.
    assert db.pool.qsize() == db.POOL_SIZE

    # Cleanup global state for test isolation
    db.pool = None


# ---------------------------------------------------
# Test: pool disabled during test environment
# ---------------------------------------------------
#
# Behavior being tested:
#
# If IS_TEST is True:
#   init_pool() should NOT create a Queue
#
def test_init_pool_skips_pool_creation_in_test_mode():

    # Save original value so we can restore it later
    original_is_test = db.IS_TEST

    # Simulate test environment
    db.IS_TEST = True

    # Run initialization
    db.init_pool()

    # Assert pool was intentionally NOT created
    #
    # Expected behavior:
    #   pool remains None
    assert db.pool is None

    # Restore original environment flag
    db.IS_TEST = original_is_test


# ---------------------------------------------------
# Test: get_db borrows and returns connection
# ---------------------------------------------------
#
# Behavior being tested:
#
# get_db() should:
#   1. remove connection from pool
#   2. yield connection to caller
#   3. return connection back to pool afterward
#
def test_get_db_returns_connection_to_pool():

    # Create fresh test pool manually
    db.pool = Queue()

    # Create one fake connection
    fake_conn = FakeConnection()

    # Put connection into pool
    db.pool.put(fake_conn)

    # Initial state:
    #
    # Pool contains 1 connection
    assert db.pool.qsize() == 1

    # Create generator from get_db()
    #
    # IMPORTANT:
    # get_db() is a generator because it uses "yield"
    generator = db.get_db()

    # Advance generator to first yield
    #
    # This executes:
    #   conn = pool.get()
    #   yield conn
    #
    conn = next(generator)

    # Assert yielded object is our fake connection
    assert conn == fake_conn

    # Assert pool size decreased
    #
    # Connection was borrowed from pool,
    # so Queue should now be empty.
    assert db.pool.qsize() == 0

    # Finish generator execution
    #
    # This resumes execution AFTER yield,
    # causing:
    #   pool.put(conn)
    #
    try:
        next(generator)
    except StopIteration:
        pass

    # Assert connection returned to pool
    #
    # Queue should contain connection again.
    assert db.pool.qsize() == 1

    # Cleanup global state
    db.pool = None