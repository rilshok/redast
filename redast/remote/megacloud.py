__all__ = ("MegaCloud",)

from ..tool import bytes_to_temp_file

from mega import Mega  # type: ignore
import tempfile


class MegaCloud:
    def __init__(self, email, password, root: str = "redast"):
        mega = Mega()
        self._mega = mega.login(email, password)
        self._root_name = root
        self._root = self._mega.create_folder(root)[root]

    def _path(self, key: str) -> str:
        return self._root_name + "/" + key

    @staticmethod
    def _assert_type_key(key):
        assert isinstance(key, str)

    @staticmethod
    def _assert_type_data(key):
        assert isinstance(key, bytes)

    def exists(self, key: str) -> bool:
        MegaCloud._assert_type_key(key)
        path = self._path(key)
        find = self._mega.find(path)
        if find is None:
            return False
        return True

    def save(self, key: str, data: bytes) -> bool:
        MegaCloud._assert_type_key(key)
        MegaCloud._assert_type_data(data)
        with bytes_to_temp_file(data) as path:
            self._mega.upload(path, self._root, key)
        # FIXME: may not be true
        return True

    def load(self, key: str) -> bytes:
        MegaCloud._assert_type_key(key)
        file_info = self._mega.find(self._path(key))
        with tempfile.TemporaryDirectory() as tempdir:
            temppath = self._mega.download(file_info, dest_path=tempdir)
            with open(temppath, "rb") as file:
                data = file.read()
        return data

    def delete(self, key: str) -> bool:
        MegaCloud._assert_type_key(key)
        file_info = self._mega.find(self._path(key))
        self._mega.delete(file_info[0])
        # FIXME: may not be true
        return True
