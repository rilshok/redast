# Compression

```python
from redast import Storage, Memory

storage = Storage(Memory())

data = b"hello"*5
key = storage.compression.push(data)
compressed = storage.load(key)
data = storage.compression.load(key)
print(len(compressed), len(data), compressed, data, sep="\n")
```

```plain
16
25
b'x\x9c\xcbH\xcd\xc9\xc9\xcf\xc0B\x00\x00\x86\xc4\ne'
b'hellohellohellohellohello'
```
