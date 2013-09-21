"""
A collection of decorators for automatically decorating functions and methods
with sphinx documentation tags.
"""
import six


def params(**argtypes):
    """
    A decorator that automatically adds parameter and return type tags to a
    function or method docstring.

    Input should be specified as the parameter keyword/name and then a tuple of
    its type and a description string. This will also use the `returns` keyword
    to identify the returned type and documentation. The following is an
    example of how to use `docparams` to automatically document arguments::

        @params(input=(str, "string to be made lowercase.")
                returns=(str, "lowercase string"))
        def lowercase(input):
            return input.lower()

    This decorator subverts the normal way decorators work to modify what is
    decorated without incuring extra overhead at call time. This means that the
    decorated function is not wrapped as a normal decorated function is, simply
    altered.

    .. seealso:: For example output see :py:func:`params_example`
    """
    def modify(function):
        def paramline(name, atype, doc):
            """Takes name, atype nd doc converts to a param docstring line."""
            return ":param {1} {0}: {2}".format(name, atype.__name__, doc)

        rtype, rdoc = argtypes.pop("returns", (None, None))
        paramlines = [paramline(name, atype, doc) for name, (atype, doc) in
                      six.iteritems(argtypes)]

        if rdoc:
            paramlines.append(":return: " + rdoc)
        if rtype:
            paramlines.append(":rtype: " + rtype.__name__)

        doc = '\n'.join(paramlines)

        if function.__doc__:
            function.__doc__ = function.__doc__ + "\n\n" +  doc
        else:
            function.__doc__ = doc
        return function
    return modify


@params(text=(str, "string to make lowercase"),
        returns=(str, "lowercased text"))
def params_example(text):
    """This is a docstring."""
    return text.lower()
