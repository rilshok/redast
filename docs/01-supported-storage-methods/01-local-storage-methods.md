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
