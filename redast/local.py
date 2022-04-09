from pathlib import Path
from typing import Union

from .core import Storage


class LocalStorage(Storage):
    def __init__(self, root: Union[Path, str], create: bool = False, **kwargs):
        root = Path(root)
        if create:
            root.mkdir(mode=0o750, parents=False, exist_ok=True)
        assert root.exists() and root.is_dir()
        self._root = root
        super().__init__(**kwargs)

    def exists(self, key: str) -> bool:
        return (self._root / key).exists()

    def save(self, key: str, data: bytes) -> None:
        # TODO: split hash by dir parts
        with open(self._root / key, "wb") as file:
            file.write(data)

    def load(self, key: str) -> bytes:
        with open(self._root / key, "rb") as file:
            data = file.read()
        return data

    def delete(self, key: str):
        Path(self._root / key).unlink()
