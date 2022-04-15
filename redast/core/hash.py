import hashlib
from typing import Iterator


def hexdigest(iterator: Iterator[bytes], algorithm) -> str:
    hasher = algorithm()
    for block in iterator:
        hasher.update(block)
    return hasher.hexdigest()


def blake2b(data: bytes, block_size=2 ** 20):
    if not isinstance(data, bytes):
        raise ValueError
    iterator = (data[i : i + block_size] for i in range(0, len(data), block_size))
    return hexdigest(iterator, hashlib.blake2b)


registry = dict(
    blake2b=blake2b,
)


def get_hash_fn(name: str):
    if name not in registry:
        raise ValueError
    return registry[name]
