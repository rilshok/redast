__all__ = ("Storage", "Link", "LocalStorage", "MemoryStorage")

import pickle
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict

from .bytes import Bytes
from .hash import Blake2b
from .typing import PathLike


class InvalidHash(ValueError):
    pass

class Storage(ABC):
    def __init__(self, algorithm: str = "blake2b"):
        if algorithm == "blake2b":
            self._alg = Blake2b
        else:
            raise NotImplementedError

    @abstractmethod
    def exists(self, key: str) -> bool:
        pass

    @abstractmethod
    def load(self, key: str) -> bytes:
        pass

    @abstractmethod
    def save(self, key: str, data: bytes):
        pass

    def hash(self, data: bytes) -> str:
        return str(self._alg(Bytes(data)))

    def push(self, data: bytes) -> str:
        assert isinstance(data, bytes)
        hash = self.hash(data)
        if not self.exists(hash):
            self.save(hash, data)
        return hash

    def pull(self, hash: str) -> bytes:
        if self.exists(hash):
            return self.load(hash)
        raise InvalidHash

    def push_object(self, obj) -> str:
        dump = pickle.dumps(obj)
        return self.push(dump)

    def pull_object(self, hash: str) -> Any:
        dump = self.pull(hash)
        obj = pickle.loads(dump)
        return obj

    def link(self, *markers) -> "Link":
        return Link(*markers, storage=self)


class Link:
    def __init__(self, *markers, storage: Storage) -> None:
        assert isinstance(storage, Storage)
        self._storage = storage

        def get_bytes(value) -> bytes:
            if isinstance(value, bytes):
                return value
            if isinstance(value, Bytes):
                return value.__class__.__name__.encode() + bytes(value)
            if "__bytes__" in dir(value):
                return bytes(value)
            return pickle.dumps(value)

        marker_bytes = b"|".join(map(get_bytes, markers))
        self._marker = self.storage.hash(marker_bytes)

    @property
    def storage(self) -> Storage:
        return self._storage

    @property
    def marker(self) -> str:
        return self._marker

    def exists(self) -> bool:
        return self.storage.exists(self.marker)

    def push(self, obj: bytes) -> None:
        obj_hash = self.storage.push(obj).encode()
        self.storage.save(self.marker, obj_hash)

    def pull(self):
        obj_hash = self.storage.pull(self.marker).decode()
        return self.storage.pull(obj_hash)

    def push_object(self, obj: Any) -> None:
        obj_hash = self.storage.push_object(obj).encode()
        self.storage.save(self.marker, obj_hash)

    def pull_object(self) -> Any:
        obj_hash = self.storage.pull(self.marker).decode()
        return self.storage.pull_object(obj_hash)


class LocalStorage(Storage):
    def __init__(
        self, root: PathLike, create: bool = False, algorithm: str = "blake2b"
    ):
        root = Path(root)
        if create:
            root.mkdir(mode=0o750, parents=False, exist_ok=True)
        assert root.exists() and root.is_dir()
        self._root = root

        super().__init__(algorithm=algorithm)

    @property
    def root(self) -> Path:
        return self._root

    def exists(self, hash: str) -> bool:
        return (self.root / hash).exists()

    def save(self, hash: str, data: bytes) -> None:
        # TODO: split hash by dir parts
        with open(self.root / hash, "wb") as file:
            file.write(data)

    def load(self, hash: str) -> bytes:
        with open(self.root / hash, "rb") as file:
            data = file.read()
        return data


class MemoryStorage(Storage):
    def __init__(self, algorithm: str = "blake2b"):
        self._memory: Dict[str, bytes] = dict()
        super().__init__(algorithm=algorithm)

    def exists(self, key: str) -> bool:
        return key in self._memory

    def load(self, key: str) -> bytes:
        return self._memory[key]

    def save(self, key: str, data: bytes):
        self._memory[key] = data
