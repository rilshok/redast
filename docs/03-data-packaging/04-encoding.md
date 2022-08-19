# Encoding

```python
from redast import Storage, Memory

storage = Storage(Memory())

value = "Hello, 世界"

key = storage.encoding.push(value)
data_encoding = storage.load(key)
data = storage.encoding.load(key)

print(data_encoding)
print(data)
```

```plain
b'Hello, \xe4\xb8\x96\xe7\x95\x8c'
Hello, 世界
```
