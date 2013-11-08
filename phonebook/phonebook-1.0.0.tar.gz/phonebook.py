###################################################################
# This is a supportive program for the Phonebook - Python course
# on codeacademy.com
#
# You can use this utility for creating a file named phonebook.txt
# which can later add, search or display contacts as needed.
#
# Author: bhumish.gajjar@gmail.com
#
###################################################################

import sys

def add():
 while 1:
  print "Press q to exit"
  name = raw_input("Enter name: ")
  if name == 'q':
   sys.exit()
  num = raw_input("Enter number: ")
  f = open('phonebook.txt','a')
  f.write(name + ' : ' + num + '\n')
  f.close()

def search():
 word = raw_input(" Enter name or number to search : \n ")
 f = open('phonebook.txt','r')
 for i in f:
  if word in i:
   print i
 f.close()

def display():
 f = open('phonebook.txt','r')
 print f.read()
 f.close()

choice = input(" 1: Add a Contact \n 2: Search for a Contact \n 3: Display whole phonebook \n ")
if choice == 1:
 add()
elif choice == 2:
 search()
elif choice == 3:
 display()
