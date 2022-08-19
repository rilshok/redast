# Data storage interface

## Push data into storage

!!! example
    === "python"
        ```python
        from redast import Storage, Memory

        storage = Storage(Memory())

        key = storage.push(b"hello world")
        print(key)
        ```
    === "result"
        ```plain
        021ced8799296ceca557832ab941a50b4a11f83478cf141f51f933f653ab9fbcc05a037cddbed06e309bf334942c4e58cdf1a46e237911ccd7fcf9787cbc7fd0
        ```

## Pull data from storage
!!! example
    === "python"
        ```python
        from redast import Storage, Memory

        storage = Storage(Memory())

        data = storage.load(key)
        print(data)
        ```

    === "result"
        ```plain
        b'hello world'
        ```

## Check for data in storage

!!! example
    === "python"
        ```python
        from redast import Storage, Memory

        storage = Storage(Memory())

        key = storage.push(b"hello world")
        ok = storage.exists(key)
        bad = storage.exists("brokenkey")
        print(ok, bad)
        ```

    === "result"
        ```plain
        True False
        ```

## Pop data from storage

!!! example
    === "python"
        ```python
        from redast import Storage, Memory

        storage = Storage(Memory())

        key = storage.push(b"hello world")
        data = storage.pop(key)
        exist = storage.exists(key)
        print(data, exist)
        ```

    === "result"
        ```plain
        b'hello world' False
        ```

## Custom links

The ``link`` method links the saved data to the user identifier.

!!! example
    === "python"
        ```python
        from redast import Storage, Memory

        storage = Storage(Memory())

        storage.link("hello").push(b"hello world")
        data = storage.link("hello").load()
        print(data)
        ```

    === "result"
        ```plain
        b'hello world'
        ```

Any python object can act as an identifier, even a lambda function.

!!! example
    === "python"
        ```python
        from redast import Storage, Memory

        storage = Storage(Memory())

        key = lambda x: x**2
        storage.link(key).push(b"squaring")
        qrt = storage.link(key).load()
        print(qrt)
        ```

    === "result"
        ```plain
        b'squaring'
        ```

A sequence of objects can be used as an identifier.

!!! example
    === "python"
        ```python
        from redast import Storage, Memory

        storage = Storage(Memory())

        storage.link("hello", "world").push(b"hello world")
        data = storage.link("hello", "world").pop()
        print(data)
        ```

    === "result"
        ```plain
        b'hello world'
        ```
