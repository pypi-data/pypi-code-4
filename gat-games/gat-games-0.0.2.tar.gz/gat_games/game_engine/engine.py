# coding: utf-8
import logging
import random
import sys
import six

import gat_games.game_engine.gat_json as json


class EndGame(Exception): pass
class AlgorithmError(Exception): pass
class AlgorithmInitializationError(AlgorithmError): pass
class AlgorithmTimeoutError(AlgorithmError): pass
class InvalidCommandError(AlgorithmError): pass


class GATLogger(object):
    FORMAT = '%(message)s'
    logging.basicConfig(format=FORMAT)
    logger = logging.getLogger('GAT')
    logger.setLevel(logging.INFO)
    verbose = False

    @classmethod
    def set_level(cls, log_level):
        cls.logger.setLevel(log_level)

    @classmethod
    def set_verbose(cls):
        cls.verbose = True

    @classmethod
    def get_log_level(cls):
        return cls.logger.getEffectiveLevel()

    @classmethod
    def is_verbose(cls):
        return cls.verbose or cls.get_log_level() == logging.DEBUG

    @classmethod
    def log(cls, message, prefix='', level=logging.INFO):
        # print(message)
        cls.logger.log(level, '[GAT][%s] %s' % (prefix, message))
        if cls.get_log_level() == logging.DEBUG:
            sys.stdout.flush()

    @classmethod
    def debug(cls, message, prefix=''):
        cls.log(message, prefix=prefix, level=logging.DEBUG)

    @classmethod
    def info(cls, message, prefix=''):
        cls.log(message, prefix=prefix, level=logging.INFO)

    @classmethod
    def error(cls, message, prefix=''):
        cls.log(message, prefix=prefix, level=logging.ERROR)

    @classmethod
    def exception(cls, e):
        cls.logger.exception(e)


class Player(object):
    '''
    Override:
    def play(self, context, **kwargs): pass
    def start(self): pass
    def stop(self): pass
    '''
    def __init__(self, name=None):
        self.name = name if name else '%s-%s' % (self.__class__.__name__, id(self))
        self.game = None

    def __str__(self):
        return self.name

    def __getstate__(self):
        odict = self.__dict__.copy()
        odict.pop('game', None)
        return odict

    def log(self, message, level=logging.INFO):
        GATLogger.log(message, prefix=self.name, level=level)

    def play(self, context, **kwargs): pass
    def start(self, **kwargs): pass
    def stop(self): pass


class GameCommand(object):
    '''
    Override:
    def execute(self, game): pass
    '''
    def __init__(self, **kwargs):
        self.kwargs = kwargs or {}

    @classmethod
    def name(cls):
        return cls.__name__.replace('Command', '')

    def pretty_log(self):
        args = []
        for name, values in self.kwargs.items():
            if hasattr(values, '__iter__'):
                arg = ','.join([str(v) for v in values])
            else:
                arg = str(values)
            args.append('%s=%s' % (name, arg))
        kwargs = ' ; '.join(args)
        return '%s(%s)' % (self.name(), kwargs)

    def replay_data(self):
        data = dict(name=self.name())
        if self.kwargs:
            data['args'] = self.kwargs
        return data

    def __str__(self):
        data = self.replay_data()
        return json.dumps(data, sort_keys=True)

    def process(self, game):
        self.execute(game)

    def read_context(self, game):
        pass

    def execute(self, game):
        pass


class PlayerGameCommand(GameCommand):
    '''
    Override:
    def validate(self, game, context): pass
    def execute(self, game): pass
    '''
    def __init__(self, player, **kwargs):
        super(PlayerGameCommand, self).__init__(**kwargs)
        self.player = player

    def pretty_log(self):
        pretty_log = super(PlayerGameCommand, self).pretty_log()
        return '[%s] %s' % (str(self.player), pretty_log)

    def replay_data(self):
        data = super(PlayerGameCommand, self).replay_data()
        data['player'] = str(self.player)
        return data

    def process(self, game):
        context = game.get_context(self.player)
        self.validate(game, context)
        super(PlayerGameCommand, self).process(game)

    def validate(self, game, context):
        'may raise an InvalidCommandError'
        pass


class StartGameCommand(GameCommand):
    def read_context(self, game):
        pass


class EndGameCommand(GameCommand):
    def read_context(self, game):
        self.kwargs['summary'] = game.get_final_result()
        self.kwargs['winners'] = game.winners
        self.kwargs['losers'] = game.losers
        self.kwargs['error_responsibles'] = game.error_responsibles
        self.kwargs['no_contest'] = game.no_contest
        self.kwargs['error'] = game.error
        self.kwargs['draw'] = game.draw


class StartRoundCommand(StartGameCommand):
    def read_context(self, game):
        pass


class EndRoundCommand(EndGameCommand):
    def read_context(self, game):
        pass


class Game(object):
    '''
    Usage:
    game = Game()
    game.start()
    game.print_summary()

    Override:
    def prepare(self): pass
    def get_context(self, player): return super(Game, self).get_context(player)
    def before_play(self): pass
    def play(self): pass
    def before_player_play(self, player, context): pass
    def after_player_play(self, player, context, response=None): pass
    def after_play(self): pass
    def is_the_end(self): return True
    def the_end(self): pass
    def summary(self): return super(Game, self).summary()
    '''
    RandomStrategy = Player
    Player = Player
    StartGameCommand = StartGameCommand
    EndGameCommand = EndGameCommand

    def __init__(self, seed, players, **kwargs):
        self.seed = seed
        self.random = random.Random()
        self.random.seed(seed)

        names = [player.name for player in players]
        if len(names) != len(set(names)):
            raise ValueError('A game can not have more thab one player with the same name.')
        self.players = players
        for player in self.players:
            player.game = self

        self.winners = []
        self.losers = []
        self.draw = False
        self.no_contest = False
        self.error = None
        self.error_message = None
        self.error_responsibles = []

        self.commands = []
        self.kwargs = kwargs

        self.prepare()

    def __getstate__(self):
        odict = self.__dict__.copy()
        return odict

    def log(self, message, level=logging.INFO):
        GATLogger.log(message, prefix=self.__class__.__name__, level=level)

    def save_command(self, command):
        command.read_context(self)
        self.log(command.pretty_log(), logging.INFO)
        # take a snapshot of the object to avoid the original be modified
        self.commands.append(json.loads(json.dumps(command.replay_data())))

    def execute_command(self, command):
        self.save_command(command)
        command.process(self)
        if self.is_the_end():
            raise EndGame()

    def set_no_contest(self, reason):
        self.log(reason, logging.ERROR)
        self.no_contest = True
        self.error = 'U'
        self.error_message = reason
        self.winners = []
        self.losers = []
        self.draw = False

    def set_runtime_error(self, player, error, exception):
        self.log(str(exception), logging.ERROR)

        self.error = error
        self.error_message = str(exception) # optimization
        self.error_responsibles = [str(player)]
        self.loser = player
        for p in self.players:
            if str(p) != str(player):
                self.winners.append(p)
                break
        self.losers = [player]
        if sys.exc_info()[1] and sys.exc_info()[2]:
            raise AlgorithmError(exception)
            # six.reraise(AlgorithmError(exception), sys.exc_info()[1], sys.exc_info()[2])
        else:
            raise AlgorithmError(exception)

    def set_draw(self):
        self.draw = True
        self.winners = []
        self.losers = []

    # Engine methods

    def prepare(self): pass

    def start(self):
        try:
            self.save_command(self.StartGameCommand())
            while not self.is_the_end() and len(self.players) > 0 and not self.error:
                self.before_play()
                self.play()
                self.after_play()
            self.the_end()
        except AlgorithmError as e:
            # set_runtime_error has already setted all variables
            pass
        except EndGame:
            self.log('Games stopped by a command', logging.DEBUG)
            self.after_play()
            self.the_end()
        except Exception as e:
            GATLogger.exception(e)
            self.set_no_contest(str(e))
        finally:
            self.save_command(self.EndGameCommand())
        return self.summary()

    def get_context(self, player):
        return {}

    def before_play(self): pass
    def play(self): pass
    def after_play(self): pass

    def before_player_play(self, player, context): pass

    def player_play(self, player, action='play'):
        context = self.get_context(player)
        self.log('-' * 50, logging.DEBUG)
        self.log('%s playing: %s' % (player, self.printable_data(context)), logging.DEBUG)
        self.before_player_play(player, context)
        try:
            response = player.play(context, action=action)
        except EndGame as e:
            self.after_player_play(player, context, None)
        except AlgorithmTimeoutError as e:
            self.set_runtime_error(player, 'T', e)
        except Exception as e:
            self.set_runtime_error(player, 'RE', e)
        else:
            self.after_player_play(player, context, response)

    def after_player_play(self, player, context, response=None): pass

    def is_the_end(self): raise NotImplementedError('%s: is_the_end' % (self.__class__.__name__))
    def the_end(self): pass

    def summary(self):
        return {
            'draw': self.draw,
            'no_contest': self.no_contest,
            'winners': [str(winner) for winner in self.winners],
            'losers': [str(loser) for loser in self.losers],
            'error': self.error,
            'error_message': self.error_message,
            'error_responsibles': self.error_responsibles,
            'summary': self.get_final_result(),
        }

    def printable_data(self, data):
        if GATLogger.is_verbose():
            return json.dumps(data, sort_keys=True, indent=2 * ' ')
        else:
            return json.dumps(data, sort_keys=True)

    def print_summary(self):
        summary = self.summary()
        self.log('_' * 75, logging.DEBUG)
        self.log(':: Summary', logging.DEBUG)
        self.log(self.printable_data(summary), logging.DEBUG)
        return summary

    def get_final_result(self):
        winners = ','.join([str(player) for player in self.winners])
        if self.error:
            if self.no_contest:
                return 'No contest! %(error)s' % dict(error=self.error_message)
            else:
                error_responsibles = ','.join([str(player) for player in self.error_responsibles])
                return 'Error: %(error)s. Winners: %(winners)s. Error responsibles: %(losers)s.' % dict(error=self.error_message, winners=winners, losers=error_responsibles)
        else:
            if self.draw:
                return 'Draw!'
            else:
                losers = ','.join([str(player) for player in self.losers])
                return 'Winners: %(winners)s. Losers: %(losers)s.' % dict(winners=winners, losers=losers)


class TurnBasedGame(Game):
    '''
    Override:
    def prepare(self): pass
    def get_context(self, player): return super(Game, self).get_context(player)
    def before_play(self): pass
    def start_new_cycle(self): pass
    def before_player_play(self, player, context): pass
    def after_player_play(self, player, context, response=None): pass
    def after_play(self): pass
    def is_the_end(self): return True
    def the_end(self): pass
    def summary(self): return super(Game, self).summary()
    '''
    def __init__(self, seed, players, **kwargs):
        super(TurnBasedGame, self).__init__(seed, players, **kwargs)
        self.random.shuffle(self.players)
        self.player_in_turn = None

    def next_player(self):
        # with this implementation, the game can remove a player safely
        if self.player_in_turn:
            index = self.players.index(self.player_in_turn)
            return self.players[(index + 1) % len(self.players)]
        else:
            return self.players[0]

    def must_start_new_cycle(self):
        return self.player_in_turn == None or self.players.index(self.player_in_turn) == len(self.players) - 1

    def start_new_cycle(self):
        pass

    def play(self):
        if self.must_start_new_cycle():
            self.start_new_cycle()
        self.player_in_turn = self.next_player()
        self.player_play(self.player_in_turn)


class GameComposite(Game):
    '''
    Override:
    Round = CustomRound
    def prepare(self): pass
    def get_context(self, player): return super(Game, self).get_context(player)
    def before_play(self): pass
    def before_start_round(self, round_game): pass
    def after_end_round(self, round_game): pass
    def after_play(self): pass
    def is_the_end(self): return True
    def the_end(self): pass
    def summary(self): return super(Game, self).summary()
    '''
    Round = Game

    def __init__(self, seed, players, **kwargs):
        super(GameComposite, self).__init__(seed, players, **kwargs)
        self.games = []

    def get_context(self, player):
        context = super(GameComposite, self).get_context(player)
        context['game_number'] = len(self.games)
        return context

    def current_game(self):
        return self.games[-1]

    def new_round(self):
        round_game = self.Round(self.random.randint(1, 999999), self.players, **self.kwargs)
        # self.games.append(round_game)
        return round_game

    def before_start_round(self, round_game):
        pass

    def play(self):
        self.log('=' * 100, logging.DEBUG)
        self.log('New round', logging.DEBUG)
        round_game = self.new_round()
        self.before_start_round(round_game)
        round_game.start()
        if round_game.error:
            if round_game.error == 'U':
                self.set_no_contest(round_game.error_message)
            elif round_game.error == 'RE':
                self.set_runtime_error(round_game.error_responsibles[0], round_game.error, round_game.error_message)
        else:
            self.after_end_round(round_game)
            self.commands.extend(round_game.commands)
        round_game.print_summary()

    def after_end_round(self, round_game):
        pass
