from functools import reduce
from multipledispatch import dispatch
from collections.abc import Callable, Iterable, Hashable

import itertools as it
import re

def compose(*fns):
    def _inner(x):
        for fn in reversed(fns):
            x = fn(x)
        return x
    return _inner

def bool_not(b):
    return not bool(b)
