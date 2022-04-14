__all__ = ("Memory",)


class Memory:
    def __init__(self):
        self._memory = dict()

    def exists(self, key: str) -> bool:
        return key in self._memory

    def save(self, key: str, data: bytes) -> bool:
        self._memory[key] = data
        return True

    def load(self, key: str) -> bytes:
        return self._memory[key]

    def delete(self, key: str) -> bool:
        if key in self._memory:
            del self._memory[key]
            return True
        return False
