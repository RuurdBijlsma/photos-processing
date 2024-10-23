import itertools
from typing import TypeVar

T = TypeVar("T")


def chunk_list_itertools(data: list[T], n: int) -> list[list[T]]:
    """Split a list into n chunks using itertools."""
    it = iter(data)
    return [
        list(itertools.islice(it, i))
        for i in [len(data) // n + (1 if x < len(data) % n else 0) for x in range(n)]
    ]
