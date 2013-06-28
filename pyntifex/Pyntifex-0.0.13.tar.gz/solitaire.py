#!/usr/bin/python2.7
'''Module solitaire is an implementation of Bruce Schneier's Pontifex playing card-based keystream algorithm.  It does this with a class called Deck().  This Deck() class takes objects as its contents, moves them around according to assignment and order, and spits them back when requested.  This implementation is more flexible than others on the net, namely it can be any size and will take any object (including other decks!).  This module also knows how to make decks out of alphabets, and the class provides methods for pushing objects onto a deck.  There is a lockDeck() method which prevents it from receiving any more 'cards', which would make no sense if you are calling advanceDeck().'''

import random
#import pyrand
import sys
import os
import re

#class declaration -
class Deck(object):
 '''Class Deck() is a pontifex deck which does an OK job reproducing the Pontifex keystream process outlined by Bruce Schneier.'''

 #constructor
 def __init__(self):
  '''Constructor takes no arguments'''
  self.__deck=[]
  self.__numCards=0
  self.__lockState=0
  self.__debug=0
  self.__pushLockState=0
  self.__randomGenerator=random.SystemRandom()

 def printDebug(self, inString):
  if self.__debug==1:
   print inString

 def pushCard(self, inTuple):
  '''Method pushCard() takes a Tuple of size 2, being (card value, card contents).  Cannot be used with a deck pushAlpha() or pushJoker() has been used on.'''
  if not self.__lockState and self.__pushLockState!=2:
   self.__pushLockState=1
   self.__numCards+=1
   self.__deck.append(inTuple)
  else:
   raise Exception('(EE): Deck feature locked in current state, check programming!')

 def pushAlpha(self, inObj):
  '''Method pushAlpha() takes an object and puts it on the deck.  Cannot be used with a deck pushCard() has been used on.'''
  if not self.__lockState and self.__pushLockState!=1:
   self.__pushLockState=2
   self.__numCards+=1
   self.__deck.append((self.__numCards,inObj))
  else:
   raise Exception('(EE): Deck feature locked in current state, check programming!')

 def pushJoker(self, inJoker):
  '''Method pushJoker() takes a number, 1 or 2, and puts that valued Joker on the deck.  Cannot be used with a deck pushCard() has been used on.'''
  if not self.__lockState and self.__pushLockState!=1:
   self.__pushLockState=2
   if inJoker<=2 and inJoker>=1:
    self.__deck.append((0-inJoker,None))
   else:
    raise Exception('(EE): Joker count cannot exceed 2 nor be less than 0')
  else:
   raise Exception('(EE): Deck feature locked in current state, check programming!')

 def shuffleVal(self, inCount):
  '''Method shuffleVal() takes the deck and shuffles the values relative to contents.'''
  if not self.__lockState:
   for j in range(inCount):
    deck2=[]
    tmp=None
    offset=-1
    for i in range(len(self.__deck)):
     tmp=(i,self.__deck.pop(self.__randomGenerator.getrandbits(256)%len(self.__deck)))
     if tmp[1][1]==None:
      deck2.append((tmp[1][0],None))
      offset+=1
     else:
      deck2.append((tmp[0]-offset,tmp[1][1]))
    self.__deck=deck2
    self.shuffleDeck(1)
  else:
   raise Exception('(EE): Deck locked before accessing protected feature')

 def shuffleDeck(self, inCount):
  '''Method shuffleDeck() takes the deck and shuffles the positions of each card in he deck.'''
  if not self.__lockState:
   deck2=[]
   for ij in range(inCount):
    for i in range(len(self.__deck)):
     deck2.append(self.__deck.pop(self.__randomGenerator.getrandbits(256)%len(self.__deck)))
    self.__deck=deck2
  else:
   raise Exception('(EE): Deck locked before accessing protected feature')

 def popState(self):
  '''Method popState() is an iterator that takes no arguments, and pops each card off the deck (no card removal).'''
  for i in range(len(self.__deck)):
   yield (i+1,self.__deck[i][0],self.__deck[i][1])

 def lockDeck(self):
  '''Method lockDeck() locks the deck and makes it advanceable, and prevents new cards from being put on.'''
  try:
   if self.__deck.index((-1,None))+1 and self.__deck.index((-2,None))+1:
    self.__lockState=1
   else:
    raise Exception('(EE): Unknown Joker error')
  except:
   raise Exception('(EE): Lacking one or more Jokers at lock')

 def makeDeck(self, inAlphaString, inShuffleCount):
  '''Method makeDeck() is an internal deck maker method which puts each letter in an alphabet into a card and shuffles the whole deck.  Works only on an empty deck.  Returns nothing.  Arguments are:
  (rawstr)inAlphaString - Alphabet string to use in making the deck.
  (int)inShuffleCount - Number of times to shuffle the deck (the higher, the more secure).'''
  if not self.__lockState:
   if len(self.__deck)==0:
    for i in inAlphaString:
     self.pushAlpha(i)
    self.pushJoker(1)
    self.pushJoker(2)
    self.shuffleDeck(inShuffleCount)
   else:
    raise Exception('(EE): Deck not empty before accessing makeDeck()')
  else:
   raise Exception('(EE): Deck locked before accessing protected feature')

 def advanceState(self):
  '''Method advanceState() advances the state of the Deck() according to the Pontifex algorithm.  There is no reversing this stepping in state.'''
  if self.__lockState:
   deck2=[]
   smJokerLoc=self.__deck.index((-1,None))
   bgJokerLoc=self.__deck.index((-2,None))
   if smJokerLoc==len(self.__deck)-1:
    deck2=self.__deck[0:1]+self.__deck[smJokerLoc:smJokerLoc+1]+self.__deck[1:smJokerLoc]
   else:
    deck2=self.__deck[:smJokerLoc]+self.__deck[smJokerLoc+1:smJokerLoc+2]+self.__deck[smJokerLoc:smJokerLoc+1]+self.__deck[smJokerLoc+2:]
   self.__deck=deck2
   deck2=[]
   smJokerLoc=self.__deck.index((-1,None))
   bgJokerLoc=self.__deck.index((-2,None))
   if bgJokerLoc==len(self.__deck)-1:
    deck2=self.__deck[0:2]+self.__deck[bgJokerLoc:bgJokerLoc+1]+self.__deck[2:bgJokerLoc]
   elif bgJokerLoc==len(self.__deck)-2:
    deck2=self.__deck[0:1]+self.__deck[bgJokerLoc:bgJokerLoc+1]+self.__deck[1:bgJokerLoc]+self.__deck[bgJokerLoc+1:bgJokerLoc+2]
   else:
    deck2=self.__deck[:bgJokerLoc]+self.__deck[bgJokerLoc+1:bgJokerLoc+3]+self.__deck[bgJokerLoc:bgJokerLoc+1]+self.__deck[bgJokerLoc+3:]
   self.__deck=deck2
   deck2=[]
   smJokerLoc=self.__deck.index((-1,None))
   bgJokerLoc=self.__deck.index((-2,None))
   if smJokerLoc<bgJokerLoc:
    deck2=self.__deck[bgJokerLoc+1:]+self.__deck[smJokerLoc:smJokerLoc+1]+self.__deck[smJokerLoc+1:bgJokerLoc]+self.__deck[bgJokerLoc:bgJokerLoc+1]+self.__deck[:smJokerLoc]
    self.__deck=deck2
   else:
    tmp=smJokerLoc
    smJokerLoc=bgJokerLoc
    bgJokerLoc=tmp
    deck2=self.__deck[bgJokerLoc+1:]+self.__deck[smJokerLoc:smJokerLoc+1]+self.__deck[smJokerLoc+1:bgJokerLoc]+self.__deck[bgJokerLoc:bgJokerLoc+1]+self.__deck[:smJokerLoc]
    self.__deck=deck2
   deck2=[]
   smJokerLoc=self.__deck.index((-1,None))
   bgJokerLoc=self.__deck.index((-2,None))
   if self.__deck[len(self.__deck)-1][0]<0:
    deck2.append(self.__deck[:])
   else:
    deck2.append(self.__deck[self.__deck[len(self.__deck)-1][0]:-1]+self.__deck[:self.__deck[len(self.__deck)-1][0]]+self.__deck[-1:])
   self.__deck=deck2[0]
  else:
   raise Exception('(EE): Deck not locked before accessing protected feature')

 def getChars(self, inSize):
  '''Method getChars() is an iterator which takes an integer argument and returns the number of next characters up to the integer provided in count.  Yields an object'''
  i=0
  while i<inSize:
   self.advanceState()
   if self.__deck[0][0]<0:
    yieldChar=self.__deck[-2][1]
   else:
    yieldChar=self.__deck[self.__deck[0][0]][1]
   if type(yieldChar)!=type(None):
    i+=1
    yield yieldChar

 def getKey(self, inSize):
  '''Method getKey() takes an integer argument and returns a string of equal size to the magnatude of the provided integer.'''
  outString=''
  for i in self.getChars(inSize):
   outString=outString+i
  return outString

 def getObj(self):
  '''Method getObj() returns the next object.  Advances state automatically then gets the object.'''
  while 1==1:
   self.advanceState()
   if self.__deck[0][0]<0:
    returnChar=self.__deck[-2][1]
   else:
    returnChar=self.__deck[self.__deck[0][0]][1]
   if type(returnChar)!=type(None):
    return returnChar

alphaDict={
'complex':'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789\'\",.<>`~[]{}/=\?+|;:-_!@#$%^&*()',
'dvkextended':'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789\'\",.<>/=?+;:-_!@#$%^&*()',
'extended':'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789\'\",.<>[]{}/?;:!@#$%^&*()',
'standard':'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
'lowercase':'abcdefghijklmnopqrstuvwxyz',
'lowercasenums':'abcdefghijklmnopqrstuvwxyz0123456789',
'uppercase':'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
'uppercasenums':'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
'numbers':'0123456789',
'solitaire':'ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZ',
'stdcrypt':'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-',
'bothcase':'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
}
'''This is a dictionary of common alphabets.  This dictionary can be referenced by functions/methods outside the solitaire module.'''

def printString(inDeck,inLength):
 '''Function printString() takes two arguments, a Deck and an integer.  This function prints a number of characters to screen in magnatude to the size of the integer provided, from the provided Deck.'''
 for i in inDeck.getChars(inLength):
  print i,
  sys.stdout.write('')

def loadState(inDeck, inFilename):
 '''Function loadState takes two arguments, a Deck and a filename string.  Create the deck first then pass it to this function with a path to a saved deck state.'''
 file=open(inFilename,'rU')
 if 'PYNTIFEX_DECK\n' not in file:
  raise Exception('(EE): Attempted to load deck file lacking magic string')
 for i in file:
  try:
   imatch=re.search('\((\d+),\s(-?\d+),\s\'(.+)\'\)', i)
   if imatch.groups()[2]=='None':
    inDeck.pushCard((int(imatch.groups()[1]),None))
   else:
    inDeck.pushCard((int(imatch.groups()[1]),imatch.groups()[2]))
  except:
   if i!='PYNTIFEX_DECK':
    raise Exception('(EE): The following line cannot be processed: '+str(i+1)+' in file: '+inFilename)
 file.close()
 inDeck.lockDeck()

def saveState(inDeck, inFilename):
 '''Function saveState() takes two arguments, a Deck and a filename string.  Take a deck that has been created/used then pass it to this function with a path to save the deck state into a file at that path.'''
 outFile=open(inFilename,'w')
 outFile.truncate(0)
 outFile.write('PYNTIFEX_DECK\n')
 for i in inDeck.popState():
  if i[1]<0:
   i=(i[0],i[1],'None')
  outFile.write(str(i)+'\n')
 outFile.flush()
 outFile.close()

def makeDeckFile():
 '''Called by method's main(), use at your own risk!'''
 alphabet=''
 outFile=''
 shuffleCount=100
 mixValues=0
 deck=Deck()
 try:
  alphabet=sys.argv[sys.argv.index('--alphastr')+1]
 except ValueError:
  try:
   alphabet=sys.argv[sys.argv.index('--alpha')+1]
   alphabet=alphaDict.get(alphabet)
   if alphabet==None:
    print '\nBad selection on --alpha, please refer to --help'
    sys.exit(1)
  except ValueError:
   print '\nBad options, should be: <command> make [--alpha <Name> | --alphastr <String>] --outfile <PathToOutputFile> [--shuffle <Integer>] [--mix-values]'
   sys.exit(1)
 try:
  outFile=sys.argv[sys.argv.index('--outfile')+1]
  try:
   shuffleCount=int(sys.argv[sys.argv.index('--shuffle')+1])
   if shuffleCount<10:
    print '\nFor security reasons, please make --shuffle 10 or larger'
    sys.exit(1)
  except ValueError:
   pass
  if '--mix-values' in sys.argv:
   mixValues=1
 except ValueError:
  print '\nBad options, should be: <command> make [--alpha <Name> | --alphastr <String>] --outfile <PathToOutputFile> [--shuffle <Integer>] [--mix-values]'
  sys.exit(1)
 deck.makeDeck(alphabet, shuffleCount)
 if mixValues==1:
  deck.shuffleVal(shuffleCount)
 deck.lockDeck()
 try:
  saveState(deck,outFile)
 except:
  print '\nError writing file to path:'
  print outFile
  sys.exit(1)
 print '\nDeck outputted successfully to:'
 print outFile
 sys.exit(0)

def printKeyString():
 '''Called by method's main(), use at your own risk!'''
 inFile=''
 outFile=''
 keyString=''
 stringLength=0
 deck=Deck()
 try:
  inFile=sys.argv[sys.argv.index('--infile')+1]
  stringLength=int(sys.argv[sys.argv.index('--length')+1])
  try:
   outFile=sys.argv[sys.argv.index('--outfile')+1]
  except ValueError:
   pass
 except:
  print '\nBad options, should be: <command> key --infile <PathToFile> --length <Integer> [--outfile <PathToFile>] [--quiet]'
  sys.exit(1)
 try:
  loadState(deck,inFile)
 except:
  print '\nError opening deck file:'
  print inFile
  sys.exit(1)
 deck.lockDeck()
 printString(deck,stringLength)
 if outFile=='':
  try:
   saveState(deck,inFile)
  except:
   if '--quiet' not in sys.argv:
    print ''
    print '\nError saving deck file:'
    print inFile
   sys.exit(1)
 else:
  try:
   saveState(deck,outFile)
  except:
   if '--quiet' not in sys.argv:
    print '\nError saving deck file:'
    print outFile
   sys.exit(1)
 sys.exit(0)

def printPassString():
 '''Called by method's main(), use at your own risk!'''
 shuffleCount=100
 alphabet=''
 stringLength=0
 try:
  stringLength=int(sys.argv[sys.argv.index('--length')+1])
 except ValueError:
  '\nBad options, should be: <command> pass [--alpha <Name> | --alphastr <String>] --length <Integer> [--shuffle <Integer>]'
 deck=Deck()
 try:
  alphabet=sys.argv[sys.argv.index('--alphastr')+1]
 except ValueError:
  try:
   alphabet=sys.argv[sys.argv.index('--alpha')+1]
   alphabet=alphaDict.get(alphabet)
   if alphabet==None:
    print '\nBad selection on --alpha, please refer to --help'
    sys.exit(1)
  except ValueError:
   print '\nBad options, should be: <command> pass [--alpha <Name> | --alphastr <String>] --length <Integer> [--shuffle <Integer>]'
   sys.exit(1)
 try:
  shuffleCount=int(sys.argv[sys.argv.index('--shuffle')+1])
  if shuffleCount<100:
   print '\nFor security reasons, please make --shuffle 100 or larger'
   sys.exit(1)
 except ValueError:
  pass
 deck.makeDeck(alphabet*3, shuffleCount)
 deck.shuffleVal(shuffleCount)
 deck.lockDeck()
 printString(deck,stringLength)
 sys.exit(0) 

def printAdvPassString():
 '''Called by method's main(), use at your own risk!'''
 if '--quiet' not in sys.argv:
  print '\nUnofficial function selected.  Advpass can take a'
  print ' really long time to output.  Output latency is pro-'
  print ' portional to (2x --count) x (--shuffle) x (--alpha len)'
  print ' length having little impact...'
 shuffleCount=100
 alphabet=''
 stringLength=0
 deckCount=1
 try:
  deckCount=int(sys.argv[sys.argv.index('--count')+1])
  stringLength=int(sys.argv[sys.argv.index('--length')+1])
 except ValueError:
  print '\nBad options, should be: <command> advpass [--alpha <Name> | --alphastr <String>] --length <Integer> --count <Integer> [--shuffle <Integer>]'
  sys.exit(1)
 deck=Deck()
 try:
  alphabet=sys.argv[sys.argv.index('--alphastr')+1]
 except ValueError:
  try:
   alphabet=sys.argv[sys.argv.index('--alpha')+1]
   alphabet=alphaDict.get(alphabet)
   if alphabet==None:
    print '\nBad selection on --alpha, please refer to --help'
    sys.exit(1)
  except ValueError:
   print '\nBad options, should be: <command> pass [--alpha <Name> | --alphastr <String>] --length <Integer> [--shuffle <Integer>]'
   sys.exit(1)
 try:
  shuffleCount=int(sys.argv[sys.argv.index('--shuffle')+1])
  if shuffleCount<10:
   print '\nFor security reasons, please make --shuffle 10 or larger'
   sys.exit(1)
 except ValueError:
  pass
 if '--quiet' not in sys.argv:
  print '\n Initializing Meta-deck...\n  ',
 for i in range(deckCount):
  deck2=Deck()
  deck2.makeDeck(alphabet,shuffleCount)
  deck2.lockDeck()
  deck.pushAlpha(deck2)
 deck.pushJoker(1)
 deck.pushJoker(2)
 deck.shuffleDeck(shuffleCount)
 deck.shuffleVal(shuffleCount)
 deck.lockDeck()
 if '--quiet' not in sys.argv:
  print '\n Compiling password string...\n'
  print ''
 for j in deck.getChars(stringLength):
  printString(j,1)
  sys.stdout.write('')
 print ''
 sys.exit(0) 

#main function -
def main():
 if '--help' in sys.argv or len(sys.argv)==1:
  print '\nOptions:'
  print ' <command> func --args args'
  print '\n Function \'make\':'
  print '  Makes a Pontifex deck.  Options are:'
  print '  --alpha String    | Pre-made alphabet to use (below)'
  print '  --alphastr String | User-provided alphabet (in single quotes, mutually exclusive with --alpha)'
  print '  --outfile Path    | Path to output deck file'
  print '  --shuffle Integer | [Optional] Shuffle count (100 Default)'
  print '  --mix-values      | [Optional] Mixes up alphabet value assignments'
  print '\n Function \'key\':'
  print '  Outputs a key string for use with a tableau.  Options are:'
  print '  --length Integer  | Output length'
  print '  --infile Path     | Deck file to use'
  print '  --outfile Path    | [Optional] Deck output path (Don\'t write endstate to infile)'
  print '                    |   (not recommended for sensitive uses)'
  print '  --quiet           | [Optional] Suppress soft errors'
  print '\n Function \'pass\':'
  print '  Outputs a complex password based on these options:'
  print '  --length Integer  | Password length'
  print '  --alpha String    | Pre-made alphabet string name (below)'
  print '  --alphastr String | User-provided alphabet (in single quotes, mutually exclusive with --alpha)'
  print '  --shuffle Integer | [Optional] Shuffle count (100 Default)'
  print '\n Function \'advpass\':'
  print '  Outputs a complex password, like pass, but with this additional option:'
  print '  --count           | Number of decks in \'meta\' deck.'
  print '  --quiet           | Suppress superfluous output.'
  print '\n  (advpass is more of a test than a function, therefore it\'s unsupported)'
  print '\n Available pre-made alphabets:'
  for i in alphaDict.keys():
   print '  '+i+': '+alphaDict.get(i)
 elif sys.argv[1]=='make':
  makeDeckFile()
 elif sys.argv[1]=='key':
  printKeyString()
 elif sys.argv[1]=='pass':
  printPassString()
 elif sys.argv[1]=='advpass':
  printAdvPassString()
 else:
  print '\nNo useable Options.  --help for info.'
  sys.exit(1)

#launch boilerplate -
if __name__ == '__main__':
 try:
  main()
 except KeyboardInterrupt:
  print '\n Program execution halted prematurely via keyboard (^C)'
