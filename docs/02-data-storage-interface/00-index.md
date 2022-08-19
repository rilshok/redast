# Data storage interface

## Push data into storage

```python
key = storage.push(b"hello world")
print(key)
```

```plain
021ced8799296ceca557832ab941a50b4a11f83478cf141f51f933f653ab9fbcc05a037cddbed06e309bf334942c4e58cdf1a46e237911ccd7fcf9787cbc7fd0
```

## Pull data from storage

```python
data = storage.load(key)
print(data)
```

```plain
b'hello world'
```

## Check for data in storage

```python
key = storage.push(b"hello world")
ok = storage.exists(key)
bad = storage.exists("brokenkey")
print(ok, bad)
```

```plain
True False
```

## Pop data from storage

```python
key = storage.push(b"hello world")
data = storage.pop(key)
exist = storage.exists(key)
print(data, exist)
```

```plain
b'hello world' False
```

## Custom links

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
