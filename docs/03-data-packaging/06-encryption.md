# Encryption

Encryption requires an encryption key or user password, from which the encryption key will be generated. When using encryption with a password, you must choose an arbitrary seed to create the salt.

You can generate a random key

!!! example
    ```python
    from redast import Encryption

    secret = Encryption.generate_key()
    print(secret)
    ```

    ```plain
    pcu398oGPbEIoc8UgXGnmjJUZOId1bQRWJ5VmpH2gQo=
    ```

## Generating an encryption key using a passphrase

!!! example
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

## Encryption with an encryption key

!!! example
    ```python
    from redast import Storage, Memory, Encryption

    storage = Storage(Memory())


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

## Encryption with a password

!!! example
    ```python
    from redast import Storage, Memory

    storage = Storage(Memory())

    key = storage.encryption(password="mypassword", seed=10).push(b"topsecret")

    encrypted = storage.load(key)
    decrypted = storage.encryption(password="mypassword", seed=10).load(key)

    print(encrypted, decrypted, sep="\n")
    ```

    ```plain
    b'\xe4\xc6\x0bc\xd0\x92\xcb\xaeQ\x0ey&\x83\xb9\x9d@'
    b'topsecret'
    ```
