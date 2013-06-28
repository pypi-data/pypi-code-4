#!/usr/bin/python2.7
'''Module formatter does text formatting.  It breaks a string up into a string of many lines, separated into groups and separated with a specified character.  For example, it can break THISISACOOLSTRING into THISI SACOO LSTRI NG if constructed with a groupsize of 5 and a separator of ' '.  The tool that does this is a class called Formatter, which descends from object.'''

import pyrand
import sys
import os
import re

class Formatter(object):
 '''Class Formatter'''

 def __init__(self, inGroupSize=5, inLineSize=5, inSeparator=r' '):
  '''Constructor can be called with the following options:
  (int)inGroupSize - [Optional] Number of characters in a group.
  (int)inLineSize - [Optional] Number of groups on a line.
  (int)inSeparator - [Optional] String used to separate groups.'''
  self.__charsPerGroup=int(inGroupSize)
  self.__groupsPerLine=int(inLineSize)-1
  self.__separatorChar=str(inSeparator)

 def format(self, inString, count=-1):
  '''Takes a string and returns a formatted string, depending on constructor options'''
  chars=0
  groups=0
  lines=0
  if count>-1:
   lines=count-1
  returnString=""
  for char in str(inString):
   if chars==self.__charsPerGroup and not (groups==self.__groupsPerLine):
    chars=0
    groups+=1
    returnString=returnString+self.__separatorChar
   if chars==self.__charsPerGroup and groups==self.__groupsPerLine:
    chars=0
    groups=0
    lines+=1
    returnString=returnString+"\n"
   if chars==0 and groups==0:
    tabstr="\t"
    if lines < 10000:
     tabstr+=tabstr
    returnString=returnString+str(lines+1)+"):"+tabstr
   returnString=returnString+char
   chars+=1
  return returnString

def main():
 iformat=Formatter(sys.argv[1],sys.argv[2],sys.argv[3])
 print iformat.format(sys.argv[4])

if __name__ == '__main__':
 try:
  main()
 except KeyboardInterrupt:
  print '\n Program execution halted prematurely via keyboard (^C)'
