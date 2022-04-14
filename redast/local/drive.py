__all__ = ("Drive",)

from pathlib import Path
from typing import Union


class Drive:
    def __init__(self, root: Union[Path, str], create: bool = False):
        root = Path(root)
        if create:
            root.mkdir(mode=0o750, parents=False, exist_ok=True)
        assert root.exists() and root.is_dir()
        self._root = root

    def exists(self, key: str) -> bool:
        return (self._root / key).exists()

    def save(self, key: str, data: bytes) -> bool:
        # TODO: split hash by dir parts
        try:
            with open(self._root / key, "wb") as file:
                file.write(data)
            return True
        except Exception:
            return False

    def load(self, key: str) -> bytes:
        with open(self._root / key, "rb") as file:
            data = file.read()
        return data

    def delete(self, key: str) -> bool:
        try:
            Path(self._root / key).unlink()
            return True
        except Exception:
            return False
