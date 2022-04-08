import base64
import pickle
import zlib
from abc import ABC, abstractmethod

import cloudpickle


class Packaging(ABC):
    @abstractmethod
    def forward(self, i):
        pass

    @abstractmethod
    def backward(self, o):
        pass


class Compression(Packaging):
    def __init__(self, level=-1):
        self._level = level

    def forward(self, i):
        return zlib.compress(i, level=self._level)

    def backward(self, o):
        return zlib.decompress(o)


class Pickling(Packaging):
    def forward(self, i):
        return cloudpickle.dumps(i)

    def backward(self, o):
        return pickle.loads(o)


class Encryption(Packaging):
    def forward(self, i):
        return NotImplemented

    def backward(self, o):
        return NotImplemented


class Encoding(Packaging):
    pass


class Base64(Encoding):
    def forward(self, i):
        return base64.b64encode(i)

    def backward(self, o):
        return base64.b64decode(o)


class Conveyor(Packaging):
    def __init__(self, *packer: Packaging):
        self._packers = packer

    def forward(self, i):
        for p in self._packers:
            i = p.forward(i)
        return i

    def backward(self, o):
        for p in reversed(self._packers):
            o = p.backward(o)
        return o
