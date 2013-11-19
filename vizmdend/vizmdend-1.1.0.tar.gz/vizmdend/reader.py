'''
Created on Nov 1, 2013

@author: jbq
'''

from logger import vlog, tr
from parser import Parser

class Reader(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self._parser = None
        self._version = '1.0.0'
    
    def parse(self, mfile):
        self._parser = Parser(mfile)
        self._parser.parse()

    def getFields(self):
        return self._parser.getFields()

    def getVersion(self):
        return self._version
    
    def plot(self, ylabel, xlabel=None):
        import matplotlib.pyplot as plt
        yvalues=self._parser.getValues(ylabel)
        xvalues=self._parser.getValues(xlabel) if xlabel else None
        if xvalues:
            plt.plot(xvalues, yvalues)
            plt.xlabel(xlabel)
        else:
            plt.plot(yvalues)
        plt.ylabel(ylabel)
        plt.show()
    
    
    version = property(fget=getVersion)
