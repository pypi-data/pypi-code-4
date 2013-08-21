from types import StringType, UnicodeType
from zope.interface import implements
from Products.Archetypes.interfaces import IVocabulary
from Products.Archetypes.atapi import DisplayList


class SimpleDynamicVocabulary(object):
    implements(IVocabulary)

    def __init__(self, values):
        """ @values - simple list of values """
        if isinstance(values, (StringType, UnicodeType)):
            # fallback for DGF <1.7 - this is not really working, just don't
            # fail if user does not use DGF < 1.7
            values = [values]
        self._values = values
        self._values_dl = DisplayList(([(key, key) for key in values]))

    def getDisplayList(self, instance):
        """ returns an object of class DisplayList as defined in
            Products.Archetypes.utils.

            The instance of the content is given as parameter.
        """
        return self._values_dl

    def getVocabularyDict(self, instance):
        """ returns the vocabulary as a dictionary with a string key and a
            string value. If it is not a flat vocabulary, the value is a
            tuple with a string and a sub-dictionary with the same format
            (or None if its a leave).

            Example for a flat vocabulary-dictionary:
            {'key1':'Value 1', 'key2':'Value 2'}

            Example for a hierachical:
            {'key1':('Value 1',{'key1.1':('Value 1.1',None)}),
             'key2':('Value 2',None)}

            The instance of the content is given as parameter.
        """
        return dict([(key, key) for key in self._values])

    def isFlat(self):
        """ returns true if the underlying vocabulary is flat, otherwise
            if its hierachical (tree-like) it returns false.
        """
        return True

    def showLeafsOnly(self):
        """ returns true for flat vocabularies. In hierachical (tree-like)
            vocabularies it defines if only leafs should be displayed, or
            knots and leafs.
        """
        return True
