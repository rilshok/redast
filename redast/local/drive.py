__all__ = ("Drive", "DriveTemp")

from pathlib import Path
import typing as tp
import tempfile


class Drive:
    # TODO: split hash by dir parts
    def __init__(self, root: tp.Union[Path, str], create: bool = False):
        root = Path(root)
        if create:
            root.mkdir(mode=0o750, parents=False, exist_ok=True)
        assert root.exists() and root.is_dir()
        self._root = root

    @staticmethod
    def _assert_type_key(key):
        assert isinstance(key, str)

    @staticmethod
    def _assert_type_data(key):
        assert isinstance(key, bytes)

    def exists(self, key: str) -> bool:
        Drive._assert_type_key(key)
        return (self._root / key).exists()

    def save(self, key: str, data: bytes) -> bool:
        Drive._assert_type_key(key)
        Drive._assert_type_data(data)
        try:
            with open(self._root / key, "wb") as file:
                file.write(data)
            return True
        except Exception:
            return False

    def load(self, key: str) -> bytes:
        Drive._assert_type_key(key)
        with open(self._root / key, "rb") as file:
            data = file.read()
        return data

    def delete(self, key: str) -> bool:
        Drive._assert_type_key(key)
        try:
            Path(self._root / key).unlink()
            return True
        except Exception:
            return False


class DriveTemp(Drive):
    def __init__(self):
        self._temp = tempfile.TemporaryDirectory()
        super().__init__(root=self._temp.name, create=False)

    def __del__(self):
        super().__del__()
        self._temp.cleanup()
