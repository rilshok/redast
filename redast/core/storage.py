__all__ = ("Storage",)

from abc import ABC, abstractmethod
from typing import Union

import cloudpickle  # type: ignore

from .hash import blake2b
from .packaging import *


class InvalidHash(ValueError):
    pass


class StorageMethod:
    def __init__(self, packaging):
        if not issubclass(packaging, Packaging):
            raise ValueError("subclass `Packaging` expected")
        self._type = packaging

    def __get__(self, instance: "Storage", owner):
        if not issubclass(owner, Storage):
            raise ValueError
        if self.key in instance._default:
            default = instance._default[self.key]
        else:
            default = dict()
        value = self._type(**default)
        return Pipe(instance, value)

    def __set__(self, instance, value):
        raise AttributeError

    def __set_name__(self, owner, name):
        self.key = name


class Storage(ABC):
    compression = StorageMethod(Compression)
    pickling = StorageMethod(Pickling)
    encryption = StorageMethod(Encryption)
    base64 = StorageMethod(Base64)

    def __init__(
        self,
        *,
        hashing: str = "blake2b",
        compression: int = -1,
        encryption_key: Union[str, bytes] = None,
        encryption_password: Union[str, bytes] = None,
        encryption_seed: int = None,
    ):
        if hashing == "blake2b":
            self._alg = blake2b
        else:
            raise ValueError
        self._default = dict(
            compression=dict(level=compression),
            encryption=dict(
                key=encryption_key
                or Encryption.generate_key(
                    password=encryption_password,
                    seed=encryption_seed,
                )
            ),
        )

    @abstractmethod
    def exists(self, key: str) -> bool:
        pass

    @abstractmethod
    def save(self, key: str, data: bytes):
        pass

    @abstractmethod
    def load(self, key: str) -> bytes:
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        pass

    def hash(self, data: bytes) -> str:
        return self._alg(data)

    def push(self, data: bytes) -> str:
        key = self.hash(data)
        self.save(key, data)
        return key

    def pop(self, key: str) -> bytes:
        data = self.load(key)
        self.delete(key)
        return data

    def link(self, *markers) -> "Link":
        return Link(*markers, storage=self)


class Pipe(Storage):
    def __init__(self, storage, wrapper: Packaging):
        if not isinstance(storage, Storage):
            raise ValueError
        if not isinstance(wrapper, Packaging):
            raise ValueError
        self._wrapper = wrapper
        self._default = storage._default
        self._storage = storage

    def __call__(self, **kwargs):
        self._wrapper = type(self._wrapper)(**kwargs)
        return self

    def exists(self, key: str) -> bool:
        return self._storage.exists(key=key)

    def save(self, key: str, data: bytes):
        wrapped = self._wrapper.forward(data)
        return self._storage.save(key=key, data=wrapped)

    def load(self, key: str):
        wrapped = self._storage.load(key=key)
        return self._wrapper.backward(wrapped)

    def delete(self, key: str):
        return self._storage.delete(key=key)

    def hash(self, data: bytes) -> str:
        wrapped = self._wrapper.forward(data)
        return self._storage.hash(wrapped)

    def push(self, data: bytes) -> str:
        wrapped = self._wrapper.forward(data)
        return self._storage.push(wrapped)

    def pop(self, key: str) -> bytes:
        wrapped = self._storage.pop(key)
        return self._wrapper.backward(wrapped)


class Link:
    def __init__(self, *markers, storage: Storage):
        if not isinstance(storage, Storage):
            raise ValueError
        self._marker = storage.hash(cloudpickle.dumps(markers))
        self._storage = storage

    # TODO: garbage collection

    def exists(self) -> bool:
        if not self._storage.exists(self._marker):
            return False
        data_key = self._storage.load(self._marker).decode()
        return self._storage.exists(data_key)

    def load(self) -> bytes:
        data_key = self._storage.load(self._marker).decode()
        return self._storage.load(data_key)

    def delete(self) -> None:
        data_key = self._storage.pop(self._marker).decode()
        return self._storage.delete(data_key)

    def hash(self, data: bytes) -> str:
        return self._storage.hash(data)

    def push(self, data: bytes) -> str:
        data_key = self._storage.push(data)
        self._storage.save(self._marker, data_key.encode())
        return data_key

    def pop(self) -> bytes:
        data_key = self._storage.pop(self._marker).decode()
        return self._storage.pop(data_key)
