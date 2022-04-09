from .core import Storage


class MemoryStorage(Storage):
    def __init__(self, **kwargs):
        self._memory = dict()
        super().__init__(**kwargs)

    def exists(self, key: str) -> bool:
        return key in self._memory

    def load(self, key: str) -> bytes:
        return self._memory[key]

    def save(self, key: str, data: bytes):
        self._memory[key] = data

    def delete(self, key: str):
        del self._memory[key]
