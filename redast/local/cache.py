__all__ = (
    "CacheDrive",
    "CacheMemory",
)

from pathlib import Path
from typing import Union

from ..core import Bridge, Keeper
from .drive import Drive
from .memory import Memory


class CacheDrive(Bridge):
    def __init__(self, src: Keeper, root: Union[Path, str], create: bool = False):
        dst = Drive(root=root, create=create)
        super().__init__(src=src, dst=dst)


class CacheMemory(Bridge):
    def __init__(self, src: Keeper):
        dst = Memory()
        super().__init__(src=src, dst=dst)
