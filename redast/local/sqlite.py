__all__ = ("Sqlite", "SqliteTemp")

from sqlitedict import SqliteDict # type: ignore
import tempfile
from pathlib import Path

class Sqlite:
    def __init__(self, path, create: bool = False):
        path = Path(path)
        if not create and not path.exists():
            raise AssertionError
        self._db = SqliteDict(filename=path, autocommit=True)

    def __del__(self):
        self._db.close()

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
    def __init__(self):
        self._temp = tempfile.NamedTemporaryFile()
        super().__init__(path=self._temp.name, create=True)

    def __del__(self):
        super().__del__()
        self._temp.close()

    def __getstate__(self):
        with open(self._temp.name, "rb") as f:
            storage = f.read()
        state = self.__dict__.copy()
        state.pop("_temp")
        state.pop("_db")
        state["__storage__"] = storage
        return state

    def __setstate__(self, state):
        temp = tempfile.NamedTemporaryFile()
        storage = state.pop("__storage__")
        with open(temp.name, "wb") as f:
            f.write(storage)

        state["_temp"] = temp
        state["_db"] = SqliteDict(filename=temp.name, autocommit=True)
        self.__dict__ = state
