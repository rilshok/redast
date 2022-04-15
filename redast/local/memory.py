__all__ = ("Memory",)

from typing import Any


class Memory:
    def __init__(self):
        self._memory = dict()

    def exists(self, key) -> bool:
        return key in self._memory

    def save(self, key, data) -> bool:
        self._memory[key] = data
        return True

    def load(self, key) -> Any:
        return self._memory[key]

    def delete(self, key) -> bool:
        if key in self._memory:
            del self._memory[key]
            return True
        return False
