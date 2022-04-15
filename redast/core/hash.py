import hashlib
import xxhash

from typing import Iterator


def iterable_hexdigest(algorithm, iterator: Iterator[bytes]) -> str:
    hasher = algorithm()
    for block in iterator:
        hasher.update(block)
    return hasher.hexdigest()


def hexdigest(algorithm, data: bytes, block_size=2 ** 20):
    if not isinstance(data, bytes):
        raise ValueError
    iterator = (data[i : i + block_size] for i in range(0, len(data), block_size))
    return iterable_hexdigest(algorithm=algorithm, iterator=iterator)


def get_hexdigest(algorithm):
    def inner(data: bytes, block_size=2 ** 20):
        return hexdigest(algorithm=algorithm, data=data, block_size=block_size)

    return inner


registry = dict(
    md5=hashlib.md5,
    sha1=hashlib.sha1,
    sha224=hashlib.sha224,
    sha256=hashlib.sha256,
    sha384=hashlib.sha384,
    sha512=hashlib.sha512,
    sha3_224=hashlib.sha3_224,
    sha3_256=hashlib.sha3_256,
    sha3_384=hashlib.sha3_384,
    sha3_512=hashlib.sha3_512,
    blake2b=hashlib.blake2b,
    blake2s=hashlib.blake2s,
    xxh32=xxhash.xxh32,
    xxh64=xxhash.xxh64,
    xxh128=xxhash.xxh128,
    xxh3_64=xxhash.xxh3_64,
    xxh3_128=xxhash.xxh3_128,
)


def get_hash_fn(algorithm):
    if isinstance(algorithm, str):
        if algorithm not in registry:
            raise ValueError
        algorithm = registry[algorithm]
    return get_hexdigest(algorithm)
