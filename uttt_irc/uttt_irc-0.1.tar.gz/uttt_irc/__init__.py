#! /usr/bin/python

import sys
import subprocess
import os.path
import operator
import json
import datetime
import time
from uttt import TicTacToe

def log(message):
  f = open('log', 'a')
  f.write('%s: %s\n' % (str(datetime.datetime.now()),str(message)))

def get_response(speaker,query):
  try:
    if 'hey' in query:
      return "Hey"
    elif 'ready' in query or 'ready?' in query:
      return "Kinda. You can play a game, but you'll have to draw out the board yourself."
    elif 'help' in query:
      return "I am an irc bot designed to handle ultimate tic tac toe games. Commands to me start with # or <myname>:. My list of commands are hey,ready,help,new,delete,move,time."
    elif str(query[0]) == 'new':
      if len(query) == 3:
        game = TicTacToe()
        return game.new(query[1],query[2])
      else:
        return "Wrong number of players"
    elif str(query[0]) == 'delete':
      game = TicTacToe()
      return game.delete()
    elif str(query[0]) == 'info':
      game = TicTacToe()
      return game.info()
    elif str(query[0]) == 'move' and len(query) == 2:
      game = TicTacToe()
      return game.move(speaker,query[1])
    elif 'time' in query:
      return datetime.datetime.now()
    else:
      return "Unknown query"
  except:
    return sys.exc_info()[1]

def parse_query(query):
  query = query.replace(',','').split()
  speaker = query[0]
  query.pop(0)
  response = get_response(speaker,query)
  game = TicTacToe()
  game.move_to_server("/srv/http/www/")
  return response
