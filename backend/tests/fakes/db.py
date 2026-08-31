# /backend/tests/fakes/db.py

from types import SimpleNamespace


class FakeCursor:
    def __init__(self, row=None):
        self.row = row
        self.query = None
        self.params = None

    def execute(self, query, params=None):
        self.query = query
        self.params = params

    def fetchone(self):
        if self.row is None:
            return None

        # Expect row as tuple: (username, created_at)
        return SimpleNamespace(
            username=self.row[0],
            created_at=self.row[1],
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeConnection:
    def __init__(self, row=None):
        self._cursor = FakeCursor(row)

    def cursor(self):
        return self._cursor

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass


class FakeDB:
    """
    Optional general-purpose DB fake (if you ever override at DB layer instead of connection).
    """
    def cursor(self):
        return FakeCursor()

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass