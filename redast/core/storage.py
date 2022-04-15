__all__ = ("Storage", "Keeper", "Bridge")

from typing import Any, Protocol, Type, Union, runtime_checkable

from cloudpickle import dumps  # type: ignore

from .hash import get_hash_fn
from .packaging import *


@runtime_checkable
class Keeper(Protocol):
    def exists(self, key) -> bool:
        pass

    def save(self, key, data) -> bool:
        pass

    def load(self, key) -> Any:
        pass

    def delete(self, key) -> bool:
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
    json = StorageMethod(Json)
    encoding = StorageMethod(Encoding)

    def __init__(
        self,
        keeper: Keeper,
        *,
        hashing: str = "blake2b",
        compression: int = -1,
        encryption_key: Union[str, bytes] = None,
        encryption_password: Union[str, bytes] = None,
        encryption_seed: int = None,
        encoding: str = "utf-8",
    ):
        if not isinstance(keeper, Keeper):
            raise ValueError
        self._keeper = keeper
        self._alg = get_hash_fn(hashing)
        self._default = dict(
            compression=dict(level=compression),
            encryption=dict(
                key=encryption_key
                or Encryption.generate_key(
                    password=encryption_password,
                    seed=encryption_seed,
                )
            ),
            encoding=dict(encoding=encoding),
        )

    def exists(self, key) -> bool:
        return self._keeper.exists(key)

    def save(self, key, data) -> bool:
        return self._keeper.save(key, data)

    def load(self, key) -> Any:
        return self._keeper.load(key)

    def delete(self, key) -> bool:
        return self._keeper.delete(key)

    def hash(self, data) -> str:
        if not isinstance(data, bytes):
            data = dumps(data)
        return self._alg(data)

    def push(self, data) -> str:
        key = self.hash(data)
        self.save(key, data)
        return key

    def pop(self, key) -> Any:
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

    def exists(self, key) -> bool:
        return self._storage.exists(key=key)

    def save(self, key, data) -> bool:
        wrapped = self._wrapper.forward(data)
        return self._storage.save(key=key, data=wrapped)

    def load(self, key) -> Any:
        wrapped = self._storage.load(key=key)
        return self._wrapper.backward(wrapped)

    def delete(self, key) -> bool:
        return self._storage.delete(key=key)

    def hash(self, data) -> str:
        wrapped = self._wrapper.forward(data)
        return self._storage.hash(wrapped)

    def push(self, data) -> Any:
        wrapped = self._wrapper.forward(data)
        return self._storage.push(wrapped)

    def pop(self, key) -> Any:
        wrapped = self._storage.pop(key)
        return self._wrapper.backward(wrapped)


class Link:
    def __init__(self, *markers, storage: Storage):
        if not isinstance(storage, Storage):
            raise ValueError
        self._marker = storage.hash(markers)
        self._storage = storage

    # TODO: garbage collection

    def exists(self) -> bool:
        if not self._storage.exists(self._marker):
            return False
        data_key = self._storage.load(self._marker).decode()
        return self._storage.exists(data_key)

    def load(self) -> Any:
        data_key = self._storage.load(self._marker).decode()
        return self._storage.load(data_key)

    def delete(self) -> bool:
        data_key = self._storage.pop(self._marker).decode()
        return self._storage.delete(data_key)

    def hash(self, data) -> str:
        return self._storage.hash(data)

    def push(self, data) -> Any:
        data_key = self._storage.push(data)
        self._storage.save(self._marker, data_key.encode())
        return data_key

    def pop(self) -> Any:
        data_key = self._storage.pop(self._marker).decode()
        return self._storage.pop(data_key)


class Bridge:
    def __init__(self, src: Keeper, dst: Keeper):
        assert isinstance(src, Keeper)
        assert isinstance(dst, Keeper)
        self._src = src
        self._dst = dst if isinstance(dst, Storage) else Storage(dst)

    def exists(self, key) -> bool:
        return self._dst.link(key).exists() or self._src.exists(key)

    def save(self, key, data) -> bool:
        # check for adequacy
        saved = self._src.save(key, data)
        if not saved:
            return False
        self._dst.link(key).push(data)
        return True

    def load(self, key) -> Any:
        try:
            data = self._dst.link(key).load()
        except Exception:
            data = self._src.load(key)
            self._dst.link(key).push(data)
        return data

    def delete(self, key) -> bool:
        self._dst.link(key).delete()
        return self._src.delete(key)
