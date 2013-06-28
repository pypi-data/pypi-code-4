#!/usr/bin/python2.7 -tt
'''This module exists to provide tableau lookup functionality.  A rough idea of what a tableau is can be summarized by the example below:
#| 0 1 2 3 4 5 6 7 8 9
======================
0| 0 1 2 3 4 5 6 7 8 9
1| 1 2 3 4 5 6 7 8 9 0
2| 2 3 4 5 6 7 8 9 0 1
3| 3 4 5 6 7 8 9 0 1 2
4| 4 5 6 7 8 9 0 1 2 3
5| 5 6 7 8 9 0 1 2 3 4
6| 6 7 8 9 0 1 2 3 4 5
7| 7 8 9 0 1 2 3 4 5 6
8| 8 9 0 1 2 3 4 5 6 7
9| 9 0 1 2 3 4 5 6 7 8

Tableaus such as this one are used as look-up tables in keystream based hand-ciphers (same idea for s-boxes in some newer symmetric algorithms) to convert text between message and cipher text using a key.

This module has two tools for dealing with this task.  They both reside in an object instanced from the class Vtableau().  Its useful methods are returnEnciphered(), returnDeciphered(), doEnc(), and doDec().  Be sure to check the constructor's and mentioned functions' comments for more information.  **Unicode not supported at this time!'''

#Imports:
import sys

class Vtableau(object):
 '''Vtableau, descends from class object.'''
 __inString = r''
 __key = r''
 __alphabet = r''

 def checkInput(self, inStr=__inString, inKey=__key, inAlpha=__alphabet):
  '''Method to check the input for sanity.  Sanity means the input string and key string lengths match and no characters were found in either that are not also in the alphabet.  Throws an exception if they aren't sane.
  (rawstr)inStr - [Optional] Input string.
  (rawstr)inKey - [Optional] Key string.
  (rawstr)inAlpha - [Optional] Alphabet string.'''
  if len(inStr)==len(inKey) and len(inStr)>0 and len(inAlpha)>0:
   for ii in inStr:
    if ii not in inAlpha:
     print '\n(EE): Invalid character not in alphabet found in input:','\''+ii+'\''
     print commandString()
     raise Exception('(EE): Invalid character not in alphabet found in input:','\''+ii+'\'')
   for ii in inKey:
    if ii not in inAlpha:
     print '\n(EE): Invalid character not in alphabet found in inputted key:','\''+ii+'\''
     print commandString()
     raise Exception('(EE): Invalid character not in alphabet found in inputted key:','\''+ii+'\'')
  elif len(inStr)>len(inKey):
   print '\n(EE): Message length is longer than key length'
   print commandString()
   raise Exception('(EE): Message length is longer than key length')
  elif len(inStr)<len(inKey):
   print '\n(EE): Message length is shorter than key length'
   print commandString()
   raise Exception('(EE): Message length is shorter than key length')
  elif len(inStr)<=0 or len(inKey)<=0 or len(inAlpha)<=0:
   print '\n(EE): One or more inputs empty'
   print commandString()
   raise Exception('(EE): One or more inputs empty')
  else:
   print '\n(EE): Unknown Error in string checker'
   print commandString()
   raise Exception('(EE): Unknown Error in string checker, this line should never have been reached')

 def __init__(self, inAlpha, inStr=r'', inKey=r''):
  '''Constructor method must be called as Vtableau(inAlpha, inStr, inKey).
  (rawstr)inAlpha - Raw string for lookup operations.
  (rawstr)inStr - [Optional] Raw plain/cipher message string to work on.
  (rawstr)inKey - [Optional] Raw key string to work with.'''
  self.checkInput(inStr,inKey,inAlpha)
  self.__alphabet=inAlpha
  if len(inKey)==0:
   self.__key=inAlpha[0]
  else:
   self.__key=inKey
  if len(inStr)==0:
   self.__inString=inAlpha[0]
  else:
   self.__inString=inStr

 def returnEnciphered(self, inStr=r'', inKey=r''):
  '''Method returnEnciphered() returns an enciphered string if one was provided at time of constructor call (or some random one if not):
  (rawstr)inStr = [Optional] String to encipher if different from one provided to constructor.
  (rawstr)inKey = [Optional] Key string to use in encipherment.'''
  if len(inStr)==0:
   inStr=self.__inString
  if len(inKey)==0:
   inKey=self.__key
  self.checkInput(inStr, inKey, self.__alphabet)
  outStr=r''
  for ii in range(len(inStr)):
#   print __alphabet[(__alphabet.index(__inString[ii])+__alphabet.index(__key[ii]))%len(__alphabet)]+'.'
   outStr=outStr+self.__alphabet[(self.__alphabet.index(inStr[ii])+self.__alphabet.index(inKey[ii]))%len(self.__alphabet)]
  return outStr

 def returnDeciphered(self, inStr=__inString, inKey=__key):
  '''Method returnDeciphered() returns a deciphered string if one was provided at time of constructor call (or some random one if not):
  (rawstr)inStr = [Optional] String to decipher if different from one provided to constructor.
  (rawstr)inKey = [Optional] Key string to use in decipherment.'''
  if len(inStr)==0:
   inStr=self.__inString
  if len(inKey)==0:
   inKey=self.__key
  self.checkInput(inStr, inKey, self.__alphabet)
  outStr=r''
  for ii in range(len(inStr)):
   outStr=outStr+self.__alphabet[(len(self.__alphabet)+self.__alphabet.index(inStr[ii])-self.__alphabet.index(inKey[ii]))%len(self.__alphabet)]
  return outStr

 def doDec(self, inStr, inKey, inAlpha=__alphabet):
  '''Method doDec() returns a deciphered string.  This is meant to be a by-character process.
  (rawstr)inStr - Input letter to be deciphered.
  (rawstr)inKey - Key letter to use in decipherment.
  (rawstr)inAlpha - [Optional] Alphabet string to use, if different from constructor provided one.'''
  if len(inAlpha)==0:
   inAlpha=self.__alphabet
  self.checkInput(inStr, inKey, inAlpha)
  return self.__alphabet[(len(self.__alphabet)+self.__alphabet.index(inStr)-self.__alphabet.index(inKey))%len(self.__alphabet)]

 def doEnc(self, inStr, inKey, inAlpha=__alphabet):
  '''Method doEnc() returns a enciphered string.  This is meant to be a by-character process.
  (rawstr)inStr - Input letter to be enciphered.
  (rawstr)inKey - Key letter to use in encipherment..
  (rawstr)inAlpha - [Optional] Alphabet string to use, if different from constructor provided one.'''
  if len(inAlpha)==0:
   inAlpha=self.__alphabet
  self.checkInput(inStr, inKey, inAlpha)
  return self.__alphabet[(self.__alphabet.index(inStr)+self.__alphabet.index(inKey))%len(self.__alphabet)]

#Main Function:
def main():
 try:
  inOpts=checkOptions()
 except:
  print '\n(EE): Input options malformed, check execution options'
  print commandString()
  sys.exit(1)
 if '--debug' in sys.argv:
  debugScript()
  sys.exit(0)
 elif '--help' in sys.argv:
  printHelp()
  sys.exit(0)
 elif (0 not in inOpts[:2]) and (inOpts[2]==1 or inOpts[2]==2):
  if inOpts[2]==1:
   print Vtableau(sys.argv[sys.argv.index('-a')+1], sys.argv[sys.argv.index('-e')+1], sys.argv[sys.argv.index('-k')+1]).returnEnciphered()
  elif inOpts[2]==2:
   print Vtableau(sys.argv[sys.argv.index('-a')+1], sys.argv[sys.argv.index('-d')+1], sys.argv[sys.argv.index('-k')+1]).returnDeciphered()
  else:
   print '\n(EE): Options Processing Error, check main() code'
   print commandString()
   sys.exit(1)
 else:
  print '\n(EE): Options provided insufficient or are unhandled'
  print commandString()
  sys.exit(1)
 sys.exit

def checkOptions():
 inOpts=[0,0,0]
 if ('-e' in sys.argv) and ('-d' not in sys.argv) and (sys.argv[sys.argv.index('-e')+1][0] is not '-'):
  inOpts[2]=1
 if ('-d' in sys.argv) and ('-e' not in sys.argv) and (sys.argv[sys.argv.index('-d')+1][0] is not '-'):
  inOpts[2]=2
 if '-a' in sys.argv and (sys.argv[sys.argv.index('-a')+1][0] is not '-'):
  inOpts[1]=1
 if '-k' in sys.argv and (sys.argv[sys.argv.index('-k')+1][0] is not '-'):
  inOpts[0]=1
 return inOpts

def debugScript():
 inString2 = r'testmessage'
 key2 = r'mnopqrstuvx'
 alphabet2 = r'abcdefghijklmnopqrstuvwxyz'

 tableau1 = Vtableau(alphabet2, inString2, key2)

 print '\ninput:',inString2
 print 'key:',key2
 print 'alphabet:',alphabet2
 tempString=tableau1.returnEnciphered()[:]
 print 'output:',tempString

 tableau2 = Vtableau(alphabet2, tempString, key2)

 print '\ninput:',tempString
 print 'key:',key2
 print 'alphabet:',alphabet2
 tempString2=tableau2.returnDeciphered()[:]
 print 'output:',tempString2

 print commandString()

 sys.exit(0)

def printHelp():
 print 'Command line options:'
 print ' -e <String> | Encipher String'
 print ' -d <String> | Decipher String'
 print ' -a <String> | Cipher Alphabet'
 print ' -k <String> | Cipher Key'
 print '\nThis Python Script provides OTP tableau functionality'
 print 'via the command line or by importing this module and'
 print 'creating an instance of Vtableau(alphabet, input, key),'
 print 'then calling .returnEnciphered() or .returnDeciphered()'

def commandString():
 outStr='\nAs executed: '
 for ii in sys.argv:
  outStr=outStr+str(ii)+' '
 return outStr

#Boilerplate:
if __name__=='__main__':
 main()
