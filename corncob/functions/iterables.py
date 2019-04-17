from functools import reduce
from multipledispatch import dispatch
from collections.abc import Callable, Iterable
from collections import defaultdict as dd

from .functions import bool_not, compose

import itertools as it


@dispatch(Iterable, [object])
def fold_left(seq, fn, init=None):
    """Fold left on general iterables."""
    if init is not None:
        return reduce(fn, seq, init)
    return reduce(fn, seq)

@dispatch([object])
def fold_left(fn, init=None):
    """Fold left curried in first argument."""
    return lambda seq: fold_left(seq, fn, init)

@dispatch(dict, [object])
def fold_left(dct, fn, init=None):
    """Fold left on dictionaries."""
    return reduce(lambda x, y: fn(x, y[0], y[1]), dct.items(), init)


@dispatch(Iterable, [object])
def fold_right(seq, fn, init=None):
    seq = iter(seq)

    if init is None:
        init = next(seq)
    return _fold_right_helper(seq, fn, init)

@dispatch([object])
def fold_right(fn, init=None):
    return lambda seq: fold_right(seq, fn, init)

def _fold_right_helper(seq, fn, init):
    try: nxt = next(seq)
    except StopIteration: return init

    return fn(nxt, fold_right_helper(seq, fn, init))

@dispatch(dict, [object])
def fold_right(dct, fn, init=None):
    return fold_right(dct.items(), lambda x, y: fn(x[0], x[1], y), init)


@dispatch(Iterable, Callable)
def map_seq(seq, fn):
    return map(fn, seq)

@dispatch(Callable)
def map_seq(fn):
    return lambda seq: map_seq(seq, fn)

@dispatch(dict, Callable)
def map_seq(dct, fn):
    for key, value in dct.items():
        yield fn(key, value)


@dispatch(Iterable, Callable)
def keep(seq, fn):
    return filter(fn, seq)

@dispatch(Callable)
def keep(fn):
    return lambda seq: keep(fn, seq)

@dispatch(dict, Callable)
def keep(dct, fn):
    for key, value in dct.items():
        if fn(key, value):
            yield (key, value)


@dispatch(Iterable, Callable)
def discard(seq, fn):
    return filter(compose(bool_not, fn), seq)

@dispatch(Callable)
def discard(fn):
    return lambda seq: discard(fn, seq)

@dispatch(dict, Callable)
def discard(dct, fn):
    for key, value in dct.items():
        if not fn(key, value):
            yield (key, value)


@dispatch(Iterable, Callable)
def take_while(seq, fn):
    return it.takewhile(fn, seq)

@dispatch(Iterable, Callable)
def take_while(seq, fn):
    return it.takewhile(fn, seq)


@dispatch(Iterable, Callable)
def drop_while(seq, fn):
    return it.dropwhile(fn, seq)

@dispatch(Iterable, Callable)
def drop_while(seq, fn):
    return it.dropwhile(fn, seq)

@dispatch(Iterable, Callable)
def group_by(seq, key):
    result = dd(list)

    for item in seq:
        result[key(item)].append(item)

    return dict(result)

@dispatch(object)
def group_by(key):
    return lambda seq: group_by(seq, key)

@dispatch(dict, object)
def group_by(dct, key):
    result = dd(dict)

    for k, v in dct.items():
        result[key(k, v)] = {**result[key(k, v)], **{k: v}}

    return dict(result)
