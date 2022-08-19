
# Pipeline data packing

In this example, the data will be converted in the following order before being stored:

* First, the object to be saved will be pickled
* After pickling, the result will be compressed
* The compression result is then encrypted
* The result of encryption is converted to base64
* The base 64 string is pushed into storage

```python
from redast import Storage, Memory

storage = Storage(Memory())

data = [("hello", "world"), "foo"]

auth = dict(
    password="mypassword",
    seed=2022,
)
pipe = storage.base64.encryption(**auth).compression(level=9).pickling

key = pipe.push(data)
stored = storage.load(key)
data = pipe.load(key)

print(stored, data, sep="\n")
```

```plain
b'z2bqXGPZoXkN_-3LB9ocrBeWi4rax7le4wJncKe1Cnz7ep-KoHgFDeV2DisMq6Az'
[('hello', 'world'), 'foo']
```

The default packing options for pipeline data can be set when creating the storage itself

```python
from redast import Storage, Memory

data = [("hello", "world"), "foo"]

storage = Storage(
    Memory(),
    compression = 9,
    encryption_password = "mypassword",
    encryption_seed = 2022,
)
pipe = storage.base64.encryption.compression.pickling


key = pipe.push(data)
stored = storage.load(key)
data = pipe.load(key)

print(stored, data, sep="\n")
```

```bash
b'z2bqXGPZoXkN_-3LB9ocrBeWi4rax7le4wJncKe1Cnz7ep-KoHgFDeV2DisMq6Az'
[('hello', 'world'), 'foo']
```

## Pipeline data packing with custom links

```python
from redast import Storage, Memory

storage = Storage(Memory())
pipe = storage.base64.compression

data = b"hello world"
pipe.link("mylink").push(data)
data = pipe.link("mylink").load()

print(data)
```

```plain
b'hello world'
```
