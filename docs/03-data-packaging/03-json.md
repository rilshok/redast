# Json

```python
from redast import Storage, Memory

storage = Storage(Memory())

value = [1, [2, 3], dict(a=4, b="5")]

key = storage.json.push(value)
data_json = storage.load(key)
data = storage.json.load(key)

print(type(data_json).__name__, data_json)
print(type(data).__name__, data)
```

```plain
str [1, [2, 3], {"a": 4, "b": "5"}]
list [1, [2, 3], {'a': 4, 'b': '5'}]
```
