# REDAST - Remote Data Storage

Redast provides a flexible interface for storing data in different types of storages.
The organization of data storage is carried out according to the principle of a data lake.

## Installation

```bash
pip install redast
```

Or from GitHub

```bash
git clone git@github.com:rilshok/redast.git
cd redast
pip install -e .
```

or

```bash
pip install git+https://github.com/rilshok/redast.git
```

## Supported storage methods

### Local storage methods

#### Memory storage

Local storage of data in RAM

```python
from redast import Storage, Memory

storage = Storage(Memory())
```

#### Drive storage

Local storage of data on drive. To open a storage, you must specify the `root` folder.
This call will create an empty directory `./myStorage`.

```python
from redast import Storage, Drive

drive = Drive(root="myStorage", create=True)
storage = Storage(drive)
```

### Cloud storage methods

#### Mega cloud storage
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

## Data storage interface

### Push data into storage

```python
key = storage.push(b"hello world")
print(key)
```

```plain
021ced8799296ceca557832ab941a50b4a11f83478cf141f51f933f653ab9fbcc05a037cddbed06e309bf334942c4e58cdf1a46e237911ccd7fcf9787cbc7fd0
```

### Pull data from storage

```python
data = storage.load(key)
print(data)
```

```plain
b'hello world'
```

### Check for data in storage

```python
key = storage.push(b"hello world")
ok = storage.exists(key)
bad = storage.exists("brokenkey")
print(ok, bad)
```

```plain
True False
```

### Pop data from storage

```python
key = storage.push(b"hello world")
data = storage.pop(key)
exist = storage.exists(key)
print(data, exist)
```

```plain
b'hello world' False
```

### Custom links

The ``link`` method links the saved data to the user identifier.

```python
storage.link("hello").push(b"hello world")
data = storage.link("hello").load()
print(data)
```

```plain
b'hello world'
```

Any python object can act as an identifier, even a lambda function.

```python
key = lambda x: x**2
storage.link(key).push(b"squaring")
qrt = storage.link(key).load()
print(qrt)
```

```plain
b'squaring'
```

A sequence of objects can be used as an identifier.

```python
storage.link("hello", "world").push(b"hello world")
data = storage.link("hello", "world").pop()
print(data)
```

```plain
b'hello world'
```

## Data packaging

Some form of pre-processing may be required to store the data. For large storages, data compression may be appropriate. Public storage may require encryption. The REDAST supports different preprocessing.

### Compression

```python
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

### Base64

```python
key = storage.base64.push(b"hello world")
data_base64 = storage.load(key)
data = storage.base64.load(key)
print(data_base64, data, sep="\n")
```

```plain
b'aGVsbG8gd29ybGQ='
b'hello world'
```

### Json

```python
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

### Encoding

```python
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

### Pickling of python objects

Different types of pre-processing can be combined into a single conveyor line

```python
data = dict(a=1, b=2)
key = storage.pickling.push(data)
data = storage.pickling.load(key)
print(data)
```

```plain
{'a': 1, 'b': 2}
```

### Encryption

Encryption requires an encryption key or user password, from which the encryption key will be generated. When using encryption with a password, you must choose an arbitrary seed to create the salt.

You can generate a random key

```python
from redast import Encryption

secret = Encryption.generate_key()
print(secret)
```

```plain
pcu398oGPbEIoc8UgXGnmjJUZOId1bQRWJ5VmpH2gQo=
```

Generating an encryption key using a passphrase

```python
from redast import Encryption

secret1 = Encryption.generate_key(password="mypassword", seed=2022)
secret2 = Encryption.generate_key(password="mypassword", seed=2022)
secret3 = Encryption.generate_key(password="mypassword", seed=2021)
print(secret1, secret2, secret3, sep="\n")
```

```plain
DZ6xJLl9D7MkHkYt6JVef1j6o36KU7XzXzYRZrUDt0w=
DZ6xJLl9D7MkHkYt6JVef1j6o36KU7XzXzYRZrUDt0w=
I4sopjxisx6wb7dCkOtwoBxDvo5lnb6tctcpdpS5jGg=
```

Encryption with an encryption key

```python
from redast import Encryption

secret = Encryption.generate_key()
key = storage.encryption(key=secret).push(b"topsecret")

encrypted = storage.load(key)
decrypted = storage.encryption(key=secret).load(key)

print(encrypted, decrypted, sep="\n")
```

```plain
b"\x00k\xd0=\x81\xedh\x94x\xed\xb0\x14\xe3\r\x96'"
b'topsecret'
```

Encryption with a password

```python
key = storage.encryption(password="mypassword", seed=10).push(b"topsecret")

encrypted = storage.load(key)
decrypted = storage.encryption(password="mypassword", seed=10).load(key)

print(encrypted, decrypted, sep="\n")
```

```plain
b'\xe4\xc6\x0bc\xd0\x92\xcb\xaeQ\x0ey&\x83\xb9\x9d@'
b'topsecret'
```

### Pipeline data packing

In this example, the data will be converted in the following order before being stored:

* First, the object to be saved will be pickled
* After pickling, the result will be compressed
* The compression result is then encrypted
* The result of encryption is converted to base64
* The base 64 string is pushed into storage

```python
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

### Pipeline data packing with custom links

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
