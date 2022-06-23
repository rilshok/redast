# The MIT License (MIT)
# Copyright (c) 2022 Vladislav A. Proskurov
# see LICENSE for full details

__all__ = (
    "Drive",
    "DriveTemp",
)

from pathlib import Path
import typing as tp
import tempfile


class Drive:
    # TODO: split hash by dir parts
    def __init__(
        self,
        root: tp.Union[Path, str],
        create: bool = False,
        unstable: bool = True,
    ):
        root = Path(root)
        if create:
            root.mkdir(
                mode=0o750,
                parents=False,
                exist_ok=True,
            )
        assert root.exists() and root.is_dir()
        self._root = root
        self._unstable = unstable

    @staticmethod
    def _assert_type_key(key):
        assert isinstance(key, str)

    @staticmethod
    def _assert_type_data(key):
        assert isinstance(key, bytes)

    def exists(self, key: str) -> bool:
        self._assert_type_key(key)
        path = self._root / key
        if self._unstable:
            try:
                with open(path, "rb"):
                    return True
            except FileNotFoundError:
                return False
            except Exception:
                pass
        return path.exists()

    def save(self, key: str, data: bytes) -> bool:
        self._assert_type_key(key)
        self._assert_type_data(data)
        try:
            with open(self._root / key, "wb") as file:
                file.write(data)
            return True
        except Exception:
            return False

    def load(self, key: str) -> bytes:
        self._assert_type_key(key)
        with open(self._root / key, "rb") as file:
            data = file.read()
        return data

    def delete(self, key: str) -> bool:
        self._assert_type_key(key)
        try:
            Path(self._root / key).unlink()
            return True
        except Exception:
            return False


class DriveTemp(Drive):
    def __init__(self):
        self._temp = tempfile.TemporaryDirectory()
        super().__init__(
            root=self._temp.name,
            create=False,
            unstable=False,
        )

    def __del__(self):
        self._temp.cleanup()

    def __getstate__(self):
        root = self._root
        storage = dict()
        for path in root.rglob("*"):
            key = str(path.relative_to(root))
            with open(path, "rb") as file:
                storage[key] = file.read()

        state = self.__dict__.copy()
        state.pop("_temp")
        state.pop("_root")
        state["__storage__"] = storage
        return state

    def __setstate__(self, state):
        temp = tempfile.TemporaryDirectory()
        state["_temp"] = temp
        state["_root"] = Path(temp.name)
        storage = state.pop("__storage__")
        self.__dict__ = state
        for key in storage:
            self.save(key, storage[key])
