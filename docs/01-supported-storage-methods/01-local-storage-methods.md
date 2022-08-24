# Local storage methods

## Memory storage

Local storage of data in RAM

```python
from redast import Storage, Memory

storage = Storage(Memory())
```

## Drive storage

Local storage of data on drive. To open a storage, you must specify the `root` folder.
This call will create an empty directory `./myStorage`.

```python
from redast import Storage, Drive

drive = Drive(root="myStorage", create=True)
storage = Storage(drive)
```

## SQLite storage

Local storage of data in a SQLite database file. To open the repository, you must specify the `path` to the file with the storage.
Using `SQLite` can be more efficient than `Drive` when interacting with a lot of small data items.
This call will create an empty database file `./storage.db`.

```python
from redast import Storage, Sqlite

db = Sqlite(path="storage.db", create=True)
storage = Storage(db)
```
