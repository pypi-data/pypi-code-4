#!/usr/bin/python2.7
'''Module password makes passwords according to criteria passed to the constructor of the PasswordMaker() class.  This module employs Vtableau, Deck, and Formatter to operate.  It creates 3 Deck()s of randomly ordered alphabets and runs their outputs through a Vtableau() doEnc/doDec combo, combining them at the end and passing them though Formatter()'s format().  The Deck()s are nested decks, meaning that the makeDeck function makes a deck using the alphabet, randomizes it, then puts the deck into a bigger deck of decks, repeat.  This is done to attempt to correct the letter bias in standard Pontifex.  This module was meant to be run from the command line.'''

import sys
import os
import re
import solitaire
import vtableau
import formatter

sys.stdout=os.fdopen(sys.stdout.fileno(), 'w', 0) 

class PasswordMaker(object):
 '''Class PasswordMaker makes passwords and prints them.'''
 def __init__(self, inAlpha, charsPerGroup=8, groupsPerLine=6):
  '''Constructor is to be called with the following options:
  (rawstr)inAlpha - Alphabet name (from solitaire module alphaDict) to derive password(s) from.
  (int)charsPerGroup - [Optional] Number of characters per group (Default 8).
  (int)groupsPerLine - [Optional] Number of groups per line (Default 6).'''
  self.__alpha=inAlpha
  self.__deck=[]
  self.__vtableau=vtableau.Vtableau(self.__alpha,self.__alpha[0],self.__alpha[0])
  self.__formatter=formatter.Formatter(charsPerGroup,groupsPerLine," ")

 def initializePool(self, numDecks=9):
  print 'Preparing pool [ 0.0%',
  for i in xrange(numDecks):
   self.__deck.append(self.makeDeck(self.__alpha))
   prct='%.1f' % (float(i+1)/numDecks*100)
   print str(prct)+'%',
  print ']'

 def makeDeck(self, inAlpha):
  '''Makes a nested deck of decks, each internal deck containing the letters of inAlpha.  There are len(inAlpha) inner decks in the container deck.  Returns the outer deck.'''
  deck=solitaire.Deck()
  for i in xrange(len(inAlpha)):
   deck2=solitaire.Deck()
   deck2.makeDeck(inAlpha,10)
   deck2.lockDeck()
   deck.pushAlpha(deck2)
  deck.pushJoker(1)
  deck.pushJoker(2)
  deck.shuffleVal(35)
  deck.shuffleDeck(35)
  deck.lockDeck()
  return deck

 def getNextChar(self):
  '''Returns the next character in the password making process'''
  worklist=[]
  for i in self.__deck:
   worklist.append([ j for j in i.getObj().getKey(4) ])
  worklist2=[]
  for i in worklist:
   worklist2.append(self.__vtableau.doEnc(self.__vtableau.doDec(self.__vtableau.doEnc(i[0],i[1]),i[2]),i[3]))
  returnStr1=''
  for i in worklist2:
   if returnStr1=='':
    returnStr1=i
    continue
   returnStr1=self.__vtableau.doEnc(returnStr1,i)
  return returnStr1

 def makePassword(self, inLength, inNumPasswords=1 ):
  '''Makes and returns a password string that is to be formatted into groups.'''
  for j in xrange(inNumPasswords):
   returnString=""
   for i in xrange(inLength):
    returnString=returnString+str(self.getNextChar())
   yield returnString

 def printPassword(self, passwordIterator, filename=None):
  '''Takes a long password string and cuts it into groups.'''
  count=0
  file1=None
  if (not filename==None) and type(filename)==type('abc'):
   file1=open(filename,'w')
  for i in passwordIterator:
   count+=1
   str1=self.__formatter.format(i,count)
   print str1
   if file1:
    file1.write(str1+'\n')
  if file1:
   file1.close()

def main():
 if '--help' in sys.argv:
  print "Usage: ./command AlphabetName CharsPerGroup GroupsPerLine Lines PoolSize FileName\n"
  print "Alphabets available:"
  for key in solitaire.alphaDict.keys():
   print key,':',solitaire.alphaDict.get(key)
  sys.exit(0)
 try:
  0<sys.argv[5]
 except:
   print "Incorrect syntax,",
   sys.argv.append('--help')
   main()
 groupLength=int(sys.argv[2])
 numGroups=int(sys.argv[3])
 numPasswords=int(sys.argv[4])
 alphabet=solitaire.alphaDict.get(sys.argv[1])
 if type(alphabet)==type(None):
  print "Incorrect syntax,",
  sys.argv.append('--help') 
  main()
 maker1=PasswordMaker(alphabet,groupLength,numGroups)
 poolsize=0
 try:
  poolsize=int(sys.argv[5])
 except Exception:
  poolsize=9
 maker1.initializePool(poolsize)
 print '\nPool output follows this line:'
 filename=None
 try:
  filename=str(sys.argv[6])
 except Exception:
  filename=None
 maker1.printPassword(maker1.makePassword(groupLength*numGroups,numPasswords),filename)
 sys.exit(0)

if __name__=='__main__':
 try:
  main()
 except KeyboardInterrupt:
  print "\n\n(WW): Execution halted via keyboard interrupt sequence..."
  sys.exit(2)
