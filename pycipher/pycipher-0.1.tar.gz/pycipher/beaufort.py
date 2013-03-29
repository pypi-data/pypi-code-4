'''
implements beaufort cipher
Author: James Lyons
Created: 2012-04-28
'''
from .base import Cipher

####################################################################################
class Beaufort(Cipher):
    def __init__(self,key='a'):
        self.key = [k.upper() for k in key]
        
    def encipher(self,string):
        string = self.remove_punctuation(string)
        ret = ''
        for (i,c) in enumerate(string):
            i = i%len(self.key)
            ret += self.i2a(self.a2i(self.key[i])-self.a2i(c))
        return ret    

    def decipher(self,string):
        return self.encipher(string)    

if __name__ == '__main__': 
    print 'use "import pycipher" to access functions'