__all__ = ("Storage", "Keeper", "Bridge")

from typing import Union, Protocol, runtime_checkable, Type
import cloudpickle  # type: ignore

from .hash import blake2b
from .packaging import *


@runtime_checkable
class Keeper(Protocol):
    def exists(self, key: str) -> bool:
        pass

    def save(self, key: str, data: bytes) -> bool:
        pass

    def load(self, key: str) -> bytes:
        pass

    def delete(self, key: str) -> bool:
        pass


class StorageMethod:
    def __init__(self, packaging: Type[Packaging]):
        if not issubclass(packaging, Packaging):
            raise TypeError("subclass `Packaging` expected")
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


class Storage:
    compression = StorageMethod(Compression)
    pickling = StorageMethod(Pickling)
    encryption = StorageMethod(Encryption)
    base64 = StorageMethod(Base64)

    def __init__(
        self,
        keeper: Keeper,
        *,
        hashing: str = "blake2b",
        compression: int = -1,
        encryption_key: Union[str, bytes] = None,
        encryption_password: Union[str, bytes] = None,
        encryption_seed: int = None,
    ):
        if not isinstance(keeper, Keeper):
            raise ValueError
        self._keeper = keeper
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

    def exists(self, key: str) -> bool:
        return self._keeper.exists(key)

    def save(self, key: str, data: bytes):
        return self._keeper.save(key, data)

    def load(self, key: str) -> bytes:
        return self._keeper.load(key)

    def delete(self, key: str) -> bool:
        return self._keeper.delete(key)

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
    def __init__(self, storage: Storage, wrapper: Packaging):
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

    def delete(self, key: str) -> bool:
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

    def delete(self) -> bool:
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


class Bridge:
    def __init__(self, src: Keeper, dst: Keeper):
        assert isinstance(src, Keeper)
        assert isinstance(dst, Keeper)
        self._src = src
        self._dst = dst if isinstance(dst, Storage) else Storage(dst)

    def exists(self, key: str) -> bool:
        return self._dst.link(key).exists() or self._src.exists(key)

    def save(self, key: str, data: bytes) -> bool:
        # check for adequacy
        saved = self._src.save(key, data)
        if not saved:
            return False
        self._dst.link(key).push(data)
        return True

    def load(self, key: str) -> bytes:
        try:
            data = self._dst.link(key).load()
        except Exception:
            data = self._src.load(key)
            self._dst.link(key).push(data)
        return data

    def delete(self, key: str) -> bool:
        self._dst.link(key).delete()
        return self._src.delete(key)
