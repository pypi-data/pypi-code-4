import os
import json
import string
import random
from subprocess import call

class TicTacToe:
    def id_generator(self, chars=string.ascii_lowercase + string.digits):
      return ''.join(random.choice(chars) for x in range(10))

    def move_to_server(self,location):
      call("sudo cp /etc/uttt/game_data %s" % (location), shell=True)

    def new(self,player1,player2):
      default_board_layout = {}
      for i in range(11, 100):
        default_board_layout[i] = None
      if os.stat("game_data")[6]==0:
        beginning_game_data = { "games" : { player1+','+player2+'1' : { 'id':self.id_generator(), 'player1':player1, 'player2':player2, 'board':default_board_layout, 'current': player1, 'active_square': None, 'move': 0 }}}
        game_data = json.dumps(beginning_game_data)
        raw_game_data = open('/etc/uttt/game_data', 'w')
        raw_game_data.write(game_data+'\n')
        raw_game_data.close()
        return "Game hosted at http://192.168.1.68/uttt.html?game=%s. First move goes to %s (x)" % (player1+','+player2+'1',player1)
      else:
        return "Game already in progress"
    
    def delete(self):
      open('/etc/uttt/game_data', 'w').close()
      return "Deleted current game"

    def info(self):
      raw_game_data = open('/etc/uttt/game_data')
      game_data = json.load(raw_game_data)
      current_game = game_data['games'][list(game_data['games'].keys())[0]]
      info = "Player 1 is %s, Player 2 is %s, the current player is %s, and the active square is %s. Link is http://192.168.1.68/uttt.html?game=%s" % (current_game['player1'],current_game['player2'],current_game['current'],current_game['active_square'],current_game['player1']+','+current_game['player2']+'1')
      return info

    def move(self,speaker,move):
      raw_game_data = open('/etc/uttt/game_data')
      game_data = json.load(raw_game_data)
      current_game = game_data['games'][list(game_data['games'].keys())[0]]
      if speaker == current_game['current']:
        if current_game['board'][move] == None:
          if not current_game['active_square'] == None:
            if int(move[0]) != int(current_game['active_square']):
              return "You need to move in the proper square"
          current_game['board'][move] = speaker
          current_game['move'] = current_game['move'] + 1
          current_game['active_square'] = str(int(move) % 10)
          if speaker == current_game['player1']:
            other_player = current_game['player2']
          elif speaker == current_game['player2']:
            other_player = current_game['player1']
          current_game['current'] = other_player
          game_data_for_writing = json.dumps(game_data)
          raw_game_data = open('/etc/uttt/game_data', 'w')
          raw_game_data.write(game_data_for_writing+'\n')
          return "successful"
        elif move == '55' and current_game['move'] == 0:
          return "You can't make your first move here!"
        else:
          return "You can't make a move here"
      else:
        return "It's not your move yet!"
