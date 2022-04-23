# -*- coding: utf-8 -*-

## Iteration Module ##
# Making iterations easier #

from collections.abc import Iterable
from typing import Optional, List, Union, Tuple

from itertools import islice

def take(n, iterable: Iterable) -> Optional[List]:
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))

def take_as_dict(n, iterable: dict) -> dict:
	"Return first n keys and values from a dictionary as a new dictionary"

	return {x: iterable[x] for x in list(iterable)[:n]}

if __name__ == '__main__':
	d = {'a': 3, 'b': 2, 'c': 3, 'd': 4}

	print(take(2, d.items()))
	print(take(3, d.items()))
	print(take(4, d.items()))

	print(take_from_dict(2, d))
	print(take_from_dict(3, d))
	print(take_from_dict(4, d))
