__all__ = (
    "Packaging",
    "Conveyor",
    "Compression",
    "Pickling",
    "Base64",
    "Json",
    "Encoding",
    "Encryption",
)

import base64
import os
import pickle
import zlib
import json
from hashlib import sha256
from typing import Any, Protocol, Union, runtime_checkable

import cloudpickle  # type: ignore
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


@runtime_checkable
class Packaging(Protocol):
    # TODO: checking for input and output types
    def forward(self, i) -> Any:
        pass

    def backward(self, o) -> Any:
        pass


class Conveyor:
    def __init__(self, *packer: Packaging):
        if not all([isinstance(p, Packaging) for p in packer]):
            raise TypeError
        self._packers = packer

    def forward(self, i) -> Any:
        for p in self._packers:
            i = p.forward(i)
        return i

    def backward(self, o) -> Any:
        for p in reversed(self._packers):
            o = p.backward(o)
        return o


class Compression:
    def __init__(self, level=-1):
        self._level = level

    def forward(self, i: bytes) -> bytes:
        assert isinstance(i, bytes)
        return zlib.compress(i, level=self._level)

    def backward(self, o: bytes) -> bytes:
        assert isinstance(o, bytes)
        return zlib.decompress(o)


class Pickling:
    def forward(self, i) -> bytes:
        return cloudpickle.dumps(i)

    def backward(self, o: bytes) -> Any:
        assert isinstance(o, bytes)
        return pickle.loads(o)


class Base64:
    def forward(self, i: bytes) -> bytes:
        assert isinstance(i, bytes)
        return base64.urlsafe_b64encode(i)

    def backward(self, o: bytes) -> bytes:
        assert isinstance(o, bytes)
        return base64.urlsafe_b64decode(o)


class Json:
    # TODO: numpy array?
    def forward(self, i) -> str:
        return json.dumps(i)

    def backward(self, o: str) -> Any:
        assert isinstance(o, str)
        return json.loads(o)


class Encoding:
    def __init__(self, encoding="utf-8"):
        assert isinstance(encoding, str)
        self._encoding = encoding

    def forward(self, i: str) -> bytes:
        assert isinstance(i, str)
        return i.encode(encoding=self._encoding)

    def backward(self, o: bytes) -> str:
        assert isinstance(o, bytes)
        return str(o, encoding=self._encoding)


class Encryption:
    def __init__(
        self,
        *,
        key: Union[str, bytes] = None,
        password: Union[str, bytes] = None,
        seed: int = None,
    ):
        if key is not None:
            if isinstance(key, str):
                key = base64.urlsafe_b64decode(key)
            if not isinstance(key, bytes):
                raise ValueError("key must be represented in bytes")

        self._key = key or base64.urlsafe_b64decode(
            Encryption.generate_key(password=password, seed=seed)
        )

    @property
    def key(self) -> str:
        return str(base64.urlsafe_b64encode(self._key), "utf-8")

    @staticmethod
    def _hash(data: bytes) -> bytes:
        hasher = sha256()
        hasher.update(data)
        return hasher.digest()

    @staticmethod
    def _cipher(key: bytes):
        return Cipher(algorithms.AES(key), modes.ECB())

    @staticmethod
    def _padding():
        return padding.PKCS7(algorithms.AES.block_size)

    @staticmethod
    def generate_key(password: Union[str, bytes] = None, seed: int = None) -> str:
        if password is None:
            return str(base64.urlsafe_b64encode(os.urandom(32)), "utf-8")
        if seed is None:
            raise ValueError("when using a password, you must specify the salt seed")
        if isinstance(password, str):
            password = password.encode("utf-8")
        salt = Encryption._hash((seed).to_bytes(16, byteorder="big"))
        password += salt
        for _ in range(390_000):
            password = Encryption._hash(password)
        return str(base64.urlsafe_b64encode(password), "utf-8")

    def forward(self, i: bytes) -> bytes:
        assert isinstance(i, bytes)
        padder = Encryption._padding().padder()
        encryptor = Encryption._cipher(self._key).encryptor()
        padded = padder.update(i) + padder.finalize()
        return encryptor.update(padded) + encryptor.finalize()

    def backward(self, o: bytes) -> bytes:
        assert isinstance(o, bytes)
        unpadder = Encryption._padding().unpadder()
        decryptor = Encryption._cipher(self._key).decryptor()
        padded = decryptor.update(o) + decryptor.finalize()
        return unpadder.update(padded) + unpadder.finalize()
