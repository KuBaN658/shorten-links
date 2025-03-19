import hashlib
import random


def generate_alias(url: str) -> str:
    hash_object = hashlib.sha256(url.encode("utf-8"))
    alias = "".join(random.choices(hash_object.hexdigest(), k=8))
    return alias
