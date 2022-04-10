__all__ = ("MegaCloudStorage",)

from ..core import Storage
from ..tool import bytes_to_temp_file

from mega import Mega  # type: ignore
import tempfile


class MegaCloudStorage(Storage):
    def __init__(self, email, password, root: str = "redast", **kwargs):
        mega = Mega()
        self._mega = mega.login(email, password)
        self._root_name = root
        self._root = self._mega.create_folder(root)[root]
        super().__init__(**kwargs)

    def _path(self, key: str) -> str:
        return self._root_name + "/" + key

    def exists(self, key: str) -> bool:
        path = self._path(key)
        find = self._mega.find(path)
        if find is None:
            return False
        return True

    def save(self, key: str, data: bytes) -> None:
        with bytes_to_temp_file(data) as path:
            self._mega.upload(path, self._root, key)

    def load(self, key: str) -> bytes:
        file_info = self._mega.find(self._path(key))
        with tempfile.TemporaryDirectory() as tempdir:
            temppath = self._mega.download(file_info, dest_path=tempdir)
            with open(temppath, "rb") as file:
                data = file.read()
        return data

    def delete(self, key: str):
        file_info = self._mega.find(self._path(key))
        self._mega.delete(file_info[0])
