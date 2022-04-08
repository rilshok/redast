import hashlib
from abc import ABC, abstractmethod
from typing import Callable, Iterator

from .bytes import Bytes


class HashString(ABC):
    def __init__(self, data: Bytes) -> None:
        assert isinstance(data, Bytes)
        hash = self.tohash(bytes(data))
        if not isinstance(hash, str):
            msg = f"value is of type `{type(hash).__name__}`, expected is `str`"
            raise TypeError(msg)
        length = self.req_length()
        if len(hash) != length:
            msg = (
                "The hash has an invalid length as a result of the evaluation. "
                f"Length is {len(hash)}, expected {length}"
            )
            raise ValueError(msg)
        self._hash = hash

    def hexdigest(self) -> str:
        return self._hash

    def __str__(self) -> str:
        return self.hexdigest()

    def __repr__(self) -> str:
        return str(self)

    @abstractmethod
    def tohash(self, data: bytes) -> str:
        pass

    @abstractmethod
    def req_length(self) -> int:
        pass


def hexdigest(iterator: Iterator[bytes], algorithm: Callable) -> str:
    hasher = algorithm()
    for block in iterator:
        hasher.update(block)
    return hasher.hexdigest()


class Blake2b(HashString):
    def tohash(self, data: bytes) -> str:
        assert isinstance(data, bytes)
        block_size = 2 ** 20
        iterator = (data[i : i + block_size] for i in range(0, len(data), block_size))
        return hexdigest(iterator, algorithm=hashlib.blake2b)

    def req_length(self) -> int:
        return 128

# TODO: xxhash
