from itertools import izip
import operator

from alignment.sequence import *


# Profile ---------------------------------------------------------------------

class SoftElement(object):

    def __init__(self, weights):
        self.__weights = dict(weights)

    def key(self):
        if len(self.__weights) == 1:
            for element in self.__weights:
                return element
        else:
            return None

    def mergedWith(self, other):
        weights = dict(self.__weights)
        for element, weight in other.__weights.iteritems():
            weights[element] = weights.get(element, 0) + weight
        return SoftElement(weights)

    def pairs(self):
        return self.__weights.iteritems()

    def sorted(self):
        return sorted(self.__weights.iteritems(), key=lambda w: (-w[1], w[0]))

    def probabilities(self):
        t = sum(self.__weights.itervalues())
        return {e: float(w) / t for e, w in self.__weights.iteritems()}

    def toDict(self):
        return self.__weights

    @classmethod
    def fromDict(cls, d):
        return cls(d)

    def __eq__(self, other):
        return self.__weights == other.__weights

    def __len__(self):
        return len(self.__weights)

    def __getitem__(self, item):
        return self.__weights[item]

    def __iter__(self):
        return iter(self.__weights)

    def __repr__(self):
        return repr(self.sorted())

    def __str__(self):
        weights = self.sorted()
        if len(weights) == 1:
            return str(weights[0][0])
        else:
            return '{%s}' % (','.join('%s:%d' % w for w in weights))

    def __unicode__(self):
        weights = self.sorted()
        if len(weights) == 1:
            return unicode(weights[0][0])
        else:
            return u'{%s}' % (u','.join(u'%s:%d' % w for w in weights))


class Profile(Sequence):

    @classmethod
    def fromSequence(cls, sequence):
        elements = [SoftElement({e: 1}) for e in sequence]
        return cls(elements)

    @classmethod
    def fromSequenceAlignment(cls, alignment):
        profile = cls()
        for i in xrange(len(alignment)):
            a = alignment.first[i]
            b = alignment.second[i]
            if a == b:
                element = SoftElement({a: 2})
            else:
                element = SoftElement({a: 1, b: 1})
            profile.push(element)
        return profile

    def __init__(self, elements=None):
        if elements is None:
            super(Profile, self).__init__(list())
        else:
            if not all(isinstance(e, SoftElement) for e in elements):
                raise ValueError(
                    'profile elements must belong to SoftElement class')
            super(Profile, self).__init__(list(elements))

    def key(self):
        return tuple(e.key() for e in self.elements)

    def pattern(self):
        words = list()
        for word in self.key():
            if word is None:
                words.append(u'*')
            else:
                words.append(word)
        return u' '.join(words)

    def minVariationCount(self):
        return max(len(e) for e in self.elements)

    def maxVariationCount(self):
        return reduce(operator.mul, (len(e) for e in self.elements))

    def mergeWith(self, other):
        if len(self) != len(other):
            raise ValueError(
                'profiles with different lengths cannot be merged')
        self.elements = [a.mergedWith(b)
                         for a, b in izip(self.elements, other.elements)]

    def toDict(self):
        return [e.toDict() for e in self.elements]

    @classmethod
    def fromDict(cls, d):
        elements = [SoftElement.fromDict(e) for e in d]
        return cls(elements)
