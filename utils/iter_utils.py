# -*- coding: utf-8 -*-

## Iteration Module ##
# Making iterations easier #

from itertools import islice

def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))

if __name__ == '__main__':
	d = {'a': 3, 'b': 2, 'c': 3, 'd': 4}

	print(take(2, d.items()))
	print(take(3, d.items()))
	print(take(4, d.items()))
