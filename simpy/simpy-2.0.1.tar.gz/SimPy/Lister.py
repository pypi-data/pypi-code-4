#!/usr / bin / env python
# $Revision: 163 $ $Date: 2008-12-15 12:47:44 +0100 (Mo, 15 Dez 2008) $ kgm
"""Lister 2.0
Pretty-printer for SimPy class objects
"""
__version__ = '2.0 $Revision: 163 $ $Date: 2008-12-15 12:47:44 +0100 (Mo, 15 Dez 2008) $'

class Lister(object):
    indent = 0
    def __str__(self):
        Lister.indent += 1
        result = (' < Instance of %s, id %s:\n%s' % (self.__class__.__name__,
                                               id(self),self.attrnames())) + '\t' * (Lister.indent - 1) + ' > '
        Lister.indent -= 1
        return result
    
    def attrnames(self):
        result = ''
        for attr in self.__dict__.keys():
            if attr[:2] == '__': #builtin
                pass
            elif attr[0] == '_': #private
                pass
            else:
                result = result + '\t' * Lister.indent + '.%s=%s\n' % (attr, self.__dict__[attr])
        return result
    def __repr__(self):
        Lister.indent += 1
        result = (' < Instance of %s, id %s:\n%s' % (self.__class__.__name__,
                                               id(self),self.attrnames())) + '\t' * (Lister.indent - 1) + ' > '
        Lister.indent -= 1
        return result

