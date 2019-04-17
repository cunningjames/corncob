from multipledispatch import dispatch
from collections.abc import Callable

from numbers import Complex

from math import (acos, asin, asinh, atan, atan2, atanh, ceil, cos, cosh,
                  degrees, erf, erfc, exp, expm1, fabs, factorial, floor,
                  fmod, frexp, gamma, gcd, hypot, isclose, isfinite, isinf,
                  isnan, ldexp, lgamma, log, log10, log1p, log2, modf, pow,
                  radians, remainder, sin, sinh, sqrt, tan, tanh, trunc)

from operator import (abs, add, and_, eq, floordiv, ge, gt, inv, le, lshift,
                      lt, mod, mul, ne, neg, not_, or_, pos, rshift,
                      sub, truediv, xor)

def upto(start_end, *args, **kwargs):
    if not len(args) and not len(kwargs):
        return lambda start: range(start, start_end)
    if not len(args) and len(kwargs):
        return lambda start: range(start, start_end, kwargs["by"])
    if len(args) and not len(kwargs):
        return range(start_end, args[0])
    if len(args) and len(kwargs):
        return range(start_end, args[0], kwargs["by"])

fmod, ldexp, pow, remainder, add, and_, eq, floordiv, ge, gt, le, lshift, lt, mod, mul, ne, not_, or_, rshift, sub, truediv, xor
