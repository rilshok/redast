__all__ = (
    "BridgeStorage",
    "DriveCacheStorage",
    "MemoryCacheStorage",
)

from pathlib import Path
from typing import Union

from .core import Storage
from .local import DriveStorage, MemoryStorage


class BridgeStorage(Storage):
    def __init__(self, src: Storage, dst: Storage, **kwargs):
        self._src = src
        self._dst = dst
        super().__init__(**kwargs)

    @property
    def src(self) -> Storage:
        return self._src

    @property
    def dst(self) -> Storage:
        return self._dst

    def exists(self, key: str) -> bool:
        return self._dst.link(key).exists() or self._src.exists(key)

    def save(self, key: str, data: bytes):
        self._src.save(key, data)
        self._dst.link(key).push(data)

    def load(self, key: str) -> bytes:
        try:
            data = self._dst.link(key).load()
        except Exception:
            data = self._src.load(key)
            self._dst.link(key).push(data)
        return data

    def delete(self, key: str) -> None:
        self._dst.link(key).delete()
        return self._src.delete(key)

    def hash(self, data: bytes) -> str:
        return self._src.hash(data)

    def push(self, data: bytes) -> str:
        key = self._src.push(data)
        self._dst.link(key).push(data)
        return key

    def pop(self, key: str) -> bytes:
        data = self._dst.link(key).pop()
        self._src.delete(key)
        return data


class DriveCacheStorage(BridgeStorage):
    def __init__(
        self, src: Storage, root: Union[Path, str], create: bool = False, **kwargs
    ):
        dst = DriveStorage(root=root, create=create)
        super().__init__(src=src, dst=dst, **kwargs)


class MemoryCacheStorage(BridgeStorage):
    def __init__(self, src: Storage, **kwargs):
        dst = MemoryStorage()
        super().__init__(src=src, dst=dst, **kwargs)
