# The MIT License (MIT)
# Copyright (c) 2022 Vladislav A. Proskurov
# see LICENSE for full details

__all__ = ("bytes_to_temp_file",)

from typing import Iterator
from pathlib import Path
import tempfile
from contextlib import contextmanager


@contextmanager
def bytes_to_temp_file(data: bytes) -> Iterator[Path]:
    tempdir = tempfile.TemporaryDirectory()
    path = Path(tempdir.name) / "temp_file"
    with open(path, "wb") as file:
        file.write(data)
    try:
        yield path
    except Exception:
        pass
    finally:
        tempdir.cleanup()
