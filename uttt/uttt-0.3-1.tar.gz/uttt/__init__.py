import os
import json
import string
import random
from subprocess import call

class TicTacToe:
    def __id_generator(self, chars=string.ascii_lowercase + string.digits):
      return ''.join(random.choice(chars) for x in range(10))

    def __default_board(self,player1,player2):
      default_board_layout = {}
      for i in range(11, 100):
        default_board_layout[i] = None
      board = { "games" : { player1+','+player2+'1' : { 'id':self.__id_generator(), 'player1':player1, 'player2':player2, 'board':default_board_layout, 'current': player1, 'active_square': None, 'move': 0, 'last_move': None }}}
      return board

    def __get_other_player(self,speaker,player1,player2):
      if speaker == player1:
        other_player = player2
      elif speaker == player2:
        other_player = player1
      return other_player

    def move_to_server(self,location):
      call("sudo cp /etc/uttt/game_data %s" % (location), shell=True)

    def new(self,player1,player2):
      if os.stat("/etc/uttt/game_data")[6]==0:
        game_data = json.dumps(self.__default_board(player1,player2))
        with open('/etc/uttt/game_data', 'w') as file:
          file.write(game_data+'\n')
        return "Game hosted at http://192.168.1.68/uttt.html?game=%s. First move goes to %s (x)" % (player1+','+player2+'1',player1)
      else:
        return "Game already in progress"
    
    def delete(self):
      open('/etc/uttt/game_data', 'w').close()
      return "Deleted current game"

    def info(self):
      with open('/etc/uttt/game_data') as raw_game_data:
        game_data = json.load(raw_game_data)
      current_game = game_data['games'][list(game_data['games'].keys())[0]]
      return "Player 1 is %s, Player 2 is %s, the current player is %s, and the active square is %s. Link is http://192.168.1.68/uttt.html?game=%s" % (current_game['player1'],current_game['player2'],current_game['current'],current_game['active_square'],current_game['player1']+','+current_game['player2']+'1')

    def move(self,speaker,move):
      with open('/etc/uttt/game_data') as file:
        game_data = json.load(file)
      current_game = game_data['games'][list(game_data['games'].keys())[0]]
      if speaker != current_game['current']:
        return "It's not your move yet!"
      if current_game['board'][move] != None:
        return "You can't make a move here!"
      if current_game['move'] == 0 and move == '55':
        return "You can't make your first move here!"
      if str(move) != str(current_game['active_square']) and current_game['active_square'] != None:
        return "You need to move in the proper square"
      current_game['board'][move] = speaker
      current_game['move'] = current_game['move'] + 1
      current_game['active_square'] = str(int(move) % 10)
      current_game['current'] = self.__get_other_player(speaker,current_game['player1'],current_game['player2'])
      current_game['last_move'] = [ speaker, move ]
      with open('/etc/uttt/game_data', 'w') as file:
        file.write(json.dumps(game_data)+'\n')
      return "%s: %s moved to %s, your turn" % (self.__get_other_player(speaker,current_game['player1'],current_game['player2']),speaker,move)

    def undo(self,speaker):
      with open('/etc/uttt/game_data') as file:
        game_data = json.load(file)
      current_game = game_data['games'][list(game_data['games'].keys())[0]]
      just_played = self.__get_other_player(current_game['current'],current_game['player1'],current_game['player2'])
      if speaker == just_played and current_game['last_move'][0] == speaker:
        move = current_game['last_move'][1]
        current_game['board'][move] = None
        current_game['move'] = current_game['move'] - 1
        if current_game['move'] == 0:
          current_game['active_square'] = None
        else:
          current_game['active_square'] = str(move)[0]
        current_game['current'] = speaker
        current_game['last_move'] = None
        with open('/etc/uttt/game_data', 'w') as file:
          file.write(json.dumps(game_data)+'\n')
        return "Undid last move"
      return "Did not undo last move"


