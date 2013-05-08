#A game on Rock Paper Scissors Lizard Spock (by Sam Kass and Karen Bryla) which was featured
#in The Big Bang Theory. Here the game-play is against Sheldon (the characeter from 
#The Big Bang Theory). Good Luck playing against him!

#!/usr/bin/python -tt

"""Keywords are used instead of whole Name of elements, so that the user does not have to 
enter the whole name each time.
Rules of the game are displayed at the beginning of the game."""

from random import choice

def game():
 """This is the game function which is the core of this game. Has a dictionary of the keywords
 for Rock Paper Scissors Lizard Spock, the machine randomly chooses one value from a list of
 the 5 elements, and compares it with the user's choice. If any of the two players reaches
 5 points, ie. by winning 5 times, the game will end. One win = One Point."""
 name = raw_input('\n\nHey, whats your name? \n>')
 n=1
 while n == 1:
  print '\n(Ro)ck		(Sc)issor	(Pa)per		(Li)zard	(Sp)ock'
  win = 0
  lose = 0
  while win<3 and lose<3:
   usr = raw_input('\n>') 
   usr = usr.lower()
   if usr=='ro' or usr=='li' or usr=='pa' or usr=='sp' or usr=='sc':
    dic = {'ro':'li','sc':'pa','pa':'ro','li':'sp','sp':'sc','sc':'li','li':'pa','pa':'sp','sp':'ro','ro':'sc'}
    lst = ['ro','pa','sc','li','sp']
    pc = choice(lst)
    if usr==pc:
     print 'Its a Tie!'
    else:
     if dic[usr] == pc:
      print 'You WIN with',getname(usr)
      print 'Sheldon chose',getname(pc)
      win += 1
     else:
      print 'You LOSE with',getname(usr)
      print 'Sheldon chose',getname(pc)
      lose += 1
    print name,'has points 	: '+str(win)
    print 'Sheldon has points 	: '+str(lose)
   else:
    print 'Entered something strange! Better be good at signs next time.'
  if win>lose:
   print '\n\n*****',name, 'is the winner! *****\n\n'
  else:
   print '\n\n>>>>>  Sheldon Wins!!!  <<<<<\n\n'
  ch = raw_input('\nWant to play again?	Press (Y)es to continue, or any other key to exit \n>')
  if ch=='y' or ch=='Y' or ch=='yes' or ch=='YES':
   n=1
  else:
   n=0

def getname(a):
 """This is the getname function which will take one keyword among the 5 as input and
 accordingly display the Name of that keyword."""
 if a=='ro':
  return 'Rock'
 elif a=='li':
  return 'Lizard'
 elif a=='pa':
  return 'Paper'
 elif a=='sp':
  return 'Spock'
 elif a=='sc':
  return 'Scissors'
 else:
  return 'Eh, whattay?'

def main():
 """This is the main function of the game which displays the rules of the game and
 further calls the game function to start the game."""
 print 'Scissors cut Paper'
 print 'Rock crushes Lizard'
 print 'Paper covers Rock'
 print 'Lizard poisons Spock'
 print 'Spock smashes Scissors'
 print 'Scissors decapitate lizard'
 print 'Lizard eats Paper'
 print 'Paper disproves Spock'
 print 'Spock vaporizes Rock'
 print 'Rock breaks Scissors'
 game()

if __name__ == '__main__':
 main()
