import operator, __builtin__
from types import FunctionType, BuiltinFunctionType
from cStringIO import StringIO
from base import generic, method


def _get_operations():
    """Enumerate all operations to implemented as methods/generics."""
    answer = []
    for name, value in operator.__dict__.iteritems():
        if name.startswith("__") and name.endswith("__") and isinstance(
                value, (FunctionType, BuiltinFunctionType)):
            answer.append((name, value))
    answer.append(("__iter__", iter))
    answer.append(("__divmod__", divmod))
    answer.sort(key=lambda element: element[0])
    return answer

operations = {}
__all__ = []
_reverse_operation_names = (
            "add", "sub", "mul", "div",
            "truediv", "floordiv", "mod", "divmod",
            "pow",
            "lshift", "rshift",
            "and", "xor", "or" )

def _install_operations():
    """Install all the operations as generics in this module."""
    for name, value in _get_operations():
        doc = value.__doc__
        doc += "\n\n"
        doc += ("Called by the :meth:`AbstractObject.%s` special method." %
                name)
        basic_name = name[2:-2]
        if basic_name in _reverse_operation_names:
            doc += "\n"
            doc += "Also called by :meth:`AbstractObject.__r%s__` "\
                   "with arguments reversed." % basic_name
        operations[name] = globals()[name] = generic(name, doc)
        __all__.append(name)

_install_operations()


__init__ = generic("__init__",
""":func:`__init__` initializes instantiates instances of :class:`AbstractObject` and it's subclasses.

It has a multi method for :class:`Object`. This multi-method does not accept any
additional parameters and has no effect.
There is no method for :class:`AbstractObject`, therefore
this class can not be instantiated.""")


__call__ = generic("__call__",
""":func:`__call__` is called when instances of :class:`AbstractObject` are called.""")

__del__ = generic("__del__",
""":func:`__del__` is called when instances of :class:`FinalizingMixin` are about to be destroyed.""")


class Writer(object):
    """A simple wrapper around a file like object.

    :class:`Writer`'s purpose is to simplify the implementation
    of the generics :func:`__out__` and :func:`__spy__`.
    
    `Writer` instances are initialised either with a file_like object
    or with no arguments. In the later case ab instance of `StringIO`
    is used.

    Output is done by simply calling the writer with at least one string object.
    The first argument acts as a %-template for formating the other arguments.

    The class is intended to be sub-classed for formatted output."""

    def __init__(self, file_like = None):
        """Initialize the `Write` with a file like object.

        :param file_like: An optional file-like object."""
        if file_like is None:
            file_like = StringIO()
        self.file = file_like

    def __call__(self, text = None, *arguments):
        """Write text % arguments on the file-like objects.

        If no arguments are passed write a newline."""
        if text is None:
            self.file.write("\n")
        else:
            self.file.write(text % arguments)

    def get_text(self):
        """Get the text written so far.

        :Note: This method is only supported if the file-like object
               implements :class:`StringIO`'s :meth:`getvalue` method."""
        return self.file.getvalue()


class AbstractObject(object):
    """An abstract (mixin) class that maps all the python magic functions to generics."""

    def __init__(self, *arguments):
        "Call the :func:`__init__` generic function."""
        __init__(self, *arguments)

    def __call__(self, *arguments):
        "Call the :func:`__call__` generic function."""
        return __call__(self, *arguments)

    def __str__(self):
        "Answer the objects print-string by calling :func:`as_string`."""
        return as_string(self)

    def __repr__(self):
        "Answer the objects debug-string by calling :func:`spy`."""
        return spy(self)

    def __float__(self):
        """Convert the object to a `float` by calling the :func:`__float__` generic."""
        return __float__(self)

    def __int__(self):
        """Convert the object to an `int` by calling the :func:`__int__` generic."""
        return __int__(self)


class Object(AbstractObject):
    """Just like `AbstractObject`, but can be instantiated."""

@method(Object)
def __init__(an_object):
    """Do nothing for :class:`Object`."""
    pass


def _install_operations():
    """Install the operations in the class."""

    def get_doc(value):
        try:
            function = getattr(operator, value.__name__)
        except AttributeError:
            function = getattr(__builtin__, value.__name__[2:-2])
        return function.__doc__


    def generate_operation(value):

        def operation(*arguments):
            #d#print "reg:", arguments
            return value(*arguments)

        doc = get_doc(value) 
        doc += "\n\n"
        doc += ("Calls the :func:`%s`-generic with its arguments." %
                value.__name__)
        operation.__doc__ = doc
        return operation

    def generate_reverse_operation(value):

        def operation(argument0, argument1):
            #d#print "rev:", argument0, argument1
            return value(argument1, argument0)
        
        doc = get_doc(value) 
        doc += "\n\n"
        doc += ("Calls the :func:`%s`-generic with its arguments reversed." %
                value.__name__)
        operation.__doc__ = doc
        return operation

    for name, value in _get_operations():
        operation = generate_operation(operations[name])
        setattr(AbstractObject, name, operation)
    for name in _reverse_operation_names:
        operation = generate_reverse_operation(operations["__%s__" % name])
        setattr(AbstractObject, "__r%s__" % name, operation)


_install_operations()

del _install_operations
del _get_operations

__float__ = generic("__float__", "Convert an :class:`AbstractObject` to a `float`.")
__int__ = generic("__int__", "Convert an :class:`AbstractObject` to an `int`.")


class FinalizingMixin(object):
    """A mixin class with `__del__` implemented as a generic function.
    
    :Note: This functionality was separated into mixin class,
           because Python's cycle garbage collector does not collect
           classes with a :meth:`__del__` method.
           Inherit from this class if you really 
           need :func:`__del__`.
           """

    def __del__(self):
        """Call the :func:`__del__` generic function."""
        __del__(self)


@generic
def as_string(self):
    """Answer an object's print string.

    This is done by creating a :class:`Writer` instance
    and calling the :func:`__out__` generic with the
    object and the writer. The using :meth:`Writer.get_text`
    to retrieve the text written."""
    writer = Writer()
    __out__(self, writer)
    return writer.get_text()

__out__ = generic("__out__",
        "Create a print string of an object using a :class:`Writer`.")

@method(object, Writer)
def __out__(self, write):
    """Write a just :func:`str` of self."""
    write(str(self))

@method(AbstractObject, Writer)
def __out__(self, write):
    """Write a just :func:`str` of self by directly calling :meth:`object.__str__`."""
    write(object.__str__(self))


@generic
def spy(self):
    """Answer an object's debug string.

    This is done by creating a :class:`Writer` instance
    and calling the :func:`__spy__` generic with the
    object and the writer. The using :meth:`Writer.get_text`
    to retrieve the text written."""
    writer = Writer()
    __spy__(self, writer)
    return writer.get_text()

__spy__ = generic("__spy__",
        "Create a print string of an object using a `Writer`.")

@method(object, Writer)
def __spy__(self, write):
    """Write a just :func:`repr` of self."""
    write(repr(self))

@method(AbstractObject, Writer)
def __spy__(self, write):
    """Write a just :func:`repr` of self by directly calling :meth:`object.__repr__`."""
    write(object.__repr__(self))

__all__.extend((
    "__spy__", "__out__", "__init__", "__call__", "__del__",
    "__float__", "__int__",
    "Writer", "AbstractObject", "Object", "FinalizingMixin",
    "spy", "as_string",
    ))
