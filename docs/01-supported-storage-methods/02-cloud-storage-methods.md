# Cloud storage methods

## Mega cloud storage

MEGA is a cloud storage and file hosting service offered by MEGA Limited.

* [mega.io](https://mega.io/) - cloud storage website
* [Mega.py](https://github.com/odwyersoftware/mega.py) - library for the Mega API

```python
from redast import Storage, MegaCloud

email = input()
password = input()
mega = MegaCloud(email=email, password=password, root='mystorage')
storage = Storage(mega)
```
