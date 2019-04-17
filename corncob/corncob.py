from multipledispatch import dispatch
from collections.abc import Callable, Iterable, Hashable

import pandas as pd
import numpy as np

import re

@dispatch(pd.DataFrame, [object])
def select(df, *args):
    return df[list(args)]

@dispatch([object])
def select(*args):
    return lambda df: select(df, *args)

@dispatch(pd.DataFrame, [object])
def mutate(df, **kwargs):
    result = df

    return result.assign(**kwargs)

@dispatch([object])
def mutate(**kwargs):
    return lambda df: mutate(df, **kwargs)

@dispatch(pd.DataFrame, [object])
def group_by(df, *args):
    return df.groupby(list(args))

@dispatch([object])
def group_by(*args):
    return lambda df: group_by(df, *args)





foo = pd.read_csv("/Users/j260381/Projects/training-datarobot-api/docs/data/ames.csv")

class intrant(object):
    """intrant -- temporary mixins

    This class is intended to be applied to an object in order to make available
    a temporary set of methods. This should not be used to create objects that
    live beyond a chain of method calls; the author cannot vouch for its
    stability in that use case. Each method call within the specified set will
    return an object of type `intrant`, however, so a chain can be maintained as
    long as necessary.

    Calling a method not within the chain, or explicity calling `exeunt`, will
    end the chain and return an object of the expected type.
    """

    def __new__(cls, item, registry):
        """Magic methods are dispatched at the class level, so in order to copy
        those I have to do so within `__new__`. The list of methods to avoid
        copying includes methods that can't be, as well as `__setattr__` (since
        Pandas DataFrame objects will throw a warning if I try).

        Args:
            item: an object to be wrapped
            registry: a dictionary mapping method names to functions
        Returns:
            A new `intrant` object with magic methods copied onto it
        """

        # Iterate over all attributes of the wrapped object, copying magic
        # methods -- except for a specified few -- to the class to be
        # instantiated:
        for attr in dir(item):
            if (re.match("^__.+__$", attr) and
                attr not in ["__init__", "__new__", "__del__", "__class__",
                             "__getattribute__", "__setattr__"]):
                setattr(cls, attr, getattr(item, attr))

        return super(intrant, cls).__new__(cls)

    def __init__(self, item, registry):
        """Initialize the `intrant` object.

        Args:
            item: an object to be wrapped
            registry: a dictionary mapping method names to functions
        """

        self.__item = item
        self.__registry = registry

    def __getattribute__(self, fn):
        """Handles dispatching any attribute access that isn't a magic method,
        routing anything that is not in the registry or directly within the
        `intrant` class to the underlying object.

        Todo: explore the possibility of namespacing the registry, perhaps
        having separate dictionaries for different types of objects to better
        support chains that can switch type back and forth.

        Args:
            fn: a string representing the attribute to be accessed
        Returns:
            the requested attribute
        """

        # For any of these, we need to short circuit this in order to avoid
        # infinite recursion:
        if fn in ["_intrant__item", "_intrant__registry", "__getattribute__"]:
            return object.__getattribute__(self, fn)

        # If the attribute name is within the registry, call the spec. method:
        if fn in self.__registry:
            return lambda *args, **kwargs: intrant(
                self.__registry[fn](self.__item, *args, **kwargs), self.__registry)

        # In all other cases, delegate to the object:
        return self.__item.__getattribute__(fn)

    def exeunt(self):
        """Returns the original wrapped object.

        Returns:
            the original wrapped object
        """

        return self.__item


class var(object):
    def __init__(self, id, stack=None):
        self._id = id

        if stack is None:
            self._stack = [("access", id)]
        else:
            self._stack = stack

    def log(self, base):
        return var(id, self._stack + [("log", base)])

    def __add__(self, other):
        return var(id, self._stack + [("add", other)])

    def __radd__(self, other):
        return var(id, self._stack + [("radd", other)])

class VarHandler(object):
    def __init__(self, item):
        self._item = item

    def _handle(self, manip, curr_value):
        which_manip, *args = manip

        if which_manip == "access":
            return self._select(args[0])

        if which_manip == "add":
            if isinstance(args[0], var):
                other = self._interpret(args[0]._stack)
            else:
                other = args[0]

            return self._add(curr_value, other)

        if which_manip == "radd":
            if isinstance(args[0], var):
                other = self._interpret(args[0]._stack)
            else:
                other = args[0]

            return self._add(other, curr_value)

        if which_manip == "log":
            return np.log(curr_value) / np.log(args[0])


class DFHandler(object):
    def __init__(self, df):
        self._df = df

    def _handle(self, manip, curr_value):
        which_manip, *args = manip

        if which_manip == "access":
            return self._df[[args[0]]]

        if which_manip == "add":
            if isinstance(args[0], var):
                other = self._interpret(args[0]._stack)
            else:
                other = args[0]

            return curr_value + other

        if which_manip == "radd":
            if isinstance(args[0], var):
                other = self._interpret(args[0]._stack)
            else:
                other = args[0]

            return other + curr_value

        if which_manip == "log":
            return np.log(curr_value) / np.log(args[0])


    def _interpret(self, stack):
        result = self._handle(stack[0], None)

        for manip in stack[1:]:
            result = self._handle(manip, result)

        return result


class DFHandler(object):
    def __init__(self, df):
        self._df = df

    def handle_log(self, id, base=None):
        if base is None:
            return np.log(self._df[[id]])
        return np.log(self._df[[id]]) / np.log(base)

    def handle_add(self, id, other):
        return self._df[[id]] + other

    def handle_id(self, id):
        return self._df[[id]]



(M(ames).
 select("Sale_Price", "Bedrooms").
 mutate(Sale_Price = col("Sale_Price").log()).
 group_by("Bedrooms").
 summarize(col("Sale_Price").mean()))

M(ames,
  select("Sale_Price", "Bedrooms"),
  mutate(Sale_Price = col("Sale_Price").log()),
  group_by("Bedrooms"),
  summarize(col("Sale_Price").mean()))
