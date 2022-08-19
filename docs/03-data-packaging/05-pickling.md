# Pickling of python objects

Different types of pre-processing can be combined into a single conveyor line

```python
from redast import Storage, Memory

storage = Storage(Memory())

data = dict(a=1, b=2)
key = storage.pickling.push(data)
data = storage.pickling.load(key)
print(data)
```

```plain
{'a': 1, 'b': 2}
```
