__all__ = ("Sqlite", "SqliteTemp")

from sqlitedict import SqliteDict


class Sqlite:
    def __init__(self, filename):
        self._db = SqliteDict(filename, autocommit=True)

    def exists(self, key: str) -> bool:
        return key in self._db

    def save(self, key: str, data) -> bool:
        try:
            self._db[key] = data
            return True
        except Exception:
            return False

    def load(self, key: str):
        return self._db[key]

    def delete(self, key: str) -> bool:
        try:
            del self._db[key]
            return True
        except Exception:
            return False


class SqliteTemp(Sqlite):
    pass
