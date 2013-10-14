#!/usr/bin/env python

"""
Abstract base class and similarity functions.
"""

import logging
from abc import ABCMeta, abstractmethod, abstractproperty  # pylint: disable=W0611


class _Base(object):  # pylint: disable=R0903
    """Shared base class."""

    def _repr(self, *args, **kwargs):
        """Return a __repr__ string from the arguments provided to __init__.
        @param args: list of arguments to __init__
        @param kwargs: dictionary of keyword arguments to __init__
        @return: __repr__ string
        """
        # Remove unnecessary empty keywords arguments
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        # Build the __repr__ string pieces
        args_repr = ', '.join(repr(arg) for arg in args)
        kwargs_repr = ', '.join(k + '=' + repr(v) for k, v in kwargs.items())
        if args_repr and kwargs_repr:
            kwargs_repr = ', ' + kwargs_repr
        name = self.__class__.__name__

        return "{}({}{})".format(name, args_repr, kwargs_repr)


class Similarity(_Base):  # pylint: disable=R0903
    """Represents the similarity between two objects."""

    def __init__(self, value, threshold=1.0):
        self.value = float(value)
        self.threshold = float(threshold)

    def __repr__(self):
        return self._repr(self.value, threshold=self.threshold)

    def __str__(self):
        return "{:.1%} similar".format(self.value)

    def __eq__(self, other):
        return abs(float(self) - float(other)) < 0.001

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        return float(self) < float(other)

    def __gt__(self, other):
        return float(self) > float(other)

    def __bool__(self):
        """In boolean scenarios, similarity is True if the threshold is met.
        """
        return self.value >= self.threshold

    def __float__(self):
        """In non-boolean scenarios, similarity is treated like a float.
        """
        return self.value

    def __add__(self, other):
        return Similarity(self.value + float(other), threshold=self.threshold)

    def __radd__(self, other):
        return Similarity(float(other) + self.value, threshold=self.threshold)

    def __iadd__(self, other):
        self.value += float(other)
        return self

    def __sub__(self, other):
        return Similarity(self.value - float(other), threshold=self.threshold)

    def __rsub__(self, other):
        return Similarity(float(other) - self.value, threshold=self.threshold)

    def __isub__(self, other):
        self.value -= float(other)
        return self

    def __mul__(self, other):
        return Similarity(self.value * float(other), threshold=self.threshold)

    def __rmul__(self, other):
        return Similarity(float(other) * self.value, threshold=self.threshold)

    def __imul__(self, other):
        self.value *= float(other)
        return self

    def __abs__(self):
        return Similarity(abs(self.value), threshold=self.threshold)

    def __round__(self, digits):
        return Similarity(round(self.value, digits), threshold=self.threshold)


class _Indent(object):
    """Indent formatter for logging calls."""

    level = 0

    @classmethod
    def more(cls):
        """Increase the indent level."""
        cls.level += 1

    @classmethod
    def less(cls):
        """Decrease the indent level."""
        cls.level = max(cls.level - 1, 0)

    @classmethod
    def indent(cls, fmt):
        """Get a new format string with indentation."""
        return '| ' * cls.level + fmt


def equal(obj1, obj2):
    """Calculate equality between two (Comparable) objects.
    """
    Comparable.log(obj1, obj2, '==')
    equality = obj1.equality(obj2)
    Comparable.log(obj1, obj2, '==', result=equality)
    return equality


def similar(obj1, obj2):
    """Calculate similarity between two (Comparable) objects.
    """
    Comparable.log(obj1, obj2, '%')
    similarity = obj1.similarity(obj2)
    Comparable.log(obj1, obj2, '%', result=similarity)
    return similarity


class Comparable(_Base, metaclass=ABCMeta):
    """Abstract Base Class for objects that are comparable.

    Subclasses directly comparable must override the 'equality' and
    'similarity' methods to return a bool and 'Similarity' object,
    respectively.

    Subclasses comparable by attributes must override the
    'attributes' property to define which (Comparable) attributes
    should be considered.

    Both types of subclasses may also override the 'threshold'
    attribute to change the default similarity threshold.
    """

    def __eq__(self, other):
        """Maps the '==' operator to be a shortcut for "equality".
        """
        return equal(self, other)

    def __ne__(self, other):
        return not (self == other)

    def __mod__(self, other):
        """Maps the '%' operator to be a shortcut for "similarity".
        """
        return similar(self, other)

    @abstractproperty
    def attributes(self):  # pragma: no cover, abstract
        """Get an attribute {name: weight} dictionary for comparisons.
        """
        return {}

    threshold = 1.0  # ratio for two objects to be considered "similar"

    @abstractmethod
    def equality(self, other):
        """Compare two objects for equality.
        @param self: first object to compare
        @param other: second object to compare
        @return: boolean result of comparison
        """
        # Compare specified attributes for equality
        cname = self.__class__.__name__
        for aname in self.attributes:
            try:
                attr1 = getattr(self, aname)
                attr2 = getattr(other, aname)
            except AttributeError as error:
                logging.debug("{}.{}: {}".format(cname, aname, error))
                return False
            self.log(attr1, attr2, '==', cname=cname, aname=aname)
            eql = (attr1 == attr2)
            self.log(attr1, attr2, '==', cname=cname, aname=aname, result=eql)
            if not eql:
                return False

        return True

    @abstractmethod
    def similarity(self, other):
        """Compare two objects for similarity.
        @param self: first object to compare
        @param other: second object to compare
        @return: L{Similarity} result of comparison
        """
        sim = self.Similarity()
        total = 0.0

        # Calculate similarity ratio for each attribute
        cname = self.__class__.__name__
        for aname, weight in self.attributes.items():

            attr1 = getattr(self, aname, None)
            attr2 = getattr(other, aname, None)
            self.log(attr1, attr2, '%', cname=cname, aname=aname)

            # Similarity is ignored if None on both objects
            if attr1 is None and attr2 is None:
                self.log(attr1, attr2, '%', cname=cname, aname=aname,
                         result="attributes are both None")
                continue

            # Similarity is 0 if either attribute is non-Comparable
            if not all((isinstance(attr1, Comparable),
                        isinstance(attr2, Comparable))):
                self.log(attr1, attr2, '%', cname=cname, aname=aname,
                         result="attributes not Comparable")
                total += weight
                continue

            # Calculate similarity between the attributes
            attr_sim = (attr1 % attr2)
            self.log(attr1, attr2, '%', cname=cname, aname=aname,
                     result=attr_sim)

            # Add the similarity to the total
            sim += attr_sim * weight
            total += weight

        # Scale the similarity so the total is 1.0
        if total:
            sim *= (1.0 / total)

        return sim

    def Similarity(self, value=None, threshold=None):  # pylint: disable=C0103
        """Constructor for new default Similarities."""
        if value is None:
            value = 0.0
        if threshold is None:
            threshold = self.threshold
        return Similarity(value, threshold=threshold)

    @staticmethod
    def log(obj1, obj2, sym, cname=None, aname=None, result=None):  # pylint: disable=R0913
        """Log the objects being compared and the result.

        When no result object is specified, subsequence calls will have an
        increased indentation level. The indentation level is decreased
        once a result object is provided.

        @param obj1: first object
        @param obj2: second object
        @param sym: operation being performed ('==' or '%')
        @param cname: name of class (when attributes are being compared)
        @param aname: name of attribute (when attributes are being compared)
        @param result: outcome of comparison
        """
        fmt = "{o1} {sym} {o2} : {r}"
        if cname or aname:
            assert cname and aname  # both must be specified
            fmt = "{c}.{a}: " + fmt

        if result is None:
            result = '...'
            fmt = _Indent.indent(fmt)
            _Indent.more()
        else:
            _Indent.less()
            fmt = _Indent.indent(fmt)

        logging.info(fmt.format(o1=repr(obj1), o2=repr(obj2),
                                c=cname, a=aname, sym=sym, r=result))


class SimpleComparable(Comparable):  # pylint: disable=W0223
    """Abstract Base Class for objects that are directly comparable.

    Subclasses directly comparable must override the 'equality' and
    'similarity' methods to return a bool and 'Similarity' object,
    respectively. They may also override the 'threshold' attribute
    to change the default similarity threshold.
    """

    @property
    def attributes(self):  # pragma: no cover, abstract
        """A simple comparable does not use the attributes property.
        """
        raise AttributeError()


class CompoundComparable(Comparable):  # pylint: disable=W0223
    """Abstract Base Class for objects that are comparable by attributes.

    Subclasses comparable by attributes must override the
    'attributes' property to define which (Comparable) attributes
    should be considered. They may also override the 'threshold'
    attribute to change the default similarity threshold.
    """

    def equality(self, other):
        """A compound comparable's equality is based on attributes.
        """
        return super().equality(other)

    def similarity(self, other):
        """A compound comparable's similarity is based on attributes.
        """
        return super().similarity(other)
