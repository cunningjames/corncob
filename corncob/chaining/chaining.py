import collections.abc as cab
import numbers

class Intrant(object):
    """Intrant -- temporary mixins

    This class is intended to be applied to an object in order to make available
    a temporary set of methods. This should not be used to create objects that
    live beyond a chain of method calls; the author cannot vouch for its
    stability in that use case. Each method call within the specified set will
    return an object of type `Intrant`, however, so a chain can be maintained as
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
            A new `Intrant` object with magic methods copied onto it
        """

        # Iterate over all attributes of the wrapped object, copying magic
        # methods -- except for a specified few -- to the class to be
        # instantiated:
        for attr in dir(item):
            if (re.match("^__.+__$", attr) and
                attr not in ["__init__", "__new__", "__del__", "__class__",
                             "__getattribute__", "__setattr__"]):
                setattr(cls, attr, getattr(item, attr))

        return super(Intrant, cls).__new__(cls)

    def __init__(self, item, registry):
        """Initialize the `Intrant` object.

        Args:
            item: an object to be wrapped
            registry: a dictionary mapping method names to functions
        """

        self.__item = item
        self.__registry = registry

    def __getattribute__(self, fn):
        """Handles dispatching any attribute access that isn't a magic method,
        routing anything that is not in the registry or directly within the
        `Intrant` class to the underlying object.

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
        if fn in ["_Intrant__item", "_Intrant__registry", "__getattribute__"]:
            return object.__getattribute__(self, fn)

        # If the attribute name is within the registry, call the spec. method:
        if fn in self.__registry:
            return lambda *args, **kwargs: Intrant(
                self.__registry[fn](self.__item, *args, **kwargs), self.__registry)

        # In all other cases, delegate to the object:
        return self.__item.__getattribute__(fn)

    def exeunt(self):
        """Returns the original wrapped object.

        Returns:
            the original wrapped object
        """

        return self.__item
