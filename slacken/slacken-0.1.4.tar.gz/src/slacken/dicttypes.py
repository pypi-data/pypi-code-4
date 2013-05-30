"""
Syntactic sugar
"""
__author__ = 'Alistair Broomhead'


def _accessor_factory(dict_):

    class AttrDict(object):
        """
        Accessor object to get dictionary keys by attribute access - can
        make for easier to read syntax (Javascript style)
        """
        @staticmethod
        def _as_dict():
            return dict_

        def __getattr__(self, item):
            if item in dict_.keys():
                x = dict_[item]
                if isinstance(x, dict):
                    return _accessor_factory(x)()
                return x

        def __setattr__(self, key, value):
            dict_[key] = value

        def __getitem__(self, item):
            if item in dict_.keys():
                x = dict_[item]
                if isinstance(x, dict):
                    return _accessor_factory(x)()
                return x

        def __setitem__(self, key, value):
            dict_[key] = value

        def __delattr__(self, item):
            if item in dict_.keys():
                del dict_[item]

        def __repr__(self):
            return repr(dict_)

        def __str__(self):
            return str(dict_)

        def __iter__(self):
            return iter(dict_)

    return AttrDict


def AttrDict(dict_=None):
    """
    Accessor object to get dictionary keys  by attribute access
    :param dict_: existing dictionary (if None given, creates a new one)
    """
    if dict_ is None:
        dict_ = {}
    cls = _accessor_factory(dict_)
    return cls()
