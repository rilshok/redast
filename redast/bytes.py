__all__ = (
    "Bytes",
    "FileBytes",
    "ObjectBytes",
    "ClassBytes",
    "StringBytes",
    "CallableBytes",
)

import inspect
import pickle
import types
from pathlib import Path
from typing import Callable, Union


class Bytes:
    def __init__(self, data: bytes) -> None:
        assert isinstance(data, bytes)
        self._data = data

    def __bytes__(self) -> bytes:
        return self._data

    def __add__(self, other: "Bytes") -> "Bytes":
        assert isinstance(other, Bytes)
        return Bytes(bytes(self) + bytes(other))

    def __repr__(self):
        return repr(bytes(self))


class FileBytes(Bytes):
    def __init__(self, path: Union[str, Path]) -> None:
        path = Path(path)
        assert path.exists()
        with open(path, "rb") as file:
            data = file.read()
        super().__init__(data)


class ObjectBytes(Bytes):
    def __init__(self, obj: object) -> None:
        assert type(obj) is not type
        data = pickle.dumps(obj)
        super().__init__(data)


class ClassBytes(Bytes):
    def __init__(self, cls: type) -> None:
        assert isinstance(cls, type)
        data = inspect.getsource(cls).encode()
        super().__init__(data)


class StringBytes(Bytes):
    def __init__(self, string: str) -> None:
        assert isinstance(string, str)
        data = string.encode()
        super().__init__(data)


class CallableBytes(Bytes):
    def __init__(self, obj: Callable) -> None:
        super().__init__(self._convert(obj))

    @staticmethod
    def _convert(obj: Callable) -> bytes:
        if obj in __builtins__.values():
            return obj.__name__.encode()
        if isinstance(obj, types.FunctionType):
            return inspect.getsource(obj).encode()
        if isinstance(obj, type):
            return inspect.getsource(obj).encode()
        # TODO: lambda
        raise NotImplementedError
